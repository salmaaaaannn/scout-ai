'use client';

import React, { useState } from 'react';
import {
  Bot,
  Send,
  Sparkles,
  ShieldCheck,
  FileText,
  AlertTriangle,
  RefreshCw,
  User,
  CheckCircle2
} from 'lucide-react';

interface Citation {
  player: string;
  player_id: string;
  data_source: string;
  verification_status: string;
}

interface AssistantResponse {
  query: string;
  answer: string;
  citations: Citation[];
  matched_players_count: number;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
}

const PRESET_QUERIES = [
  "Explain why Andre Siddharth is recommended for Rajasthan Royals middle-order.",
  "Compare Vidwath Kaverappa's death-over economy against IPL baselines.",
  "What is our primary middle-over spin weakness post-Chahal?",
  "Recommend an uncapped pace bowler with low lateral trunk spine stress."
];

export default function AssistantPage() {
  const [inputQuery, setInputQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        "Welcome, Coach Sangakkara & Director Lindsay. I am ROYALS ScoutIQ Tactical Assistant. Ask me any question regarding uncapped player sabermetrics, RoyalVision biomechanics, auction economics, or our matchday Playing XI strategy. Every technical claim cites verified video timestamps and official domestic match logs.",
    },
  ]);
  const [loading, setLoading] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  async function handleSendQuery(queryToSend?: string) {
    const q = queryToSend || inputQuery;
    if (!q.trim()) return;

    const userMsg: Message = { role: 'user', content: q };
    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const res = await fetch(`${apiUrl}/api/assistant/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q }),
      });

      if (res.ok) {
        const data: AssistantResponse = await res.json();
        const assistantMsg: Message = {
          role: 'assistant',
          content: data.answer,
          citations: data.citations,
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: 'ScoutIQ Assistant encountered an error connecting to the retrieval dispatcher.',
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Network connection failed. Ensure the FastAPI backend is running on :8000.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-pink-500/20 p-2 text-pink-400">
              <Bot className="h-6 w-6" />
            </div>
            <h1 className="text-2xl font-black tracking-wide text-white">
              AI Assistance
            </h1>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Grounded tactical AI assistant synthesizing structured match records with verified RoyalVision biomechanics.
          </p>
        </div>
      </div>

      {/* Preset Query Chips */}
      <div className="mb-6 flex flex-wrap gap-2">
        {PRESET_QUERIES.map((preset, idx) => (
          <button
            key={idx}
            onClick={() => handleSendQuery(preset)}
            className="rounded-full border border-pink-500/20 bg-slate-900/80 px-3 py-1.5 text-xs text-slate-300 hover:border-pink-500/50 hover:text-white transition-all"
          >
            {preset}
          </button>
        ))}
      </div>

      {/* Chat Messages */}
      <div className="mb-6 flex flex-col gap-4 rounded-2xl border border-white/10 bg-slate-900/50 p-6 min-h-[480px] backdrop-blur-md overflow-y-auto">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex gap-3 ${
              m.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {m.role === 'assistant' && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-pink-600/20 text-pink-400 border border-pink-500/30">
                <Bot className="h-4 w-4" />
              </div>
            )}

            <div
              className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed ${
                m.role === 'user'
                  ? 'bg-gradient-to-r from-pink-600 to-rose-600 text-white font-medium'
                  : 'bg-slate-950/80 border border-white/10 text-slate-200'
              }`}
            >
              <div className="whitespace-pre-wrap">{m.content}</div>

              {/* Citations Box */}
              {m.citations && m.citations.length > 0 && (
                <div className="mt-4 pt-3 border-t border-white/10">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" /> Evidence Citations:
                  </span>
                  <div className="mt-1.5 space-y-1">
                    {m.citations.map((c, cIdx) => (
                      <div
                        key={cIdx}
                        className="flex items-center justify-between text-[11px] text-slate-300 bg-white/5 rounded px-2 py-1"
                      >
                        <span>
                          <strong>{c.player}</strong> — {c.data_source}
                        </span>
                        <span className="rounded bg-emerald-500/20 px-1.5 py-0.2 text-[9px] font-bold text-emerald-400">
                          {c.verification_status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {m.role === 'user' && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-800 text-slate-300">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-xs text-slate-400 p-2">
            <RefreshCw className="h-4 w-4 animate-spin text-pink-500" />
            Synthesizing evidence-grounded scouting brief with verified match citations...
          </div>
        )}
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSendQuery();
        }}
        className="flex gap-2"
      >
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder="Ask about a player's pressure stats, biomechanical risk, or auction fit..."
          className="flex-1 rounded-xl border border-white/10 bg-slate-950 px-4 py-3 text-xs text-white placeholder-slate-500 focus:border-pink-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading || !inputQuery.trim()}
          className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-pink-600 to-rose-600 px-6 py-3 text-xs font-bold text-white shadow-lg shadow-pink-500/20 hover:from-pink-500 hover:to-rose-500 transition-all disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
          Send
        </button>
      </form>
    </div>
  );
}
