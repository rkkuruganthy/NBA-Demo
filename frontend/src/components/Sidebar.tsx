"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSidebar } from "@/context/SidebarContext";
import { 
  ChevronLeft, 
  ChevronRight, 
  LayoutDashboard, 
  PlusCircle, 
  ShieldCheck, 
  ScrollText, 
  Network,
  Activity,
  BarChart2,
  GitBranch
} from "lucide-react";

const navigation = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: <LayoutDashboard className="w-5 h-5" />,
  },
  {
    name: "New Case",
    href: "/cases/new",
    icon: <PlusCircle className="w-5 h-5" />,
  },
  {
    name: "Decisions",
    href: "/decisions",
    icon: <ShieldCheck className="w-5 h-5" />,
  },
  {
    name: "Calibration",
    href: "/decisions/calibration",
    icon: <BarChart2 className="w-5 h-5" />,
  },
  {
    name: "Policies",
    href: "/policies",
    icon: <ScrollText className="w-5 h-5" />,
  },
  {
    name: "Graph Explorer",
    href: "/explorer",
    icon: <Network className="w-5 h-5" />,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isCollapsed, toggleSidebar } = useSidebar();

  return (
    <aside 
      className={`
        fixed inset-y-0 left-0 bg-gray-900/80 backdrop-blur-xl border-r border-gray-800/50 
        flex flex-col z-50 transition-all duration-300 ease-in-out
        ${isCollapsed ? "w-20" : "w-64"}
      `}
    >
      {/* Logo Section */}
      <div className={`h-16 flex items-center border-b border-gray-800/50 relative ${isCollapsed ? "justify-center" : "px-6"}`}>
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-8 h-8 shrink-0 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Activity className="w-5 h-5 text-white" />
          </div>
          {!isCollapsed && (
            <div className="animate-fade-in whitespace-nowrap">
              <h1 className="text-sm font-bold tracking-tight text-white">NBA Engine</h1>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest">Context Graph</p>
            </div>
          )}
        </div>
        
        {/* Toggle Button */}
        <button 
          onClick={toggleSidebar}
          className={`
            absolute -right-3 top-6 w-6 h-6 rounded-full bg-gray-800 border border-gray-700 
            flex items-center justify-center text-gray-400 hover:text-white hover:border-indigo-500/50
            transition-all shadow-xl z-50
          `}
        >
          {isCollapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Navigation */}
      <nav className={`flex-1 py-4 space-y-1 ${isCollapsed ? "px-2" : "px-3"}`}>
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
          return (
            <Link
              key={item.name}
              href={item.href}
              title={isCollapsed ? item.name : ""}
              className={`
                flex items-center rounded-xl text-sm font-medium
                transition-all duration-200 group relative
                ${isCollapsed ? "justify-center px-0 py-3" : "gap-3 px-3 py-2.5"}
                ${
                  isActive
                    ? "bg-indigo-500/10 text-indigo-400 glow-indigo"
                    : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/50"
                }
              `}
            >
              <span className={`transition-colors shrink-0 ${isActive ? "text-indigo-400" : "text-gray-500 group-hover:text-gray-300"}`}>
                {item.icon}
              </span>
              {!isCollapsed && <span className="animate-fade-in font-semibold">{item.name}</span>}
              
              {/* Active Indicator */}
              {isActive && (
                <div className="absolute left-0 w-1 h-6 bg-indigo-500 rounded-r-full shadow-[0_0_10px_rgba(99,102,241,0.5)]" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* System status */}
      <div className={`py-4 border-t border-gray-800/50 ${isCollapsed ? "px-2" : "px-4"}`}>
        <div className={`p-3 rounded-xl transition-all ${isCollapsed ? "bg-transparent border-none" : "glass-card"}`}>
          <div className={`flex items-center gap-2 ${isCollapsed ? "justify-center" : "mb-2"}`}>
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-glow" />
            {!isCollapsed && <span className="text-xs text-gray-400 font-medium whitespace-nowrap">System Status</span>}
          </div>
          {!isCollapsed && (
            <div className="space-y-1.5 animate-fade-in">
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-gray-500 uppercase tracking-tighter">Neo4j</span>
                <span className="text-emerald-400 font-mono">ONLINE</span>
              </div>
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-gray-500 uppercase tracking-tighter">Engine</span>
                <span className="text-emerald-400 font-mono">ACTIVE</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
