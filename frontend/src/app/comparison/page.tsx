'use client';

import React, { useState, useEffect } from 'react';
import {
  GitCompare,
  Users,
  Award,
  ShieldCheck,
  TrendingUp,
  Activity,
  ArrowRight,
  Flame,
  CheckCircle2
} from 'lucide-react';

interface PlayerProfile {
  id: string;
  name: string;
  role: string;
  team: string;
  age: string;
  caps: string;
  stats: string;
  fit: string;
  bpri: number;
  bowpri: number;
  tsr: string;
  ter: string;
}

const CANDIDATES_POOL: PlayerProfile[] = [
  {
    id: "UNSTOP_0034",
    name: "Andre Siddharth",
    role: "Middle-Order RH Batter",
    team: "Tamil Nadu",
    age: "20y 02m 11d",
    caps: "0 Tests, 0 ODIs, 0 T20Is (Uncapped)",
    stats: "Ranji Trophy 2024-25: 15 FC matches, 1,021 runs, HS 121, 2x100s, 8x50s; TNPL: 21 matches, 443 runs, SR 133.80.",
    fit: "High-ceiling middle-order anchor to stabilize RR top-order power hitters (Yashasvi Jaiswal, Riyan Parag).",
    bpri: 82.4,
    bowpri: 0.0,
    tsr: "+18.4",
    ter: "N/A"
  },
  {
    id: "UNSTOP_0098",
    name: "Hardik Raj",
    role: "Slow Left-Arm Orthodox All-Rounder",
    team: "Karnataka",
    age: "20y 07m 29d",
    caps: "0 Tests, 0 ODIs, 0 T20Is (Uncapped)",
    stats: "Ranji Trophy 2024-25: 11 FC matches, 34 wickets, BBI 5/42, Econ 2.68; Batting: 412 runs, HS 82*.",
    fit: "Elite left-arm spin replacement to solve RR's 2024-2026 middle-over dot drought post-Chahal release.",
    bpri: 74.2,
    bowpri: 84.8,
    tsr: "+8.2",
    ter: "-1.42"
  },
  {
    id: "UNSTOP_0012",
    name: "Vidwath Kaverappa",
    role: "Right-Arm Fast Medium",
    team: "Karnataka",
    age: "27y 08m 14d",
    caps: "Uncapped Senior",
    stats: "SMAT: 34 wickets, Econ 6.82; Death Overs Economy: 8.12 RPO.",
    fit: "Disciplined seam pacer providing support to Trent Boult and Matheesha Pathirana in the powerplay and middle phases.",
    bpri: 0.0,
    bowpri: 86.5,
    tsr: "N/A",
    ter: "-1.88"
  },
  {
    id: "UNSTOP_0145",
    name: "Ashutosh Sharma",
    role: "Right-Hand Death Finisher",
    team: "Railways",
    age: "28y 01m 20d",
    caps: "Uncapped",
    stats: "SMAT fastest fifty (11 balls). IPL death overs Strike Rate 204.8.",
    fit: "Pace-hitting death finisher to complement Shimron Hetmyer and Dhruv Jurel in overs 16–20.",
    bpri: 85.2,
    bowpri: 0.0,
    tsr: "+32.6",
    ter: "N/A"
  }
];

