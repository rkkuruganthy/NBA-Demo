"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { API_URL } from "@/lib/config";

interface DriftSignal {
  signal: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  details: string;
  delta?: number;
}

interface TimelineEntry {
  decision_id: string;
  action: string;
  confidence: number;
  status: string;
  reasoning: string;
  trigger_event: string;
  utilization?: number;
  risk_score?: number;
  policies_applied: string[];
  outcome?: string;
  negotiation_steps: number;
  created_at?: string;
}

interface DriftResult {
  customer_id: string;
  has_drift: boolean;
  drift_signals: DriftSignal[];
  decisions_analyzed: number;
  message?: string;
}

interface TimelineResult {
  customer_id: string;
  total_decisions: number;
  timeline: TimelineEntry[];
}

export default function TimelinePage() {
  const params = useParams();
  const customerId = params.customer_id as string;

  const [drift, setDrift] = useState<DriftResult | null>(null);
  const [timeline, setTimeline] = useState<TimelineResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/temporal/${customerId}/drift`).then((r) => r.json()),
      fetch(`${API_URL}/temporal/${customerId}/timeline`).then((r) => r.json()),
    ])
      .then(([d, t]) => {
        setDrift(d);
        setTimeline(t);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [customerId]);

  const getActionConfig = (action: string) => {
    switch (action) {
      case "APPROVE": return { badge: "badge-approve", icon: "✓", color: "text-emerald-400", dot: "bg-emerald-400", line: "border-emerald-500/30" };
      case "DECLINE": return { badge: "badge-decline", icon: "✕", color: "text-red-400", dot: "bg-red-400", line: "border-red-500/30" };
      case "ESCALATE_FOR_REVIEW": return { badge: "badge-escalate", icon: "↑", color: "text-amber-400", dot: "bg-amber-400", line: "border-amber-500/30" };
      case "OFFER_SMS": return { badge: "badge-approve", icon: "💬", color: "text-cyan-400", dot: "bg-cyan-400", line: "border-cyan-500/30" };
      case "OFFER_TRADE_IN": return { badge: "badge-retention", icon: "🔄", color: "text-blue-400", dot: "bg-blue-400", line: "border-blue-500/30" };
      default: return { badge: "", icon: "?", color: "text-gray-400", dot: "bg-gray-400", line: "border-gray-700" };
    }
  };

  const getSeverityConfig = (severity: string) => {
    switch (severity) {
      case "HIGH": return { color: "text-red-400 bg-red-500/10 border-red-500/30", dot: "bg-red-400" };
      case "MEDIUM": return { color: "text-amber-400 bg-amber-500/10 border-amber-500/30", dot: "bg-amber-400" };
      default: return { color: "text-blue-400 bg-blue-500/10 border-blue-500/30", dot: "bg-blue-400" };
    }
  };

  const getOutcomeConfig = (outcome?: string) => {
    switch (outcome) {
      case "POSITIVE": return "text-emerald-400";
      case "NEGATIVE": return "text-red-400";
      case "NEUTRAL": return "text-gray-400";
      default: return "text-gray-600";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  const entries = timeline?.timeline || [];

  return (
    <div className="animate-fade-in p-8 h-full overflow-auto max-w-5xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link href="/decisions" className="text-gray-500 hover:text-gray-300 transition-colors">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Decision Timeline</h1>
          <div className="flex items-center gap-2">
            <p className="text-gray-500 text-sm">Customer</p>
            <span className="font-mono text-xs text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">{customerId}</span>
            <span className="text-gray-500 text-xs">· {timeline?.total_decisions || 0} decisions</span>
          </div>
        </div>
      </div>

      {/* Drift Alert Banner */}
      {drift?.has_drift && drift.drift_signals.length > 0 && (
        <div className="glass-card p-5 mb-8 border border-red-500/20 bg-red-500/5">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
            <h2 className="text-sm font-semibold text-red-400">Behavioral Drift Detected</h2>
            <span className="text-xs text-gray-500">· {drift.drift_signals.length} signal{drift.drift_signals.length !== 1 ? "s" : ""}</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {drift.drift_signals.map((signal, i) => {
              const cfg = getSeverityConfig(signal.severity);
              return (
                <div key={i} className={`flex items-start gap-3 p-3 rounded-xl border ${cfg.color}`}>
                  <div className={`w-2 h-2 rounded-full mt-0.5 shrink-0 ${cfg.dot}`} />
                  <div>
                    <span className="text-xs font-semibold block mb-0.5">{signal.signal.replace(/_/g, " ")}</span>
                    <span className="text-xs opacity-80">{signal.details}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {drift && !drift.has_drift && drift.decisions_analyzed >= 2 && (
        <div className="glass-card p-4 mb-8 border border-emerald-500/20 bg-emerald-500/5 flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-emerald-400" />
          <p className="text-sm text-emerald-400">No behavioral drift detected across {drift.decisions_analyzed} evaluations.</p>
        </div>
      )}

      {/* Timeline */}
      {entries.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <p className="text-gray-500 text-sm">No decisions found for customer <span className="font-mono text-indigo-400">{customerId}</span>.</p>
          <Link href="/cases/new" className="text-indigo-400 hover:text-indigo-300 text-sm mt-3 inline-block">
            Create a case →
          </Link>
        </div>
      ) : (
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-[20px] top-6 bottom-6 w-px bg-gray-800" />

          <div className="space-y-6">
            {entries.map((entry, i) => {
              const cfg = getActionConfig(entry.action);
              const isFirst = i === 0;
              return (
                <div key={entry.decision_id} className="flex gap-6 animate-fade-in" style={{ animationDelay: `${i * 50}ms` }}>
                  {/* Timeline node */}
                  <div className="relative flex-shrink-0">
                    <div className={`w-10 h-10 rounded-full border-2 ${cfg.line} bg-gray-900 flex items-center justify-center z-10 relative`}>
                      <div className={`w-3 h-3 rounded-full ${cfg.dot}`} />
                    </div>
                    {isFirst && (
                      <span className="absolute -top-5 left-1/2 -translate-x-1/2 text-[10px] text-indigo-400 font-semibold whitespace-nowrap">Latest</span>
                    )}
                  </div>

                  {/* Card */}
                  <div className="flex-1 glass-card p-5 mb-0 hover:bg-gray-800/20 transition-all">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Link href={`/cases/${entry.decision_id}`}>
                          <span className="font-mono text-xs text-indigo-400 hover:text-indigo-300 transition-colors">{entry.decision_id}</span>
                        </Link>
                        <span className={`badge text-xs ${cfg.badge}`}>
                          {entry.action.replace(/_/g, " ")}
                        </span>
                      </div>
                      <div className="text-right">
                        {entry.outcome ? (
                          <span className={`text-xs font-semibold ${getOutcomeConfig(entry.outcome)}`}>
                            {entry.outcome === "POSITIVE" ? "✓" : entry.outcome === "NEGATIVE" ? "✕" : "~"} {entry.outcome}
                          </span>
                        ) : (
                          <span className="text-xs text-gray-600">No outcome recorded</span>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs mb-3">
                      <div>
                        <p className="text-gray-500 mb-0.5">Confidence</p>
                        <div className="flex items-center gap-1.5">
                          <div className="w-12 h-1 rounded-full bg-gray-800 overflow-hidden">
                            <div className="h-full rounded-full confidence-gradient" style={{ width: `${entry.confidence * 100}%` }} />
                          </div>
                          <span className="text-white font-mono">{(entry.confidence * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-gray-500 mb-0.5">Trigger</p>
                        <p className="text-white">{entry.trigger_event?.replace(/_/g, " ").toLowerCase()}</p>
                      </div>
                      <div>
                        <p className="text-gray-500 mb-0.5">Status</p>
                        <p className={`font-medium ${
                          entry.status === "COMPLETED" ? "text-emerald-400" :
                          entry.status === "OVERRIDDEN" ? "text-violet-400" :
                          "text-amber-400"
                        }`}>{entry.status}</p>
                      </div>
                      <div>
                        <p className="text-gray-500 mb-0.5">Negotiation Steps</p>
                        <p className="text-white">{entry.negotiation_steps || 0}</p>
                      </div>
                    </div>

                    {entry.policies_applied?.length > 0 && (
                      <div className="flex flex-wrap gap-1.5">
                        {entry.policies_applied.map((pol, j) => (
                          <span key={j} className="text-[10px] text-gray-400 bg-gray-800/60 border border-gray-700/50 px-2 py-0.5 rounded">
                            {pol}
                          </span>
                        ))}
                      </div>
                    )}

                    {entry.created_at && (
                      <p className="text-[10px] text-gray-600 mt-2">
                        {new Date(entry.created_at).toLocaleString()}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
