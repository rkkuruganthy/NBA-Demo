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
  const [tooltip, setTooltip] = useState<{ x: number, y: number, content: string, label: string, properties: any, visible: boolean }>({
    x: 0, y: 0, content: "", label: "", properties: null, visible: false
  });

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
    <div 
      className="w-full h-full relative overflow-hidden" 
      ref={containerRef}
    >
      {/* Tooltip */}
      {tooltip.visible && (
        <div 
          className="fixed z-[9999] pointer-events-none px-3 py-2 bg-gray-950/95 border border-indigo-500/50 rounded-xl shadow-[0_0_30px_rgba(79,70,229,0.3)] backdrop-blur-xl animate-in fade-in zoom-in duration-200 min-w-[220px]"
          style={{ 
            left: tooltip.x + 20, 
            top: tooltip.y + 20,
            transform: 'translate3d(0, 0, 0)' // Force hardware acceleration
          }}
        >
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between border-b border-gray-800/50 pb-1.5 mb-0.5">
              <span className="text-[9px] text-indigo-400 uppercase tracking-widest font-black">
                {tooltip.label}
              </span>
              <span className="text-[9px] text-gray-600 font-mono">{String(tooltip.properties?.id || '').substring(0, 8)}</span>
            </div>
            
            <span className="text-sm text-white font-bold leading-tight">
              {tooltip.content}
            </span>

            {/* Properties List */}
            {tooltip.properties && (
              <div className="flex flex-col gap-1 mt-1">
                {Object.entries(tooltip.properties).map(([key, value]) => {
                  if (['id', 'name', 'reasoning', 'graph_features', 'ranked_actions', 'applied_policies', 'precedent_cases'].includes(key)) return null;
                  if (key.includes('date') || key.includes('timestamp')) return null;
                  return (
                    <div key={key} className="flex items-center justify-between bg-white/5 px-1.5 py-0.5 rounded text-[10px]">
                      <span className="text-gray-500 lowercase">{key.replace(/_/g, ' ')}:</span>
                      <span className="text-indigo-200 font-mono ml-3">
                        {typeof value === 'number' ? (key.includes('score') || key === 'confidence' ? `${(value * 100).toFixed(0)}%` : value) : String(value)}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
            
            <div className="flex items-center gap-1.5 mt-1 border-t border-gray-800/50 pt-1.5">
              <div className="w-1 h-1 rounded-full bg-indigo-500 animate-pulse" />
              <span className="text-[8px] text-gray-500 uppercase tracking-tighter">
                Click node to lock properties in side panel
              </span>
            </div>
          </div>
        </div>
      )}

      <div className="absolute top-4 left-4 z-10 flex gap-2">
         {/* Graph Legend */}
         <div className="glass-card px-3 py-2 text-[10px] flex items-center gap-3 bg-gray-900/80 mt-0 flex-wrap max-w-xl border border-gray-800/50">
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
            onHover: (element: any, _hitTargets: any, event: MouseEvent) => {
              // element is the NVL render object (id, caption, color…) — no labels property.
              // Match against our original data to get labels + properties.
              if (element && data) {
                const originalNode = data.nodes.find((n: any) => n.id === element.id);
                if (originalNode) {
                  setTooltip({
                    x: event.clientX,
                    y: event.clientY,
                    label: originalNode.labels?.[1] || originalNode.labels?.[0] || "Node",
                    content: originalNode.properties?.name || originalNode.properties?.action || originalNode.id,
                    properties: originalNode.properties,
                    visible: true,
                  });
                  return;
                }
              }
              // No node under cursor (empty canvas or relationship) — hide tooltip
              setTooltip(prev => ({ ...prev, visible: false }));
            },
            // Force these to true to ensure graph is NEVER locked
            onZoom: true,
            onPan: true,
            onDrag: true,
          }}
        />
      </div>
    </div>
  );
}
