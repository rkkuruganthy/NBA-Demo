"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { API_URL } from "@/lib/config";
import { 
  Users, 
  Activity, 
  Briefcase, 
  CreditCard, 
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  PlusCircle,
  FileText
} from "lucide-react";

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
  { value: "CREDIT_LIMIT_REVIEW", label: "Credit Limit Review", icon: <CreditCard className="w-4 h-4" /> },
  { value: "CREDIT_LIMIT_REQUEST", label: "Credit Limit Request", icon: <PlusCircle className="w-4 h-4" /> },
  { value: "PAYMENT_DELINQUENCY", label: "Payment Delinquency", icon: <AlertTriangle className="w-4 h-4" /> },
  { value: "CHURN_SIGNAL", label: "Churn Signal", icon: <Activity className="w-4 h-4" /> },
  { value: "ACCOUNT_REVIEW", label: "Account Review", icon: <FileText className="w-4 h-4" /> },
  { value: "CUSTOMER_COMPLAINT", label: "Customer Complaint", icon: <Users className="w-4 h-4" /> },
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
    switch (segment?.toLowerCase()) {
      case "premium": return "text-amber-400 bg-amber-400/10 border-amber-400/20";
      case "business": return "text-cyan-400 bg-cyan-400/10 border-cyan-400/20";
      case "young_professional": return "text-violet-400 bg-violet-400/10 border-violet-400/20";
      default: return "text-gray-400 bg-gray-400/10 border-gray-400/20";
    }
  };

  return (
    <div className="max-w-4xl animate-fade-in mx-auto p-8 h-full overflow-auto">
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

      <form onSubmit={handleSubmit} className="space-y-6 pb-20">
        {/* Customer Selection */}
        <div className="glass-card p-6 border-gray-800/50">
          <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2 uppercase tracking-wider">
            <Users className="w-4 h-4 text-indigo-400" />
            Select Customer
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {(customers || []).map((c) => (
              <button
                type="button"
                key={c.customer_id}
                onClick={() => setSelectedCustomer(c)}
                className={`
                  text-left p-4 rounded-xl border transition-all duration-200 group
                  ${selectedCustomer?.customer_id === c.customer_id
                    ? "border-indigo-500/50 bg-indigo-500/10 glow-indigo"
                    : "border-gray-800/50 bg-gray-900/30 hover:border-gray-700/50 hover:bg-gray-800/30"
                  }
                `}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-sm font-medium transition-colors ${selectedCustomer?.customer_id === c.customer_id ? "text-indigo-300" : "text-white group-hover:text-indigo-200"}`}>
                    {c.name}
                  </span>
                  <span className={`badge text-[10px] border ${getSegmentColor(c.segment)}`}>
                    {c.segment}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-[10px]">
                  <div>
                    <span className="text-gray-500 uppercase tracking-tighter">Credit</span>
                    <p className="text-gray-300 font-mono font-bold">{(c.credit_score || 0).toFixed(0)}</p>
                  </div>
                  <div>
                    <span className="text-gray-500 uppercase tracking-tighter">Util</span>
                    <p className="text-gray-300 font-mono font-bold">{((c.utilization_pct || 0) * 100).toFixed(0)}%</p>
                  </div>
                  <div>
                    <span className="text-gray-500 uppercase tracking-tighter">Risk</span>
                    <p className={`font-mono font-bold ${(c.risk_score || 0) > 0.5 ? "text-red-400" : (c.risk_score || 0) > 0.3 ? "text-amber-400" : "text-emerald-400"}`}>
                      {((c.risk_score || 0) * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Selected Customer Detail */}
        {selectedCustomer && (
          <div className="glass-card p-6 animate-fade-in border-indigo-500/20 bg-indigo-500/5">
            <h2 className="text-sm font-semibold text-indigo-300 mb-4 flex items-center gap-2 uppercase tracking-wider">
              <Briefcase className="w-4 h-4" />
              Customer Profile
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div>
                <span className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">Account Type</span>
                <p className="text-sm text-gray-200 mt-1 font-medium capitalize">{(selectedCustomer.account_type || "Unknown").replace("_", " ")}</p>
              </div>
              <div>
                <span className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">Credit Limit</span>
                <p className="text-sm text-cyan-300 mt-1 font-mono font-bold">
                  ${(Number(selectedCustomer.credit_limit || 0)).toLocaleString()}
                </p>
              </div>
              <div>
                <span className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">Utilization</span>
                <p className="text-sm text-gray-200 mt-1 font-mono font-bold">
                  {((selectedCustomer.utilization_pct || 0) * 100).toFixed(0)}%
                </p>
              </div>
              <div>
                <span className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">Risk Score</span>
                <p className={`text-sm mt-1 font-mono font-bold ${(selectedCustomer.risk_score || 0) > 0.5 ? "text-red-400" : "text-emerald-400"}`}>
                  {(selectedCustomer.risk_score || 0.0).toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Trigger Event */}
        <div className="glass-card p-6 border-gray-800/50">
          <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2 uppercase tracking-wider">
            <Activity className="w-4 h-4 text-emerald-400" />
            Trigger Event
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {triggerEvents.map((t) => (
              <button
                type="button"
                key={t.value}
                onClick={() => setTriggerEvent(t.value)}
                className={`
                  p-4 rounded-xl border text-xs text-left transition-all duration-200 flex flex-col gap-2
                  ${triggerEvent === t.value
                    ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-300 glow-cyan"
                    : "border-gray-800/50 bg-gray-900/30 text-gray-400 hover:border-gray-700/50 hover:text-gray-300"
                  }
                `}
              >
                <div className={`${triggerEvent === t.value ? "text-emerald-400" : "text-gray-500"}`}>
                  {t.icon}
                </div>
                <span className="font-semibold">{t.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Notes */}
        <div className="glass-card p-6 border-gray-800/50">
          <h2 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider flex items-center gap-2">
            <FileText className="w-4 h-4 text-gray-400" />
            Contextual Intelligence Notes
          </h2>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add relevant notes (e.g., requested amount, specific concerns, or customer feedback)..."
            rows={4}
            className="w-full bg-gray-950/50 border border-gray-800 rounded-xl px-4 py-3 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 resize-none transition-all"
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={!selectedCustomer || !triggerEvent || loading}
          className={`
            w-full py-4 rounded-xl text-sm font-bold transition-all duration-300 flex items-center justify-center gap-2
            ${!selectedCustomer || !triggerEvent || loading
              ? "bg-gray-800 text-gray-500 cursor-not-allowed border border-gray-700"
              : "bg-gradient-to-r from-indigo-600 to-cyan-600 text-white hover:from-indigo-500 hover:to-cyan-500 hover:shadow-lg hover:shadow-indigo-500/20 active:scale-[0.99] shadow-xl"
            }
          `}
        >
          {loading ? (
            <>
              <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Analyzing Context Engine...
            </>
          ) : (
            <>
              <CheckCircle2 className="w-5 h-5" />
              Trigger Recommendation
            </>
          )}
        </button>
      </form>
    </div>
  );
}
