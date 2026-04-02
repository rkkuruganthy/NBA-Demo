"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const API_URL = "http://localhost:8001";

interface Customer {
  customer_id: string;
  name: string;
  segment: string;
  risk_score: number;
  credit_score: number;
  account_id: string;
  account_type: string;
  utilization_pct: number;
  credit_limit: number;
}

const triggerEvents = [
  { value: "CREDIT_LIMIT_REVIEW", label: "Credit Limit Review" },
  { value: "CREDIT_LIMIT_REQUEST", label: "Credit Limit Request" },
  { value: "PAYMENT_DELINQUENCY", label: "Payment Delinquency" },
  { value: "CHURN_SIGNAL", label: "Churn Signal" },
  { value: "ACCOUNT_REVIEW", label: "Account Review" },
  { value: "CUSTOMER_COMPLAINT", label: "Customer Complaint" },
];

export default function NewCasePage() {
  const router = useRouter();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [triggerEvent, setTriggerEvent] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_URL}/customers`)
      .then((r) => r.json())
      .then(setCustomers)
      .catch((e) => setError("Failed to load customers. Is the backend running?"));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCustomer || !triggerEvent) return;

    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_URL}/cases/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: selectedCustomer.customer_id,
          account_id: selectedCustomer.account_id,
          trigger_event: triggerEvent,
          notes: notes || undefined,
        }),
      });

      if (!res.ok) throw new Error(await res.text());
      const result = await res.json();
      sessionStorage.setItem(`decision_${result.decision_id}`, JSON.stringify(result));
      router.push(`/cases/${result.decision_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed");
      setLoading(false);
    }
  };

  const getSegmentColor = (segment: string) => {
    switch (segment) {
      case "premium": return "text-amber-400 bg-amber-400/10 border-amber-400/20";
      case "business": return "text-cyan-400 bg-cyan-400/10 border-cyan-400/20";
      case "young_professional": return "text-violet-400 bg-violet-400/10 border-violet-400/20";
      default: return "text-gray-400 bg-gray-400/10 border-gray-400/20";
    }
  };

  return (
    <div className="max-w-4xl animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">New Case Evaluation</h1>
        <p className="text-gray-500 text-sm">Select a customer and trigger event to generate a recommendation</p>
      </div>

      {error && (
        <div className="glass-card p-4 mb-6 border-red-500/20 flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-red-400" />
          <span className="text-sm text-red-300">{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Customer Selection */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
            </svg>
            Select Customer
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {customers.map((c) => (
              <button
                type="button"
                key={c.customer_id}
                onClick={() => setSelectedCustomer(c)}
                className={`
                  text-left p-4 rounded-xl border transition-all duration-200
                  ${selectedCustomer?.customer_id === c.customer_id
                    ? "border-indigo-500/50 bg-indigo-500/10 glow-indigo"
                    : "border-gray-800/50 bg-gray-900/30 hover:border-gray-700/50 hover:bg-gray-800/30"
                  }
                `}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-white">{c.name}</span>
                  <span className={`badge text-[10px] border ${getSegmentColor(c.segment)}`}>
                    {c.segment}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500">Credit</span>
                    <p className="text-gray-300 font-mono">{c.credit_score}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Utilization</span>
                    <p className="text-gray-300 font-mono">{c.utilization_pct}%</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Risk</span>
                    <p className={`font-mono ${c.risk_score > 0.5 ? "text-red-400" : c.risk_score > 0.3 ? "text-amber-400" : "text-emerald-400"}`}>
                      {(c.risk_score * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Selected Customer Detail */}
        {selectedCustomer && (
          <div className="glass-card p-6 animate-fade-in">
            <h2 className="text-sm font-semibold text-white mb-4">Customer Profile</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <span className="text-xs text-gray-500 uppercase">Account Type</span>
                <p className="text-sm text-gray-200 mt-1">{(selectedCustomer.account_type || "Unknown").replace("_", " ")}</p>
              </div>
              <div>
                <span className="text-xs text-gray-500 uppercase">Credit Limit</span>
                <p className="text-sm text-gray-200 mt-1 font-mono">${(selectedCustomer.credit_limit || 0).toLocaleString()}</p>
              </div>
              <div>
                <span className="text-xs text-gray-500 uppercase">Utilization</span>
                <p className="text-sm text-gray-200 mt-1 font-mono">{((selectedCustomer.utilization_pct || 0) * 100).toFixed(0)}%</p>
              </div>
              <div>
                <span className="text-xs text-gray-500 uppercase">Risk Score</span>
                <p className={`text-sm mt-1 font-mono ${(selectedCustomer.risk_score || 0) > 0.5 ? "text-red-400" : "text-emerald-400"}`}>
                  {(selectedCustomer.risk_score || 0.0).toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Trigger Event */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
            Trigger Event
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {triggerEvents.map((t) => (
              <button
                type="button"
                key={t.value}
                onClick={() => setTriggerEvent(t.value)}
                className={`
                  p-3 rounded-xl border text-sm text-left transition-all duration-200
                  ${triggerEvent === t.value
                    ? "border-indigo-500/50 bg-indigo-500/10 text-indigo-300"
                    : "border-gray-800/50 bg-gray-900/30 text-gray-400 hover:border-gray-700/50 hover:text-gray-300"
                  }
                `}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Notes */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-white mb-4">Notes (Optional)</h2>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add context about this evaluation..."
            rows={3}
            className="w-full bg-gray-900/50 border border-gray-800/50 rounded-xl px-4 py-3 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 resize-none transition-all"
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={!selectedCustomer || !triggerEvent || loading}
          className={`
            w-full py-4 rounded-xl text-sm font-semibold transition-all duration-300
            ${!selectedCustomer || !triggerEvent || loading
              ? "bg-gray-800 text-gray-500 cursor-not-allowed"
              : "bg-gradient-to-r from-indigo-600 to-cyan-600 text-white hover:from-indigo-500 hover:to-cyan-500 hover:shadow-lg hover:shadow-indigo-500/20 active:scale-[0.99]"
            }
          `}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Evaluating...
            </span>
          ) : (
            "Generate Recommendation"
          )}
        </button>
      </form>
    </div>
  );
}
