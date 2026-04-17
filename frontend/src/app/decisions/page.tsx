"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { API_URL } from "@/lib/config";

interface Decision {
  decision_id: string;
  customer_name: string;
  customer_id: string;
  action: string;
  confidence: number;
  status: string;
  trigger_event: string;
  outcome?: string;
  created_at: string;
}

interface OutcomeModalProps {
  decisionId: string;
  onClose: () => void;
  onSuccess: (decisionId: string, result: string) => void;
}

function OutcomeModal({ decisionId, onClose, onSuccess }: OutcomeModalProps) {
  const [result, setResult] = useState("POSITIVE");
  const [revenue, setRevenue] = useState("");
  const [retained, setRetained] = useState(true);
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/decisions/${decisionId}/outcome`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          actual_result: result,
          revenue_impact: revenue ? parseFloat(revenue) : null,
          customer_retained: retained,
          notes,
        }),
      });
      if (!res.ok) throw new Error("Failed");
      onSuccess(decisionId, result);
      onClose();
    } catch {
      setError("Failed to record outcome. Please try again.");
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="glass-card p-6 w-full max-w-md animate-fade-in">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-white">Record Outcome</h2>
            <p className="text-xs text-gray-500 font-mono mt-0.5">{decisionId}</p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors text-xl leading-none">×</button>
        </div>

        <div className="space-y-4">
          {/* Outcome result */}
          <div>
            <label className="text-xs text-gray-400 uppercase tracking-wider mb-2 block">Actual Result</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { val: "POSITIVE", label: "✓ Positive", cls: "border-emerald-500/50 text-emerald-400 bg-emerald-500/10" },
                { val: "NEGATIVE", label: "✕ Negative", cls: "border-red-500/50 text-red-400 bg-red-500/10" },
                { val: "NEUTRAL", label: "~ Neutral", cls: "border-gray-600/50 text-gray-400 bg-gray-800/50" },
              ].map(({ val, label, cls }) => (
                <button
                  key={val}
                  onClick={() => setResult(val)}
                  className={`py-2.5 rounded-xl border text-xs font-medium transition-all ${
                    result === val ? cls : "border-gray-700 text-gray-500 hover:border-gray-600"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Revenue Impact */}
          <div>
            <label className="text-xs text-gray-400 uppercase tracking-wider mb-2 block">Revenue Impact ($)</label>
            <input
              type="number"
              placeholder="e.g. 42000"
              value={revenue}
              onChange={(e) => setRevenue(e.target.value)}
              className="w-full bg-gray-900/50 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500/50 transition-colors"
            />
          </div>

          {/* Customer Retained */}
          <div className="flex items-center justify-between p-4 rounded-xl bg-gray-900/50 border border-gray-700">
            <span className="text-sm text-gray-300">Customer Retained?</span>
            <button
              onClick={() => setRetained(!retained)}
              className={`relative w-10 h-5 rounded-full transition-all ${retained ? "bg-indigo-500" : "bg-gray-700"}`}
            >
              <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all ${retained ? "left-5.5 translate-x-[-2px]" : "left-0.5"}`} style={{ left: retained ? "22px" : "2px" }} />
            </button>
          </div>

          {/* Notes */}
          <div>
            <label className="text-xs text-gray-400 uppercase tracking-wider mb-2 block">Notes (optional)</label>
            <textarea
              placeholder="Add context about this outcome..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              className="w-full bg-gray-900/50 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500/50 transition-colors resize-none"
            />
          </div>

          {error && <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">{error}</p>}

          <div className="flex gap-3 pt-2">
            <button onClick={onClose} className="flex-1 py-3 rounded-xl border border-gray-700 text-gray-400 text-sm hover:border-gray-600 transition-all">
              Cancel
            </button>
            <button
              onClick={submit}
              disabled={loading}
              className="flex-1 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 text-white text-sm font-medium hover:from-indigo-500 hover:to-cyan-500 transition-all disabled:opacity-50"
            >
              {loading ? "Recording..." : "Record Outcome →"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DecisionsPage() {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalDecisionId, setModalDecisionId] = useState<string | null>(null);
  const [recordedOutcomes, setRecordedOutcomes] = useState<Record<string, string>>({});

  useEffect(() => {
    fetch(`${API_URL}/decisions/`)
      .then((r) => r.json())
      .then((data) => {
        setDecisions(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleOutcomeSuccess = (decisionId: string, result: string) => {
    setRecordedOutcomes((prev) => ({ ...prev, [decisionId]: result }));
  };

  const getActionBadge = (action: string) => {
    switch (action) {
      case "APPROVE": return "badge-approve";
      case "DECLINE": return "badge-decline";
      case "ESCALATE_FOR_REVIEW": return "badge-escalate";
      case "OFFER_RETENTION": return "badge-retention";
      case "REQUEST_DOCUMENTS": return "badge-documents";
      case "OFFER_SMS": return "badge-approve";
      case "OFFER_TRADE_IN": return "badge-retention";
      case "SCARCITY_ALERT": return "badge-escalate";
      case "VIP_SHOWROOM_INVITE": return "badge-documents";
      default: return "";
    }
  };

  const getActionLabel = (action: string) =>
    action.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, (l) => l.toUpperCase());

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLETED": return "text-emerald-400";
      case "PENDING": return "text-amber-400";
      case "OVERRIDDEN": return "text-violet-400";
      case "ESCALATED": return "text-red-400";
      default: return "text-gray-400";
    }
  };

  const getOutcomeBadge = (outcome: string) => {
    switch (outcome) {
      case "POSITIVE": return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
      case "NEGATIVE": return "text-red-400 bg-red-500/10 border-red-500/30";
      case "NEUTRAL": return "text-gray-400 bg-gray-800/50 border-gray-600/30";
      default: return "text-gray-600 bg-gray-900/30 border-gray-800/30";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="animate-fade-in p-8 h-full overflow-auto">
      {modalDecisionId && (
        <OutcomeModal
          decisionId={modalDecisionId}
          onClose={() => setModalDecisionId(null)}
          onSuccess={handleOutcomeSuccess}
        />
      )}

      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Decision History</h1>
          <p className="text-gray-500 text-sm">All recommendations, analyst actions, and outcome feedback</p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/decisions/calibration"
            className="px-4 py-2 rounded-xl border border-indigo-500/40 text-indigo-400 text-sm font-medium hover:bg-indigo-500/10 transition-all"
          >
            📊 Calibration Report
          </Link>
          <Link
            href="/cases/new"
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 text-white text-sm font-medium hover:from-indigo-500 hover:to-cyan-500 transition-all hover:shadow-lg hover:shadow-indigo-500/20"
          >
            + New Case
          </Link>
        </div>
      </div>

      <div className="glass-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800/30">
              <th className="text-left px-6 py-3 font-medium">Decision ID</th>
              <th className="text-left px-6 py-3 font-medium">Customer</th>
              <th className="text-left px-6 py-3 font-medium">Action</th>
              <th className="text-left px-6 py-3 font-medium">Confidence</th>
              <th className="text-left px-6 py-3 font-medium">Status</th>
              <th className="text-left px-6 py-3 font-medium">Trigger</th>
              <th className="text-left px-6 py-3 font-medium">Outcome</th>
              <th className="text-left px-6 py-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/30">
            {decisions.map((d, i) => {
              const effectiveOutcome = recordedOutcomes[d.decision_id] || d.outcome;
              return (
                <tr
                  key={d.decision_id}
                  className="hover:bg-gray-800/20 transition-colors animate-fade-in"
                  style={{ animationDelay: `${i * 50}ms` }}
                >
                  <td className="px-6 py-4">
                    <Link href={`/cases/${d.decision_id}`} className="text-sm font-mono text-indigo-400 hover:text-indigo-300 transition-colors">
                      {d.decision_id}
                    </Link>
                  </td>
                  <td className="px-6 py-4">
                    <Link href={`/decisions/timeline/${d.customer_id}`} className="text-sm text-gray-300 hover:text-indigo-300 transition-colors">
                      {d.customer_name || "—"}
                    </Link>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`badge ${getActionBadge(d.action)}`}>
                      {getActionLabel(d.action)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 rounded-full bg-gray-800 overflow-hidden">
                        <div className="h-full rounded-full confidence-gradient" style={{ width: `${d.confidence * 100}%` }} />
                      </div>
                      <span className="text-xs text-gray-400 font-mono">{d.confidence?.toFixed(2)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-xs font-medium ${getStatusColor(d.status)}`}>{d.status}</span>
                  </td>
                  <td className="px-6 py-4 text-xs text-gray-500">
                    {d.trigger_event?.replace(/_/g, " ").toLowerCase()}
                  </td>
                  <td className="px-6 py-4">
                    {effectiveOutcome ? (
                      <span className={`text-xs font-medium px-2 py-1 rounded-lg border ${getOutcomeBadge(effectiveOutcome)}`}>
                        {effectiveOutcome}
                      </span>
                    ) : (
                      <span className="text-xs text-gray-600">—</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => setModalDecisionId(d.decision_id)}
                      className="text-xs text-indigo-400 hover:text-indigo-300 border border-indigo-500/30 hover:border-indigo-400/50 px-2.5 py-1 rounded-lg transition-all whitespace-nowrap"
                    >
                      + Outcome
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {decisions.length === 0 && (
          <div className="p-12 text-center">
            <p className="text-gray-500 text-sm">No decisions yet</p>
            <Link href="/cases/new" className="text-indigo-400 hover:text-indigo-300 text-sm mt-2 inline-block">
              Create your first case →
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
