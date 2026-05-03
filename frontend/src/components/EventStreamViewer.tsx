"use client";

import { useEffect, useState, useRef } from "react";
import axios from "axios";
import { clsx } from "clsx";
import { 
  Activity, AlertTriangle, CheckCircle, Clock, Search, Code, PenTool, BrainCircuit, Terminal, Play, Loader2
} from "lucide-react";

interface StreamEvent {
  type: string;
  data: any;
  timestamp: number;
}

interface EventStreamViewerProps {
  threadId: string | null;
}

export default function EventStreamViewer({ threadId }: EventStreamViewerProps) {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [status, setStatus] = useState<"idle" | "running" | "awaiting_approval" | "finished" | "error">("idle");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!threadId) {
      setEvents([]);
      setStatus("idle");
      return;
    }

    setEvents([]);
    setStatus("running");

    const eventSource = new EventSource(`http://127.0.0.1:8000/tasks/${threadId}/stream`);

    eventSource.onmessage = (e) => {
      try {
        const parsed = JSON.parse(e.data);
        if (parsed.type === "done") {
          eventSource.close();
          setStatus((prev) => prev === "running" ? "finished" : prev);
          return;
        }

        if (parsed.type === "awaiting_approval") setStatus("awaiting_approval");
        if (parsed.type === "error") setStatus("error");
        if (parsed.type === "finished") setStatus("finished");
        if (parsed.type === "rejected") setStatus("finished");

        setEvents((prev) => [...prev, { ...parsed, timestamp: Date.now() }]);
      } catch (err) {
        console.error("Parse error", err);
      }
    };

    eventSource.onerror = () => {
      console.log("EventSource connection closed or failed.");
      eventSource.close();
      setStatus((prev) => prev === "running" ? "finished" : prev);
    };

    return () => {
      eventSource.close();
    };
  }, [threadId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  const handleApprove = async () => {
    if (!threadId) return;
    setStatus("running");
    try {
      await axios.post(`http://127.0.0.1:8000/tasks/${threadId}/approve`);
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  const handleReject = async () => {
    if (!threadId) return;
    setStatus("finished");
    try {
      await axios.post(`http://127.0.0.1:8000/tasks/${threadId}/reject`);
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  const getIconForNode = (node: string, type: string, iconStr?: string) => {
    if (type === "tool_call") return <Terminal className="w-4 h-4 text-zinc-400" />;
    if (type === "finished") return <CheckCircle className="w-4 h-4 text-green-400" />;
    if (type === "error") return <AlertTriangle className="w-4 h-4 text-red-400" />;
    if (type === "awaiting_approval") return <Clock className="w-4 h-4 text-amber-400" />;
    
    if (iconStr === "search" || node?.includes("Research")) return <Search className="w-4 h-4 text-purple-400" />;
    if (iconStr === "code" || node?.includes("Coder")) return <Code className="w-4 h-4 text-cyan-400" />;
    if (iconStr === "pen" || node?.includes("Writer")) return <PenTool className="w-4 h-4 text-emerald-400" />;
    if (node === "Supervisor") return <BrainCircuit className="w-4 h-4 text-blue-400" />;
    
    return <Activity className="w-4 h-4 text-zinc-400" />;
  };

  if (!threadId) {
    return (
      <div className="glass-panel flex-1 rounded-xl flex items-center justify-center min-h-[400px] border border-dashed border-zinc-700">
        <div className="flex flex-col items-center gap-3 text-zinc-500">
          <Terminal className="w-8 h-8 opacity-50" />
          <p>No active tasks. Dispatch a task to view real-time traces.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-panel flex-1 rounded-xl flex flex-col overflow-hidden border-zinc-800 shadow-2xl relative">
      <div className="border-b border-zinc-800 bg-black/40 px-4 py-3 flex justify-between items-center z-10">
        <h3 className="text-sm font-medium text-white flex items-center gap-2">
          <Activity className={clsx("w-4 h-4", status === "running" ? "text-blue-400 animate-pulse" : "text-zinc-500")} />
          Live Trace <span className="text-zinc-500 text-xs ml-2 font-mono">#{threadId.split('-')[0]}</span>
        </h3>
        <div className="flex gap-2 items-center">
          <span className={clsx(
            "text-xs px-2 py-1 rounded-full uppercase tracking-wider font-bold",
            status === "running" && "bg-blue-500/10 text-blue-400 border border-blue-500/20",
            status === "awaiting_approval" && "bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse",
            status === "finished" && "bg-green-500/10 text-green-400 border border-green-500/20",
            status === "error" && "bg-red-500/10 text-red-400 border border-red-500/20"
          )}>
            {status.replace("_", " ")}
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3 font-mono text-xs relative">
        {events.map((ev, idx) => (
          <div key={idx} className="flex gap-3 items-start animate-in slide-in-from-bottom-2 fade-in duration-300">
            <div className="mt-1 bg-black/50 p-1.5 rounded-md border border-zinc-800">
              {getIconForNode(ev.data?.node, ev.type, ev.data?.icon)}
            </div>
            
            <div className="flex-1 bg-black/20 border border-zinc-800/50 rounded-lg p-3">
              <div className="flex justify-between items-start mb-1">
                <span className={clsx(
                  "font-semibold",
                  ev.type === "error" ? "text-red-400" :
                  ev.type === "awaiting_approval" ? "text-amber-400" :
                  "text-zinc-300"
                )}>
                  {ev.data?.node || ev.type.toUpperCase()}
                </span>
                <span className="text-zinc-600 text-[10px]">
                  {new Date(ev.timestamp).toLocaleTimeString()}
                </span>
              </div>
              
              <div className="text-zinc-400 break-words whitespace-pre-wrap leading-relaxed">
                {ev.type === "tool_call" && (
                  <div className="text-cyan-200 mt-1">
                    <span className="text-zinc-500">Executing: </span> {ev.data.tool}
                    <div className="bg-black/50 p-2 mt-2 rounded border border-zinc-800 text-zinc-500 text-[10px]">
                      {ev.data.input}
                    </div>
                  </div>
                )}
                {ev.type === "plan_ready" && (
                  <div className="mt-1">
                    <p className="text-zinc-300 mb-2 italic">"{ev.data.reasoning}"</p>
                    <ul className="space-y-1">
                      {ev.data.steps.map((s: any, i: number) => (
                        <li key={i} className="flex gap-2 items-start">
                          <span className="text-blue-400 shrink-0">[{s.specialist}]</span> 
                          <span className="text-zinc-400">{s.description}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {(ev.type === "node_start" || ev.type === "node_finish" || ev.type === "finished" || ev.type === "error" || ev.type === "awaiting_approval") && (
                  <span className={clsx(
                    ev.type === "node_finish" && "text-zinc-300",
                    ev.type === "awaiting_approval" && "text-amber-200 font-medium",
                  )}>
                    {ev.data.message || ev.data.result}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {status === "running" && (
          <div className="flex gap-3 items-center opacity-50 p-2">
            <Loader2 className="w-4 h-4 text-zinc-500 animate-spin" />
            <span className="text-zinc-500">Agent thinking...</span>
          </div>
        )}

        <div ref={bottomRef} className="h-1 pb-4" />
      </div>

      {status === "awaiting_approval" && (
        <div className="absolute bottom-4 left-4 right-4 bg-amber-950/90 border border-amber-500/50 rounded-lg p-4 shadow-2xl backdrop-blur-md animate-in slide-in-from-bottom-5">
          <div className="flex flex-col gap-3">
            <h4 className="text-amber-400 font-semibold flex items-center gap-2 text-sm">
              <AlertTriangle className="w-4 h-4" /> Human Verification Required
            </h4>
            <p className="text-amber-200/70 text-xs">
              The reviewer agent flagged this execution due to low confidence. Do you approve the intermediate outputs to proceed?
            </p>
            <div className="flex gap-3 mt-2">
              <button 
                onClick={handleApprove}
                className="flex-1 bg-amber-600 hover:bg-amber-500 text-white py-2 rounded-md font-medium text-sm transition-colors flex items-center justify-center gap-2"
              >
                <Play className="w-4 h-4" /> Approve & Continue
              </button>
              <button 
                onClick={handleReject}
                className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 py-2 rounded-md font-medium text-sm transition-colors"
              >
                Reject & Abort
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
