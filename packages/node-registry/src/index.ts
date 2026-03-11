import type { WorkflowNode, WorkflowNodeKind } from "@flowforge/shared-types";

export interface RegistryNodeMeta extends WorkflowNode {
  kind: WorkflowNodeKind;
  tags?: string[];
  category?: string;
}

export const nodeRegistry: RegistryNodeMeta[] = [
  {
    id: "input",
    kind: "input",
    label: "User Input",
    description: "Entry point for user-provided data or prompts.",
    category: "core",
    tags: ["core", "entry"],
    outputs: [{ id: "out", label: "Output" }]
  },
  {
    id: "llm",
    kind: "llm",
    label: "LLM Call",
    description: "Call an LLM with a prompt and optional context.",
    category: "ai",
    tags: ["ai", "llm"],
    inputs: [
      { id: "prompt", label: "Prompt" },
      { id: "context", label: "Context" }
    ],
    outputs: [{ id: "result", label: "Result" }]
  },
  {
    id: "output",
    kind: "output",
    label: "Workflow Output",
    description: "Finalize and return the workflow result.",
    category: "core",
    tags: ["core", "exit"],
    inputs: [{ id: "in", label: "Input" }]
  }
];

export function getNodeById(id: string): RegistryNodeMeta | undefined {
  return nodeRegistry.find((n) => n.id === id);
}

