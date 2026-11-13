import os
import csv
import pytest

DELIVERABLES = [
    "batter_pressure_rankings.csv",
    "bowler_pressure_rankings.csv",
    "long_term_investment_shortlist.csv",
    "multi_format_player_research.csv",
    "phase_statistics.csv",
    "current_ipl_team_status.csv",
    "rr_existing_player_exclusions.csv",
    "player_evidence_sources.csv",
    "player_exclusion_log.csv",
    "data_coverage_report.md",
    "pressure_analysis_methodology.md",
    "player_scouting_report.md",
]


def test_all_12_deliverables_exist():
    for f in DELIVERABLES:
        assert os.path.isfile(f), f"Missing Phase 2 deliverable: {f}"
        assert os.path.getsize(f) > 0, f"Deliverable is empty: {f}"


def test_top10_rankings_integrity():
    with open("batter_pressure_rankings.csv", "r", encoding="utf-8") as f:
        batters = list(csv.DictReader(f))
    with open("bowler_pressure_rankings.csv", "r", encoding="utf-8") as f:
        bowlers = list(csv.DictReader(f))

    assert len(batters) == 10, f"Expected 10 top batters, got {len(batters)}"
    assert len(bowlers) == 10, f"Expected 10 top bowlers, got {len(bowlers)}"

    # Scores must be in descending order
    bat_scores = [float(b["composite_score"]) for b in batters]
    bowl_scores = [float(b["composite_score"]) for b in bowlers]
    assert bat_scores == sorted(bat_scores, reverse=True), "Batter rankings not in descending order"
    assert bowl_scores == sorted(bowl_scores, reverse=True), "Bowler rankings not in descending order"

    # Wicket noise control check on bowlers
    for b in bowlers:
        metrics = b["metrics_used"]
        if int(b["pressure_wickets"]) < 3 or int(b["baseline_wickets"]) < 2:
            assert "wicket" not in metrics, f"Bowler {b['player_name']} has low wickets but wicket metric included"


def test_shortlist_no_rr_players_and_weights():
    with open("rr_existing_player_exclusions.csv", "r", encoding="utf-8") as f:
        rr_pids = set(r["player_id"] for r in csv.DictReader(f))

    with open("long_term_investment_shortlist.csv", "r", encoding="utf-8") as f:
        shortlist = list(csv.DictReader(f))

    assert len(shortlist) <= 20
    assert len(shortlist) >= 10

    shortlist_pids = set(r["player_id"] for r in shortlist)
    # G2: Zero RR players in shortlist
    rr_in_shortlist = shortlist_pids.intersection(rr_pids)
    assert not rr_in_shortlist, f"Found RR players in shortlist: {rr_in_shortlist}"

    for r in shortlist:
        score = float(r["investment_score"])
        assert 0.0 <= score <= 100.0, f"Score out of range: {score}"
        cov = float(r["evidence_coverage_pct"])
        assert cov >= 85.0, f"Evidence coverage below threshold: {cov}"


def test_as_of_date_in_availability_files():
    for f_path in ["current_ipl_team_status.csv", "player_scouting_report.md", "data_coverage_report.md"]:
        with open(f_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "2026-11-11" in content, f"Missing As-Of Date 2026-11-11 in {f_path}"
