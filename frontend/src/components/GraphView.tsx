"use client";

import { useEffect, useState, useRef, useMemo } from "react";

// NVL Types
interface NvlNode {
  id: string;
  caption?: string;
  color?: string;
  size?: number;
  selected?: boolean;
}

interface NvlRelationship {
  id: string;
  from: string;
  to: string;
  caption?: string;
  color?: string;
  width?: number;
  selected?: boolean;
}

interface GraphData {
  nodes: any[];
  relationships: any[];
}

export default function GraphView({
  data,
  onNodeClick,
  selectedNodeId,
}: {
  data: GraphData | null;
  onNodeClick?: (node: any) => void;
  selectedNodeId?: string;
}) {
  const [NvlComponent, setNvlComponent] = useState<any>(null);
  const [isReady, setIsReady] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Dynamic import of NVL to avoid SSR issues
  useEffect(() => {
    import("@neo4j-nvl/react").then((mod) => {
      setNvlComponent(() => mod.InteractiveNvlWrapper);
    });
  }, []);

  // Delay interactivity slightly to ensure NVL has fully loaded its canvas
  useEffect(() => {
    if (NvlComponent && data && data.nodes.length > 0) {
      const timer = setTimeout(() => setIsReady(true), 100);
      return () => clearTimeout(timer);
    }
  }, [NvlComponent, data]);

  const nvlData = useMemo(() => {
    if (!data) return { nodes: [], relationships: [] };

    const getColorForLabel = (labels: string[], props?: any) => {
      if (labels.includes("Person") || labels.includes("Patient")) return "#818cf8"; // indigo-400
      if (labels.includes("Device") || labels.includes("IPAddress")) return "#9ca3af"; // gray-400
      if (labels.includes("Fraudster") || labels.includes("Threat")) return "#ef4444"; // red-500
      if (labels.includes("Account")) return "#34d399"; // emerald-400
      if (labels.includes("Decision")) {
        // New decisions (with reasoning from graph traversal) get distinct colors by action
        if (props?.reasoning) {
          const action = props.action || "";
          if (action === "APPROVE") return "#22d3ee"; // cyan-400 — approvals
          if (action === "DECLINE") return "#f59e0b"; // amber-500 — denials
          return "#a855f7"; // purple-500 — escalations/reviews
        }
        return "#f87171"; // red-400 — old decisions without reasoning
      }
      if (labels.includes("NegotiationStep")) return "#fb923c"; // orange-400
      if (labels.includes("Policy")) return "#a78bfa"; // violet-400
      if (labels.includes("DecisionContext") || labels.includes("Context")) return "#fbbf24"; // amber-400
      if (labels.includes("Encounter") || labels.includes("Transaction")) return "#38bdf8"; // sky-400
      if (labels.includes("Prescription") || labels.includes("Diagnosis")) return "#f472b6"; // pink-400
      if (labels.includes("Entity") || labels.includes("Location")) return "#facc15"; // yellow-400
      return "#9ca3af"; // gray-400
    };

    const nodes: NvlNode[] = data.nodes.map((n) => {
      const isSelected = n.id === selectedNodeId;
      const isNewDecision = n.labels.includes("Decision") && n.properties.reasoning;
      
      // Build a meaningful caption
      let caption = n.properties.name || n.labels[0] || "Node";
      if (isNewDecision) {
        // Show the action as caption for new decisions (e.g., "DECLINE", "APPROVE")
        caption = n.properties.action || "Decision";
      } else if (n.labels.includes("Decision")) {
        caption = "Decision";
      } else if (n.properties.decision_type) {
        caption = n.properties.decision_type.replace(/_/g, " ");
      }
      
      return {
        id: n.id,
        caption,
        color: getColorForLabel(n.labels, n.properties),
        size: isNewDecision ? 35 : (isSelected ? 40 : 25),
        selected: isSelected,
      };
    });

    const relationships: NvlRelationship[] = data.relationships.map((r) => {
      return {
        id: r.id,
        from: r.startNode,
        to: r.endNode,
        caption: r.type,
        color: "#4b5563", // gray-600
        width: 1.5,
      };
    });

    return { nodes, relationships };
  }, [data, selectedNodeId]);

  if (!NvlComponent) {
    return (
      <div className="w-full h-full flex items-center justify-center text-gray-500 text-sm">
        <svg className="animate-spin w-5 h-5 mr-3" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        Loading Visualizer...
      </div>
    );
  }

  if (nvlData.nodes.length === 0) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center text-gray-500 text-sm">
        <svg className="w-12 h-12 mb-4 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
        <p>No graph context loaded.</p>
        <p className="text-xs mt-1">Select a case or customer to visualize the context graph.</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full relative" ref={containerRef}>
      <div className="absolute top-4 left-4 z-10 flex gap-2">
         {/* Graph Legend */}
         <div className="glass-card px-3 py-2 text-[10px] flex items-center gap-3 bg-gray-900/80 mt-0 flex-wrap max-w-xl">
           {[
              {label: "Person/Patient", color: "bg-indigo-400"},
              {label: "Account", color: "bg-emerald-400"},
              {label: "Threat/Fraudster", color: "bg-red-500"},
              {label: "Device", color: "bg-gray-400"},
              {label: "Transaction/Event", color: "bg-sky-400"},
              {label: "Medical", color: "bg-pink-400"},
              {label: "Context", color: "bg-amber-400"},
              {label: "Policy", color: "bg-violet-400"},
              {label: "Negotiation", color: "bg-orange-400"},
              {label: "Approve", color: "bg-cyan-400", shape: "diamond"},
              {label: "Decline", color: "bg-amber-500", shape: "diamond"},
              {label: "Escalate", color: "bg-purple-500", shape: "diamond"},
            ].map((legendItem: any, i) => (
              <div key={legendItem.label} className="flex items-center gap-1.5">
                <div className={`w-2 h-2 ${legendItem.shape === 'diamond' ? 'rotate-45' : 'rounded-full'} ${legendItem.color}`} />
                <span className="text-gray-300">{legendItem.label}</span>
              </div>
            ))}
         </div>
      </div>

      <div className="w-full h-full cursor-grab active:cursor-grabbing">
        <NvlComponent
          nodes={nvlData.nodes}
          rels={nvlData.relationships}
          nvlOptions={{
            layout: "random",
            initialZoom: 0.8,
            minZoom: 0.1,
            maxZoom: 5,
            relationshipThickness: 2,
          }}
          mouseEventCallbacks={{
            onNodeClick: (node: NvlNode) => {
              if (onNodeClick && data) {
                const originalNode = data.nodes.find(n => n.id === node.id);
                if (originalNode) onNodeClick(originalNode);
              }
            },
            onZoom: isReady,
            onPan: isReady,
            onDrag: isReady,
          }}
        />
      </div>
    </div>
  );
}
