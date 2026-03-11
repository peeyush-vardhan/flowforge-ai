from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI
from pydantic import BaseModel


NodeType = Literal["input", "llm", "tool", "branch", "output"]
WorkflowNodeKind = NodeType

NodeOutputReference = str

WorkflowStatus = Literal["draft", "active", "archived"]
ExecutionStatus = Literal["queued", "running", "succeeded", "failed", "cancelled"]
NodeExecutionStatus = Literal["pending", "running", "succeeded", "failed", "skipped"]


class WorkflowPort(BaseModel):
  id: str
  label: str


class NodeConfig(BaseModel):
  __root__: Dict[str, Any | NodeOutputReference]


class Node(BaseModel):
  id: str
  type: NodeType
  label: str
  description: Optional[str] = None
  inputs: Optional[List[WorkflowPort]] = None
  outputs: Optional[List[WorkflowPort]] = None
  config: Optional[NodeConfig] = None


class WorkflowNode(Node):
  kind: Optional[WorkflowNodeKind] = None


class Edge(BaseModel):
  id: str
  sourceNodeId: str
  sourcePortId: Optional[str] = None
  targetNodeId: str
  targetPortId: Optional[str] = None
  label: Optional[str] = None
  condition: Optional[str] = None


class Workflow(BaseModel):
  id: str
  name: str
  description: Optional[str] = None
  nodes: List[Node]
  edges: List[Edge]
  createdAt: Optional[datetime] = None
  updatedAt: Optional[datetime] = None
  version: Optional[int] = None
  status: Optional[WorkflowStatus] = None


WorkflowGraph = Workflow


class StepExecution(BaseModel):
  id: str
  nodeId: str
  status: NodeExecutionStatus
  startedAt: Optional[datetime] = None
  finishedAt: Optional[datetime] = None
  input: Optional[Any] = None
  output: Optional[Any] = None
  error: Optional[str] = None
  logs: Optional[List[str]] = None


class ExecutionRun(BaseModel):
  id: str
  workflowId: str
  status: ExecutionStatus
  startedAt: Optional[datetime] = None
  finishedAt: Optional[datetime] = None
  steps: List[StepExecution]
  input: Optional[Any] = None
  output: Optional[Any] = None
  error: Optional[str] = None


class ValidationError(BaseModel):
  code: str
  message: str
  path: Optional[List[str]] = None
  nodeId: Optional[str] = None


class DecomposedStep(BaseModel):
  id: str
  summary: str
  detail: Optional[str] = None
  dependsOn: Optional[List[str]] = None


class PlannerOutput(BaseModel):
  workflow: Workflow
  validationErrors: Optional[List[ValidationError]] = None
  reasoning: Optional[str] = None


class DecompositionOutput(BaseModel):
  originalPrompt: str
  steps: List[DecomposedStep]


class CompileRequest(BaseModel):
  prompt: str


class CompileResponse(BaseModel):
  workflow: Workflow


app = FastAPI(
  title="FlowForge AI API",
  description="Compile natural language into executable workflow graphs.",
  version="0.1.0",
)


@app.get("/health")
def health() -> dict:
  return {"status": "ok"}


@app.post("/workflow/compile", response_model=CompileResponse)
def compile_workflow(body: CompileRequest) -> CompileResponse:
  """
  Placeholder compiler that returns a simple three-node workflow graph
  matching the shared TypeScript types. In a real implementation, this
  would call an LLM and synthesize a graph.
  """
  now = datetime.utcnow()
  workflow = Workflow(
    id="example-1",
    name="Example workflow",
    description="Example graph synthesized from natural language.",
    nodes=[
      Node(
        id="input",
        type="input",
        label="User Input",
        outputs=[WorkflowPort(id="out", label="Output")],
      ),
      Node(
        id="llm",
        type="llm",
        label="LLM Call",
        inputs=[
          WorkflowPort(id="prompt", label="Prompt"),
          WorkflowPort(id="context", label="Context"),
        ],
        outputs=[WorkflowPort(id="result", label="Result")],
      ),
      Node(
        id="output",
        type="output",
        label="Workflow Output",
        inputs=[WorkflowPort(id="in", label="Input")],
      ),
    ],
    edges=[
      Edge(
        id="e1",
        sourceNodeId="input",
        sourcePortId="out",
        targetNodeId="llm",
        targetPortId="prompt",
        label="prompt",
      ),
      Edge(
        id="e2",
        sourceNodeId="llm",
        sourcePortId="result",
        targetNodeId="output",
        targetPortId="in",
        label="result",
      ),
    ],
    createdAt=now,
    updatedAt=now,
  )
  return CompileResponse(workflow=workflow)

