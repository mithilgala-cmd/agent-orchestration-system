"use client";

import { useState } from "react";
import Header from "@/components/Header";
import TaskRunner from "@/components/TaskRunner";
import EventStreamViewer from "@/components/EventStreamViewer";
import { TraceExplorer } from "@/components/TraceExplorer";
import { Bot } from "lucide-react";


export default function Home() {
  const [currentThread, setCurrentThread] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"live" | "history">("live");

  return (
    <main className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-blue-500/30">
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />


      <div className="flex-1 max-w-7xl w-full mx-auto p-6 flex flex-col md:flex-row gap-6">
        {activeTab === "live" ? (
          <>
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
      </>
      ) : (
        <div className="w-full">
          <TraceExplorer />
        </div>
      )}
      </div>
    </main>
  );
}
