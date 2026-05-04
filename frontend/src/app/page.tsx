"use client";

import { useState } from "react";
import TaskRunner from "@/components/TaskRunner";
import EventStreamViewer from "@/components/EventStreamViewer";
import { Bot, Network } from "lucide-react";

export default function Home() {
  const [currentThread, setCurrentThread] = useState<string | null>(null);

  return (
    <main className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-blue-500/30">
      <header className="border-b border-white/5 bg-black/40 sticky top-0 z-50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600/20 p-2 rounded-lg border border-blue-500/30">
              <Network className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h1 className="font-bold text-lg leading-tight text-white tracking-tight">Agent Orchestrator</h1>
              <p className="text-xs text-zinc-500 font-medium tracking-wide">MULTIPLE AGENT SYSTEM</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2 text-xs font-medium text-zinc-400 bg-zinc-900/50 px-3 py-1.5 rounded-full border border-white/5">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
            System Online
          </div>
        </div>
      </header>

      <div className="flex-1 max-w-7xl w-full mx-auto p-6 flex flex-col md:flex-row gap-6">
        <div className="w-full md:w-1/3 flex flex-col gap-6">
          <TaskRunner 
            onTaskStarted={(threadId) => setCurrentThread(threadId)} 
          />
          
          <div className="glass-panel rounded-xl p-5 border-zinc-800 flex-1">
            <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <Bot className="w-4 h-4 text-purple-400" /> 
              Active Agents
            </h3>
            
            <div className="space-y-3">
              {[
                { name: "Supervisor", desc: "Task decomposition & routing", colorClass: "bg-blue-500 shadow-blue-500/50" },
                { name: "Research Agent", desc: "Web search & info gathering", colorClass: "bg-purple-500 shadow-purple-500/50" },
                { name: "Coder Agent", desc: "Python REPL execution", colorClass: "bg-cyan-500 shadow-cyan-500/50" },
                { name: "Writer Agent", desc: "File editing & formatting", colorClass: "bg-emerald-500 shadow-emerald-500/50" },
                { name: "Reviewer Agent", desc: "Output validation & HITL", colorClass: "bg-amber-500 shadow-amber-500/50" }
              ].map((agent, i) => (
                <div key={i} className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors group">
                  <div className={`w-2 h-2 rounded-full ${agent.colorClass} shadow-lg opacity-50 group-hover:opacity-100 transition-opacity`} />
                  <div>
                    <div className="text-xs font-semibold text-zinc-300">{agent.name}</div>
                    <div className="text-[10px] text-zinc-500">{agent.desc}</div>
                  </div>
                </div>
              ))}
            </div>
            
            {currentThread && (
              <div className="mt-6 pt-4 border-t border-zinc-800">
                <button 
                  onClick={() => setCurrentThread(null)}
                  className="w-full py-2 bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-300 text-xs font-medium rounded-lg border border-zinc-800 transition-colors"
                >
                  Clear Active Task
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="w-full md:w-2/3 flex flex-col">
          <EventStreamViewer threadId={currentThread} />
        </div>
      </div>
    </main>
  );
}
