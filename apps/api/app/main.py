from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple

from fastapi import FastAPI
from pydantic import BaseModel, RootModel


# Core workflow graph and execution schema (shared with frontend)

NodeType = Literal["input", "llm", "tool", "branch", "output"]
WorkflowNodeKind = NodeType

NodeOutputReference = str

WorkflowStatus = Literal["draft", "active", "archived"]
ExecutionStatus = Literal["queued", "running", "succeeded", "failed", "cancelled"]
NodeExecutionStatus = Literal["pending", "running", "succeeded", "failed", "skipped"]


class WorkflowPort(BaseModel):
  id: str
  label: str


class NodeConfig(RootModel[Dict[str, Any | NodeOutputReference]]):
  """Arbitrary node configuration mapping with support for NodeOutputReference."""
  pass


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


# Lightweight Python view of the node registry (kept in sync with the TS registry)


class RegistryNode(BaseModel):
  id: str
  display_name: str
  category: str
  description: str
  node_type: NodeType
  example_use_cases: List[str]
  prompt_hints_for_planner: List[str]


NODE_REGISTRY: List[RegistryNode] = [
  RegistryNode(
    id="manual_trigger",
    display_name="Manual Trigger",
    category="triggers",
    description="Starts a workflow manually from the UI or an API call.",
    node_type="input",
    example_use_cases=[
      "Run a workflow on demand from an internal tool.",
      "Test a workflow graph before connecting real triggers.",
    ],
    prompt_hints_for_planner=[
      "Use manual_trigger when the user says they want to run the workflow manually or from the app.",
      "Prefer manual_trigger for prototypes or one-off jobs.",
    ],
  ),
  RegistryNode(
    id="webhook_trigger",
    display_name="Webhook Trigger",
    category="triggers",
    description="Starts a workflow when an HTTP webhook is received.",
    node_type="input",
    example_use_cases=[
      "Trigger a workflow when a CRM sends a webhook.",
      "Receive events from a Stripe or Shopify webhook.",
    ],
    prompt_hints_for_planner=[
      "Use webhook_trigger when the user mentions 'webhook', 'HTTP callback', or 'when an external system sends a POST'.",
    ],
  ),
  RegistryNode(
    id="gmail_trigger_mock",
    display_name="Gmail Trigger (Mock)",
    category="triggers",
    description="Simulates a Gmail new-email trigger for prototyping email workflows.",
    node_type="input",
    example_use_cases=[
      "Prototype an email triage workflow without connecting to real Gmail.",
      "Demo summarization or classification of incoming emails.",
    ],
    prompt_hints_for_planner=[
      "Use gmail_trigger_mock when the user describes workflows starting from 'an incoming email' but no real Gmail integration is required.",
      "Prefer gmail_trigger_mock for examples, evals, or offline simulations.",
    ],
  ),
  RegistryNode(
    id="llm_summarize",
    display_name="LLM Summarize",
    category="llm",
    description="Summarizes long text into a concise summary using an LLM.",
    node_type="llm",
    example_use_cases=[
      "Summarize customer support tickets before routing.",
      "Generate short summaries of long status reports.",
    ],
    prompt_hints_for_planner=[
      "Use llm_summarize when the user asks to 'summarize', 'condense', 'TL;DR', or 'shorten' text.",
      "Combine with triggers like gmail_trigger_mock or webhook_trigger when summarizing incoming content.",
    ],
  ),
  RegistryNode(
    id="llm_classify",
    display_name="LLM Classify",
    category="llm",
    description="Classifies text into one of several categories using an LLM.",
    node_type="llm",
    example_use_cases=[
      "Route incoming requests to 'sales', 'support', or 'billing'.",
      "Classify feedback as positive, negative, or neutral.",
    ],
    prompt_hints_for_planner=[
      "Use llm_classify when the user wants to bucket or route items into discrete categories.",
      "Look for words like 'classify', 'label', 'categorize', or 'route based on type'.",
    ],
  ),
  RegistryNode(
    id="llm_extract_fields",
    display_name="LLM Extract Fields",
    category="llm",
    description="Extracts structured fields from unstructured text using an LLM.",
    node_type="llm",
    example_use_cases=[
      "Extract customer name, company, and intent from an email.",
      "Parse order numbers and totals from invoices.",
    ],
    prompt_hints_for_planner=[
      "Use llm_extract_fields when the user wants 'structured data' or 'fields' from free text.",
      "Look for instructions like 'pull out', 'extract', or 'parse into JSON'.",
    ],
  ),
  RegistryNode(
    id="slack_send",
    display_name="Slack Send Message",
    category="integrations",
    description="Sends a message to a Slack channel or user.",
    node_type="tool",
    example_use_cases=[
      "Post a summary of new support tickets to #support.",
      "Send approval requests to a manager in Slack.",
    ],
    prompt_hints_for_planner=[
      "Use slack_send when the user wants to notify a Slack channel or user.",
      "Look for phrases like 'send a Slack message', 'post to Slack', or 'notify in Slack'.",
    ],
  ),
  RegistryNode(
    id="notion_create_page",
    display_name="Notion Create Page",
    category="integrations",
    description="Creates a new Notion page in a specified database.",
    node_type="tool",
    example_use_cases=[
      "Log summarized meeting notes into a Notion database.",
      "Create a page for each new deal or opportunity.",
    ],
    prompt_hints_for_planner=[
      "Use notion_create_page when the user wants to store results or notes in Notion.",
      "Look for phrases like 'log into Notion', 'create a Notion page', or 'save in Notion database'.",
    ],
  ),
  RegistryNode(
    id="http_request",
    display_name="HTTP Request",
    category="integrations",
    description="Performs an HTTP request to an external API.",
    node_type="tool",
    example_use_cases=[
      "Call an internal microservice with data extracted by the LLM.",
      "Send data to a third-party webhook or REST API.",
    ],
    prompt_hints_for_planner=[
      "Use http_request when the user wants to 'call an API', 'send a POST request', or 'hit an endpoint'.",
      "Prefer http_request for generic HTTP integrations that are not covered by a more specific node.",
    ],
  ),
  RegistryNode(
    id="branch_condition",
    display_name="Branch Condition",
    category="control",
    description="Routes execution down different paths based on a boolean condition.",
    node_type="branch",
    example_use_cases=[
      "Route urgent tickets to a priority queue.",
      "Send high-value leads to an account executive while others go to SDRs.",
    ],
    prompt_hints_for_planner=[
      "Use branch_condition when the user describes 'if/else' logic or different flows based on a condition.",
      "Combine with llm_classify or llm_extract_fields when the condition depends on model output.",
    ],
  ),
  RegistryNode(
    id="wait_delay",
    display_name="Wait / Delay",
    category="control",
    description="Pauses execution for a specified duration before continuing.",
    node_type="tool",
    example_use_cases=[
      "Wait 1 hour before sending a follow-up email.",
      "Introduce a small delay to respect external API rate limits.",
    ],
    prompt_hints_for_planner=[
      "Use wait_delay when the user says 'wait', 'pause', 'delay', or 'after X minutes/hours'.",
    ],
  ),
  RegistryNode(
    id="human_approval",
    display_name="Human Approval",
    category="control",
    description="Pauses execution until a human approves or rejects a decision.",
    node_type="tool",
    example_use_cases=[
      "Require manager approval before sending a large discount offer.",
      "Have a human check a generated email before sending to a VIP customer.",
    ],
    prompt_hints_for_planner=[
      "Use human_approval when the user wants 'a human in the loop', 'manual review', or 'manager approval'.",
      "Prefer human_approval for high-risk actions like financial changes or external communications.",
    ],
  ),
]


