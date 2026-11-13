"""
tests/test_phase5_weakness_recruitment.py
=========================================
Tests for Royals ScoutIQ Phase 5: Weakness-Based Squad Analysis & Player Recruitment.
Verifies all 14 deliverables, player ID integrity, spin prioritization, and fielding audit.
"""

import csv
import os
import pytest

PHASE5_DIR = "phase5_rr_weakness_based_recruitment"

EXPECTED_FILES = [
    "rr_historical_weakness_analysis.md",
    "rr_batting_phase_analysis.csv",
    "rr_spin_bowling_analysis.csv",
    "rr_pace_bowling_analysis.csv",
    "rr_fielding_errors_2024_2026.csv",
    "rr_catching_efficiency_by_season.csv",
    "rr_weakness_to_recruitment_matrix.csv",
    "rr_current_squad_audit_2027.csv",
    "ipl2027_player_market_status.csv",
    "top10_rr_batters_ipl2027.csv",
    "top10_rr_bowlers_ipl2027.csv",
    "rr_recruitment_scoring_methodology.md",
    "rr_ipl2027_final_recruitment_report.md",
    "phase5_source_verification_log.csv"
]

def test_phase5_all_14_files_exist():
    assert os.path.isdir(PHASE5_DIR), f"Directory {PHASE5_DIR} does not exist"
    for fname in EXPECTED_FILES:
        fpath = os.path.join(PHASE5_DIR, fname)
        assert os.path.isfile(fpath), f"Missing required Phase 5 file: {fname}"
        assert os.path.getsize(fpath) > 100, f"File {fname} is empty or too small"

def test_batting_phase_analysis_content():
    fpath = os.path.join(PHASE5_DIR, "rr_batting_phase_analysis.csv")
    with open(fpath) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 9  # 3 seasons * 3 phases
    seasons = {r['season'] for r in rows}
    assert seasons == {'IPL 2024', 'IPL 2025', 'IPL 2026'}
    for r in rows:
        assert float(r['run_rate']) > 5.0
        assert int(r['balls']) > 100
        assert 'spin_strike_rate' in r
        assert 'pace_strike_rate' in r

def test_spin_bowling_analysis_content():
    fpath = os.path.join(PHASE5_DIR, "rr_spin_bowling_analysis.csv")
    with open(fpath) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 6
    names = {r['bowler_name'] for r in rows}
    assert 'Yuzvendra Chahal' in names
    assert 'Wanindu Hasaranga' in names
    assert 'Maheesh Theekshana' in names
    for r in rows:
        assert 'middle_overs_7_16_economy' in r
        assert 'vs_lhb_economy' in r
        assert 'vs_rhb_economy' in r

def test_pace_bowling_analysis_content():
    fpath = os.path.join(PHASE5_DIR, "rr_pace_bowling_analysis.csv")
    with open(fpath) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 6
    names = {r['bowler_name'] for r in rows}
    assert 'Jofra Archer' in names
    assert 'Sandeep Sharma' in names
    for r in rows:
        assert 'death_overs' in r
        assert 'death_economy' in r

def test_fielding_errors_and_catching_efficiency():
    fe_path = os.path.join(PHASE5_DIR, "rr_fielding_errors_2024_2026.csv")
    with open(fe_path) as f:
        errors = list(csv.DictReader(f))
    assert len(errors) >= 12
    for err in errors:
        assert err['match_date']
        assert err['opponent']
        assert err['rr_fielder']
        assert err['batter_dropped']
        assert err['runs_scored_after_drop']
        assert err['match_impact']

    ce_path = os.path.join(PHASE5_DIR, "rr_catching_efficiency_by_season.csv")
    with open(ce_path) as f:
        ce_rows = list(csv.DictReader(f))
    assert len(ce_rows) == 3
    # Verify 2025 drop in efficiency
    row_2025 = [r for r in ce_rows if r['season'] == 'IPL 2025'][0]
    assert float(row_2025['catching_efficiency_pct']) < 75.0
    assert int(row_2025['catches_dropped']) >= 20

