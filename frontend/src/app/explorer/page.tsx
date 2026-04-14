"use client";

import { useState, useEffect, useRef } from "react";
import { Panel, Group as PanelGroup, Separator as PanelResizeHandle } from "react-resizable-panels";
import { MessageSquare, Network, BrainCircuit, Activity, AlertCircle, Maximize2, X, ArrowRight, CheckCircle, XCircle, RefreshCw } from "lucide-react";
import dynamic from "next/dynamic";
import Link from "next/link";

// Dynamically import GraphView to avoid SSR issues with canvas
const GraphView = dynamic(() => import("../../components/GraphView"), {
  ssr: false,
  loading: () => <div className="p-8 text-gray-500 animate-pulse">Loading visualizer...</div>
});

import { API_URL } from "../../lib/config";
import { useSidebar } from "@/context/SidebarContext";

export default function ExplorerPage() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [graphData, setGraphData] = useState<any>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  
  // Action state
  const [activeCustomer, setActiveCustomer] = useState("");
  const [triggerEvent, setTriggerEvent] = useState("CREDIT_LIMIT_REVIEW");
  const [logs, setLogs] = useState<any[]>([]);
  const [isEvaluating, setIsEvaluating] = useState(false);
  
  // Negotiation state
  const [activeDecision, setActiveDecision] = useState<any>(null);
  const [showCounterInput, setShowCounterInput] = useState(false);
  const [counterValue, setCounterValue] = useState("");
  const [isNegotiating, setIsNegotiating] = useState(false);
  
  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [industryFilter, setIndustryFilter] = useState("");
  const [popCount, setPopCount] = useState<any>({ total: 0, financial: 0, aml: 0, healthcare: 0, ecommerce: 0 });
  const [showSearch, setShowSearch] = useState(false);
  
  const logEndRef = useRef<HTMLDivElement>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Fetch population count
    fetch(`${API_URL}/customers/count`)
      .then(res => res.json())
      .then(data => setPopCount(data))
      .catch(console.error);
    
    // Fetch initial page of customers
    fetch(`${API_URL}/customers?limit=50`)
      .then(res => res.json())
      .then(data => setCustomers(data))
      .catch(console.error);
    
    setLogs([{
      id: "sys-0",
      role: "system",
      content: "Welcome to the Context Graph Explorer. Select a customer and trigger an evaluation to see the decision trace.",
      timestamp: new Date().toISOString()
    }]);
  }, []);

  // Debounced search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    searchTimeoutRef.current = setTimeout(() => {
      const params = new URLSearchParams({ limit: "50" });
      if (query) params.set("search", query);
      if (industryFilter) params.set("industry", industryFilter);
      fetch(`${API_URL}/customers?${params}`)
        .then(res => res.json())
        .then(data => setCustomers(data))
        .catch(console.error);
    }, 300);
  };

  const handleIndustryFilter = (ind: string) => {
    const newInd = industryFilter === ind ? "" : ind;
    setIndustryFilter(newInd);
    const params = new URLSearchParams({ limit: "50" });
    if (searchQuery) params.set("search", searchQuery);
    if (newInd) params.set("industry", newInd);
    fetch(`${API_URL}/customers?${params}`)
      .then(res => res.json())
      .then(data => setCustomers(data))
      .catch(console.error);
  };

  const selectCustomer = (id: string, trigger?: string) => {
    setActiveCustomer(id);
    setSelectedNode(null);
    setActiveDecision(null);
    setShowCounterInput(false);
    if (trigger) setTriggerEvent(trigger);
    else {
      if (id.startsWith("AML") || id.includes("AML")) setTriggerEvent("FRAUD_DETECTION");
      else if (id.startsWith("MED") || id.includes("MED")) setTriggerEvent("CARE_GAP_REVIEW");
      else if (id.startsWith("ECOM") || id.includes("ECOM")) setTriggerEvent("ABANDONED_SESSION");
      else setTriggerEvent("CREDIT_LIMIT_REVIEW");
    }
    if (id) {
      loadGraph(id);
      setLogs(prev => [...prev, {
        id: `sys-${Date.now()}`,
        role: "system",
        content: `Loaded context graph for customer ${id}.`,
        timestamp: new Date().toISOString()
      }]);
    } else {
      setGraphData(null);
    }
  };

  // Auto-scroll logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const loadGraph = async (customerId: string) => {
    try {
      const res = await fetch(`${API_URL}/explorer/customer/${customerId}`);
      const data = await res.json();
      setGraphData(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleEvaluate = async () => {
    if (!activeCustomer) return;
    
    setIsEvaluating(true);
    setActiveDecision(null);
    setShowCounterInput(false);
    const customer = customers.find(c => c.customer_id === activeCustomer);
    
    setLogs(prev => [...prev, {
      id: `user-${Date.now()}`,
      role: "user",
      content: `Evaluate case for ${customer?.name || activeCustomer} (${triggerEvent})`,
      timestamp: new Date().toISOString()
    }]);

    try {
      const res = await fetch(`${API_URL}/cases/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: activeCustomer,
          account_id: customer?.account_id,
          trigger_event: triggerEvent,
        }),
      });
      const result = await res.json();
      
      setTimeout(() => {
        setLogs(prev => [...prev, {
          id: `sys-${Date.now()}`,
          role: "agent",
          content: `Evaluation complete. Recommended action: ${result.recommended_action} (${(result.confidence * 100).toFixed(0)}% confidence).`,
          decision: result,
          ai_narrative: result.ai_narrative,
          timestamp: new Date().toISOString()
        }]);
        
        // Set active decision for negotiation
        setActiveDecision(result);
        setIsEvaluating(false);
        loadGraph(activeCustomer);
      }, 600);
      
    } catch (e) {
      setLogs(prev => [...prev, {
        id: `sys-err-${Date.now()}`,
        role: "system",
        content: "Evaluation failed. Check backend connection.",
        error: true,
        timestamp: new Date().toISOString()
      }]);
      setIsEvaluating(false);
    }
  };

  const handleNegotiate = async (response: string, value?: string) => {
    if (!activeDecision) return;
    setIsNegotiating(true);
    setShowCounterInput(false);

    const label = response === "ACCEPT" ? "✅ Accepted the recommendation" :
                  response === "DECLINE" ? "❌ Declined the recommendation" :
                  `🔄 Counter-proposal: ${value}`;

    setLogs(prev => [...prev, {
      id: `user-neg-${Date.now()}`,
      role: "user",
      content: label,
      timestamp: new Date().toISOString()
    }]);

    try {
      const res = await fetch(`${API_URL}/cases/${activeDecision.decision_id}/negotiate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          response: response,
          counter_value: value || null,
          reason: response === "DECLINE" ? "Customer declined" : null,
        }),
      });
      const result = await res.json();
      
      setTimeout(() => {
        setLogs(prev => [...prev, {
          id: `sys-neg-${Date.now()}`,
          role: "negotiation",
          content: result.message,
          negotiation: result,
          timestamp: new Date().toISOString()
        }]);
        
        if (result.is_final) {
          setActiveDecision(null);
        } else if (result.counter_offer) {
          // Engine made a new counter — keep negotiation alive
          setActiveDecision({ ...activeDecision, counter_offer: result.counter_offer });
        }
        
        setIsNegotiating(false);
        loadGraph(activeCustomer);
      }, 500);

    } catch (e) {
      setLogs(prev => [...prev, {
        id: `sys-neg-err-${Date.now()}`,
        role: "system",
        content: "Negotiation request failed.",
        error: true,
        timestamp: new Date().toISOString()
      }]);
      setIsNegotiating(false);
    }
  };

  const { isCollapsed } = useSidebar();

  return (
    <div className="h-full w-full bg-gray-950 flex flex-col overflow-hidden animate-fade-in relative pt-0">
      {/* Top Bar */}
      <div className="border-b border-gray-800/50 bg-gray-900/50 flex flex-col shrink-0 backdrop-blur-sm z-10">
        <div className="h-14 flex items-center px-4">
          <Activity className="w-5 h-5 text-indigo-400 mr-2" />
          <h1 className="text-sm font-semibold text-white tracking-wide">Context Explorer</h1>
          
          {/* Population Counter */}
          <div className="ml-4 flex items-center gap-1.5 text-[10px] text-gray-500 bg-gray-900/50 rounded px-2 py-1 border border-gray-800/50">
            <span className="text-indigo-400 font-bold">{popCount.total.toLocaleString()}</span> users
            <span className="text-gray-700 mx-1">|</span>
            <span className="text-red-400">{popCount.aml.toLocaleString()}</span> AML
            <span className="text-emerald-400">{popCount.healthcare.toLocaleString()}</span> MED
            <span className="text-amber-400">{popCount.ecommerce?.toLocaleString() || 0}</span> ECOM
          </div>

          <div className="ml-auto flex items-center gap-2 text-[10px] pr-2">
            {/* Search Toggle */}
            <button
              onClick={() => setShowSearch(!showSearch)}
              className={`px-2 py-1 rounded border transition-all ${showSearch ? 'bg-indigo-600 border-indigo-500 text-white' : 'border-gray-700 text-gray-400 hover:text-white hover:bg-gray-800'}`}
            >
              🔍 Search {popCount.total.toLocaleString()} Users
            </button>
            
            {/* Hero Shortcuts */}
            <div className="flex items-center bg-gray-900/50 rounded p-1 border border-gray-800">
              <span className="text-gray-500 mr-2 ml-1 uppercase tracking-wider font-semibold">Showcases:</span>
              <button onClick={() => selectCustomer("CUST-CLI-HAPPY", "CREDIT_LIMIT_REVIEW")}
                className={`px-2 py-1 rounded transition-all ${activeCustomer === "CUST-CLI-HAPPY" ? "bg-indigo-600 text-white" : "text-gray-400 hover:text-white hover:bg-gray-700"}`}>
                CLI ✅
              </button>
              <button onClick={() => selectCustomer("CUST-CLI-SAD", "CREDIT_LIMIT_REVIEW")}
                className={`px-2 py-1 rounded transition-all ${activeCustomer === "CUST-CLI-SAD" ? "bg-indigo-600 text-white" : "text-gray-400 hover:text-white hover:bg-gray-700"}`}>
                CLI ❌
              </button>
              <button onClick={() => selectCustomer("CUST-AML-HAPPY", "FRAUD_DETECTION")}
                className={`px-2 py-1 rounded transition-all ${activeCustomer === "CUST-AML-HAPPY" ? "bg-red-600 text-white" : "text-gray-400 hover:text-white hover:bg-gray-700"}`}>
                AML ✅
              </button>
              <button onClick={() => selectCustomer("CUST-AML-SAD", "FRAUD_DETECTION")}
                className={`px-2 py-1 rounded transition-all ${activeCustomer === "CUST-AML-SAD" ? "bg-red-600 text-white" : "text-gray-400 hover:text-white hover:bg-gray-700"}`}>
                AML ❌
              </button>
              <button onClick={() => selectCustomer("CUST-MED-HAPPY", "CARE_GAP_REVIEW")}
                className={`px-2 py-1 rounded transition-all ${activeCustomer === "CUST-MED-HAPPY" ? "bg-emerald-600 text-white" : "text-gray-400 hover:text-white hover:bg-gray-700"}`}>
                MED ✅
              </button>
              <button onClick={() => selectCustomer("CUST-MED-SAD", "CARE_GAP_REVIEW")}
                className={`px-2 py-1 rounded transition-all ${activeCustomer === "CUST-MED-SAD" ? "bg-emerald-600 text-white" : "text-gray-400 hover:text-white hover:bg-gray-700"}`}>
                MED ❌
              </button>
              <button onClick={() => selectCustomer("CUST-ECOM-HAPPY", "ABANDONED_SESSION")}
                className={`px-2 py-1 rounded transition-all ${activeCustomer === "CUST-ECOM-HAPPY" ? "bg-amber-600 text-white" : "text-gray-400 hover:text-white hover:bg-gray-700"}`}>
                ECOM ✅
              </button>
              <button onClick={() => selectCustomer("CUST-ECOM-SAD", "ABANDONED_SESSION")}
                className={`px-2 py-1 rounded transition-all ${activeCustomer === "CUST-ECOM-SAD" ? "bg-amber-600 text-white" : "text-gray-400 hover:text-white hover:bg-gray-700"}`}>
                ECOM ❌
              </button>
            </div>
          </div>
        </div>

        {/* Expandable Search Panel */}
        {showSearch && (
          <div className="px-4 pb-3 pt-1 border-t border-gray-800/30 bg-gray-900/30 animate-slide-in-right">
            <div className="flex items-center gap-2 mb-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                placeholder="Search by name or ID across all 10K users..."
                className="flex-1 bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500"
                autoFocus
              />
              <div className="flex gap-1">
                {["financial", "aml", "healthcare", "ecommerce"].map(ind => (
                  <button key={ind} onClick={() => handleIndustryFilter(ind)}
                    className={`px-2 py-1.5 rounded text-[10px] font-semibold uppercase transition-all border ${
                      industryFilter === ind
                        ? ind === "financial" ? "bg-blue-600 border-blue-500 text-white" :
                          ind === "aml" ? "bg-red-600 border-red-500 text-white" :
                          ind === "healthcare" ? "bg-emerald-600 border-emerald-500 text-white" :
                          "bg-amber-600 border-amber-500 text-white"
                        : "border-gray-700 text-gray-400 hover:text-white hover:bg-gray-800"
                    }`}>
                    {ind === "financial" ? "💳 FIN" : ind === "aml" ? "🚨 AML" : ind === "healthcare" ? "🏥 MED" : "🛒 ECOM"}
                  </button>
                ))}
              </div>
            </div>
            <div className="max-h-40 overflow-y-auto custom-scrollbar space-y-0.5">
              {customers.map(c => (
                <button key={c.customer_id}
                  onClick={() => { selectCustomer(c.customer_id); setShowSearch(false); }}
                  className={`w-full flex items-center justify-between px-3 py-1.5 rounded text-xs transition-all ${
                    activeCustomer === c.customer_id ? "bg-indigo-600/20 border border-indigo-500/30 text-white" : "text-gray-400 hover:bg-gray-800 hover:text-white"
                  }`}>
                  <span className="font-medium">{c.name}</span>
                  <span className="flex items-center gap-2 text-[10px]">
                    <span className="text-gray-600">{c.customer_id}</span>
                    <span className={`px-1.5 py-0.5 rounded ${
                      c.segment === "Affluent" || c.segment === "Low" ? "bg-emerald-500/20 text-emerald-300" :
                      c.segment === "Subprime" || c.segment === "High" ? "bg-red-500/20 text-red-300" :
                      "bg-gray-700/50 text-gray-400"
                    }`}>{c.segment}</span>
                    {c.risk_score > 0.5 && <span className="text-red-400">⚠</span>}
                  </span>
                </button>
              ))}
              {customers.length === 50 && (
                <p className="text-[10px] text-gray-600 text-center py-2">Showing first 50 results. Use search to narrow down.</p>
              )}
            </div>
          </div>
        )}
      </div>

      <PanelGroup orientation="horizontal" className="flex-1 overflow-hidden">
        
        {/* LEFT PANE: Action/Log */}
        <Panel defaultSize={25} minSize={20} className="bg-gray-900/30 flex flex-col z-0 relative">
          <div className="p-3 border-b border-gray-800/50 bg-gray-900/40 flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-gray-400" />
            <h2 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Engine Log</h2>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs custom-scrollbar">
            {(logs || []).map((log) => (
              <div key={log.id} className={`flex flex-col ${log.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`
                  max-w-[90%] rounded-lg p-3 relative
                  ${log.role === 'user' ? 'bg-indigo-600/20 border border-indigo-500/30 text-indigo-200' : 
                    log.role === 'agent' ? 'bg-gray-800/50 border border-gray-700/50 text-gray-200' : 
                    log.role === 'negotiation' ? 'bg-amber-950/40 border border-amber-500/30 text-amber-100' :
                    log.error ? 'bg-red-900/20 border border-red-500/30 text-red-300' :
                    'text-gray-500 bg-transparent border-none p-1'}
                `}>
                  {log.role === 'negotiation' && (
                    <strong className="text-amber-400 flex items-center gap-1.5 mb-1.5 uppercase tracking-wider text-[10px]">
                      <RefreshCw className="w-3 h-3" />
                      Negotiation Engine
                    </strong>
                  )}
                  <p>{log.content}</p>
                  
                  {/* Decision details with counter-offer and ranked actions */}
                  {log.decision && (
                    <div className="mt-3 pt-3 border-t border-gray-700/50 space-y-2">
                      <p className="text-[10px] text-gray-400">Policies Applied: {log.decision.applied_policies?.length || 0}</p>
                      <p className="text-[10px] text-gray-400">Precedents Found: {log.decision.precedent_cases?.length || 0}</p>
                      
                      {/* Counter-Offer Card */}
                      {log.decision.counter_offer && (
                        <div className="mt-2 p-3 bg-amber-950/50 border border-amber-500/30 rounded-lg">
                          <strong className="text-amber-300 flex items-center gap-1.5 mb-2 uppercase tracking-wider text-[10px]">
                            <ArrowRight className="w-3 h-3" />
                            Counter-Offer Available
                          </strong>
                          <p className="text-amber-100 text-xs mb-1"><strong>Suggested:</strong> {log.decision.counter_offer.suggested_value}</p>
                          <p className="text-amber-100/70 text-[10px] mb-2">{log.decision.counter_offer.rationale}</p>
                          {log.decision.counter_offer.conditions?.length > 0 && (
                            <div className="space-y-1">
                              <p className="text-[10px] text-amber-300 font-semibold">Conditions:</p>
                              {(log.decision.counter_offer.conditions || []).map((c: string, i: number) => (
                                <p key={i} className="text-[10px] text-amber-100/60 pl-2">• {c}</p>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* Ranked Actions */}
                      {(log.decision.ranked_actions || []).length > 0 && (
                        <div className="mt-2 space-y-1.5">
                          <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider">Ranked Actions:</p>
                          {log.decision.ranked_actions.map((ra: any) => (
                            <div key={ra.rank} className={`p-2 rounded border text-[10px] ${ra.rank === 1 ? 'bg-indigo-950/50 border-indigo-500/30' : 'bg-gray-900/50 border-gray-800/50'}`}>
                              <div className="flex items-center justify-between mb-0.5">
                                <span className={`font-bold ${ra.rank === 1 ? 'text-indigo-300' : 'text-gray-400'}`}>
                                  #{ra.rank} {ra.action}
                                </span>
                                <span className="text-gray-500">{((ra.confidence || 0) * 100).toFixed(0)}%</span>
                              </div>
                              <p className="text-gray-400">{ra.description}</p>
                              {ra.revenue_impact && <p className="text-emerald-400 mt-0.5">{ra.revenue_impact}</p>}
                            </div>
                          ))}
                        </div>
                      )}

                      {/* AI Narrative */}
                      {log.ai_narrative && (
                         <div className="mt-3 p-3 bg-indigo-950/80 border border-indigo-500/30 rounded-md text-xs text-indigo-100 shadow-sm leading-relaxed">
                           <strong className="text-indigo-300 flex items-center gap-1.5 mb-1.5 uppercase tracking-wider text-[10px]">
                              <BrainCircuit className="w-3 h-3" />
                              AI Synthesizer
                           </strong>
                           {log.ai_narrative}
                         </div>
                      )}
                    </div>
                  )}

                  {/* Negotiation step counter-offer */}
                  {log.negotiation?.counter_offer && (
                    <div className="mt-2 p-2 bg-amber-950/40 border border-amber-600/20 rounded text-[10px]">
                      <p className="text-amber-200 font-semibold mb-1">Engine Counter: {log.negotiation.counter_offer.suggested_value}</p>
                      {(log.negotiation.counter_offer.conditions || []).map((c: string, i: number) => (
                        <p key={i} className="text-amber-100/50 pl-2">• {c}</p>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {(isEvaluating || isNegotiating) && (
              <div className="flex items-start">
                <div className="bg-gray-800/50 border border-gray-700/50 text-gray-400 rounded-lg p-3 text-xs flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></span>
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse delay-75"></span>
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse delay-150"></span>
                </div>
              </div>
            )}
            <div ref={logEndRef} />
          </div>

          {/* Bottom Action Panel */}
          <div className="p-3 border-t border-gray-800/50 bg-gray-900/80 shrink-0">
            <div className="flex flex-col gap-2">
              <div className="w-full bg-gray-950 border border-gray-800 rounded-md px-3 py-2 text-xs text-brand-blue-300 font-semibold text-center flex items-center justify-center gap-2">
                <AlertCircle className="w-3.5 h-3.5 text-brand-blue-400" />
                {triggerEvent === "CREDIT_LIMIT_REVIEW" ? "Credit Limit Review" :
                 triggerEvent === "FRAUD_DETECTION" ? "AML Fraud Detection" : 
                 triggerEvent === "ABANDONED_SESSION" ? "Intent-to-Lease Conversion" : 
                 "Care Gap Review"}
              </div>

              {/* Negotiation Action Buttons — shown when a decision with counter-offer is active */}
              {activeDecision && (activeDecision.counter_offer || (activeDecision.ranked_actions || []).length > 0) ? (
                <div className="space-y-2">
                  <p className="text-[10px] text-amber-400 font-semibold uppercase tracking-wider text-center">Respond to Decision</p>
                  
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleNegotiate("ACCEPT")}
                      disabled={isNegotiating}
                      className="flex-1 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50 text-xs"
                    >
                      <CheckCircle className="w-3.5 h-3.5" />
                      Accept
                    </button>
                    <button
                      onClick={() => setShowCounterInput(!showCounterInput)}
                      disabled={isNegotiating}
                      className="flex-1 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-semibold flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50 text-xs"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                      Counter
                    </button>
                    <button
                      onClick={() => handleNegotiate("DECLINE")}
                      disabled={isNegotiating}
                      className="flex-1 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white font-semibold flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50 text-xs"
                    >
                      <XCircle className="w-3.5 h-3.5" />
                      Decline
                    </button>
                  </div>

                  {/* Counter-proposal input */}
                  {showCounterInput && (
                    <div className="flex gap-2 animate-slide-in-right">
                      <input
                        type="text"
                        value={counterValue}
                        onChange={(e) => setCounterValue(e.target.value)}
                        placeholder={triggerEvent === "CREDIT_LIMIT_REVIEW" ? "e.g. $3,000" : triggerEvent === "FRAUD_DETECTION" ? "e.g. Release $5,000" : "e.g. Pharmacy outreach only"}
                        className="flex-1 bg-gray-950 border border-amber-700/50 rounded-lg px-3 py-2 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-amber-500"
                      />
                      <button
                        onClick={() => { handleNegotiate("COUNTER", counterValue); setCounterValue(""); }}
                        disabled={!counterValue || isNegotiating}
                        className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs disabled:opacity-50 transition-colors"
                      >
                        Send
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <button 
                  onClick={handleEvaluate}
                  disabled={!activeCustomer || isEvaluating}
                  className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold flex items-center justify-center gap-2 transition-colors disabled:opacity-50 text-xs"
                >
                  {isEvaluating ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Analyzing Graph Paths...
                    </>
                  ) : "Trigger Evaluation"}
                </button>
              )}
            </div>
          </div>
        </Panel>

        <PanelResizeHandle className="w-1 bg-gray-800/50 hover:bg-indigo-500/50 transition-colors cursor-col-resize flex items-center justify-center">
          <div className="h-8 w-0.5 bg-gray-700 rounded-full" />
        </PanelResizeHandle>

        {/* CENTER PANE: Graph */}
        <Panel defaultSize={45} minSize={30} className="relative bg-[#0a0f1c]">
          <GraphView 
            data={graphData} 
            onNodeClick={setSelectedNode} 
            selectedNodeId={selectedNode?.id} 
          />
        </Panel>

        <PanelResizeHandle className="w-1 bg-gray-800/50 hover:bg-indigo-500/50 transition-colors cursor-col-resize flex items-center justify-center">
          <div className="h-8 w-0.5 bg-gray-700 rounded-full" />
        </PanelResizeHandle>

        {/* RIGHT PANE: Properties */}
        <Panel defaultSize={30} minSize={20} className="bg-gray-900/30 flex flex-col border-l border-gray-800/50 relative overflow-hidden">
            <div className="p-3 border-b border-gray-800/50 bg-gray-900/40 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BrainCircuit className="w-4 h-4 text-emerald-400" />
                <h2 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Node Details</h2>
              </div>
              {selectedNode && (
                <button onClick={() => setSelectedNode(null)} className="text-gray-500 hover:text-white transition-colors">
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
              {!selectedNode ? (
                <div className="h-full flex flex-col items-center justify-center text-center text-gray-600 space-y-3">
                  <Network className="w-8 h-8 opacity-20" />
                  <p className="text-sm">Select any node in the graph<br/>to examine its properties.</p>
                </div>
              ) : (
                <div className="space-y-4 animate-slide-in-right">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      {selectedNode.labels?.[0]}
                    </span>
                    <span className="text-xs text-gray-500 font-mono truncate">{selectedNode.id}</span>
                  </div>

                  <div className="space-y-px rounded-lg overflow-hidden border border-gray-800/50">
                    {Object.entries(selectedNode.properties || {}).map(([key, value]) => {
                      // Hide raw fields that we display in the reasoning section
                      if (key === 'id' || key === 'decision_id' || key === 'reasoning' || key === 'graph_features' || key === 'policies_applied') return null;
                      return (
                        <div key={key} className="bg-gray-900/50 px-3 py-2 flex flex-col border-b border-gray-800/50 last:border-0">
                          <span className="text-[10px] text-gray-500 uppercase tracking-wider mb-0.5">{key.replace(/_/g, ' ')}</span>
                          <span className={`${typeof value === 'number' ? 'font-mono text-cyan-300' : 'text-gray-200'} text-xs break-words`}>
                            {typeof value === 'number' && key === 'confidence' ? `${((value || 0) * 100).toFixed(1)}%` : String(value)}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                  
                  {selectedNode.labels?.includes("Decision") && (
                    <>
                      {/* Decision Reasoning Section */}
                      {selectedNode.properties?.reasoning && (
                        <div className="mt-4 p-3 rounded-lg border border-indigo-500/20 bg-indigo-950/30">
                          <h4 className="text-xs font-semibold text-indigo-300 mb-2 flex items-center gap-1.5 uppercase tracking-wider">
                            <BrainCircuit className="w-3.5 h-3.5" />
                            Why This Decision Was Made
                          </h4>
                          <div className="space-y-1.5">
                            {String(selectedNode.properties.reasoning).split('\n').map((line: string, i: number) => (
                              <p key={i} className="text-[11px] text-indigo-100/80 leading-relaxed">{line}</p>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Graph Features Extracted */}
                      {selectedNode.properties?.graph_features && selectedNode.properties?.graph_features !== 'N/A' && (
                        <div className="mt-3 p-3 rounded-lg border border-cyan-500/20 bg-cyan-950/20">
                          <h4 className="text-xs font-semibold text-cyan-300 mb-2 flex items-center gap-1.5 uppercase tracking-wider">
                            <Network className="w-3.5 h-3.5" />
                            Graph Features Extracted
                          </h4>
                          <div className="flex flex-wrap gap-1.5">
                            {String(selectedNode.properties.graph_features).split(' | ').map((feat: string, i: number) => {
                              const [k, v] = feat.split(': ');
                              const isAlert = v === 'True' || v === 'true';
                              const isDanger = (k?.includes('threat') || k?.includes('critical') || k?.includes('high_risk')) && isAlert;
                              return (
                                <span key={i} className={`px-2 py-1 rounded text-[10px] font-mono border ${
                                  isDanger ? 'bg-red-950/50 border-red-500/30 text-red-300' :
                                  isAlert ? 'bg-amber-950/50 border-amber-500/30 text-amber-300' :
                                  'bg-gray-900/50 border-gray-700/50 text-gray-300'
                                }`}>
                                  <span className="text-gray-500">{k}:</span> {v}
                                </span>
                              );
                            })}
                          </div>
                        </div>
                      )}

                      {/* Policies Applied */}
                      {selectedNode.properties?.policies_applied && (
                        <div className="mt-3 p-3 rounded-lg border border-violet-500/20 bg-violet-950/20">
                          <h4 className="text-xs font-semibold text-violet-300 mb-2 flex items-center gap-1.5 uppercase tracking-wider">
                            <AlertCircle className="w-3.5 h-3.5" />
                            Policies Applied
                          </h4>
                          <p className="text-[11px] text-violet-200/80">{selectedNode.properties.policies_applied}</p>
                        </div>
                      )}

                      {/* Analyst Action */}
                      <div className="glass-card p-3 mt-3 border-emerald-500/20 bg-emerald-500/5">
                        <h4 className="text-xs font-semibold text-emerald-400 mb-2 flex items-center gap-1.5">
                          <AlertCircle className="w-3.5 h-3.5" />
                          Analyst Action Available
                        </h4>
                        <p className="text-[10px] text-gray-400 mb-3">
                          This decision is awaiting manual review or override confirmation.
                        </p>
                        <Link href={`/cases/${selectedNode.id}`}>
                          <button className="w-full py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs rounded transition-colors border border-gray-700">
                            View Full Trace →
                          </button>
                        </Link>
                      </div>
                    </>
                  )}

                  {selectedNode.labels?.includes("NegotiationStep") && (
                    <div className="glass-card p-3 mt-4 border-amber-500/20 bg-amber-500/5">
                      <h4 className="text-xs font-semibold text-amber-400 mb-2 flex items-center gap-1.5">
                        <RefreshCw className="w-3.5 h-3.5" />
                        Negotiation Step
                      </h4>
                      <p className="text-[10px] text-gray-400">
                        Step #{selectedNode.properties?.step_number} — {selectedNode.properties?.customer_response} → {selectedNode.properties?.engine_action}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
        </Panel>
      </PanelGroup>
    </div>
  );
}