def list_nodes_py() -> List[RegistryNode]:
  return NODE_REGISTRY


def rank_relevant_nodes_py(user_prompt: str, limit: int = 8) -> List[Tuple[RegistryNode, float]]:
  q = user_prompt.strip().lower()
  if not q:
    return [(n, 1.0) for n in NODE_REGISTRY[:limit]]

  scored: List[Tuple[RegistryNode, float]] = []
  for node in NODE_REGISTRY:
    id_text = node.id.lower()
    name = node.display_name.lower()
    cat = node.category.lower()
    desc = node.description.lower()
    examples = " ".join(node.example_use_cases).lower()
    hints = " ".join(node.prompt_hints_for_planner).lower()

    score = 0.0
    if q in id_text:
      score += 4.0
    if q in name:
      score += 4.0
    if q in cat:
      score += 2.0
    if q in desc:
      score += 3.0
    if q in examples:
      score += 2.0
    if q in hints:
      score += 2.0

    if score > 0:
      scored.append((node, score))

  scored.sort(key=lambda pair: pair[1], reverse=True)
  return scored[:limit]


# Planner / decomposition models


class PlanRequest(BaseModel):
  prompt: str


class RankedNode(BaseModel):
  id: str
  display_name: str
  category: str
  score: float
  reason: Optional[str] = None


