"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { API_URL } from "@/lib/config";

interface HealthStatus { status: string; service: string; version: string; neo4j: string; }
interface CustomerCounts { total: number; financial: number; aml: number; healthcare: number; insurance: number; ecommerce: number; }
interface RecentDecision { decision_id: string; customer_name: string; customer_id: string; action: string; confidence: number; status: string; trigger_event: string; outcome?: string; }
interface CalibrationSummary { accuracy: number; total_decisions_with_outcomes: number; }

export default function DashboardPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [counts, setCounts] = useState<CustomerCounts | null>(null);
  const [recentDecisions, setRecentDecisions] = useState<RecentDecision[]>([]);
  const [calibration, setCalibration] = useState<CalibrationSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      fetch(`${API_URL}/health`).then((r) => r.json()),
      fetch(`${API_URL}/customers/count`).then((r) => r.json()),
      fetch(`${API_URL}/decisions/?limit=5`).then((r) => r.json()),
      fetch(`${API_URL}/decisions/calibration/report`).then((r) => r.json()),
    ]).then(([h, c, d, cal]) => {
      if (h.status === "fulfilled") setHealth(h.value);
      if (c.status === "fulfilled") setCounts(c.value);
      if (d.status === "fulfilled" && Array.isArray(d.value)) setRecentDecisions(d.value);
      if (cal.status === "fulfilled" && (cal.value as any)?.accuracy !== undefined) setCalibration(cal.value as any);
      setLoading(false);
    });
  }, []);

  const getActionBadgeClass = (action: string) => {
    const map: Record<string, string> = {
      APPROVE: "badge-approve", DECLINE: "badge-decline", ESCALATE_FOR_REVIEW: "badge-escalate",
      OFFER_RETENTION: "badge-retention", REQUEST_DOCUMENTS: "badge-documents",
      OFFER_SMS: "badge-approve", OFFER_TRADE_IN: "badge-retention", SCARCITY_ALERT: "badge-escalate",
    };
    return map[action] || "";
  };

  const getActionLabel = (action: string) =>
    action.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, (l) => l.toUpperCase());

  const verticals = [
    { label: "Financial", count: counts?.financial, icon: "💳", bg: "bg-emerald-400", color: "text-emerald-400" },
    { label: "AML/Fraud", count: counts?.aml, icon: "🚨", bg: "bg-red-400", color: "text-red-400" },
    { label: "Healthcare", count: counts?.healthcare, icon: "🏥", bg: "bg-blue-400", color: "text-blue-400" },
    { label: "Insurance", count: counts?.insurance, icon: "🛡️", bg: "bg-violet-400", color: "text-violet-400" },
    { label: "E-Commerce", count: counts?.ecommerce, icon: "🛒", bg: "bg-amber-400", color: "text-amber-400" },
  ];

  return (
    <div className="animate-fade-in p-8 h-full overflow-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Dashboard</h1>
        <p className="text-gray-500 text-sm">Context Graph Decision Engine — live system overview</p>
      </div>

      {loading ? (
        <div className="glass-card p-4 mb-6 flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-yellow-400 animate-pulse" />
          <span className="text-sm text-gray-400">Connecting to graph engine...</span>
        </div>
      ) : health ? (
        <div className="glass-card p-4 mb-6 flex items-center justify-between border-emerald-500/20">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-emerald-400" />
            <span className="text-sm text-gray-300">
              {health.service} v{health.version} · Neo4j: <span className="text-emerald-400 font-medium">{health.neo4j}</span>
            </span>
          </div>
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span>{counts?.total?.toLocaleString() || "—"} entities</span>
            <span>·</span>
            <span>5 industry verticals</span>
          </div>
        </div>
      ) : (
        <div className="glass-card p-4 mb-6 flex items-center gap-3 border-red-500/20">
          <div className="w-3 h-3 rounded-full bg-red-400" />
          <span className="text-sm text-gray-400">Backend unavailable — <code className="text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded text-xs">docker compose up</code></span>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Total Population", value: counts?.total?.toLocaleString() || "—", sub: "Entities in graph" },
          { label: "Recent Decisions", value: recentDecisions.length > 0 ? recentDecisions.length + "+" : "—", sub: "Loaded" },
          { label: "Engine Accuracy", value: calibration ? `${(calibration.accuracy * 100).toFixed(0)}%` : "—", sub: calibration ? `${calibration.total_decisions_with_outcomes} outcomes` : "No outcomes recorded", highlight: !!calibration },
          { label: "Verticals Active", value: "5", sub: "Fin · AML · Health · Ins · ECOM" },
        ].map((s) => (
          <div key={s.label} className="glass-card p-5">
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{s.label}</p>
            <p className={`text-3xl font-bold mb-1 ${s.highlight ? "text-emerald-400" : "text-white"}`}>{s.value}</p>
            <p className="text-xs text-gray-600">{s.sub}</p>
          </div>
        ))}
      </div>

      {/* Population breakdown */}
      <div className="glass-card p-6 mb-8">
        <h2 className="text-sm font-semibold text-white mb-4">Population by Vertical</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {verticals.map((v) => {
            const pct = counts?.total ? ((v.count || 0) / counts.total) * 100 : 0;
            return (
              <div key={v.label} className="text-center">
                <div className="text-2xl mb-1">{v.icon}</div>
                <p className={`text-lg font-bold font-mono ${v.color}`}>{v.count?.toLocaleString() || "—"}</p>
                <p className="text-xs text-gray-500 mb-2">{v.label}</p>
                <div className="w-full h-1 rounded-full bg-gray-800 overflow-hidden">
                  <div className={`h-full rounded-full ${v.bg}`} style={{ width: `${pct}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Decisions */}
      <div className="glass-card overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-800/50 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white">Recent Decisions</h2>
          <div className="flex items-center gap-4">
            <Link href="/decisions/calibration" className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">📊 Calibration →</Link>
            <Link href="/decisions" className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">All Decisions →</Link>
            <Link href="/cases/new" className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">+ New Case</Link>
          </div>
        </div>
        <table className="w-full">
          <thead>
            <tr className="text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800/30">
              <th className="text-left px-6 py-3 font-medium">Decision ID</th>
              <th className="text-left px-6 py-3 font-medium">Customer</th>
              <th className="text-left px-6 py-3 font-medium">Action</th>
              <th className="text-left px-6 py-3 font-medium">Confidence</th>
              <th className="text-left px-6 py-3 font-medium">Status</th>
              <th className="text-left px-6 py-3 font-medium">Trigger</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/30">
            {recentDecisions.length > 0 ? recentDecisions.map((d, i) => (
              <tr key={d.decision_id} className="hover:bg-gray-800/20 transition-colors" style={{ animationDelay: `${i * 50}ms` }}>
                <td className="px-6 py-4">
                  <Link href={`/cases/${d.decision_id}`} className="text-sm font-mono text-indigo-400 hover:text-indigo-300 transition-colors">{d.decision_id}</Link>
                </td>
                <td className="px-6 py-4 text-sm text-gray-300">{d.customer_name || "—"}</td>
                <td className="px-6 py-4"><span className={`badge ${getActionBadgeClass(d.action)}`}>{getActionLabel(d.action)}</span></td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 rounded-full bg-gray-800 overflow-hidden">
                      <div className="h-full rounded-full confidence-gradient" style={{ width: `${d.confidence * 100}%` }} />
                    </div>
                    <span className="text-xs text-gray-400 font-mono">{d.confidence?.toFixed(2)}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-400">{d.status}</td>
                <td className="px-6 py-4 text-xs text-gray-500">{d.trigger_event?.replace(/_/g, " ").toLowerCase()}</td>
              </tr>
            )) : (
              [0,1,2,3,4].map((i) => (
                <tr key={i} className="border-b border-gray-800/20">
                  {[140, 100, 80, 70, 60, 90].map((w, j) => (
                    <td key={j} className="px-6 py-4"><div className="h-3 bg-gray-800/60 rounded animate-pulse" style={{ width: `${w}px` }} /></td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
