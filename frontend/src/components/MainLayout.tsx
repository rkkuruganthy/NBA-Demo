"use client";

import React from "react";
import { Sidebar } from "@/components/Sidebar";
import { useSidebar } from "@/context/SidebarContext";

export function MainLayout({ children }: { children: React.ReactNode }) {
  const { isCollapsed } = useSidebar();

  return (
    <div className="flex w-full min-h-screen bg-gray-950">
      <Sidebar />
      <main 
        className={`
          flex-1 transition-all duration-300 ease-in-out
          ${isCollapsed ? "ml-20" : "ml-64"}
          h-screen overflow-hidden
        `}
      >
        {children}
      </main>
    </div>
  );
}
