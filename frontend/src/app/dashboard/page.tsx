"use client";

import { useEffect, useState } from "react";

interface HealthStatus {
  status: string;
  service: string;
  version: string;
  neo4j: string;
}

export default function DashboardPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8001/health")
      .then((res) => res.json())
      .then((data) => {
        setHealth(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const stats = [
    { label: "Pending Cases", value: "12", change: "+3 today", trend: "up" },
    { label: "Decisions Made", value: "847", change: "+28 this week", trend: "up" },
    { label: "Approval Rate", value: "73%", change: "+2.1%", trend: "up" },
    { label: "Avg Confidence", value: "0.87", change: "-0.02", trend: "down" },
  ];

  const recentCases = [
    { id: "CSE-1042", customer: "Sarah Chen", action: "APPROVE", confidence: 0.94, status: "Completed", time: "2h ago" },
    { id: "CSE-1041", customer: "Marcus Williams", action: "ESCALATE_FOR_REVIEW", confidence: 0.72, status: "Pending Review", time: "3h ago" },
    { id: "CSE-1040", customer: "Elena Rodriguez", action: "OFFER_RETENTION", confidence: 0.88, status: "Awaiting Action", time: "5h ago" },
    { id: "CSE-1039", customer: "James Park", action: "DECLINE", confidence: 0.91, status: "Completed", time: "6h ago" },
    { id: "CSE-1038", customer: "Aisha Patel", action: "REQUEST_DOCUMENTS", confidence: 0.85, status: "Pending", time: "8h ago" },
  ];

  const getActionBadgeClass = (action: string) => {
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
    switch (action) {
      case "APPROVE": return "Approve";
      case "DECLINE": return "Decline";
      case "ESCALATE_FOR_REVIEW": return "Escalate";
      case "OFFER_RETENTION": return "Retention";
      case "REQUEST_DOCUMENTS": return "Documents";
      default: return action;
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Dashboard</h1>
        <p className="text-gray-500 text-sm">Next Best Action overview and recent activity</p>
      </div>

      {/* Backend status banner */}
      {loading ? (
        <div className="glass-card p-4 mb-6 flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-yellow-400 animate-pulse" />
          <span className="text-sm text-gray-400">Connecting to backend...</span>
        </div>
      ) : health ? (
        <div className="glass-card p-4 mb-6 flex items-center gap-3 border-emerald-500/20">
          <div className="w-3 h-3 rounded-full bg-emerald-400" />
          <span className="text-sm text-gray-300">
            {health.service} v{health.version} — Neo4j: {health.neo4j}
          </span>
        </div>
      ) : (
        <div className="glass-card p-4 mb-6 flex items-center gap-3 border-red-500/20">
          <div className="w-3 h-3 rounded-full bg-red-400" />
          <span className="text-sm text-gray-400">Backend unavailable — start with <code className="text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded text-xs">docker compose up</code></span>
        </div>
      )}

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat, i) => (
          <div
            key={stat.label}
            className="glass-card p-5 transition-all duration-300 hover:scale-[1.02] cursor-default"
            style={{ animationDelay: `${i * 100}ms` }}
          >
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{stat.label}</p>
            <p className="text-2xl font-bold text-white mb-1">{stat.value}</p>
            <p className={`text-xs ${stat.trend === "up" ? "text-emerald-400" : "text-red-400"}`}>
              {stat.change}
            </p>
          </div>
        ))}
      </div>

      {/* Recent Cases Table */}
      <div className="glass-card overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-800/50 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white">Recent Cases</h2>
          <a href="/cases/new" className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">
            + New Case
          </a>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800/30">
                <th className="text-left px-6 py-3 font-medium">Case ID</th>
                <th className="text-left px-6 py-3 font-medium">Customer</th>
                <th className="text-left px-6 py-3 font-medium">Recommendation</th>
                <th className="text-left px-6 py-3 font-medium">Confidence</th>
                <th className="text-left px-6 py-3 font-medium">Status</th>
                <th className="text-left px-6 py-3 font-medium">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/30">
              {recentCases.map((c, i) => (
                <tr
                  key={c.id}
                  className="hover:bg-gray-800/20 transition-colors cursor-pointer animate-fade-in"
                  style={{ animationDelay: `${i * 50}ms` }}
                >
                  <td className="px-6 py-4">
                    <span className="text-sm font-mono text-indigo-400">{c.id}</span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-300">{c.customer}</td>
                  <td className="px-6 py-4">
                    <span className={`badge ${getActionBadgeClass(c.action)}`}>
                      {getActionLabel(c.action)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 rounded-full bg-gray-800 overflow-hidden">
                        <div
                          className="h-full rounded-full confidence-gradient"
                          style={{ width: `${c.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400 font-mono">{c.confidence.toFixed(2)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-400">{c.status}</td>
                  <td className="px-6 py-4 text-xs text-gray-500">{c.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
