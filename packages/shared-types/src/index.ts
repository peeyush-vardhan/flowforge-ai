export type WorkflowNodeKind =
  | "input"
  | "llm"
  | "tool"
  | "branch"
  | "output";

export interface WorkflowNodeIOPort {
  id: string;
  label: string;
}

export interface WorkflowNode {
  id: string;
  kind: WorkflowNodeKind;
  label: string;
  description?: string;
  inputs?: WorkflowNodeIOPort[];
  outputs?: WorkflowNodeIOPort[];
  config?: Record<string, unknown>;
}

export interface WorkflowEdge {
  id: string;
  sourceNodeId: string;
  sourcePortId?: string;
  targetNodeId: string;
  targetPortId?: string;
  label?: string;
}

export interface WorkflowGraph {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  createdAt?: string;
  updatedAt?: string;
}

