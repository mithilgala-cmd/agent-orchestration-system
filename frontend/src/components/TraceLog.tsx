"use client";

import React, { useEffect, useRef } from "react";
import { Terminal } from "lucide-react";

export interface TraceEntry {
  timestamp: string;
  type: "node_start" | "node_finish" | "tool_call" | "plan_ready" | "awaiting_approval" | "finished" | "error" | "rejected";
  node: string;
  message: string;
}

interface TraceLogProps {
  entries: TraceEntry[];
  isRunning: boolean;
}

const TYPE_STYLE: Record<string, { color: string; prefix: string }> = {
  node_start:         { color: "#93c5fd", prefix: "▶" },
  node_finish:        { color: "#6ee7b7", prefix: "✓" },
  tool_call:          { color: "#c4b5fd", prefix: "⚡" },
  plan_ready:         { color: "#fcd34d", prefix: "📋" },
  awaiting_approval:  { color: "#fcd34d", prefix: "⏸" },
  finished:           { color: "#6ee7b7", prefix: "✅" },
  error:              { color: "#fca5a5", prefix: "✗" },
  rejected:           { color: "#fca5a5", prefix: "✗" },
};

export default function TraceLog({ entries, isRunning }: TraceLogProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [entries.length]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold flex items-center gap-2">
          <Terminal className="w-4 h-4" style={{ color: "var(--blue)" }} />
          Execution Trace
        </h2>
        <div className="flex items-center gap-2">
          {isRunning && (
            <span className="badge badge-blue">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
              Live
            </span>
          )}
          <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
            {entries.length} events
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-1.5 pr-1 max-h-[420px]">
        {entries.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full py-16 gap-3">
            <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ background: "var(--surface)" }}>
              <Terminal className="w-5 h-5" style={{ color: "var(--text-muted)" }} />
            </div>
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              No active execution trace.
            </p>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              Submit a task to see real-time agent decisions.
            </p>
          </div>
        )}

        {entries.map((entry, i) => {
          const style = TYPE_STYLE[entry.type] ?? { color: "var(--text-secondary)", prefix: "·" };
          return (
            <div key={i} className="slide-in flex gap-3 py-1.5 px-2 rounded-lg hover:bg-white/5 transition-colors group">
              <span className="mono text-xs shrink-0 pt-0.5" style={{ color: "var(--text-muted)", minWidth: 64 }}>
                {entry.timestamp}
              </span>
              <span className="shrink-0" style={{ color: style.color }}>{style.prefix}</span>
              <div className="min-w-0">
                {entry.node && (
                  <span className="text-xs font-semibold mr-2" style={{ color: style.color }}>
                    [{entry.node}]
                  </span>
                )}
                <span className="text-xs break-words" style={{ color: "var(--text-primary)" }}>
                  {entry.message}
                </span>
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