class PlanResult(BaseModel):
  user_goal: str
  inputs: List[str]
  outputs: List[str]
  trigger_candidates: List[str]
  action_candidates: List[str]
  external_systems_needed: List[str]
  constraints: List[str]
  unsupported_requirements: List[str]
  clarification_questions_if_needed: List[str]
  confidence_score: float
  ranked_relevant_nodes: List[RankedNode]
  assumptions: List[str]
  warnings: List[str]


class CompileFromPlanRequest(BaseModel):
  plan: PlanResult
  node_ids: Optional[List[str]] = None


class CompileFromPlanResponse(BaseModel):
  workflow: Workflow


def decompose_prompt(prompt: str) -> PlanResult:
  text = prompt.strip()
  lowered = text.lower()

  user_goal = text

  inputs: List[str] = []
  outputs: List[str] = []
  trigger_candidates: List[str] = []
  action_candidates: List[str] = []
  external_systems_needed: List[str] = []
  constraints: List[str] = []
  unsupported_requirements: List[str] = []
  clarification_questions: List[str] = []
  assumptions: List[str] = []
  warnings: List[str] = []

  # Very lightweight heuristics to detect triggers and actions from the prompt.

  if "webhook" in lowered or "http" in lowered:
    trigger_candidates.append("webhook_trigger")
    external_systems_needed.append("http_webhook")

  if "email" in lowered or "gmail" in lowered or "inbox" in lowered:
    trigger_candidates.append("gmail_trigger_mock")
    external_systems_needed.append("email")
    inputs.append("incoming_email")

  if "slack" in lowered:
    action_candidates.append("slack_send")
    external_systems_needed.append("slack")

  if "notion" in lowered:
    action_candidates.append("notion_create_page")
    external_systems_needed.append("notion")

  if "http" in lowered or "api" in lowered or "endpoint" in lowered:
    action_candidates.append("http_request")
    external_systems_needed.append("external_api")

  if any(word in lowered for word in ["summarize", "summary", "summarise", "tl;dr", "shorten"]):
    action_candidates.append("llm_summarize")
    outputs.append("summary")

  if any(word in lowered for word in ["classify", "classification", "label", "route based on type"]):
    action_candidates.append("llm_classify")
    outputs.append("classification_label")

  if any(word in lowered for word in ["extract", "pull out", "parse", "structured data", "fields"]):
    action_candidates.append("llm_extract_fields")
    outputs.append("structured_fields")

  if any(word in lowered for word in ["if ", "else", "branch", "different paths", "depending on"]):
    action_candidates.append("branch_condition")

  if any(word in lowered for word in ["wait", "delay", "after ", "minutes", "hours", "days"]):
    action_candidates.append("wait_delay")

  if any(word in lowered for word in ["approve", "approval", "review", "human in the loop", "manager"]):
    action_candidates.append("human_approval")

  # Unsupported hints (nodes not in registry)
  if "sms" in lowered or "twilio" in lowered:
    unsupported_requirements.append("SMS delivery is not currently supported. Consider using http_request with a custom integration.")

  # Ensure at least one trigger
  if not trigger_candidates:
    trigger_candidates.append("manual_trigger")
    assumptions.append("No explicit trigger mentioned; assuming a manual trigger from the UI.")

  # Remove duplicates while preserving order
  def dedupe(seq: List[str]) -> List[str]:
    seen: set[str] = set()
    result: List[str] = []
    for item in seq:
      if item not in seen:
        seen.add(item)
        result.append(item)
    return result

  trigger_candidates = [c for c in dedupe(trigger_candidates) if c]
  action_candidates = [c for c in dedupe(action_candidates) if c]
  inputs = dedupe(inputs)
  outputs = dedupe(outputs)
  external_systems_needed = dedupe(external_systems_needed)

  # Clarification if nothing or very little was understood
  if not action_candidates:
    clarification_questions.append(
      "What are the main actions this workflow should perform after it is triggered?"
    )
    warnings.append("Planner could not confidently map the request to specific actions.")

  # Rank relevant nodes using the registry as the primary source of truth
  ranked_pairs = rank_relevant_nodes_py(prompt)
  ranked_nodes: List[RankedNode] = []
  for node, score in ranked_pairs:
    ranked_nodes.append(
      RankedNode(
        id=node.id,
        display_name=node.display_name,
        category=node.category,
        score=score,
        reason=f"Matched on category/description/examples for '{prompt}'",
      )
    )

  # Confidence: rough heuristic based on how many registry nodes were matched as triggers/actions.
  matched_ids = set(trigger_candidates + action_candidates)
  matched_count = len([n for n, _ in ranked_pairs if n.id in matched_ids])
  confidence = min(1.0, 0.4 + 0.15 * matched_count)

  return PlanResult(
    user_goal=user_goal,
    inputs=inputs,
    outputs=outputs,
    trigger_candidates=trigger_candidates,
    action_candidates=action_candidates,
    external_systems_needed=external_systems_needed,
    constraints=constraints,
    unsupported_requirements=unsupported_requirements,
    clarification_questions_if_needed=clarification_questions,
    confidence_score=confidence,
    ranked_relevant_nodes=ranked_nodes,
    assumptions=assumptions,
    warnings=warnings,
  )


