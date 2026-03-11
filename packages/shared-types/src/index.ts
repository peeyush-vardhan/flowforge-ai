/** Node type / kind within a workflow graph. */
export type NodeType = "input" | "llm" | "tool" | "branch" | "output";

/** Backwards-compatible alias. */
export type WorkflowNodeKind = NodeType;

/** String reference to another node output, e.g. `{{nodeId.output.field}}`. */
export type NodeOutputReference = string;

export type WorkflowStatus = "draft" | "active" | "archived";

export type ExecutionStatus =
  | "queued"
  | "running"
  | "succeeded"
  | "failed"
  | "cancelled";

export type NodeExecutionStatus =
  | "pending"
  | "running"
  | "succeeded"
  | "failed"
  | "skipped";

export interface WorkflowPort {
  id: string;
  label: string;
}

export interface NodeConfig {
  /**
   * Arbitrary node configuration. Values may include string references to
   * other node outputs using the `{{nodeId.output.field}}` syntax.
   */
  [key: string]: unknown | NodeOutputReference;
}

export interface Node {
  id: string;
  type: NodeType;
  label: string;
  description?: string;
  inputs?: WorkflowPort[];
  outputs?: WorkflowPort[];
  config?: NodeConfig;
}

/** Backwards-compatible aliases for older names. */
export type WorkflowNodeIOPort = WorkflowPort;
export interface WorkflowNode extends Node {
  kind?: WorkflowNodeKind;
}

export interface Edge {
  id: string;
  sourceNodeId: string;
  sourcePortId?: string;
  targetNodeId: string;
  targetPortId?: string;
  label?: string;
  /**
   * Optional expression controlling whether this edge is taken.
   * May include references such as `{{nodeId.output.field}}`.
   */
  condition?: string;
}

export interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: Node[];
  edges: Edge[];
  createdAt?: string;
  updatedAt?: string;
  version?: number;
  status?: WorkflowStatus;
}

/** Backwards-compatible alias. */
export type WorkflowGraph = Workflow;

export interface StepExecution {
  id: string;
  nodeId: string;
  status: NodeExecutionStatus;
  startedAt?: string;
  finishedAt?: string;
  input?: unknown;
  output?: unknown;
  error?: string;
  logs?: string[];
}

export interface ExecutionRun {
  id: string;
  workflowId: string;
  status: ExecutionStatus;
  startedAt?: string;
  finishedAt?: string;
  steps: StepExecution[];
  input?: unknown;
  output?: unknown;
  error?: string;
}

export interface ValidationError {
  code: string;
  message: string;
  /**
   * JSON-style path into the workflow or config, e.g. ["nodes", "0", "config", "model"].
   */
  path?: string[];
  nodeId?: string;
}

export interface DecomposedStep {
  id: string;
  summary: string;
  detail?: string;
  dependsOn?: string[];
}

export interface PlannerOutput {
  workflow: Workflow;
  validationErrors?: ValidationError[];
  reasoning?: string;
}

export interface DecompositionOutput {
  originalPrompt: string;
  steps: DecomposedStep[];
}


