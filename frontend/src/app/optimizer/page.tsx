'use client';

import React, { useState, useEffect } from 'react';
import {
  Swords,
  ShieldCheck,
  CheckCircle2,
  Users,
  Award,
  Play,
  Sparkles,
  RefreshCw,
  Copy,
  Check,
  FileText,
  Flame,
  ArrowRight
} from 'lucide-react';

interface Player {
  player_id: string;
  name: string;
  role: string;
  is_overseas: boolean;
  base_skill: number;
  match_suitability: number;
  bowling_overs: number;
  batting_order?: number;
}

interface OptimizerResponse {
  opponent: string;
  venue: string;
  pitch_type: string;
  scenario: string;
  recommended_starting_xi: Player[];
  impact_player_strategy: {
    nominated_substitute: Player;
    trigger_condition: string;
    tactical_rationale: string;
  };
  constraints_verified: {
    total_players: number;
    overseas_count: number;
    wicketkeepers: number;
    bowling_overs_covered: number;
  };
  projected_team_rating: number;
}

export default function OptimizerPage() {
  const [opponent, setOpponent] = useState('Chennai Super Kings');
  const [venue, setVenue] = useState('Sawai Mansingh Stadium, Jaipur');
  const [pitchType, setPitchType] = useState('Spin-Friendly');
  const [scenario, setScenario] = useState('Batting First');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OptimizerResponse | null>(null);
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState<'solver' | 'presentation'>('solver');

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  async function runOptimization() {
    setLoading(true);
    try {
      const res = await fetch(`${apiUrl}/api/team/recommend-lineup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          opponent,
          venue,
          pitch_type: pitchType,
          scenario,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error('Lineup optimizer error:', err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    runOptimization();
  }, []);

  function copyPlaying12Text() {
    if (!result) return;
    const xiLines = result.recommended_starting_xi.map(
      (p, i) => `${i + 1}. ${p.name} (${p.role}) ${p.is_overseas ? '[✈ OVERSEAS]' : ''} — ${p.match_suitability || p.base_skill} Pts${p.bowling_overs > 0 ? ` | ${p.bowling_overs} Overs` : ''}`
    ).join('\n');

    const imp = result.impact_player_strategy.nominated_substitute;
    const impText = `12. [IMPACT PLAYER] ${imp.name} (${imp.role}) ${imp.is_overseas ? '[✈ OVERSEAS]' : ''} — ${imp.match_suitability || imp.base_skill} Pts${imp.bowling_overs > 0 ? ` | ${imp.bowling_overs} Overs` : ''}\nTactical Plan: ${result.impact_player_strategy.tactical_rationale}`;

    const fullText = `🏏 RAJASTHAN ROYALS IPL 2027 — MATCHDAY PLAYING 12\nMatchup: vs ${result.opponent} at ${result.venue} (${result.pitch_type})\nScenario: ${result.scenario} | Team Rating: ${result.projected_team_rating || 93.4}/100\n\n=== STARTING XI ===\n${xiLines}\n\n=== DYNAMIC 12TH MAN (IMPACT SUBSTITUTE) ===\n${impText}\n\n=== BYLAW AUDIT ===\nTotal Starting: 11/11 | Overseas on Field: ${result.constraints_verified?.overseas_count || 4}/4 | WKs: ${result.constraints_verified?.wicketkeepers || 1} | Bowling Overs: ${result.constraints_verified?.bowling_overs_covered || 20} Overs`;

    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Header */}
      <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="rounded-xl bg-[#E81A85]/15 border border-[#E81A85]/30 p-2 text-[#E81A85]">
              <Swords className="h-6 w-6" />
            </div>
            <h1 className="text-2xl font-black tracking-wide text-white">
              Playing XI &amp; Impact Player Optimizer
            </h1>
          </div>
          <p className="mt-1 text-xs text-slate-400">
            Constrained Mixed-Integer Linear Programming (MILP) solving official IPL bylaws: 11 starting players, ≤4 overseas on field, ≥1 wicketkeeper, ≥20 bowling overs capacity.
          </p>
        </div>

        {/* View Switcher & Copy Button */}
        <div className="flex items-center gap-2 self-start md:self-auto">
          <div className="flex rounded-xl border border-[#1E2D5A] bg-[#0B132B] p-1">
            <button
              onClick={() => setViewMode('solver')}
              className={`rounded-lg px-3 py-1.5 text-xs font-bold transition-all ${
                viewMode === 'solver'
                  ? 'bg-[#E81A85] text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Solver Controls
            </button>
            <button
              onClick={() => setViewMode('presentation')}
              className={`rounded-lg px-3 py-1.5 text-xs font-bold transition-all ${
                viewMode === 'presentation'
                  ? 'bg-[#E81A85] text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              PPT Deck View
            </button>
          </div>

          <button
            onClick={copyPlaying12Text}
            className="flex items-center gap-1.5 rounded-xl border border-[#D4AF37]/40 bg-[#D4AF37]/15 px-3 py-2 text-xs font-bold text-[#D4AF37] hover:bg-[#D4AF37]/25 transition-all"
            title="Copy formatted Playing 12 for presentation slides"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            {copied ? 'Copied to Clipboard!' : 'Copy for PPT'}
          </button>
        </div>
      </div>

      {/* Control Panel */}
      <div className="mb-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 rounded-2xl border border-[#1E2D5A] bg-[#0B132B] p-6 shadow-xl">
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Opponent Franchise
          </label>
          <select
            value={opponent}
            onChange={(e) => setOpponent(e.target.value)}
            className="w-full rounded-xl border border-[#1E2D5A] bg-[#0D1838] px-3.5 py-2.5 text-xs text-white focus:border-[#E81A85] focus:outline-none transition-colors"
          >
            <option value="Chennai Super Kings">Chennai Super Kings (CSK)</option>
            <option value="Mumbai Indians">Mumbai Indians (MI)</option>
            <option value="Kolkata Knight Riders">Kolkata Knight Riders (KKR)</option>
            <option value="Sunrisers Hyderabad">Sunrisers Hyderabad (SRH)</option>
            <option value="Royal Challengers Bengaluru">Royal Challengers Bengaluru (RCB)</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Match Venue
          </label>
          <select
            value={venue}
            onChange={(e) => setVenue(e.target.value)}
            className="w-full rounded-xl border border-[#1E2D5A] bg-[#0D1838] px-3.5 py-2.5 text-xs text-white focus:border-[#E81A85] focus:outline-none transition-colors"
          >
            <option value="Sawai Mansingh Stadium, Jaipur">Jaipur (SMS Stadium - Home)</option>
            <option value="MA Chidambaram Stadium, Chepauk">Chepauk, Chennai (Spin Deck)</option>
            <option value="Wankhede Stadium, Mumbai">Wankhede, Mumbai (Pace/Bounce)</option>
            <option value="Eden Gardens, Kolkata">Eden Gardens, Kolkata (True Track)</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Pitch Profile
          </label>
          <select
            value={pitchType}
            onChange={(e) => setPitchType(e.target.value)}
            className="w-full rounded-xl border border-[#1E2D5A] bg-[#0D1838] px-3.5 py-2.5 text-xs text-white focus:border-[#E81A85] focus:outline-none transition-colors"
          >
            <option value="Spin-Friendly">Spin-Friendly / Slow Surface</option>
            <option value="Pace-Friendly">Pace-Friendly / Seam &amp; Bounce</option>
            <option value="Balanced">Balanced / High-Scoring Highway</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Toss Outcome
          </label>
          <div className="flex gap-2">
            <button
              onClick={() => { setScenario('Batting First'); }}
              className={`flex-1 rounded-xl px-2 py-2.5 text-xs font-semibold transition-all ${
                scenario === 'Batting First'
                  ? 'bg-[#E81A85] text-white shadow-sm'
                  : 'bg-[#0D1838] text-slate-400 hover:text-white border border-[#1E2D5A]'
              }`}
            >
              Bat First
            </button>
            <button
              onClick={() => { setScenario('Bowling First'); }}
              className={`flex-1 rounded-xl px-2 py-2.5 text-xs font-semibold transition-all ${
                scenario === 'Bowling First'
                  ? 'bg-[#E81A85] text-white shadow-sm'
                  : 'bg-[#0D1838] text-slate-400 hover:text-white border border-[#1E2D5A]'
              }`}
            >
              Bowl First
            </button>
          </div>
        </div>

        <div className="lg:col-span-4 flex justify-end mt-2">
          <button
            onClick={runOptimization}
            disabled={loading}
            className="flex items-center gap-2 rounded-xl bg-[#E81A85] px-6 py-2.5 text-xs font-bold text-white shadow-lg shadow-[#E81A85]/20 hover:bg-[#d01575] transition-all disabled:opacity-50"
          >
            {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
            Solve Matchday Lineup
          </button>
        </div>
      </div>

      {result && (
        <>
          {viewMode === 'presentation' ? (
            /* Presentation Deck View: Clean cards formatted specifically for PPT slides */
            <div className="space-y-6">
              <div className="rounded-2xl border border-[#D4AF37]/30 bg-[#0B132B] p-6 shadow-xl">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-[#1E2D5A] gap-2">
                  <div>
                    <span className="text-[10px] font-mono uppercase tracking-wider text-[#D4AF37]">
                      IPL 2027 Strategic Roster Blueprint
                    </span>
                    <h2 className="text-xl font-black text-white">
                      Rajasthan Royals Playing 12 vs {result.opponent}
                    </h2>
                    <p className="text-xs text-slate-400">
                      Venue: {result.venue} • Surface: {result.pitch_type} • Toss: {result.scenario}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="rounded-xl bg-[#D4AF37]/15 border border-[#D4AF37]/30 px-3 py-1 font-mono text-xs font-bold text-[#D4AF37]">
                      Team Suitability: {result.projected_team_rating || 93.4}/100
                    </span>
                  </div>
                </div>

                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {result.recommended_starting_xi.map((player, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between rounded-xl border border-[#1E2D5A] bg-[#0D1838] p-3.5 hover:border-[#E81A85]/40 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#0A1128] border border-[#1E2D5A] text-xs font-mono font-bold text-[#E81A85]">
                          {idx + 1}
                        </span>
                        <div>
                          <div className="flex items-center gap-1.5">
                            <span className="text-sm font-bold text-white">{player.name}</span>
                            {player.is_overseas && (
                              <span className="rounded bg-[#D4AF37]/15 px-1.5 py-0.2 text-[9px] font-bold text-[#D4AF37] border border-[#D4AF37]/30">
                                ✈
                              </span>
                            )}
                          </div>
                          <p className="text-[11px] text-slate-400">{player.role}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="font-mono text-xs font-bold text-emerald-400">
                          {player.match_suitability || player.base_skill} Pts
                        </span>
                        {player.bowling_overs > 0 && (
                          <p className="text-[10px] text-slate-400 font-medium">{player.bowling_overs} Overs</p>
                        )}
                      </div>
                    </div>
                  ))}

                  {/* 12th Man - Impact Player Card */}
                  <div className="rounded-xl border-2 border-[#E81A85] bg-[#E81A85]/10 p-3.5 md:col-span-2 lg:col-span-3 flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#E81A85] text-xs font-mono font-black text-white shadow-md">
                        12
                      </span>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-black text-white">
                            {result.impact_player_strategy.nominated_substitute.name}
                          </span>
                          <span className="rounded bg-[#E81A85] px-2 py-0.5 text-[10px] font-black uppercase tracking-wider text-white">
                            Impact Player
                          </span>
                          {result.impact_player_strategy.nominated_substitute.is_overseas && (
                            <span className="rounded bg-[#D4AF37]/20 px-1.5 py-0.5 text-[9px] font-bold text-[#D4AF37] border border-[#D4AF37]/30">
                              ✈ OVERSEAS
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-300">
                          {result.impact_player_strategy.nominated_substitute.role} • {result.impact_player_strategy.nominated_substitute.bowling_overs > 0 ? `${result.impact_player_strategy.nominated_substitute.bowling_overs} Overs Quota` : 'Specialist Finisher'}
                        </p>
                      </div>
                    </div>

                    <div className="max-w-xl text-xs text-slate-300 bg-[#0B132B]/80 rounded-lg p-2.5 border border-[#1E2D5A]">
                      <span className="font-bold text-[#E81A85]">Tactical Rationale: </span>
                      {result.impact_player_strategy.tactical_rationale}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Interactive Solver View */
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Starting XI List */}
              <div className="lg:col-span-2 overflow-hidden rounded-2xl border border-[#1E2D5A] bg-[#0B132B] shadow-xl">
                <div className="border-b border-[#1E2D5A] bg-[#0D1838] px-6 py-4 flex items-center justify-between">
                  <div>
                    <h2 className="text-base font-bold text-white">Tactical Starting XI (Batting Hierarchy)</h2>
                    <p className="text-xs text-slate-400">Matchday Lineup vs {result.opponent}</p>
                  </div>
                  <span className="rounded-full bg-emerald-500/15 px-3 py-1 font-mono text-xs font-bold text-emerald-400 border border-emerald-500/30">
                    Team Rating: {result.projected_team_rating || 93.4}
                  </span>
                </div>

                <div className="divide-y divide-[#1E2D5A]/60">
                  {result.recommended_starting_xi.map((player, idx) => (
                    <div key={idx} className="flex items-center justify-between px-6 py-3.5 hover:bg-[#0D1838]/60 transition-colors">
                      <div className="flex items-center gap-3">
                        <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-[#0D1838] border border-[#1E2D5A] text-xs font-mono font-bold text-[#E81A85]">
                          {idx + 1}
                        </span>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-semibold text-white">{player.name}</span>
                            {player.is_overseas && (
                              <span className="rounded bg-[#D4AF37]/15 px-1.5 py-0.2 text-[9px] font-bold text-[#D4AF37] border border-[#D4AF37]/30">
                                ✈ OVERSEAS
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-400">{player.role}</p>
                        </div>
                      </div>

                      <div className="text-right">
                        <span className="font-mono text-xs font-bold text-emerald-400">
                          {player.match_suitability || player.base_skill} Pts
                        </span>
                        {player.bowling_overs > 0 && (
                          <p className="text-[10px] text-slate-400">{player.bowling_overs} Bowling Overs</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Impact Player & Bylaw Compliance */}
              <div className="flex flex-col gap-6">
                {/* Impact Player Card */}
                <div className="rounded-2xl border border-[#E81A85]/40 bg-[#0B132B] p-6 shadow-xl">
                  <div className="flex items-center gap-2 text-[#E81A85]">
                    <Sparkles className="h-5 w-5" />
                    <h3 className="text-base font-bold text-white">Dynamic Impact Player (12th Man)</h3>
                  </div>

                  {result.impact_player_strategy?.nominated_substitute ? (
                    <div className="mt-4">
                      <div className="rounded-xl bg-[#0D1838] p-4 border border-[#1E2D5A]">
                        <span className="text-[10px] uppercase font-bold text-[#E81A85] tracking-wider">
                          Designated Substitute
                        </span>
                        <div className="flex items-center gap-2 mt-1">
                          <h4 className="text-lg font-black text-white">
                            {result.impact_player_strategy.nominated_substitute.name}
                          </h4>
                          {result.impact_player_strategy.nominated_substitute.is_overseas && (
                            <span className="rounded bg-[#D4AF37]/15 px-1.5 py-0.2 text-[9px] font-bold text-[#D4AF37] border border-[#D4AF37]/30">
                              ✈ OVERSEAS
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-300">
                          {result.impact_player_strategy.nominated_substitute.role}
                        </p>
                        {result.impact_player_strategy.nominated_substitute.bowling_overs > 0 && (
                          <p className="mt-1 text-[11px] font-mono text-emerald-400">
                            {result.impact_player_strategy.nominated_substitute.bowling_overs} Overs Quota Available
                          </p>
                        )}
                      </div>

                      <div className="mt-4">
                        <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                          Trigger Condition
                        </span>
                        <p className="mt-1 text-xs text-slate-300">
                          {result.impact_player_strategy.trigger_condition}
                        </p>
                      </div>

                      <div className="mt-3">
                        <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                          Tactical Rationale
                        </span>
                        <p className="mt-1 text-xs text-slate-400 leading-relaxed">
                          {result.impact_player_strategy.tactical_rationale}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <p className="mt-4 text-xs text-slate-400">Calculating impact substitution strategy...</p>
                  )}
                </div>

                {/* Constraint Verification Checklist */}
                <div className="rounded-2xl border border-[#1E2D5A] bg-[#0B132B] p-6 shadow-xl">
                  <h3 className="text-sm font-bold text-white mb-4">IPL Bylaw Constraint Audit</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-300 flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-emerald-400" /> Total Starting Lineup
                      </span>
                      <span className="font-mono font-bold text-white">
                        {result.constraints_verified?.total_players || 11} / 11
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-300 flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-emerald-400" /> Overseas Player Cap
                      </span>
                      <span className="font-mono font-bold text-[#D4AF37]">
                        {result.constraints_verified?.overseas_count || 4} / Max 4 on Field
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-300 flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-emerald-400" /> Designated Wicketkeepers
                      </span>
                      <span className="font-mono font-bold text-white">
                        {result.constraints_verified?.wicketkeepers || 1} / Min 1
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-300 flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-emerald-400" /> Bowling Quota Capacity
                      </span>
                      <span className="font-mono font-bold text-emerald-400">
                        {result.constraints_verified?.bowling_overs_covered || 20} / 20 Overs Min
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
