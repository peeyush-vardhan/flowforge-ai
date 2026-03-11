from datetime import datetime
from typing import List, Literal, Optional

from fastapi import FastAPI
from pydantic import BaseModel

WorkflowNodeKind = Literal["input", "llm", "tool", "branch", "output"]


class WorkflowNodeIOPort(BaseModel):
  id: str
  label: str


class WorkflowNode(BaseModel):
  id: str
  kind: WorkflowNodeKind
  label: str
  description: Optional[str] = None
  inputs: Optional[List[WorkflowNodeIOPort]] = None
  outputs: Optional[List[WorkflowNodeIOPort]] = None
  config: Optional[dict] = None


class WorkflowEdge(BaseModel):
  id: str
  sourceNodeId: str
  sourcePortId: Optional[str] = None
  targetNodeId: str
  targetPortId: Optional[str] = None
  label: Optional[str] = None


class WorkflowGraph(BaseModel):
  id: str
  name: str
  description: Optional[str] = None
  nodes: List[WorkflowNode]
  edges: List[WorkflowEdge]
  createdAt: Optional[datetime] = None
  updatedAt: Optional[datetime] = None


class CompileRequest(BaseModel):
  prompt: str


class CompileResponse(BaseModel):
  workflow: WorkflowGraph


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
  workflow = WorkflowGraph(
    id="example-1",
    name="Example workflow",
    description="Example graph synthesized from natural language.",
    nodes=[
      WorkflowNode(id="input", kind="input", label="User Input", outputs=[WorkflowNodeIOPort(id="out", label="Output")]),
      WorkflowNode(
        id="llm",
        kind="llm",
        label="LLM Call",
        inputs=[
          WorkflowNodeIOPort(id="prompt", label="Prompt"),
          WorkflowNodeIOPort(id="context", label="Context"),
        ],
        outputs=[WorkflowNodeIOPort(id="result", label="Result")],
      ),
      WorkflowNode(id="output", kind="output", label="Workflow Output", inputs=[WorkflowNodeIOPort(id="in", label="Input")]),
    ],
    edges=[
      WorkflowEdge(id="e1", sourceNodeId="input", sourcePortId="out", targetNodeId="llm", targetPortId="prompt", label="prompt"),
      WorkflowEdge(id="e2", sourceNodeId="llm", sourcePortId="result", targetNodeId="output", targetPortId="in", label="result"),
    ],
    createdAt=now,
    updatedAt=now,
  )
  return CompileResponse(workflow=workflow)

