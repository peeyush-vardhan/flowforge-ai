"use client";

import React, { useCallback, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  Connection,
  Edge,
  Node
} from "reactflow";
import "reactflow/dist/style.css";

import { Button } from "../components/ui/button";

type WorkflowNodeData = {
  label: string;
};

const initialNodes: Node<WorkflowNodeData>[] = [
  {
    id: "1",
    position: { x: 0, y: 50 },
    data: { label: "User Input" },
    type: "input"
  },
  {
    id: "2",
    position: { x: 250, y: 50 },
    data: { label: "LLM: Draft Workflow" }
  },
  {
    id: "3",
    position: { x: 500, y: 50 },
    data: { label: "Execute Graph" },
    type: "output"
  }
];

const initialEdges: Edge[] = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e2-3", source: "2", target: "3" }
];

export default function HomePage() {
  const [nodes, setNodes] = useState<Node<WorkflowNodeData>[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);
  const [prompt, setPrompt] = useState(
    "Create a three step workflow that takes user input, calls an LLM, and returns the result."
  );

  const onConnect = useCallback(
    (connection: Connection) => setEdges((eds) => addEdge(connection, eds)),
    []
  );

  const handleGenerate = () => {
    // Placeholder: in a real app this would call the API to compile
    // the natural language prompt into a workflow graph.
    console.log("Generate workflow from prompt:", prompt);
  };

  return (
    <main className="flex min-h-screen flex-col gap-4 bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900 px-6 py-4 text-slate-50">
      <header className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            FlowForge AI
          </h1>
          <p className="text-sm text-slate-400">
            Convert natural language into executable workflow graphs.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => window.open("https://localhost:8000/docs", "_blank")}
        >
          API docs
        </Button>
      </header>

      <section className="grid gap-4 md:grid-cols-[minmax(0,1.1fr)_minmax(0,1.7fr)]">
        <div className="flex flex-col gap-3 rounded-2xl border border-slate-800 bg-slate-950/70 p-4 shadow-sm">
          <h2 className="text-sm font-medium text-slate-200">
            Describe your workflow
          </h2>
          <textarea
            className="min-h-[140px] resize-none rounded-xl border border-slate-800 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Create a workflow that validates input, calls an LLM, and then posts results to a webhook."
          />
          <div className="flex items-center justify-between gap-2">
            <p className="text-xs text-slate-500">
              The API will return a strongly-typed workflow graph.
            </p>
            <Button size="sm" onClick={handleGenerate}>
              Generate workflow graph
            </Button>
          </div>
        </div>

        <div className="min-h-[360px] overflow-hidden rounded-2xl border border-slate-800 bg-slate-950/70 shadow-sm">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={setNodes}
            onEdgesChange={setEdges}
            onConnect={onConnect}
            fitView
          >
            <Background gap={16} size={1} />
            <MiniMap />
            <Controls />
          </ReactFlow>
        </div>
      </section>
    </main>
  );
}