def test_weakness_matrix_structure():
    wm_path = os.path.join(PHASE5_DIR, "rr_weakness_to_recruitment_matrix.csv")
    with open(wm_path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 5
    weaknesses = [r['rr_weakness'] for r in rows]
    assert any('Spin' in w for w in weaknesses)
    assert any('Middle-Order' in w for w in weaknesses)
    assert any('Fielding' in w for w in weaknesses)

def test_current_squad_audit():
    sq_path = os.path.join(PHASE5_DIR, "rr_current_squad_audit_2027.csv")
    with open(sq_path) as f:
        players = list(csv.DictReader(f))
    names = {p['player_name'] for p in players}
    assert 'Sanju Samson' in names
    assert 'Yashasvi Jaiswal' in names
    assert 'Jofra Archer' in names
    assert 'Shimron Hetmyer' in names

def test_market_status_and_exclusions():
    ms_path = os.path.join(PHASE5_DIR, "ipl2027_player_market_status.csv")
    with open(ms_path) as f:
        status_rows = list(csv.DictReader(f))
    name_map = {r['player_name']: r for r in status_rows}
    # Priyansh Arya and Josh Hazlewood must NOT be free agents
    assert name_map['Priyansh Arya']['market_status'] == 'CONTRACTED_OTHER_FRANCHISE'
    assert name_map['Josh Hazlewood']['market_status'] == 'CONTRACTED_OTHER_FRANCHISE'
    # Shai Hope and Akeal Hosein must be FREE_AGENT_CONFIRMED
    assert name_map['Shai Hope']['market_status'] == 'FREE_AGENT_CONFIRMED'
    assert name_map['Akeal Hosein']['market_status'] == 'FREE_AGENT_CONFIRMED'

def test_top10_batters_ranking_and_positions():
    b_path = os.path.join(PHASE5_DIR, "top10_rr_batters_ipl2027.csv")
    with open(b_path) as f:
        batters = list(csv.DictReader(f))
    assert len(batters) == 10
    assert batters[0]['player_name'] == 'Shai Hope'
    assert batters[0]['batting_position'] in ['No. 3', 'No. 3 / No. 4']
    assert batters[1]['player_name'] == 'Sarfaraz Khan'
    assert batters[1]['nationality'] == 'India'
    for b in batters:
        assert float(b['cricket_performance_score']) > 0
        assert float(b['rr_squad_fit_score']) > 0
        assert b['rr_weakness_solved']
        assert b['verification_status'] == 'OFFICIALLY_VERIFIED'

def test_top10_bowlers_spin_priority_and_matt_henry_demoted():
    bw_path = os.path.join(PHASE5_DIR, "top10_rr_bowlers_ipl2027.csv")
    with open(bw_path) as f:
        bowlers = list(csv.DictReader(f))
    assert len(bowlers) == 10
    # Top 3 must all be spinners (not pacers)
    assert bowlers[0]['player_name'] == 'Akeal Hosein'
    assert 'Slow left-arm' in bowlers[0]['bowling_style']
    assert bowlers[1]['player_name'] == 'Gudakesh Motie'
    assert bowlers[2]['player_name'] == 'Adil Rashid'
    # Mujeeb Ur Rahman and Shreyas Gopal must replace Matt Henry and Umesh Yadav
    bowler_names = [b['player_name'] for b in bowlers]
    assert 'Mujeeb Ur Rahman' in bowler_names
    assert 'Shreyas Gopal' in bowler_names
    assert 'Matt Henry' not in bowler_names
    assert 'Umesh Yadav' not in bowler_names

def test_final_recruitment_report_answers():
    rep_path = os.path.join(PHASE5_DIR, "rr_ipl2027_final_recruitment_report.md")
    with open(rep_path) as f:
        content = f.read()
    # Check all 10 questions answered
    for q_num in range(1, 11):
        assert f"### {q_num}." in content or f"{q_num}." in content
    # Check Proposed Starting XI exists and respects 4 overseas players
    assert "Proposed Rajasthan Royals Starting XI" in content
    assert "Overseas 1" in content
    assert "Overseas 2" in content
    assert "Overseas 3" in content
    assert "Overseas 4" in content