def compile_plan_to_workflow(plan: PlanResult, node_ids: Optional[List[str]] = None) -> Workflow:
  """
  Compile a simple linear workflow graph from a decomposition plan and an optional
  explicit node selection. Uses only nodes defined in NODE_REGISTRY.
  """
  # Start from user-provided node_ids, falling back to plan triggers/actions and ranked nodes.
  selected_ids: List[str] = []

  if node_ids:
    selected_ids = node_ids[:]
  else:
    selected_ids.extend(plan.trigger_candidates)
    selected_ids.extend(plan.action_candidates)
    # If still sparse, add top ranked nodes until we have a few to work with.
    if len(selected_ids) < 3:
      for rn in plan.ranked_relevant_nodes:
        if rn.id not in selected_ids:
          selected_ids.append(rn.id)
          if len(selected_ids) >= 5:
            break

  # Keep order, drop unknown or duplicates, and restrict to supported nodes.
  registry_by_id: Dict[str, RegistryNode] = {n.id: n for n in NODE_REGISTRY}
  unique_supported_ids: List[str] = []
  for nid in selected_ids:
    if nid in registry_by_id and nid not in unique_supported_ids:
      unique_supported_ids.append(nid)

  if not unique_supported_ids:
    # Minimal fallback: manual trigger only
      unique_supported_ids = ["manual_trigger"]

  # Ensure the first node is a trigger; if not, prepend manual_trigger.
  first_node = registry_by_id.get(unique_supported_ids[0])
  if first_node and first_node.node_type != "input":
    if "manual_trigger" not in unique_supported_ids and "manual_trigger" in registry_by_id:
      unique_supported_ids.insert(0, "manual_trigger")

  nodes: List[Node] = []
  edges: List[Edge] = []

  # Simple mapping from registry node to workflow node ports.
  for idx, nid in enumerate(unique_supported_ids):
    reg = registry_by_id[nid]
    wf_node_id = reg.id

    # Default ports by type/category for MVP.
    if reg.node_type == "input":
      outputs = [WorkflowPort(id="event", label="Event")]
      inputs_ports: Optional[List[WorkflowPort]] = None
    elif reg.node_type == "llm":
      inputs_ports = [WorkflowPort(id="input", label="Input")]
      outputs = [WorkflowPort(id="output", label="Output")]
    elif reg.node_type == "branch":
      inputs_ports = [WorkflowPort(id="input", label="Input")]
      outputs = [
        WorkflowPort(id="true", label="True"),
        WorkflowPort(id="false", label="False"),
      ]
    else:
      inputs_ports = [WorkflowPort(id="input", label="Input")]
      outputs = [WorkflowPort(id="output", label="Output")]

    node = Node(
      id=wf_node_id,
      type=reg.node_type,
      label=reg.display_name,
      description=reg.description,
      inputs=inputs_ports,
      outputs=outputs,
    )
    nodes.append(node)

    if idx > 0:
      prev = nodes[idx - 1]
      edge = Edge(
        id=f"e{idx}",
        sourceNodeId=prev.id,
        sourcePortId=(prev.outputs[0].id if prev.outputs else None),
        targetNodeId=node.id,
        targetPortId=(node.inputs[0].id if node.inputs else None),
      )
      edges.append(edge)

  now = datetime.utcnow()
  workflow = Workflow(
    id="compiled-" + now.strftime("%Y%m%d%H%M%S"),
    name="Compiled workflow",
    description=f"Workflow compiled from plan for: {plan.user_goal}",
    nodes=nodes,
    edges=edges,
    createdAt=now,
    updatedAt=now,
    status="draft",
  )
  return workflow


