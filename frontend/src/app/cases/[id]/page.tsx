"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { API_URL } from "@/lib/config";

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

interface ReplayResult {
  decision_id: string;
  customer_id: string;
  trigger_event: string;
  original: { action: string; confidence: number; reasoning?: string; policies?: string[] };
  replayed: { action: string; confidence: number; reasoning?: string; policies?: string[] };
  delta: { action_changed: boolean; confidence_delta: number; drift_detected: boolean };
}

interface WhatIfResult {
  decision_id: string;
  overrides_applied: Record<string, unknown>;
  original: { action: string; confidence: number };
  what_if_result: { action: string; confidence: number; factors?: string[]; policies?: string[] };
  delta: { action_changed: boolean; confidence_delta: number };
}

export default function CaseDetailPage() {
  const params = useParams();
  const decisionId = params.id as string;
  const [decision, setDecision] = useState<Decision | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [actionResult, setActionResult] = useState("");

  // Replay state
  const [replayResult, setReplayResult] = useState<ReplayResult | null>(null);
  const [replayLoading, setReplayLoading] = useState(false);

  // What-If state
  const [whatIfResult, setWhatIfResult] = useState<WhatIfResult | null>(null);
  const [whatIfLoading, setWhatIfLoading] = useState(false);
  const [whatIfOverrides, setWhatIfOverrides] = useState<Record<string, string | number | boolean>>({});
  const [showWhatIf, setShowWhatIf] = useState(false);

  useEffect(() => {
    const stored = sessionStorage.getItem(`decision_${decisionId}`);
    if (stored) {
      setDecision(JSON.parse(stored));
      setLoading(false);
      sessionStorage.removeItem(`decision_${decisionId}`);
      return;
    }
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
      const body =
        action === "approve"
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
      setActionResult(`${action.charAt(0).toUpperCase() + action.slice(1)}d successfully`);
    } catch {
      setActionResult(`${action} failed`);
    }
    setActionLoading("");
  };

  const handleReplay = async () => {
    setReplayLoading(true);
    setReplayResult(null);
    try {
      const res = await fetch(`${API_URL}/cases/${decisionId}/replay`, { method: "POST" });
      const data = await res.json();
      setReplayResult(data);
    } catch {
      console.error("Replay failed");
    }
    setReplayLoading(false);
  };

  const handleWhatIf = async () => {
    setWhatIfLoading(true);
    setWhatIfResult(null);
    try {
      const res = await fetch(`${API_URL}/cases/${decisionId}/what-if`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(whatIfOverrides),
      });
      const data = await res.json();
      setWhatIfResult(data);
    } catch {
      console.error("What-if failed");
    }
    setWhatIfLoading(false);
  };

  const getActionConfig = (action: string) => {
    switch (action) {
      case "APPROVE": return { badge: "badge-approve", label: "Approve", icon: "✓" };
      case "DECLINE": return { badge: "badge-decline", label: "Decline", icon: "✕" };
      case "ESCALATE_FOR_REVIEW": return { badge: "badge-escalate", label: "Escalate", icon: "↑" };
      case "OFFER_RETENTION": return { badge: "badge-retention", label: "Retention", icon: "♥" };
      case "REQUEST_DOCUMENTS": return { badge: "badge-documents", label: "Documents", icon: "📄" };
      case "OFFER_SMS": return { badge: "badge-approve", label: "Send SMS", icon: "💬" };
      case "OFFER_TRADE_IN": return { badge: "badge-retention", label: "Trade-In Offer", icon: "🔄" };
      case "SCARCITY_ALERT": return { badge: "badge-escalate", label: "Scarcity Alert", icon: "⚡" };
      case "VIP_SHOWROOM_INVITE": return { badge: "badge-documents", label: "VIP Invite", icon: "⭐" };
      default: return { badge: "", label: action, icon: "?" };
    }
  };

  const getDeltaColor = (delta: number, changed: boolean) => {
    if (changed) return delta > 0 ? "text-emerald-400" : "text-red-400";
    return delta > 0 ? "text-emerald-400" : delta < 0 ? "text-amber-400" : "text-gray-400";
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
  const policies = (decision.applied_policies || (decision as any).policies || []) as any[];
  const precedents = (decision.precedent_cases || (decision as any).precedents || []) as any[];
  const customerId = (decision as any).customer?.id || (decision as any).customer_summary?.id || "";

  return (
    <div className="animate-fade-in max-w-6xl p-8 h-full overflow-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <Link href="/decisions" className="text-gray-500 hover:text-gray-300 transition-colors">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
              </svg>
            </Link>
            <h1 className="text-2xl font-bold text-white">Case {decisionId}</h1>
          </div>
          <p className="text-gray-500 text-sm ml-8">Decision trace, replay, and what-if analysis</p>
        </div>
        <div className="flex items-center gap-3">
          {customerId && (
            <Link
              href={`/decisions/timeline/${customerId}`}
              className="px-3 py-2 rounded-xl border border-gray-700 text-gray-400 text-sm hover:text-indigo-300 hover:border-indigo-500/40 transition-all"
            >
              📈 View Timeline
            </Link>
          )}
          <span className={`badge text-sm ${actionConfig.badge}`}>
            {actionConfig.icon} {actionConfig.label}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Action Card */}
          <div className={`glass-card p-6 border-l-4 ${
            (decision.recommended_action || (decision as any).action) === "APPROVE" ? "border-l-emerald-500" :
            (decision.recommended_action || (decision as any).action) === "DECLINE" ? "border-l-red-500" :
            (decision.recommended_action || (decision as any).action) === "ESCALATE_FOR_REVIEW" ? "border-l-amber-500" :
            (decision.recommended_action || (decision as any).action) === "OFFER_SMS" ? "border-l-cyan-500" :
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

          {/* ── REPLAY PANEL ── */}
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-white">Decision Replay</h3>
                <p className="text-xs text-gray-500 mt-0.5">Re-run against the current graph state to detect drift</p>
              </div>
              <button
                onClick={handleReplay}
                disabled={replayLoading}
                className="px-4 py-2 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 text-xs font-medium hover:bg-indigo-600/30 transition-all disabled:opacity-50 flex items-center gap-2"
              >
                {replayLoading ? (
                  <><span className="animate-spin w-3 h-3 border border-indigo-400 border-t-transparent rounded-full" /> Replaying...</>
                ) : (
                  "↻ Replay Decision"
                )}
              </button>
            </div>

            {replayResult && (
              <div className="grid grid-cols-2 gap-4 animate-fade-in">
                {/* Original */}
                <div className="p-4 rounded-xl bg-gray-900/50 border border-gray-700">
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Original</p>
                  <div className={`badge mb-2 ${getActionConfig(replayResult.original.action).badge}`}>
                    {replayResult.original.action.replace(/_/g, " ")}
                  </div>
                  <p className="text-xs text-gray-400 font-mono">Confidence: {((replayResult.original.confidence || 0) * 100).toFixed(0)}%</p>
                </div>
                {/* Replayed */}
                <div className={`p-4 rounded-xl border ${
                  replayResult.delta.action_changed
                    ? "bg-amber-500/5 border-amber-500/30"
                    : "bg-emerald-500/5 border-emerald-500/30"
                }`}>
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Replayed (Now)</p>
                  <div className={`badge mb-2 ${getActionConfig(replayResult.replayed.action).badge}`}>
                    {replayResult.replayed.action.replace(/_/g, " ")}
                  </div>
                  <p className="text-xs font-mono">
                    <span className="text-gray-400">Confidence: </span>
                    <span className={getDeltaColor(replayResult.delta.confidence_delta, replayResult.delta.action_changed)}>
                      {(replayResult.replayed.confidence * 100).toFixed(0)}%
                      {replayResult.delta.confidence_delta !== 0 && (
                        <> ({replayResult.delta.confidence_delta > 0 ? "+" : ""}{(replayResult.delta.confidence_delta * 100).toFixed(0)}%)</>
                      )}
                    </span>
                  </p>
                </div>
                {/* Delta Summary */}
                <div className="col-span-2 p-3 rounded-lg bg-gray-900/30 border border-gray-800/50 flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full shrink-0 ${replayResult.delta.drift_detected ? "bg-amber-400" : "bg-emerald-400"}`} />
                  <p className="text-xs text-gray-400">
                    {replayResult.delta.action_changed
                      ? `⚠ Decision drifted: ${replayResult.original.action} → ${replayResult.replayed.action}. Graph state has changed since the original evaluation.`
                      : `✓ No drift detected. The decision would be identical today against the current graph state.`}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* ── WHAT-IF PANEL ── */}
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-white">What-If Analysis</h3>
                <p className="text-xs text-gray-500 mt-0.5">Override graph features and instantly re-evaluate</p>
              </div>
              <button
                onClick={() => setShowWhatIf(!showWhatIf)}
                className="px-4 py-2 rounded-xl bg-violet-600/20 border border-violet-500/30 text-violet-400 text-xs font-medium hover:bg-violet-600/30 transition-all"
              >
                {showWhatIf ? "▲ Collapse" : "▼ Configure Scenario"}
              </button>
            </div>

            {showWhatIf && (
              <div className="animate-fade-in">
                <p className="text-xs text-gray-500 mb-3">Enter override values — only fields you fill will be applied:</p>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
                  {[
                    { key: "utilization_pct", label: "Utilization %", placeholder: "0.50" },
                    { key: "dpd", label: "Days Past Due", placeholder: "0" },
                    { key: "credit_score", label: "Credit Score", placeholder: "720" },
                    { key: "risk_score", label: "Risk Score", placeholder: "0.3" },
                    { key: "view_count", label: "Web Views", placeholder: "4" },
                    { key: "test_drive_count", label: "Test Drives", placeholder: "1" },
                    { key: "care_gap_days", label: "Care Gap Days", placeholder: "7" },
                    { key: "claim_amount", label: "Claim Amount $", placeholder: "50000" },
                    { key: "wire_amount", label: "Wire Amount $", placeholder: "9500" },
                  ].map(({ key, label, placeholder }) => (
                    <div key={key}>
                      <label className="text-[10px] text-gray-500 uppercase tracking-wider mb-1 block">{label}</label>
                      <input
                        type="text"
                        placeholder={placeholder}
                        value={whatIfOverrides[key] !== undefined ? String(whatIfOverrides[key]) : ""}
                        onChange={(e) => {
                          const val = e.target.value;
                          if (val === "") {
                            const next = { ...whatIfOverrides };
                            delete next[key];
                            setWhatIfOverrides(next);
                          } else {
                            setWhatIfOverrides((prev) => ({ ...prev, [key]: isNaN(Number(val)) ? val : Number(val) }));
                          }
                        }}
                        className="w-full bg-gray-900/50 border border-gray-700 rounded-lg px-3 py-2 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-violet-500/50 transition-colors font-mono"
                      />
                    </div>
                  ))}
                </div>
                <button
                  onClick={handleWhatIf}
                  disabled={whatIfLoading || Object.keys(whatIfOverrides).length === 0}
                  className="px-6 py-2.5 rounded-xl bg-violet-600/20 border border-violet-500/30 text-violet-400 text-xs font-medium hover:bg-violet-600/30 transition-all disabled:opacity-50 flex items-center gap-2"
                >
                  {whatIfLoading ? (
                    <><span className="animate-spin w-3 h-3 border border-violet-400 border-t-transparent rounded-full" /> Running...</>
                  ) : (
                    "Run What-If Analysis →"
                  )}
                </button>
              </div>
            )}

            {whatIfResult && (
              <div className="mt-4 animate-fade-in">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-gray-900/50 border border-gray-700">
                    <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Original</p>
                    <div className={`badge mb-2 ${getActionConfig(whatIfResult.original.action).badge}`}>
                      {whatIfResult.original.action.replace(/_/g, " ")}
                    </div>
                    <p className="text-xs text-gray-400 font-mono">Confidence: {((whatIfResult.original.confidence || 0) * 100).toFixed(0)}%</p>
                  </div>
                  <div className={`p-4 rounded-xl border ${
                    whatIfResult.delta.action_changed
                      ? "bg-violet-500/5 border-violet-500/30"
                      : "bg-gray-900/50 border-gray-700"
                  }`}>
                    <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">With Overrides</p>
                    <div className={`badge mb-2 ${getActionConfig(whatIfResult.what_if_result.action).badge}`}>
                      {whatIfResult.what_if_result.action.replace(/_/g, " ")}
                    </div>
                    <p className="text-xs font-mono">
                      <span className="text-gray-400">Confidence: </span>
                      <span className={getDeltaColor(whatIfResult.delta.confidence_delta, whatIfResult.delta.action_changed)}>
                        {(whatIfResult.what_if_result.confidence * 100).toFixed(0)}%
                        {whatIfResult.delta.confidence_delta !== 0 && (
                          <> ({whatIfResult.delta.confidence_delta > 0 ? "+" : ""}{(whatIfResult.delta.confidence_delta * 100).toFixed(0)}%)</>
                        )}
                      </span>
                    </p>
                  </div>
                </div>
                {/* Applied overrides */}
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {Object.entries(whatIfResult.overrides_applied).map(([k, v]) => (
                    <span key={k} className="text-[10px] text-violet-400 bg-violet-500/10 border border-violet-500/20 px-2 py-0.5 rounded font-mono">
                      {k}: {String(v)}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Decision Factors */}
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
                    <span className="text-gray-300 font-mono">{typeof val === "number" ? (key.includes("limit") ? `$${val.toLocaleString()}` : val) : String(val)}</span>
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
              <button onClick={() => handleAction("approve")} disabled={!!actionLoading}
                className="flex-1 py-3 rounded-xl bg-emerald-600/20 border border-emerald-500/30 text-emerald-400 text-sm font-medium hover:bg-emerald-600/30 transition-all disabled:opacity-50">
                {actionLoading === "approve" ? "..." : "✓ Approve"}
              </button>
              <button onClick={() => handleAction("override")} disabled={!!actionLoading}
                className="flex-1 py-3 rounded-xl bg-amber-600/20 border border-amber-500/30 text-amber-400 text-sm font-medium hover:bg-amber-600/30 transition-all disabled:opacity-50">
                {actionLoading === "override" ? "..." : "↻ Override"}
              </button>
              <button onClick={() => handleAction("escalate")} disabled={!!actionLoading}
                className="flex-1 py-3 rounded-xl bg-red-600/20 border border-red-500/30 text-red-400 text-sm font-medium hover:bg-red-600/30 transition-all disabled:opacity-50">
                {actionLoading === "escalate" ? "..." : "↑ Escalate"}
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar — Precedents + Info */}
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
                    <div key={p.decision_id} className="p-4 rounded-xl bg-gray-900/50 border border-gray-800/30">
                      <div className="flex items-center justify-between mb-2">
                        <Link href={`/cases/${p.decision_id}`}>
                          <span className="text-xs font-mono text-indigo-400 hover:text-indigo-300 transition-colors">{p.decision_id}</span>
                        </Link>
                        <span className={`badge text-[10px] ${pConfig.badge}`}>{pConfig.label}</span>
                      </div>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Similarity</span>
                          <span className="text-gray-300 font-mono">{(p.similarity_score * 100).toFixed(0)}%</span>
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
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

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
