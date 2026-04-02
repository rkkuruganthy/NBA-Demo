"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_URL = "http://localhost:8001";

interface Decision {
  decision_id: string;
  customer_name: string;
  customer_id: string;
  action: string;
  confidence: number;
  status: string;
  trigger_event: string;
  created_at: string;
}

export default function DecisionsPage() {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/decisions/`)
      .then((r) => r.json())
      .then((data) => {
        setDecisions(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const getActionBadge = (action: string) => {
    switch (action) {
      case "APPROVE": return "badge-approve";
      case "DECLINE": return "badge-decline";
      case "ESCALATE_FOR_REVIEW": return "badge-escalate";
      case "OFFER_RETENTION": return "badge-retention";
      case "REQUEST_DOCUMENTS": return "badge-documents";
      default: return "";
    }
  };

  const getActionLabel = (action: string) => {
    return action.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLETED": return "text-emerald-400";
      case "PENDING": return "text-amber-400";
      case "OVERRIDDEN": return "text-violet-400";
      case "ESCALATED": return "text-red-400";
      default: return "text-gray-400";
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
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Decision History</h1>
          <p className="text-gray-500 text-sm">All recommendations and analyst actions</p>
        </div>
        <Link
          href="/cases/new"
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 text-white text-sm font-medium hover:from-indigo-500 hover:to-cyan-500 transition-all hover:shadow-lg hover:shadow-indigo-500/20"
        >
          + New Case
        </Link>
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
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/30">
            {decisions.map((d, i) => (
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
                <td className="px-6 py-4 text-sm text-gray-300">{d.customer_name || "—"}</td>
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
              </tr>
            ))}
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