export default function ComparisonPage() {
  const [playerAId, setPlayerAId] = useState<string>(CANDIDATES_POOL[0].id);
  const [playerBId, setPlayerBId] = useState<string>(CANDIDATES_POOL[1].id);

  const playerA = CANDIDATES_POOL.find((p) => p.id === playerAId) || CANDIDATES_POOL[0];
  const playerB = CANDIDATES_POOL.find((p) => p.id === playerBId) || CANDIDATES_POOL[1];

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-pink-500/20 p-2 text-pink-400">
            <GitCompare className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-black tracking-wide text-white">
            Head-to-Head Candidate Intelligence
          </h1>
        </div>
        <p className="mt-1 text-sm text-slate-400">
          Compare candidate sabermetric indicators, pressure indexes, role scarcity, and Rajasthan Royals strategic fit.
        </p>
      </div>

      {/* Selectors */}
      <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="rounded-xl border border-pink-500/30 bg-slate-900/60 p-4">
          <label className="block text-xs font-semibold uppercase tracking-wider text-pink-400 mb-2">
            Select Player A
          </label>
          <select
            value={playerAId}
            onChange={(e) => setPlayerAId(e.target.value)}
            className="w-full rounded-lg border border-white/10 bg-slate-950 px-3 py-2 text-sm text-white focus:border-pink-500 focus:outline-none"
          >
            {CANDIDATES_POOL.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.role} · {p.team})
              </option>
            ))}
          </select>
        </div>

        <div className="rounded-xl border border-blue-500/30 bg-slate-900/60 p-4">
          <label className="block text-xs font-semibold uppercase tracking-wider text-blue-400 mb-2">
            Select Player B
          </label>
          <select
            value={playerBId}
            onChange={(e) => setPlayerBId(e.target.value)}
            className="w-full rounded-lg border border-white/10 bg-slate-950 px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
          >
            {CANDIDATES_POOL.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.role} · {p.team})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Player A Card */}
        <div className="rounded-2xl border border-pink-500/30 bg-gradient-to-b from-pink-950/20 via-slate-900/60 to-slate-950 p-6 backdrop-blur-md">
          <div className="flex items-start justify-between">
            <div>
              <span className="rounded bg-pink-500/20 px-2 py-0.5 text-[10px] font-bold text-pink-400 border border-pink-500/30">
                {playerA.team}
              </span>
              <h2 className="mt-2 text-xl font-black text-white">{playerA.name}</h2>
              <p className="text-xs text-slate-400">{playerA.role}</p>
            </div>
            <div className="text-right">
              <span className="text-[10px] uppercase tracking-wider text-slate-500">Age</span>
              <p className="font-mono text-sm font-semibold text-slate-200">{playerA.age}</p>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-slate-950/60 p-3 border border-white/5">
              <span className="text-[10px] text-slate-400 uppercase">Pressure Score</span>
              <p className="font-mono text-lg font-bold text-pink-400">
                {playerA.bpri > 0 ? `BPRI ${playerA.bpri}` : `BOWPRI ${playerA.bowpri}`}
              </p>
            </div>
            <div className="rounded-xl bg-slate-950/60 p-3 border border-white/5">
              <span className="text-[10px] text-slate-400 uppercase">Impact Metric</span>
              <p className="font-mono text-lg font-bold text-emerald-400">
                {playerA.tsr !== 'N/A' ? `TSR ${playerA.tsr}` : `TER ${playerA.ter}`}
              </p>
            </div>
          </div>

          <div className="mt-6">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Domestic Performance</h4>
            <p className="mt-1 text-xs text-slate-400 leading-relaxed">{playerA.stats}</p>
          </div>

          <div className="mt-4 border-t border-white/5 pt-4">
            <h4 className="text-xs font-semibold text-pink-400 uppercase tracking-wider">Rajasthan Royals Fit</h4>
            <p className="mt-1 text-xs text-slate-300 leading-relaxed">{playerA.fit}</p>
          </div>
        </div>

        {/* Player B Card */}
        <div className="rounded-2xl border border-blue-500/30 bg-gradient-to-b from-blue-950/20 via-slate-900/60 to-slate-950 p-6 backdrop-blur-md">
          <div className="flex items-start justify-between">
            <div>
              <span className="rounded bg-blue-500/20 px-2 py-0.5 text-[10px] font-bold text-blue-400 border border-blue-500/30">
                {playerB.team}
              </span>
              <h2 className="mt-2 text-xl font-black text-white">{playerB.name}</h2>
              <p className="text-xs text-slate-400">{playerB.role}</p>
            </div>
            <div className="text-right">
              <span className="text-[10px] uppercase tracking-wider text-slate-500">Age</span>
              <p className="font-mono text-sm font-semibold text-slate-200">{playerB.age}</p>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-slate-950/60 p-3 border border-white/5">
              <span className="text-[10px] text-slate-400 uppercase">Pressure Score</span>
              <p className="font-mono text-lg font-bold text-blue-400">
                {playerB.bpri > 0 ? `BPRI ${playerB.bpri}` : `BOWPRI ${playerB.bowpri}`}
              </p>
            </div>
            <div className="rounded-xl bg-slate-950/60 p-3 border border-white/5">
              <span className="text-[10px] text-slate-400 uppercase">Impact Metric</span>
              <p className="font-mono text-lg font-bold text-emerald-400">
                {playerB.tsr !== 'N/A' ? `TSR ${playerB.tsr}` : `TER ${playerB.ter}`}
              </p>
            </div>
          </div>

          <div className="mt-6">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Domestic Performance</h4>
            <p className="mt-1 text-xs text-slate-400 leading-relaxed">{playerB.stats}</p>
          </div>

          <div className="mt-4 border-t border-white/5 pt-4">
            <h4 className="text-xs font-semibold text-blue-400 uppercase tracking-wider">Rajasthan Royals Fit</h4>
            <p className="mt-1 text-xs text-slate-300 leading-relaxed">{playerB.fit}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
