"use client";

import { useEffect, useState } from "react";
import { Activity, Clock, DollarSign, Target, ChevronRight } from "lucide-react";

interface TraceMetrics {
  total_tokens?: number;
  prompt_tokens?: number;
  completion_tokens?: number;
  duration?: number;
}

interface Trace {
  thread_id: string;
  task: string;
  status: string;
  total_tokens: number;
  estimated_cost: number;
  duration_seconds: number;
  created_at: string;
  metrics: string | TraceMetrics;
}

export function TraceExplorer() {
  const [traces, setTraces] = useState<Trace[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchTraces() {
      try {
        const response = await fetch("http://127.0.0.1:8000/traces");
        const data = await response.json();
        setTraces(data.traces || []);
      } catch (error) {
        console.error("Failed to fetch traces", error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchTraces();
    // Refresh every 10 seconds to keep traces updated
    const intervalId = setInterval(fetchTraces, 10000);
    return () => clearInterval(intervalId);
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center rounded-2xl border border-white/10 bg-black/40 backdrop-blur-xl">
        <Activity className="h-6 w-6 animate-pulse text-neutral-400" />
      </div>
    );
  }

  if (traces.length === 0) {
    return (
      <div className="flex h-64 flex-col items-center justify-center space-y-4 rounded-2xl border border-white/10 bg-black/40 backdrop-blur-xl">
        <div className="rounded-full bg-neutral-900/80 p-4 ring-1 ring-white/10">
          <Activity className="h-6 w-6 text-neutral-500" />
        </div>
        <p className="text-sm text-neutral-400">No traces recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-white/10 bg-black/40 p-4 backdrop-blur-xl transition-all hover:bg-black/60">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-500/10 p-2 text-blue-400">
              <Target className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-neutral-500">Total Tasks</p>
              <p className="text-xl font-semibold text-neutral-200">{traces.length}</p>
            </div>
          </div>
        </div>
        <div className="rounded-2xl border border-white/10 bg-black/40 p-4 backdrop-blur-xl transition-all hover:bg-black/60">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-green-500/10 p-2 text-green-400">
              <DollarSign className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-neutral-500">Est. Total Cost</p>
              <p className="text-xl font-semibold text-neutral-200">
                ${traces.reduce((sum, t) => sum + t.estimated_cost, 0).toFixed(4)}
              </p>
            </div>
          </div>
        </div>
        <div className="rounded-2xl border border-white/10 bg-black/40 p-4 backdrop-blur-xl transition-all hover:bg-black/60">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-purple-500/10 p-2 text-purple-400">
              <Clock className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-neutral-500">Avg. Duration</p>
              <p className="text-xl font-semibold text-neutral-200">
                {(traces.reduce((sum, t) => sum + t.duration_seconds, 0) / traces.length).toFixed(1)}s
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-white/10 bg-black/40 backdrop-blur-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-neutral-300">
            <thead className="bg-white/[0.02] text-xs uppercase text-neutral-500">
              <tr>
                <th className="px-6 py-4 font-medium">Task</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium">Tokens</th>
                <th className="px-6 py-4 font-medium">Cost</th>
                <th className="px-6 py-4 font-medium">Duration</th>
                <th className="px-6 py-4 font-medium">Date</th>
                <th className="px-6 py-4 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {traces.map((trace) => (
                <tr key={trace.thread_id} className="transition-colors hover:bg-white/[0.02]">
                  <td className="max-w-[200px] truncate px-6 py-4 font-medium text-neutral-200">
                    {trace.task}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${
                        trace.status === "completed"
                          ? "bg-green-500/10 text-green-400 ring-green-500/20"
                          : trace.status === "error"
                          ? "bg-red-500/10 text-red-400 ring-red-500/20"
                          : "bg-amber-500/10 text-amber-400 ring-amber-500/20"
                      }`}
                    >
                      {trace.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-neutral-400">
                    {trace.total_tokens.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 font-mono text-neutral-400">
                    ${trace.estimated_cost.toFixed(4)}
                  </td>
                  <td className="px-6 py-4 font-mono text-neutral-400">
                    {trace.duration_seconds.toFixed(1)}s
                  </td>
                  <td className="px-6 py-4 text-xs text-neutral-500">
                    {new Date(trace.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-neutral-500 transition-colors hover:text-neutral-300">
                      <ChevronRight className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
