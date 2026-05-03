import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agent Orchestrator — Multi-Agent AI Platform",
  description:
    "Production-grade multi-agent orchestration system with tool use, persistent memory, and human-in-the-loop escalation. Built with LangGraph and Groq.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col relative z-10">{children}</body>
    </html>
  );
}
