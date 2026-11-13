'use client';

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Award,
  ShieldCheck,
  TrendingUp,
  Target,
  Sparkles,
  CheckCircle2,
  Search,
  ExternalLink
} from "lucide-react";

interface Phase4PlayerRow {
  rank: number;
  player_id: string;
  player_name: string;
  nationality: string;
  age: number;
  batting_role?: string;
  bowling_style?: string;
  bowling_role?: string;
  wicketkeeper?: string;
  current_franchise: string;
  latest_contract_status: string;
  release_status: string;
  auction_eligibility: string;
  availability_status: string;
  ipl_matches: number;
  ipl_runs?: number;
  ipl_average?: number;
  ipl_strike_rate?: number;
  ipl_wickets?: number;
  ipl_economy?: number;
  t20i_summary: string;
  domestic_t20_summary: string;
  recent_form_12_months: string;
  pressure_score: number;
  strengths: string;
  weaknesses: string;
  rr_role_fit: string;
  evidence_sources: string;
  verification_status: string;
}

export default function ScoutingPage() {
  const [activeTab, setActiveTab] = useState<"top10_batters" | "top10_bowlers" | "shai_hope">("top10_batters");
  const [batters, setBatters] = useState<Phase4PlayerRow[]>([]);
  const [bowlers, setBowlers] = useState<Phase4PlayerRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const [batRes, bowlRes] = await Promise.all([
          fetch(`${apiUrl}/api/rankings/phase4/top10_batters`),
          fetch(`${apiUrl}/api/rankings/phase4/top10_bowlers`),
        ]);

        if (batRes.ok) {
          const d = await batRes.json();
          setBatters(d.top10_batters || []);
        }
        if (bowlRes.ok) {
          const d = await bowlRes.json();
          setBowlers(d.top10_bowlers || []);
        }
      } catch (err) {
        console.error("Failed to load verified market data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const filteredBatters = batters.filter(b => 
    !searchTerm || 
    b.player_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (b.batting_role || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
    b.nationality.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredBowlers = bowlers.filter(b => 
    !searchTerm || 
    b.player_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (b.bowling_style || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
    b.nationality.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Clean Rajasthan Royals Header Banner */}
      <section className="rounded-2xl border border-slate-800 bg-[#0B132B] p-6 md:p-8 shadow-sm">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-[#E81A85] text-white">
                RAJASTHAN ROYALS SCOUTING
              </span>
              <span className="text-xs font-semibold uppercase tracking-wider text-[#D4AF37]">
                Verified Available Targets
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Player Acquisition Shortlist
            </h1>
            <p className="text-xs text-slate-400 mt-1 max-w-3xl leading-relaxed">
              Audited against official BCCI contracts and IPL auction registrations. Only verified free agents and confirmed available talent are qualified for recruitment.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <span className="px-3.5 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" /> Contract Status Verified
            </span>
          </div>
        </div>

        {/* Tab Controls & Search */}
        <div className="mt-6 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-2 text-xs font-semibold">
            <button
              onClick={() => setActiveTab("top10_batters")}
              className={`px-4 py-2 rounded-xl transition flex items-center gap-2 ${
                activeTab === "top10_batters"
                  ? "bg-[#E81A85] text-white shadow-md shadow-pink-500/20"
                  : "bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800"
              }`}
            >
              <Target className="w-4 h-4" />
              Final 10 Batters
            </button>
            <button
              onClick={() => setActiveTab("top10_bowlers")}
              className={`px-4 py-2 rounded-xl transition flex items-center gap-2 ${
                activeTab === "top10_bowlers"
                  ? "bg-[#E81A85] text-white shadow-md shadow-pink-500/20"
                  : "bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800"
              }`}
            >
              <TrendingUp className="w-4 h-4" />
              Final 10 Bowlers
            </button>
            <button
              onClick={() => setActiveTab("shai_hope")}
              className={`px-4 py-2 rounded-xl transition flex items-center gap-2 ${
                activeTab === "shai_hope"
                  ? "bg-[#E81A85] text-white shadow-md shadow-pink-500/20"
                  : "bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800"
              }`}
            >
              <Sparkles className="w-4 h-4 text-[#D4AF37]" />
              Shai Hope (Key Target Dossier)
            </button>
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search candidate or role..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#E81A85]"
            />
          </div>
        </div>
      </section>

      {/* TAB 1: TOP 10 BATTERS */}
      {activeTab === "top10_batters" && (
        <div className="space-y-4">
          <div className="rounded-xl border border-slate-800 bg-[#0D1838] p-4 flex items-center justify-between text-xs text-slate-300">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Available Batting Targets for Rajasthan Royals Middle-Overs &amp; Top-Order Reinforcement</span>
            </div>
            <span className="font-mono text-slate-400 font-semibold">{filteredBatters.length} Available</span>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-800 bg-[#0B132B]">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
                <tr>
                  <th className="p-3.5">Rank</th>
                  <th className="p-3.5">Player &amp; Role</th>
                  <th className="p-3.5">Nationality / Age</th>
                  <th className="p-3.5">Availability</th>
                  <th className="p-3.5">IPL Career</th>
                  <th className="p-3.5">Recent Form &amp; Evidence</th>
                  <th className="p-3.5">RR Tactical Fit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {filteredBatters.map((b) => (
                  <tr key={b.player_id} className="hover:bg-slate-900/40 transition">
                    <td className="p-3.5 font-bold font-mono text-[#D4AF37]">#{b.rank}</td>
                    <td className="p-3.5">
                      <div className="font-bold text-white text-sm flex items-center gap-1.5">
                        {b.player_name}
                        {b.rank === 1 && (
                          <span className="px-1.5 py-0.2 rounded text-[9px] bg-[#E81A85] text-white font-black uppercase">
                            #1 TARGET
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-slate-400">{b.batting_role}</div>
                      <div className="text-[10px] text-slate-500 font-mono">ID: {b.player_id}</div>
                    </td>
                    <td className="p-3.5 text-slate-300">
                      <div>{b.nationality}</div>
                      <div className="text-slate-500 text-[10px]">{b.age}y</div>
                    </td>
                    <td className="p-3.5">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold block w-fit">
                        {b.availability_status}
                      </span>
                      <span className="text-[10px] text-slate-500 block mt-0.5">
                        {b.current_franchise}
                      </span>
                    </td>
                    <td className="p-3.5 text-slate-300 font-mono">
                      <div>{b.ipl_matches}M · {b.ipl_runs}R</div>
                      <div className="text-[#D4AF37] text-[11px] font-bold">SR: {b.ipl_strike_rate != null ? Number(b.ipl_strike_rate).toFixed(1) : 'N/A'}</div>
                    </td>
                    <td className="p-3.5 text-slate-400 max-w-xs text-[11px]">
                      <p>{b.recent_form_12_months}</p>
                    </td>
                    <td className="p-3.5 text-slate-300 max-w-sm text-[11px]">
                      {b.rr_role_fit}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: TOP 10 BOWLERS */}
      {activeTab === "top10_bowlers" && (
        <div className="space-y-4">
          <div className="rounded-xl border border-slate-800 bg-[#0D1838] p-4 flex items-center justify-between text-xs text-slate-300">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Available Bowling Targets for Rajasthan Royals Death Overs &amp; Powerplay Control</span>
            </div>
            <span className="font-mono text-slate-400 font-semibold">{filteredBowlers.length} Available</span>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-800 bg-[#0B132B]">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
                <tr>
                  <th className="p-3.5">Rank</th>
                  <th className="p-3.5">Player &amp; Style</th>
                  <th className="p-3.5">Nationality / Age</th>
                  <th className="p-3.5">Availability</th>
                  <th className="p-3.5">IPL Career</th>
                  <th className="p-3.5">Recent Form &amp; Evidence</th>
                  <th className="p-3.5">RR Tactical Fit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {filteredBowlers.map((b) => (
                  <tr key={b.player_id} className="hover:bg-slate-900/40 transition">
                    <td className="p-3.5 font-bold font-mono text-[#D4AF37]">#{b.rank}</td>
                    <td className="p-3.5">
                      <div className="font-bold text-white text-sm flex items-center gap-1.5">
                        {b.player_name}
                        {b.rank === 1 && (
                          <span className="px-1.5 py-0.2 rounded text-[9px] bg-[#E81A85] text-white font-black uppercase">
                            #1 TARGET
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-slate-400">{b.bowling_style}</div>
                      <div className="text-[10px] text-slate-500 font-mono">ID: {b.player_id}</div>
                    </td>
                    <td className="p-3.5 text-slate-300">
                      <div>{b.nationality}</div>
                      <div className="text-slate-500 text-[10px]">{b.age}y</div>
                    </td>
                    <td className="p-3.5">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold block w-fit">
                        {b.availability_status}
                      </span>
                      <span className="text-[10px] text-slate-500 block mt-0.5">
                        {b.current_franchise}
                      </span>
                    </td>
                    <td className="p-3.5 text-slate-300 font-mono">
                      <div>{b.ipl_matches}M · {b.ipl_wickets}W</div>
                      <div className="text-emerald-400 text-[11px] font-bold">Econ: {b.ipl_economy != null ? Number(b.ipl_economy).toFixed(2) : 'N/A'}</div>
                    </td>
                    <td className="p-3.5 text-slate-400 max-w-xs text-[11px]">
                      <p>{b.recent_form_12_months}</p>
                    </td>
                    <td className="p-3.5 text-slate-300 max-w-sm text-[11px]">
                      {b.rr_role_fit}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: SHAI HOPE DOSSIER */}
      {activeTab === "shai_hope" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-800 bg-[#0B132B] p-6">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
              <div>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-[#D4AF37] text-black">
                  PRIORITY TARGET
                </span>
                <h2 className="text-2xl font-black text-white mt-1.5">Shai Diego Hope</h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  West Indies White-Ball Captain &amp; Wicketkeeper-Batter · Age 33 · Free Agent · Confirmed Available
                </p>
              </div>
              <div className="text-right">
                <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold font-mono">
                  FREE AGENT CONFIRMED
                </span>
              </div>
            </div>

            {/* Performance Stats */}
            <div className="mt-6 rounded-xl bg-[#0D1838] p-5 border border-slate-800">
              <h3 className="text-sm font-bold uppercase text-[#D4AF37] flex items-center gap-2 mb-4">
                <Sparkles className="w-4 h-4 text-[#D4AF37]" /> Verified Series: West Indies in India 2026
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 font-mono text-center">
                <div className="bg-slate-900/60 rounded-lg p-3 border border-slate-800/80">
                  <div className="text-slate-400 text-[10px] uppercase">Innings</div>
                  <div className="text-lg font-bold text-white mt-1">4</div>
                </div>
                <div className="bg-slate-900/60 rounded-lg p-3 border border-slate-800/80">
                  <div className="text-slate-400 text-[10px] uppercase">Runs</div>
                  <div className="text-lg font-bold text-white mt-1">261</div>
                </div>
                <div className="bg-slate-900/60 rounded-lg p-3 border border-slate-800/80">
                  <div className="text-slate-400 text-[10px] uppercase">Average</div>
                  <div className="text-lg font-bold text-emerald-400 mt-1">130.50</div>
                </div>
                <div className="bg-slate-900/60 rounded-lg p-3 border border-slate-800/80">
                  <div className="text-slate-400 text-[10px] uppercase">Strike Rate</div>
                  <div className="text-lg font-bold text-[#E81A85] mt-1">190.51</div>
                </div>
                <div className="bg-slate-900/60 rounded-lg p-3 border border-slate-800/80">
                  <div className="text-slate-400 text-[10px] uppercase">Boundaries</div>
                  <div className="text-lg font-bold text-[#D4AF37] mt-1">17x4, 18x6</div>
                </div>
              </div>
              <p className="text-xs text-slate-300 mt-4 leading-relaxed">
                Two match-winning centuries in India: <strong>102* off 45b</strong> at Raipur (SR 226.7) and <strong>102* off 50b</strong> at Pune (SR 204.0). Demonstrated mastery against elite subcontinental spin.
              </p>
            </div>

            {/* Tactical Fit Rationale */}
            <div className="mt-6 rounded-xl bg-slate-900/60 border border-slate-800 p-5">
              <span className="text-[10px] uppercase font-bold text-[#E81A85] tracking-wider block mb-1">
                Rajasthan Royals Tactical Alignment
              </span>
              <p className="text-xs text-slate-300 leading-relaxed">
                Directly addresses RR&apos;s need for a high-tactical IQ No. 3/4 spin manipulator capable of accelerating beyond 180+ SR. Provides wicketkeeping depth alongside Dhruv Jurel and international captaincy leadership at an optimal valuation.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
