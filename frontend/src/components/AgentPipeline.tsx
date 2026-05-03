"use client";

import React from "react";
import { Search, Code, PenLine, Shield, UserCheck, CheckCircle, Loader2, Clock } from "lucide-react";

interface Step {
  specialist: string;
  description: string;
}

interface AgentPipelineProps {
  steps: Step[];
  activeNode: string;
  completedNodes: string[];
}

const SPECIALIST_META: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  research: { label: "Research", icon: <Search className="w-4 h-4" />, color: "var(--blue)" },
  coder:    { label: "Coder",    icon: <Code    className="w-4 h-4" />, color: "var(--purple)" },
  writer:   { label: "Writer",  icon: <PenLine  className="w-4 h-4" />, color: "var(--green)" },
  review:   { label: "Reviewer", icon: <Shield  className="w-4 h-4" />, color: "var(--yellow)" },
  human_review: { label: "Human", icon: <UserCheck className="w-4 h-4" />, color: "var(--red)" },
};

function PipelineNode({ step, isActive, isDone }: { step: Step; isActive: boolean; isDone: boolean }) {
  const meta = SPECIALIST_META[step.specialist] ?? SPECIALIST_META.research;

  return (
    <div className="pipeline-node" style={{ minWidth: 90 }}>
      <div
        className="w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-500"
        style={{
          borderColor: isDone ? "var(--green)" : isActive ? meta.color : "var(--border)",
          background: isDone
            ? "rgba(16,185,129,0.15)"
            : isActive
            ? `rgba(59,130,246,0.15)`
            : "var(--surface)",
          boxShadow: isActive ? `0 0 16px ${meta.color}55` : "none",
          color: isDone ? "var(--green)" : isActive ? meta.color : "var(--text-secondary)",
        }}
      >
        {isDone ? (
          <CheckCircle className="w-4 h-4" />
        ) : isActive ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          meta.icon
        )}
      </div>
      <span className="text-xs font-medium" style={{ color: isDone ? "var(--green)" : isActive ? "var(--text-primary)" : "var(--text-secondary)" }}>
        {meta.label}
      </span>
      {step.description && (
        <span className="text-xs text-center leading-tight" style={{ color: "var(--text-secondary)", maxWidth: 90 }}>
          {step.description.length > 40 ? step.description.slice(0, 40) + "…" : step.description}
        </span>
      )}
    </div>
  );
}

export default function AgentPipeline({ steps, activeNode, completedNodes }: AgentPipelineProps) {
  const allSteps: Step[] = [
    { specialist: "supervisor", description: "Plan & delegate" },
    ...steps,
    { specialist: "review", description: "Validate outputs" },
  ];

  if (allSteps.length <= 1) {
    return (
      <div className="flex items-center justify-center py-8 gap-2" style={{ color: "var(--text-secondary)" }}>
        <Clock className="w-4 h-4" />
        <span className="text-sm">Waiting for task submission…</span>
      </div>
    );
  }

  return (
    <div className="flex items-start justify-between gap-2 py-4 px-2 overflow-x-auto">
      {allSteps.map((step, i) => {
        const nodeKey = step.specialist;
        const isActive = activeNode.toLowerCase().includes(nodeKey);
        const isDone = completedNodes.some((n) => n.toLowerCase().includes(nodeKey));
        return (
          <React.Fragment key={i}>
            <PipelineNode step={step} isActive={isActive} isDone={isDone} />
            {i < allSteps.length - 1 && (
              <div
                className="flex-1 h-0.5 mt-5 transition-all duration-500"
                style={{
                  background: isDone
                    ? "linear-gradient(90deg, var(--green), var(--border))"
                    : "var(--border)",
                  minWidth: 20,
                }}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}
