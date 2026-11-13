'use client';

import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  AlertTriangle,
  TrendingDown,
  Activity,
  Layers,
  ChevronRight,
  Flame,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';

interface WeaknessItem {
  area: string;
  metric: string;
  benchmark: string;
  rr_value: string;
  severity: string;
  impact_summary: string;
  recruitment_fix: string;
}

export default function WeaknessPage() {
  const [weaknessItems, setWeaknessItems] = useState<WeaknessItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [reportText, setReportText] = useState<string>('');

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    async function loadWeaknessData() {
      setLoading(true);
      try {
        const [matrixRes, reportRes] = await Promise.all([
          fetch(`${apiUrl}/api/rankings/phase5/weakness_matrix`),
          fetch(`${apiUrl}/api/rankings/phase5/historical_weakness_report`),
        ]);

        if (matrixRes.ok) {
          const data = await matrixRes.json();
          setWeaknessItems(Array.isArray(data) ? data : data.records || []);
        }
        if (reportRes.ok) {
          const txt = await reportRes.text();
          setReportText(txt);
        }
      } catch (err) {
        console.error('Failed to load weakness data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadWeaknessData();
  }, [apiUrl]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-pink-500/20 p-2 text-pink-400">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-black tracking-wide text-white">
            Rajasthan Royals 2024–2026 Historical Weakness Audit
          </h1>
        </div>
        <p className="mt-1 text-sm text-slate-400">
          Forensic sabermetric breakdown of middle-over dot ball droughts, defending economy spikes, and post-Chahal spin bowling collapse.
        </p>
      </div>

      {/* 3 Core Structural Flaws Cards */}
      <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="rounded-2xl border border-rose-500/30 bg-gradient-to-b from-rose-950/20 to-slate-950 p-6 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="rounded bg-rose-500/20 px-2.5 py-0.5 text-[10px] font-bold text-rose-400 border border-rose-500/30">
              CRITICAL SEVERITY
            </span>
            <span className="font-mono text-xs text-slate-400">Overs 7–15</span>
          </div>
          <h3 className="mt-3 text-lg font-bold text-white">Middle-Over Dot Ball Drought</h3>
          <p className="mt-2 text-xs text-slate-300 leading-relaxed">
            Dot ball percentage in overs 7–15 rose to <strong className="text-rose-400">41.8%</strong> (tournament baseline: 33.4%). Over-reliance on isolated top-order batting led to stalling against wrist-spin.
          </p>
          <div className="mt-4 pt-3 border-t border-white/5 text-[11px] text-amber-400">
            <strong>Recruitment Fix:</strong> Shai Hope / Spin-manipulating anchor with &lt;28% dot rate against spin.
          </div>
        </div>

        <div className="rounded-2xl border border-amber-500/30 bg-gradient-to-b from-amber-950/20 to-slate-950 p-6 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="rounded bg-amber-500/20 px-2.5 py-0.5 text-[10px] font-bold text-amber-400 border border-amber-500/30">
              HIGH SEVERITY
            </span>
            <span className="font-mono text-xs text-slate-400">Overs 16–20</span>
          </div>
          <h3 className="mt-3 text-lg font-bold text-white">Death Defending Economy Spikes</h3>
          <p className="mt-2 text-xs text-slate-300 leading-relaxed">
            When defending totals &gt;180, RR death bowling conceded <strong className="text-amber-400">11.84 RPO</strong> with an average boundary every 3.8 balls whenever frontline seamers were rotated out.
          </p>
          <div className="mt-4 pt-3 border-t border-white/5 text-[11px] text-amber-400">
            <strong>Recruitment Fix:</strong> Vidwath Kaverappa / 140k+ express yorker pacer with sub-8.5 RPO.
          </div>
        </div>

        <div className="rounded-2xl border border-blue-500/30 bg-gradient-to-b from-blue-950/20 to-slate-950 p-6 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="rounded bg-blue-500/20 px-2.5 py-0.5 text-[10px] font-bold text-blue-400 border border-blue-500/30">
              SYSTEMIC GAP
            </span>
            <span className="font-mono text-xs text-slate-400">Post-Chahal Era</span>
          </div>
          <h3 className="mt-3 text-lg font-bold text-white">Spin Bowling Strike Rate Collapse</h3>
          <p className="mt-2 text-xs text-slate-300 leading-relaxed">
            Middle-over spin strike rate plummeted to <strong className="text-blue-400">31.2 balls/wicket</strong> following Yuzvendra Chahal's departure, forcing pacers to bowl defensively in non-ideal phases.
          </p>
          <div className="mt-4 pt-3 border-t border-white/5 text-[11px] text-amber-400">
            <strong>Recruitment Fix:</strong> Hardik Raj (Slow Left-Arm Orthodox) with 2.68 FC economy.
          </div>
        </div>
      </div>

      {/* Weakness Matrix Table */}
      <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900/50 backdrop-blur-md">
        <div className="border-b border-white/10 px-6 py-4">
          <h2 className="text-base font-bold text-white">Phase-by-Phase Failure Mode Audit</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-white/10 bg-slate-950/80 text-[11px] uppercase tracking-wider text-slate-400">
              <tr>
                <th className="px-4 py-3">Flaw Category</th>
                <th className="px-4 py-3">Metric</th>
                <th className="px-4 py-3">Tournament Benchmark</th>
                <th className="px-4 py-3">RR Actual Performance</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Strategic Impact &amp; Target Solution</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              <tr className="hover:bg-white/5">
                <td className="px-4 py-3 font-semibold text-white">Middle-Overs Batting (7–15)</td>
                <td className="px-4 py-3 text-slate-300">Dot-Ball %</td>
                <td className="px-4 py-3 font-mono text-slate-400">33.4%</td>
                <td className="px-4 py-3 font-mono font-bold text-rose-400">41.8% (+8.4%)</td>
                <td className="px-4 py-3"><span className="rounded bg-rose-500/20 px-2 py-0.5 text-[10px] font-bold text-rose-400">CRITICAL</span></td>
                <td className="px-4 py-3 text-slate-300">Inability to rotate strike against left-arm finger spin. Solution: Andre Siddharth.</td>
              </tr>
              <tr className="hover:bg-white/5">
                <td className="px-4 py-3 font-semibold text-white">Middle-Overs Bowling (7–15)</td>
                <td className="px-4 py-3 text-slate-300">Spin Wickets / Match</td>
                <td className="px-4 py-3 font-mono text-slate-400">1.82</td>
                <td className="px-4 py-3 font-mono font-bold text-amber-400">0.94 (-48%)</td>
                <td className="px-4 py-3"><span className="rounded bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-400">HIGH</span></td>
                <td className="px-4 py-3 text-slate-300">Lack of wicket-taking spin threat. Solution: Hardik Raj.</td>
              </tr>
              <tr className="hover:bg-white/5">
                <td className="px-4 py-3 font-semibold text-white">Death Overs Bowling (16–20)</td>
                <td className="px-4 py-3 text-slate-300">Economy (Defending)</td>
                <td className="px-4 py-3 font-mono text-slate-400">9.60 RPO</td>
                <td className="px-4 py-3 font-mono font-bold text-rose-400">11.84 RPO</td>
                <td className="px-4 py-3"><span className="rounded bg-rose-500/20 px-2 py-0.5 text-[10px] font-bold text-rose-400">CRITICAL</span></td>
                <td className="px-4 py-3 text-slate-300">Boundary leakage in final 18 balls. Solution: Express Pacer / Vidwath Kaverappa.</td>
              </tr>
              <tr className="hover:bg-white/5">
                <td className="px-4 py-3 font-semibold text-white">Catching &amp; Outfielding</td>
                <td className="px-4 py-3 text-slate-300">Catch Conversion Rate</td>
                <td className="px-4 py-3 font-mono text-slate-400">82.5%</td>
                <td className="px-4 py-3 font-mono font-bold text-blue-400">76.8% (-5.7%)</td>
                <td className="px-4 py-3"><span className="rounded bg-blue-500/20 px-2 py-0.5 text-[10px] font-bold text-blue-400">MODERATE</span></td>
                <td className="px-4 py-3 text-slate-300">Boundary riding mistakes in dew games at Jaipur. Solution: Athletic uncapped outfielders.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
