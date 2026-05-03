"use client";

import { useState } from "react";
import axios from "axios";
import { Send, Loader2 } from "lucide-react";
import { clsx } from "clsx";

interface TaskRunnerProps {
  onTaskStarted: (threadId: string, task: string) => void;
}

export default function TaskRunner({ onTaskStarted }: TaskRunnerProps) {
  const [task, setTask] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/tasks", {
        task: task.trim(),
      });
      onTaskStarted(response.data.thread_id, task.trim());
      setTask("");
    } catch (err) {
      console.error("Failed to start task", err);
      alert("Failed to start task. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel rounded-xl p-6 mb-6 flex flex-col gap-4 shadow-xl">
      <div className="flex flex-col gap-1">
        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
          <Send className="w-5 h-5 text-blue-400" /> New Orchestration Task
        </h2>
        <p className="text-sm text-zinc-400">
          Enter a high-level goal. The Supervisor agent will decompose it and delegate work.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <textarea
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder="e.g., Research latest advancements in solid state batteries, summarize the top 3 players, and write a report."
          className={clsx(
            "w-full h-32 bg-black/40 border border-white/10 rounded-lg p-4 text-white placeholder-zinc-500",
            "focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-none transition-all"
          )}
          disabled={loading}
        />
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading || !task.trim()}
            className={clsx(
              "px-6 py-2.5 rounded-lg font-medium flex items-center gap-2 transition-all",
              "bg-blue-600 hover:bg-blue-500 text-white shadow-[0_0_15px_rgba(37,99,235,0.3)] hover:shadow-[0_0_20px_rgba(37,99,235,0.5)]",
              "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-600 disabled:hover:shadow-[0_0_15px_rgba(37,99,235,0.3)]"
            )}
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Dispatch Task"}
          </button>
        </div>
      </form>
    </div>
  );
}
