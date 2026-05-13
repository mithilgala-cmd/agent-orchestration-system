"use client";

import { useEffect, useState } from "react";
import { Network, LayoutDashboard, History } from "lucide-react";

interface HeaderProps {
  activeTab: "live" | "history";
  setActiveTab: (tab: "live" | "history") => void;
}

export default function Header({ activeTab, setActiveTab }: HeaderProps) {
  const [status, setStatus] = useState<"online" | "offline" | "checking">("checking");

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${apiUrl}/health`);
        if (res.ok) {
          setStatus("online");
        } else {
          setStatus("offline");
        }
      } catch (err) {
        setStatus("offline");
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="border-b border-white/5 bg-black/40 sticky top-0 z-50 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600/20 p-2 rounded-lg border border-blue-500/30">
            <Network className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight text-white tracking-tight">Sentinel Orchestrator</h1>
            <p className="text-xs text-zinc-500 font-medium tracking-wide text-uppercase">v2.1 — Multi-Agent System</p>
          </div>
        </div>
        
        <div className="flex bg-zinc-900/50 p-1 rounded-lg border border-white/5">
          <button
            onClick={() => setActiveTab("live")}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-xs font-medium transition-colors ${
              activeTab === "live" ? "bg-zinc-800 text-white shadow-sm" : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            Live Run
          </button>
          <button
            onClick={() => setActiveTab("history")}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-xs font-medium transition-colors ${
              activeTab === "history" ? "bg-zinc-800 text-white shadow-sm" : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <History className="w-3.5 h-3.5" />
            Trace History
          </button>
        </div>

        <div className="flex items-center gap-2 text-xs font-medium text-zinc-400 bg-zinc-900/50 px-3 py-1.5 rounded-full border border-white/5 transition-all">
          <div className={`w-2 h-2 rounded-full animate-pulse shadow-lg ${
            status === "online" ? "bg-emerald-500 shadow-emerald-500/50" : 
            status === "offline" ? "bg-rose-500 shadow-rose-500/50" : "bg-amber-500"
          }`} />
          {status === "online" ? "System Online" : status === "offline" ? "Backend Offline" : "Checking..."}
        </div>
      </div>
    </header>
  );
}
