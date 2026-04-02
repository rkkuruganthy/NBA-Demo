"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

const API_URL = "http://localhost:8001";

interface AppliedPolicy {
  policy_id: string;
  policy_name: string;
  family: string;
  matched: boolean;
  details: string;
}

interface Precedent {
  decision_id: string;
  action: string;
  confidence: number;
  outcome: string | null;
  similarity_score: number;
  customer_segment: string;
  trigger_event: string;
  created_at: string | null;
}

interface Decision {
  decision_id: string;
  recommended_action: string;
  confidence: number;
  requires_human_review: boolean;
  applied_policies: AppliedPolicy[];
  precedent_cases: Precedent[];
  explanation_inputs: Record<string, unknown>;
  customer_summary: Record<string, unknown>;
  account_summary: Record<string, unknown>;
}

export default function CaseDetailPage() {
  const params = useParams();
  const decisionId = params.id as string;
  const [decision, setDecision] = useState<Decision | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [actionResult, setActionResult] = useState("");

  useEffect(() => {
    // Try loading from sessionStorage first (just-created decision)
    const stored = sessionStorage.getItem(`decision_${decisionId}`);
    if (stored) {
      setDecision(JSON.parse(stored));
      setLoading(false);
      sessionStorage.removeItem(`decision_${decisionId}`);
      return;
    }

    // Otherwise fetch from API
    fetch(`${API_URL}/decisions/${decisionId}/trace`)
      .then((r) => r.json())
      .then((data) => {
        setDecision(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [decisionId]);

  const handleAction = async (action: string) => {
    setActionLoading(action);
    try {
      const body = action === "approve"
        ? { analyst_id: "analyst_01", notes: "Approved via dashboard" }
        : action === "override"
        ? { analyst_id: "analyst_01", new_action: "APPROVE", rationale: "Override based on additional context and analyst judgment" }
        : { analyst_id: "analyst_01", reason: "Requires senior review due to complex case factors", target_reviewer: "risk_manager_01", urgency: "MEDIUM" };

      const res = await fetch(`${API_URL}/decisions/${decisionId}/${action}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) throw new Error("Action failed");
      const result = await res.json();
      setActionResult(`${action.charAt(0).toUpperCase() + action.slice(1)}d successfully`);
    } catch {
      setActionResult(`${action} failed`);
    }
    setActionLoading("");
  };

  const getActionConfig = (action: string) => {
    switch (action) {
      case "APPROVE": return { badge: "badge-approve", label: "Approve", icon: "✓", gradient: "from-emerald-600 to-emerald-500" };
      case "DECLINE": return { badge: "badge-decline", label: "Decline", icon: "✕", gradient: "from-red-600 to-red-500" };
      case "ESCALATE_FOR_REVIEW": return { badge: "badge-escalate", label: "Escalate", icon: "↑", gradient: "from-amber-600 to-amber-500" };
      case "OFFER_RETENTION": return { badge: "badge-retention", label: "Retention", icon: "♥", gradient: "from-blue-600 to-blue-500" };
      case "REQUEST_DOCUMENTS": return { badge: "badge-documents", label: "Documents", icon: "📄", gradient: "from-violet-600 to-violet-500" };
      default: return { badge: "", label: action, icon: "?", gradient: "from-gray-600 to-gray-500" };
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!decision) {
    return (
      <div className="glass-card p-8 text-center">
        <p className="text-gray-400">Decision not found</p>
        <Link href="/dashboard" className="text-indigo-400 hover:text-indigo-300 mt-4 inline-block text-sm">
          ← Back to Dashboard
        </Link>
      </div>
    );
  }

  const actionConfig = getActionConfig(decision.recommended_action || (decision as any).action);
  const factors = (decision.explanation_inputs as { factors?: string[] })?.factors || [];
  const policies = decision.applied_policies || (decision as any).policies || [];
  const precedents = decision.precedent_cases || (decision as any).precedents || [];

  return (
    <div className="animate-fade-in max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <Link href="/dashboard" className="text-gray-500 hover:text-gray-300 transition-colors">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
              </svg>
            </Link>
            <h1 className="text-2xl font-bold text-white">Case {decisionId}</h1>
          </div>
          <p className="text-gray-500 text-sm ml-8">Recommendation details and decision controls</p>
        </div>
        <span className={`badge text-sm ${actionConfig.badge}`}>
          {actionConfig.icon} {actionConfig.label}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Panel — Recommendation */}
        <div className="lg:col-span-2 space-y-6">
          {/* Action Card */}
          <div className={`glass-card p-6 border-l-4 ${
            decision.recommended_action === "APPROVE" ? "border-l-emerald-500" :
            decision.recommended_action === "DECLINE" ? "border-l-red-500" :
            decision.recommended_action === "ESCALATE_FOR_REVIEW" ? "border-l-amber-500" :
            decision.recommended_action === "OFFER_RETENTION" ? "border-l-blue-500" :
            "border-l-violet-500"
          }`}>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-white mb-1">Recommended Action</h2>
                <p className="text-3xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                  {actionConfig.label}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500 uppercase tracking-wider">Confidence</p>
                <p className="text-3xl font-bold text-white font-mono">{(decision.confidence * 100).toFixed(0)}%</p>
                <div className="w-24 h-2 rounded-full bg-gray-800 mt-2 overflow-hidden">
                  <div className="h-full rounded-full confidence-gradient" style={{ width: `${decision.confidence * 100}%` }} />
                </div>
              </div>
            </div>

            {decision.requires_human_review && (
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-amber-500/10 border border-amber-500/20 mt-3">
                <div className="w-2 h-2 rounded-full bg-amber-400 animate-pulse-glow" />
                <span className="text-xs text-amber-300">Requires human review before action</span>
              </div>
            )}
          </div>

          {/* Explanation Factors */}
          {factors.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-sm font-semibold text-white mb-4">Decision Factors</h3>
              <div className="space-y-2">
                {factors.map((factor, i) => (
                  <div key={i} className="flex items-start gap-3 text-sm">
                    <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                    <span className="text-gray-300">{factor}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Applied Policies */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold text-white mb-4">Applied Policies</h3>
            <div className="space-y-3">
              {policies.map((policy: any) => (
                <div key={policy.policy_id || policy.id || Math.random()} className="p-4 rounded-xl bg-gray-900/50 border border-gray-800/30">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${policy.matched ? "bg-emerald-400" : "bg-gray-600"}`} />
                      <span className="text-sm font-medium text-white">{policy.policy_name}</span>
                    </div>
                    <span className="text-xs text-gray-500 font-mono">{policy.policy_id}</span>
                  </div>
                  <p className="text-xs text-gray-400 ml-4">{policy.details}</p>
                  <span className="inline-block mt-2 ml-4 text-[10px] text-gray-500 bg-gray-800/50 px-2 py-0.5 rounded">{policy.family}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Customer & Account Summary */}
          <div className="grid grid-cols-2 gap-4">
            <div className="glass-card p-6">
              <h3 className="text-sm font-semibold text-white mb-3">Customer</h3>
              <div className="space-y-2 text-xs">
                {Object.entries((decision as any).customer_summary || (decision as any).customer || {}).map(([key, val]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-gray-500 capitalize">{key.replace(/_/g, " ")}</span>
                    <span className="text-gray-300 font-mono">{typeof val === "number" ? (val < 1 && val > 0 ? `${(val * 100).toFixed(0)}%` : val.toLocaleString()) : String(val)}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="glass-card p-6">
              <h3 className="text-sm font-semibold text-white mb-3">Account</h3>
              <div className="space-y-2 text-xs">
                {Object.entries((decision as any).account_summary || (decision as any).account || {}).map(([key, val]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-gray-500 capitalize">{key.replace(/_/g, " ")}</span>
                    <span className="text-gray-300 font-mono">{typeof val === "number" ? (key.includes("limit") ? `$${val.toLocaleString()}` : key.includes("pct") || key.includes("score") ? val : val) : String(val)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Analyst Actions */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold text-white mb-4">Analyst Actions</h3>
            {actionResult && (
              <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 mb-4 text-sm text-emerald-300">
                {actionResult}
              </div>
            )}
            <div className="flex gap-3">
              <button
                onClick={() => handleAction("approve")}
                disabled={!!actionLoading}
                className="flex-1 py-3 rounded-xl bg-emerald-600/20 border border-emerald-500/30 text-emerald-400 text-sm font-medium hover:bg-emerald-600/30 transition-all disabled:opacity-50"
              >
                {actionLoading === "approve" ? "..." : "✓ Approve"}
              </button>
              <button
                onClick={() => handleAction("override")}
                disabled={!!actionLoading}
                className="flex-1 py-3 rounded-xl bg-amber-600/20 border border-amber-500/30 text-amber-400 text-sm font-medium hover:bg-amber-600/30 transition-all disabled:opacity-50"
              >
                {actionLoading === "override" ? "..." : "↻ Override"}
              </button>
              <button
                onClick={() => handleAction("escalate")}
                disabled={!!actionLoading}
                className="flex-1 py-3 rounded-xl bg-red-600/20 border border-red-500/30 text-red-400 text-sm font-medium hover:bg-red-600/30 transition-all disabled:opacity-50"
              >
                {actionLoading === "escalate" ? "..." : "↑ Escalate"}
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar — Precedents */}
        <div className="space-y-6">
          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold text-white mb-4">Similar Precedents</h3>
            {precedents.length === 0 ? (
              <p className="text-xs text-gray-500">No similar precedents found</p>
            ) : (
              <div className="space-y-3">
                {precedents.map((p: any) => {
                  const pConfig = getActionConfig(p.action);
                  return (
                    <div key={p.decision_id} className="p-4 rounded-xl bg-gray-900/50 border border-gray-800/30 animate-slide-in-right">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-mono text-indigo-400">{p.decision_id}</span>
                        <span className={`badge text-[10px] ${pConfig.badge}`}>{pConfig.label}</span>
                      </div>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Similarity</span>
                          <div className="flex items-center gap-2">
                            <div className="w-12 h-1 rounded-full bg-gray-800 overflow-hidden">
                              <div className="h-full rounded-full bg-indigo-400" style={{ width: `${p.similarity_score * 100}%` }} />
                            </div>
                            <span className="text-gray-300 font-mono">{(p.similarity_score * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Confidence</span>
                          <span className="text-gray-300 font-mono">{(p.confidence * 100).toFixed(0)}%</span>
                        </div>
                        {p.outcome && (
                          <div className="flex justify-between">
                            <span className="text-gray-500">Outcome</span>
                            <span className={`font-mono ${p.outcome === "POSITIVE" ? "text-emerald-400" : p.outcome === "NEGATIVE" ? "text-red-400" : "text-gray-400"}`}>
                              {p.outcome}
                            </span>
                          </div>
                        )}
                        <div className="flex justify-between">
                          <span className="text-gray-500">Segment</span>
                          <span className="text-gray-300">{p.customer_segment}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Trigger</span>
                          <span className="text-gray-300">{p.trigger_event.replace(/_/g, " ").toLowerCase()}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Quick Stats */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold text-white mb-3">Decision Info</h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">Decision ID</span>
                <span className="text-gray-300 font-mono">{decision.decision_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Human Review</span>
                <span className={decision.requires_human_review ? "text-amber-400" : "text-emerald-400"}>
                  {decision.requires_human_review ? "Required" : "Not Required"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Policies Used</span>
                <span className="text-gray-300">{policies.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Precedents</span>
                <span className="text-gray-300">{precedents.length}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
