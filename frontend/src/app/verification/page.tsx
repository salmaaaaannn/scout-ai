'use client';

import React, { useState, useEffect } from 'react';
import {
  CheckSquare,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Edit3,
  RotateCcw,
  Sparkles,
  Users,
  RefreshCw,
  Clock,
  AlertCircle
} from 'lucide-react';

interface VerificationItem {
  obs_id: string;
  player_id: string;
  player_name: string;
  video_id: string;
  timestamp_seconds: number;
  original_ai_observation: string;
  current_observation: string;
  ai_observation: string;
  confidence_multiplier: number;
  status: string;
  analyst_name?: string;
  review_notes?: string;
  created_at?: string;
  verified_at?: string;
}

export default function VerificationPage() {
  const [pendingQueue, setPendingQueue] = useState<VerificationItem[]>([]);
  const [historyList, setHistoryList] = useState<VerificationItem[]>([]);
  const [analystName, setAnalystName] = useState('Giles Lindsay');
  const [editingObsId, setEditingObsId] = useState<string | null>(null);
  const [correctedText, setCorrectedText] = useState('');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  async function loadQueueData() {
    setLoading(true);
    try {
      const [pendingRes, historyRes] = await Promise.all([
        fetch(`${apiUrl}/api/verification/pending`),
        fetch(`${apiUrl}/api/verification/history`),
      ]);

      if (pendingRes.ok) {
        const pData = await pendingRes.json();
        setPendingQueue(Array.isArray(pData) ? pData : pData.pending_queue || []);
      }
      if (historyRes.ok) {
        const hData = await historyRes.json();
        setHistoryList(Array.isArray(hData) ? hData : hData.history || []);
      }
    } catch (err) {
      console.error('Error loading verification queue:', err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadQueueData();
  }, []);

  async function handleConfirm(obsId: string) {
    try {
      const res = await fetch(`${apiUrl}/api/verification/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          obs_id: obsId,
          analyst_name: analystName,
        }),
      });
      if (res.ok) {
        setMessage(`Confirmed observation ${obsId}. Confidence boosted to 1.0.`);
        loadQueueData();
      }
    } catch (err) {
      console.error('Confirm error:', err);
    }
  }

  async function handleCorrect(obsId: string) {
    if (!correctedText) return;
    try {
      const res = await fetch(`${apiUrl}/api/verification/correct`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          obs_id: obsId,
          analyst_name: analystName,
          corrected_observation: correctedText,
          notes: 'Analyst manual correction via War Room portal',
        }),
      });
      if (res.ok) {
        setMessage(`Corrected observation ${obsId} successfully.`);
        setEditingObsId(null);
        setCorrectedText('');
        loadQueueData();
      }
    } catch (err) {
      console.error('Correct error:', err);
    }
  }

  async function handleReject(obsId: string) {
    try {
      const res = await fetch(`${apiUrl}/api/verification/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          obs_id: obsId,
          analyst_name: analystName,
          reason: 'Excluded due to video anomaly / low confidence detection',
        }),
      });
      if (res.ok) {
        setMessage(`Rejected observation ${obsId}. Multiplier set to 0.0 (excluded from AI indexing).`);
        loadQueueData();
      }
    } catch (err) {
      console.error('Reject error:', err);
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Header */}
      <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-pink-500/20 p-2 text-pink-400">
              <CheckSquare className="h-6 w-6" />
            </div>
            <h1 className="text-2xl font-black tracking-wide text-white">
              Human-in-the-Loop Analyst Verification Queue
            </h1>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Franchise analysts confirm (1.0), correct, or reject (0.0) AI biomechanical and scouting claims before AI Assistance indexing.
          </p>
        </div>

        {/* Analyst Selector */}
        <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-slate-900/60 p-2">
          <span className="text-xs text-slate-400 uppercase font-semibold pl-2">Logged in:</span>
          <select
            value={analystName}
            onChange={(e) => setAnalystName(e.target.value)}
            className="rounded-lg border border-white/10 bg-slate-950 px-3 py-1.5 text-xs text-white focus:border-pink-500 focus:outline-none"
          >
            <option value="Giles Lindsay">Giles Lindsay (Director of Strategy)</option>
            <option value="Kumar Sangakkara">Kumar Sangakkara (Head Coach)</option>
            <option value="Senior Scout">Senior Scout (Domestic Talent)</option>
          </select>
        </div>
      </div>

      {message && (
        <div className="mb-6 rounded-xl border border-emerald-500/30 bg-emerald-950/20 px-4 py-3 text-xs text-emerald-300">
          {message}
        </div>
      )}

      {/* Pending Queue Section */}
      <div className="mb-10 overflow-hidden rounded-2xl border border-white/10 bg-slate-900/50 backdrop-blur-md">
        <div className="border-b border-white/10 bg-slate-950/80 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-amber-400" />
            <h2 className="text-base font-bold text-white">Pending Observations Awaiting Sign-Off</h2>
          </div>
          <span className="rounded-full bg-amber-500/20 px-2.5 py-0.5 text-xs font-mono font-bold text-amber-400 border border-amber-500/30">
            {pendingQueue.length} PENDING
          </span>
        </div>

        {loading ? (
          <div className="flex justify-center p-8">
            <RefreshCw className="h-6 w-6 animate-spin text-pink-500" />
          </div>
        ) : pendingQueue.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-400">
            All video observations have been verified by franchise analysts. Zero pending items.
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {pendingQueue.map((item) => (
              <div key={item.obs_id} className="p-6 hover:bg-white/5 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs font-bold text-pink-400">{item.obs_id}</span>
                    <span className="font-semibold text-white text-sm">{item.player_name}</span>
                    <span className="text-xs text-slate-400 font-mono">({item.player_id})</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-mono text-slate-300">
                      t = {item.timestamp_seconds}s
                    </span>
                    <span className="rounded bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-400 border border-amber-500/30">
                      Multiplier: {item.confidence_multiplier}
                    </span>
                  </div>
                </div>

                <div className="mt-3 rounded-xl bg-slate-950/60 p-4 border border-white/5 text-xs text-slate-200">
                  {editingObsId === item.obs_id ? (
                    <div>
                      <textarea
                        value={correctedText}
                        onChange={(e) => setCorrectedText(e.target.value)}
                        className="w-full rounded-lg border border-pink-500/40 bg-slate-900 p-2 text-xs text-white focus:outline-none"
                        rows={2}
                      />
                      <div className="mt-2 flex justify-end gap-2">
                        <button
                          onClick={() => setEditingObsId(null)}
                          className="rounded px-3 py-1 text-xs text-slate-400 hover:text-white"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => handleCorrect(item.obs_id)}
                          className="rounded bg-pink-600 px-3 py-1 text-xs font-bold text-white hover:bg-pink-500"
                        >
                          Save Correction
                        </button>
                      </div>
                    </div>
                  ) : (
                    item.current_observation || item.ai_observation
                  )}
                </div>

                {editingObsId !== item.obs_id && (
                  <div className="mt-4 flex flex-wrap items-center justify-end gap-2">
                    <button
                      onClick={() => handleConfirm(item.obs_id)}
                      className="flex items-center gap-1.5 rounded-lg bg-emerald-600/20 px-3 py-1.5 text-xs font-semibold text-emerald-400 border border-emerald-500/30 hover:bg-emerald-600/30 transition-colors"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5" /> Confirm (Weight 1.0)
                    </button>
                    <button
                      onClick={() => {
                        setEditingObsId(item.obs_id);
                        setCorrectedText(item.current_observation || item.ai_observation);
                      }}
                      className="flex items-center gap-1.5 rounded-lg bg-amber-600/20 px-3 py-1.5 text-xs font-semibold text-amber-400 border border-amber-500/30 hover:bg-amber-600/30 transition-colors"
                    >
                      <Edit3 className="h-3.5 w-3.5" /> Correct Observation
                    </button>
                    <button
                      onClick={() => handleReject(item.obs_id)}
                      className="flex items-center gap-1.5 rounded-lg bg-rose-600/20 px-3 py-1.5 text-xs font-semibold text-rose-400 border border-rose-500/30 hover:bg-rose-600/30 transition-colors"
                    >
                      <XCircle className="h-3.5 w-3.5" /> Reject (Weight 0.0)
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* History of Verified Observations */}
      <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900/50 backdrop-blur-md">
        <div className="border-b border-white/10 bg-slate-950/80 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            <h2 className="text-base font-bold text-white">Verified Ground Truth History</h2>
          </div>
          <span className="font-mono text-xs text-slate-400">Indexed for AI Assistance</span>
        </div>

        <div className="divide-y divide-white/5">
          {historyList.map((h) => (
            <div key={h.obs_id} className="p-4 flex items-start justify-between gap-4 text-xs">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white">{h.player_name}</span>
                  <span className={`rounded px-1.5 py-0.2 text-[9px] font-bold border ${
                    h.status === 'CONFIRMED'
                      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                      : h.status === 'CORRECTED'
                      ? 'bg-blue-500/20 text-blue-400 border-blue-500/30'
                      : 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                  }`}>
                    {h.status}
                  </span>
                  <span className="text-slate-500 text-[10px]">by {h.analyst_name || 'Giles Lindsay'}</span>
                </div>
                <p className="mt-1 text-slate-300">{h.current_observation || h.ai_observation}</p>
              </div>
              <span className="font-mono text-xs font-semibold text-slate-400 shrink-0">
                W={h.confidence_multiplier}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
