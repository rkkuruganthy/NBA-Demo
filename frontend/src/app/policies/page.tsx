"use client";

import { useState } from "react";
import Link from "next/link";

export default function PoliciesPage() {
  const [policies] = useState([
    {
      id: "POL-001",
      name: "Credit Limit Increase - Standard",
      family: "credit_limit",
      description: "Standard credit limit increase eligibility rules.",
      active: true,
    },
    {
      id: "POL-002",
      name: "High Risk Decline",
      family: "risk_management",
      description: "Auto-decline high risk factors like severe delinquency or extremely high utilization.",
      active: true,
    },
    {
      id: "POL-003",
      name: "Retention Offer Eligibility",
      family: "retention",
      description: "Identify churn risks and authorize retention offers.",
      active: true,
    },
    {
      id: "POL-004",
      name: "Escalate Complex Case",
      family: "risk_management",
      description: "Escalate cases with medium-high risk and conflicting positive signals.",
      active: true,
    },
    {
      id: "POL-005",
      name: "Document Request Policy",
      family: "compliance",
      description: "Request additional income verification for specific risk profiles.",
      active: true,
    },
  ]);

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Decision Policies</h1>
          <p className="text-gray-500 text-sm">Rules engine configurations mapping to your graph schema</p>
        </div>
      </div>

      <div className="grid gap-4">
        {policies.map((pol, i) => (
          <div key={pol.id} className="glass-card p-6 border-l-4 border-l-indigo-500 hover:bg-gray-800/20 transition-all">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="text-lg font-bold text-white">{pol.name}</h3>
                <span className="text-xs font-mono text-indigo-400 mt-1 block">{pol.id}</span>
              </div>
              <span className={`px-2 py-1 text-xs rounded-full ${pol.active ? 'bg-emerald-500/10 text-emerald-400' : 'bg-gray-500/10 text-gray-400'}`}>
                {pol.active ? 'Active' : 'Draft'}
              </span>
            </div>
            <p className="text-sm text-gray-400 mt-3">{pol.description}</p>
            <div className="mt-4 flex gap-2">
              <span className="text-xs bg-gray-800 text-gray-300 px-2 py-1 flex items-center gap-1 rounded border border-gray-700">
                <span className="w-2 h-2 rounded-full bg-cyan-400 inline-block"></span>
                {pol.family}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
