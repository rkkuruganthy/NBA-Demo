"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { API_URL } from "@/lib/config";

interface CalibrationReport {
  total_decisions_with_outcomes: number;
  accuracy: number;
  overconfidence_rate: number;
  underconfidence_rate: number;
  by_action: Record<string, { total: number; positive: number; negative: number; neutral: number }>;
  message?: string;
}

interface PolicyEffectiveness {
  policy_id: string;
  policy_name: string;
  total_applications: number;
  positive_outcomes: number;
  negative_outcomes: number;
  pending_outcomes: number;
  effectiveness_rate: number | null;
  avg_confidence: number | null;
}

export default function CalibrationPage() {
  const [report, setReport] = useState<CalibrationReport | null>(null);
  const [policies, setPolicies] = useState<PolicyEffectiveness[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/decisions/calibration/report`).then((r) => r.json()),
      fetch(`${API_URL}/decisions/calibration/policy-effectiveness`).then((r) => r.json()),
    ])
      .then(([rep, pol]) => {
        setReport(rep);
        setPolicies(pol);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const getEffectivenessColor = (rate: number | null) => {
    if (rate === null) return "text-gray-500";
    if (rate >= 0.75) return "text-emerald-400";
    if (rate >= 0.5) return "text-amber-400";
    return "text-red-400";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  const hasOutcomes = report && report.total_decisions_with_outcomes > 0;

  return (
    <div className="animate-fade-in p-8 h-full overflow-auto max-w-6xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link href="/decisions" className="text-gray-500 hover:text-gray-300 transition-colors">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Calibration Report</h1>
          <p className="text-gray-500 text-sm">Predicted confidence vs. actual outcomes — the feedback loop that makes the graph compound</p>
        </div>
      </div>

      {/* Thesis callout */}
      <div className="glass-card p-5 mb-8 border-l-4 border-l-indigo-500 bg-indigo-500/5">
        <p className="text-sm text-gray-300 leading-relaxed">
          <span className="text-indigo-400 font-semibold">Context Graph Insight: </span>
          Every decision trace linked to an <span className="font-mono text-xs bg-indigo-500/20 px-1.5 py-0.5 rounded text-indigo-300">(:Outcome)</span> node enables this calibration. 
          Captured traces become searchable precedent. Every automated decision adds another data point to the graph.
        </p>
      </div>

      {!hasOutcomes ? (
        /* Empty state — guide the user to record outcomes */
        <div className="glass-card p-12 text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">📊</span>
          </div>
          <h2 className="text-white font-semibold mb-2">No Outcomes Recorded Yet</h2>
          <p className="text-gray-500 text-sm max-w-sm mx-auto mb-6">
            Record the actual business result of each decision using the &quot;+ Outcome&quot; button on the Decisions page. 
            The calibration report will calculate accuracy, overconfidence and underconfidence rates automatically.
          </p>
          <Link
            href="/decisions"
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 text-white text-sm font-medium hover:from-indigo-500 hover:to-cyan-500 inline-block transition-all"
          >
            Go to Decision History →
          </Link>
        </div>
      ) : (
        <>
          {/* Three Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="glass-card p-6 text-center">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Accuracy</p>
              <p className="text-5xl font-bold text-white font-mono mb-1">
                {(report!.accuracy * 100).toFixed(0)}%
              </p>
              <div className="w-full h-2 rounded-full bg-gray-800 mt-3 overflow-hidden">
                <div className="h-full rounded-full bg-emerald-400" style={{ width: `${report!.accuracy * 100}%` }} />
              </div>
              <p className="text-xs text-gray-500 mt-2">Decisions that produced a positive outcome</p>
            </div>

            <div className="glass-card p-6 text-center">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Overconfidence Rate</p>
              <p className={`text-5xl font-bold font-mono mb-1 ${report!.overconfidence_rate > 0.2 ? "text-red-400" : "text-amber-400"}`}>
                {(report!.overconfidence_rate * 100).toFixed(0)}%
              </p>
              <div className="w-full h-2 rounded-full bg-gray-800 mt-3 overflow-hidden">
                <div className="h-full rounded-full bg-red-400" style={{ width: `${report!.overconfidence_rate * 100}%` }} />
              </div>
              <p className="text-xs text-gray-500 mt-2">Confidence &gt; 80% but outcome was negative</p>
            </div>

            <div className="glass-card p-6 text-center">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Underconfidence Rate</p>
              <p className={`text-5xl font-bold font-mono mb-1 ${report!.underconfidence_rate > 0.2 ? "text-amber-400" : "text-emerald-400"}`}>
                {(report!.underconfidence_rate * 100).toFixed(0)}%
              </p>
              <div className="w-full h-2 rounded-full bg-gray-800 mt-3 overflow-hidden">
                <div className="h-full rounded-full bg-amber-400" style={{ width: `${report!.underconfidence_rate * 100}%` }} />
              </div>
              <p className="text-xs text-gray-500 mt-2">Confidence &lt; 60% but outcome was positive (missed revenue)</p>
            </div>
          </div>

          {/* Actions Breakdown */}
          {Object.keys(report!.by_action).length > 0 && (
            <div className="glass-card p-6 mb-8">
              <h2 className="text-sm font-semibold text-white mb-4">Outcomes by Action Type</h2>
              <div className="space-y-3">
                {Object.entries(report!.by_action).map(([action, counts]) => {
                  const successRate = counts.total > 0 ? counts.positive / counts.total : 0;
                  return (
                    <div key={action} className="flex items-center gap-4">
                      <span className="text-xs text-gray-400 w-40 shrink-0">{action.replace(/_/g, " ")}</span>
                      <div className="flex-1 h-3 rounded-full bg-gray-800 overflow-hidden flex">
                        <div className="h-full bg-emerald-500/70" style={{ width: `${(counts.positive / counts.total) * 100}%` }} />
                        <div className="h-full bg-red-500/70" style={{ width: `${(counts.negative / counts.total) * 100}%` }} />
                        <div className="h-full bg-gray-600/50" style={{ width: `${(counts.neutral / counts.total) * 100}%` }} />
                      </div>
                      <span className="text-xs text-gray-500 w-10 text-right font-mono">{counts.total}</span>
                      <span className={`text-xs font-medium w-14 text-right font-mono ${successRate >= 0.7 ? "text-emerald-400" : successRate >= 0.5 ? "text-amber-400" : "text-red-400"}`}>
                        {(successRate * 100).toFixed(0)}%
                      </span>
                    </div>
                  );
                })}
              </div>
              <div className="flex items-center gap-4 mt-4 text-[10px] text-gray-500">
                <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-sm bg-emerald-500/70 inline-block" /> Positive</span>
                <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-sm bg-red-500/70 inline-block" /> Negative</span>
                <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-sm bg-gray-600/50 inline-block" /> Neutral</span>
              </div>
            </div>
          )}
        </>
      )}

      {/* Policy Effectiveness Table */}
      <div className="glass-card overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-800/50">
          <h2 className="text-sm font-semibold text-white">Policy Effectiveness</h2>
          <p className="text-xs text-gray-500 mt-0.5">Which policies lead to positive outcomes — enables data-driven rule refinement</p>
        </div>
        {policies.length === 0 ? (
          <div className="p-8 text-center text-gray-500 text-sm">
            No policy data yet. Evaluate cases and record outcomes to populate this table.
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800/30">
                <th className="text-left px-6 py-3 font-medium">Policy</th>
                <th className="text-left px-6 py-3 font-medium">Applications</th>
                <th className="text-left px-6 py-3 font-medium">Positive</th>
                <th className="text-left px-6 py-3 font-medium">Negative</th>
                <th className="text-left px-6 py-3 font-medium">Pending</th>
                <th className="text-left px-6 py-3 font-medium">Effectiveness</th>
                <th className="text-left px-6 py-3 font-medium">Avg Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/30">
              {policies.map((p) => (
                <tr key={p.policy_id} className="hover:bg-gray-800/20 transition-colors">
                  <td className="px-6 py-4">
                    <div>
                      <p className="text-sm text-white font-medium">{p.policy_name}</p>
                      <p className="text-xs text-gray-500 font-mono">{p.policy_id}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-300 font-mono">{p.total_applications}</td>
                  <td className="px-6 py-4 text-sm text-emerald-400 font-mono">{p.positive_outcomes}</td>
                  <td className="px-6 py-4 text-sm text-red-400 font-mono">{p.negative_outcomes}</td>
                  <td className="px-6 py-4 text-sm text-gray-500 font-mono">{p.pending_outcomes}</td>
                  <td className="px-6 py-4">
                    {p.effectiveness_rate !== null ? (
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 rounded-full bg-gray-800 overflow-hidden">
                          <div className={`h-full rounded-full ${p.effectiveness_rate >= 0.75 ? "bg-emerald-400" : p.effectiveness_rate >= 0.5 ? "bg-amber-400" : "bg-red-400"}`}
                            style={{ width: `${p.effectiveness_rate * 100}%` }} />
                        </div>
                        <span className={`text-xs font-mono ${getEffectivenessColor(p.effectiveness_rate)}`}>
                          {(p.effectiveness_rate * 100).toFixed(0)}%
                        </span>
                      </div>
                    ) : (
                      <span className="text-xs text-gray-600">—</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-xs text-gray-400 font-mono">
                    {p.avg_confidence ? `${(p.avg_confidence * 100).toFixed(0)}%` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