app = FastAPI(
  title="FlowForge AI API",
  description="Plan and compile natural language into executable workflow graphs.",
  version="0.2.0",
)


@app.get("/health")
def health() -> dict:
  return {"status": "ok"}


@app.post("/plan", response_model=PlanResult)
def plan(body: PlanRequest) -> PlanResult:
  """
  Decompose a natural-language workflow description into a structured planning
  artifact that can be inspected by the frontend and used by the compiler.
  """
  return decompose_prompt(body.prompt)


@app.post("/compile", response_model=CompileFromPlanResponse)
def compile_from_plan(body: CompileFromPlanRequest) -> CompileFromPlanResponse:
  """
  Compile a decomposition plan and selected nodes into a concrete workflow graph.
  Only nodes from the supported registry are used.
  """
  workflow = compile_plan_to_workflow(plan=body.plan, node_ids=body.node_ids)
  return CompileFromPlanResponse(workflow=workflow)


# Legacy endpoint kept for backwards compatibility with earlier scaffolding.


class LegacyCompileRequest(BaseModel):
  prompt: str


class LegacyCompileResponse(BaseModel):
  workflow: Workflow


@app.post("/workflow/compile", response_model=LegacyCompileResponse)
def compile_workflow_legacy(body: LegacyCompileRequest) -> LegacyCompileResponse:
  """
  Backwards-compatible compile endpoint that ignores the prompt and returns a
  simple three-node example graph. Prefer /plan and /compile for new clients.
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
  return LegacyCompileResponse(workflow=workflow)


