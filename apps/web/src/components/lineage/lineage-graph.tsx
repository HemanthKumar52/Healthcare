"use client";

import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  Position,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Badge } from "@/components/ui/badge";

interface LineageData {
  nodes: {
    id: string;
    name: string;
    type: "SOURCE" | "TRANSFORM" | "TARGET";
    description?: string;
  }[];
  edges: {
    id: string;
    source: string;
    target: string;
    label?: string;
  }[];
}

const nodeColors: Record<string, string> = {
  SOURCE: "#3b82f6",
  TRANSFORM: "#f59e0b",
  TARGET: "#22c55e",
};

function LineageNode({ data }: { data: { label: string; type: string; description?: string } }) {
  const color = nodeColors[data.type] ?? "#6b7280";

  return (
    <div className="bg-white border-2 rounded-lg shadow-md px-4 py-3 min-w-[180px]" style={{ borderColor: color }}>
      <div className="flex items-center gap-2 mb-1">
        <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
        <span className="text-xs font-medium uppercase tracking-wide" style={{ color }}>
          {data.type}
        </span>
      </div>
      <div className="font-semibold text-sm text-gray-900">{data.label}</div>
      {data.description && (
        <div className="text-xs text-gray-500 mt-1">{data.description}</div>
      )}
    </div>
  );
}

const nodeTypes = { lineage: LineageNode };

interface LineageGraphProps {
  data: LineageData;
  className?: string;
}

export function LineageGraph({ data, className }: LineageGraphProps) {
  const initialNodes: Node[] = useMemo(() => {
    const sources = data.nodes.filter((n) => n.type === "SOURCE");
    const transforms = data.nodes.filter((n) => n.type === "TRANSFORM");
    const targets = data.nodes.filter((n) => n.type === "TARGET");

    const positionNodes = (nodes: typeof data.nodes, x: number) =>
      nodes.map((n, i) => ({
        id: n.id,
        type: "lineage" as const,
        position: { x, y: i * 120 },
        data: { label: n.name, type: n.type, description: n.description },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
      }));

    return [
      ...positionNodes(sources, 0),
      ...positionNodes(transforms, 350),
      ...positionNodes(targets, 700),
    ];
  }, [data.nodes]);

  const initialEdges: Edge[] = useMemo(
    () =>
      data.edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label,
        animated: true,
        style: { stroke: "#94a3b8", strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#94a3b8" },
      })),
    [data.edges]
  );

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className={className ?? "w-full h-[500px] border rounded-lg bg-gray-50"}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={20} size={1} />
        <Controls />
        <MiniMap
          nodeColor={(node) => nodeColors[(node.data as { type: string }).type] ?? "#6b7280"}
          maskColor="rgba(255, 255, 255, 0.8)"
        />
      </ReactFlow>

      <div className="flex items-center gap-4 p-3 border-t bg-white rounded-b-lg">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-blue-500" />
          <span className="text-xs text-muted-foreground">Source</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-amber-500" />
          <span className="text-xs text-muted-foreground">Transform</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-xs text-muted-foreground">Target</span>
        </div>
      </div>
    </div>
  );
}
