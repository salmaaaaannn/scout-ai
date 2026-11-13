import os
import csv
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse, PlainTextResponse

router = APIRouter(prefix="/api/rankings", tags=["Rankings & Player Intelligence"])

CLEANED_DIR = "data/cleaned"
PROCESSED_DIR = "data/processed"
REPORTS_DIR = "data/reports"
PHASE5_DIR = "phase5_rr_weakness_based_recruitment"


def _get_file_path(filename: str) -> str:
    """Finds path prioritizing phase5 folder, then root workspace, then data/processed, then data/cleaned, then data/reports."""
    p_p5 = os.path.join(PHASE5_DIR, filename)
    if os.path.isfile(p_p5):
        return p_p5
    if os.path.isfile(filename):
        return filename
    p_proc = os.path.join(PROCESSED_DIR, filename)
    if os.path.isfile(p_proc):
        return p_proc
    p_clean = os.path.join(CLEANED_DIR, filename)
    if os.path.isfile(p_clean):
        return p_clean
    p_rep = os.path.join(REPORTS_DIR, filename)
    if os.path.isfile(p_rep):
        return p_rep
    return filename


def _load_csv(filename: str) -> List[Dict]:
    file_path = _get_file_path(filename)
    if not os.path.isfile(file_path):
        return []
    try:
        result = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                result.append(row)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading {filename}: {str(e)}")


@router.get("/players")
def list_players(
    q: Optional[str] = Query(None, description="Search by player_id, canonical_name, or team"),
    role: Optional[str] = Query(None, description="Filter by Batter, Bowler, All-Rounder"),
    is_ipl: Optional[bool] = Query(None, description="Filter by IPL player status"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Search and filter from verified player_master.csv.
    Uses player_id as identity key, with canonical display names.
    """
    players = _load_csv("player_master.csv")
    if not players:
        raise HTTPException(status_code=404, detail="Player master data not found. Run cleaning pipeline first.")

    filtered = players
    if q:
        q_lower = q.strip().lower()
        filtered = [
            p for p in filtered
            if q_lower in p.get("player_id", "").lower()
            or q_lower in p.get("canonical_name", "").lower()
            or q_lower in p.get("original_name", "").lower()
            or q_lower in p.get("primary_team", "").lower()
        ]

    if role and role.upper() != "ALL":
        r_lower = role.strip().lower()
        filtered = [p for p in filtered if r_lower in p.get("primary_role", "").lower()]

    if is_ipl is not None:
        filtered = [p for p in filtered if (p.get("is_ipl_player", "").lower() == "true") == is_ipl]

    total = len(filtered)
    paged = filtered[offset : offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "players": paged,
    }


@router.get("/players/{player_id}")
def get_player_profile(player_id: str):
    """
    Returns verified player master profile, alias history, and pressure metrics for a player_id.
    """
    players = _load_csv("player_master.csv")
    matched = [p for p in players if p.get("player_id") == str(player_id).strip()]
    if not matched:
        raise HTTPException(status_code=404, detail=f"Player ID '{player_id}' not found in master registry.")

    player = matched[0]

    # Load aliases
    aliases = _load_csv("player_aliases.csv")
    player_aliases = [a for a in aliases if a.get("player_id") == str(player_id).strip()]

    # Load mapping verification
    mappings = _load_csv("player_id_mapping.csv")
    mapping_row = next((m for m in mappings if m.get("player_id") == str(player_id).strip()), {})

    # Check if present in pressure rankings
    bat_rankings = _load_csv("batter_pressure_rankings.csv")
    bat_metric = next((b for b in bat_rankings if b.get("player_id") == str(player_id).strip()), None)

    bowl_rankings = _load_csv("bowler_pressure_rankings.csv")
    bowl_metric = next((b for b in bowl_rankings if b.get("player_id") == str(player_id).strip()), None)

    # Check if shortlisted
    shortlist = _load_csv("long_term_investment_shortlist.csv")
    shortlist_entry = next((s for s in shortlist if s.get("player_id") == str(player_id).strip()), None)

    return {
        "player_id": player_id,
        "profile": player,
        "verification": mapping_row,
        "aliases": player_aliases,
        "batter_pressure_ranking": bat_metric,
        "bowler_pressure_ranking": bowl_metric,
        "investment_shortlist_profile": shortlist_entry,
    }


@router.get("/batter_top10")
def get_top10_batters():
    """
    Returns Top-10 Diagnostic Batter Pressure Reliability Rankings as JSON.
    """
    rankings = _load_csv("batter_pressure_rankings.csv")
    if rankings:
        formatted = []
        for b in rankings[:10]:
            formatted.append({
                "player_id": b["player_id"],
                "full_name": b["player_name"],
                "role": "Batter",
                "team": b["team"],
                "pressure_balls": int(b["pressure_balls"]),
                "baseline_balls": int(b["baseline_balls"]),
                "delta_SR": float(b["delta_SR"]),
                "delta_boundary_pct": float(b["delta_boundary_pct"]),
                "delta_dot_pct": float(b["delta_dot_pct"]),
                "delta_dismissal_rate": float(b["delta_dismissal_rate"]),
                "composite_score": float(b["composite_score"]),
                "reliability_score": float(b["composite_score"]),
                "ci_low": b["ci_low"],
                "ci_high": b["ci_high"],
                "robustness": b["robustness_flag"],
                "status": "VALIDATED",
            })
        return {"top10_batters": formatted}

    raise HTTPException(status_code=404, detail="Batter pressure rankings not found. Run pipeline first.")


@router.get("/bowler_top10")
def get_top10_bowlers():
    """
    Returns Top-10 Diagnostic Bowler Pressure Reliability Rankings as JSON.
    """
    rankings = _load_csv("bowler_pressure_rankings.csv")
    if rankings:
        formatted = []
        for b in rankings[:10]:
            formatted.append({
                "player_id": b["player_id"],
                "full_name": b["player_name"],
                "role": "Bowler",
                "team": b["team"],
                "pressure_balls": int(b["pressure_balls"]),
                "baseline_balls": int(b["baseline_balls"]),
                "delta_econ": float(b["delta_econ"]),
                "delta_dot_pct": float(b["delta_dot_pct"]),
                "delta_wicket_rate": float(b["delta_wicket_rate"]),
                "composite_score": float(b["composite_score"]),
                "reliability_score": float(b["composite_score"]),
                "ci_low": b["ci_low"],
                "ci_high": b["ci_high"],
                "robustness": b["robustness_flag"],
                "status": "VALIDATED",
            })
        return {"top10_bowlers": formatted}

    raise HTTPException(status_code=404, detail="Bowler pressure rankings not found. Run pipeline first.")


@router.get("/shortlist")
def get_investment_shortlist():
    """
    Returns Rajasthan Royals 2027 Long-Term Investment Shortlist (Top 20 Recommendations).
    """
    shortlist = _load_csv("long_term_investment_shortlist.csv")
    if not shortlist:
        raise HTTPException(status_code=404, detail="Investment shortlist not found. Run pipeline first.")
    return {"total": len(shortlist), "shortlist": shortlist}


@router.get("/validation_report")
def get_validation_report(download: bool = Query(False, description="Set true to download as CSV file")):
    """
    Serves data_validation_report.csv as JSON or downloadable CSV file.
    """
    file_path = _get_file_path("data_validation_report.csv")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Validation report CSV not found.")

    if download:
        return FileResponse(
            file_path,
            media_type="text/csv",
            filename="royals_scoutiq_data_validation_report.csv"
        )

    rows = _load_csv("data_validation_report.csv")
    return {"total_issues": len(rows), "issues": rows}


@router.get("/cleaning_summary")
def get_cleaning_summary():
    """
    Returns markdown cleaning summary of the data pack audit.
    """
    file_path = _get_file_path("cleaning_summary.md")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Cleaning summary document not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return PlainTextResponse(content, media_type="text/markdown")


@router.get("/data_coverage")
def get_data_coverage_report():
    """
    Returns markdown Data Coverage Pre-Check Report.
    """
    file_path = _get_file_path("data_coverage_report.md")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Data coverage report not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return PlainTextResponse(content, media_type="text/markdown")


@router.get("/methodology_report")
def get_methodology_report():
    """
    Returns markdown Pressure Analysis Methodology Report.
    """
    file_path = _get_file_path("pressure_analysis_methodology.md")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Methodology report not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return PlainTextResponse(content, media_type="text/markdown")


@router.get("/scouting_report")
def get_player_scouting_report():
    """
    Returns comprehensive markdown Player Scouting Intelligence Report.
    """
    file_path = _get_file_path("player_scouting_report.md")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Scouting report not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return PlainTextResponse(content, media_type="text/markdown")


@router.get("/rr_exclusions")
def get_rr_exclusions():
    """
    Returns register of excluded existing Rajasthan Royals players (§10.7).
    """
    exclusions = _load_csv("rr_existing_player_exclusions.csv")
    return {"total": len(exclusions), "exclusions": exclusions}


@router.get("/phase3_findings")
def get_phase3_audit_findings():
    """
    Returns Phase 3 audit findings (10 audited claims regarding eligibility, trades, and status).
    """
    findings = _load_csv("phase3_audit_findings.csv")
    return {"total": len(findings), "findings": findings}


@router.get("/trade_audit")
def get_ipl_eligibility_and_trade_audit():
    """
    Returns 20-player IPL eligibility, franchise affiliation, and trade audit register.
    """
    trade_audit = _load_csv("ipl_eligibility_and_trade_audit.csv")
    return {"total": len(trade_audit), "trade_audit": trade_audit}


@router.get("/shai_hope_report")
def get_shai_hope_report():
    """
    Returns comprehensive Shai Hope multi-format intelligence dossier as Markdown.
    """
    file_path = _get_file_path("shai_hope_multi_format_report.md")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Shai Hope report not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return PlainTextResponse(content, media_type="text/markdown")


@router.get("/shai_hope_statistics")
def get_shai_hope_statistics():
    """
    Returns Shai Hope format-by-format breakdown statistics as JSON.
    """
    stats = _load_csv("shai_hope_format_statistics.csv")
    return {"total": len(stats), "format_statistics": stats}


@router.get("/phase3_verification_report")
def get_phase3_verification_report():
    """
    Returns Phase 3 Governance & Verification Report as Markdown.
    """
    file_path = _get_file_path("phase3_verification_report.md")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Phase 3 verification report not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return PlainTextResponse(content, media_type="text/markdown")


# =============================================================================
# PHASE 4: VERIFIED IPL 2027 PLAYER MARKET RESEARCH & TOP 10+10 RECOMMENDATIONS
# =============================================================================

@router.get("/phase4/previous_errors")
def get_phase4_previous_errors():
    """
    Returns audit of previous player classification errors (PBKS, RCB, SRH contracts).
    """
    errors = _load_csv("phase4_previous_errors.csv")
    return {"total": len(errors), "previous_errors": errors}


@router.get("/phase4/market_status")
def get_phase4_market_status():
    """
    Returns comprehensive market status of investigated players.
    """
    market = _load_csv("ipl2027_market_status.csv")
    return {"total": len(market), "market_status": market}


@router.get("/phase4/top10_batters")
def get_phase4_top10_batters():
    """
    Returns Authoritative Top 10 Batters (Verified Free Agents / Released / Unsold).
    """
    batters = _load_csv("top10_batters_ipl2027.csv")
    return {"total": len(batters), "top10_batters": batters}


@router.get("/phase4/top10_bowlers")
def get_phase4_top10_bowlers():
    """
    Returns Authoritative Top 10 Bowlers (Verified Free Agents / Released / Unsold).
    """
    bowlers = _load_csv("top10_bowlers_ipl2027.csv")
    return {"total": len(bowlers), "top10_bowlers": bowlers}


@router.get("/phase4/rr_exclusions")
def get_phase4_rr_exclusions():
    """
    Returns Phase 4 RR existing player exclusions.
    """
    exclusions = _load_csv("rr_existing_player_exclusions_phase4.csv")
    return {"total": len(exclusions), "exclusions": exclusions}


@router.get("/phase4/evidence_sources")
def get_phase4_evidence_sources():
    """
    Returns Phase 4 multi-source evidence citations (Cricbuzz, ESPNcricinfo, BCCI/IPLT20).
    """
    sources = _load_csv("phase4_player_evidence_sources.csv")
    return {"total": len(sources), "evidence_sources": sources}


@router.get("/phase4/market_report")
def get_phase4_market_report():
    """
    Returns Phase 4 Comprehensive Market Research Report as Markdown.
    """
    file_path = _get_file_path("phase4_market_research_report.md")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Market research report not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return PlainTextResponse(content, media_type="text/markdown")


@router.get("/phase4/verification_report")
def get_phase4_verification_report():
    """
    Returns Phase 4 Governance & Verification Report as Markdown.
    """
    file_path = _get_file_path("phase4_verification_report.md")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Verification report not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return PlainTextResponse(content, media_type="text/markdown")


# ==========================================
# PHASE 5: WEAKNESS-BASED RECRUITMENT ENDPOINTS
# ==========================================

@router.get("/phase5/batting_phase_analysis")
def get_phase5_batting_phase_analysis():
    """
    Returns Phase 5 Batting Phase Breakdown (Powerplay, Middle, Death across 2024, 2025, 2026).
    """
    data = _load_csv("rr_batting_phase_analysis.csv")
    return {"total": len(data), "batting_phase_analysis": data}


@router.get("/phase5/spin_bowling_analysis")
def get_phase5_spin_bowling_analysis():
    """
    Returns Phase 5 Spin Bowling Analysis (Overs 7-16, vs LHB/RHB metrics, Chahal aftermath).
    """
    data = _load_csv("rr_spin_bowling_analysis.csv")
    return {"total": len(data), "spin_bowling_analysis": data}


@router.get("/phase5/pace_bowling_analysis")
def get_phase5_pace_bowling_analysis():
    """
    Returns Phase 5 Pace Bowling Breakdown across PP, Middle, and Death phases.
    """
    data = _load_csv("rr_pace_bowling_analysis.csv")
    return {"total": len(data), "pace_bowling_analysis": data}


@router.get("/phase5/fielding_errors")
def get_phase5_fielding_errors():
    """
    Returns Phase 5 Dropped Catch Log (2024-2026 match-by-match incidents with runs conceded).
    """
    data = _load_csv("rr_fielding_errors_2024_2026.csv")
    return {"total": len(data), "fielding_errors": data}


@router.get("/phase5/catching_efficiency")
def get_phase5_catching_efficiency():
    """
    Returns Phase 5 Catching Efficiency across 2024, 2025, and 2026.
    """
    data = _load_csv("rr_catching_efficiency_by_season.csv")
    return {"total": len(data), "catching_efficiency": data}


@router.get("/phase5/weakness_matrix")
def get_phase5_weakness_matrix():
    """
    Returns Phase 5 Weakness-to-Recruitment Matrix (W1 to W5 with required player profiles).
    """
    data = _load_csv("rr_weakness_to_recruitment_matrix.csv")
    return {"total": len(data), "weakness_matrix": data}


@router.get("/phase5/current_squad")
def get_phase5_current_squad():
    """
    Returns Phase 5 Audited Current RR Squad (Contracts, roles, overseas status).
    """
    data = _load_csv("rr_current_squad_audit_2027.csv")
    return {"total": len(data), "current_squad": data}


@router.get("/phase5/market_status")
def get_phase5_market_status():
    """
    Returns Phase 5 Player Market Status (Free agents, released, contracted, benchmarks).
    """
    data = _load_csv("ipl2027_player_market_status.csv")
    return {"total": len(data), "market_status": data}


@router.get("/phase5/top10_batters")
def get_phase5_top10_batters():
    """
    Returns Phase 5 Top 10 Batters for RR IPL 2027 (Spin destroyers, anchors, finishers).
    """
    data = _load_csv("top10_rr_batters_ipl2027.csv")
    return {"total": len(data), "top10_batters": data}


@router.get("/phase5/top10_bowlers")
def get_phase5_top10_bowlers():
    """
    Returns Phase 5 Top 10 Bowlers for RR IPL 2027 (Specialist spinners elevated, Matt Henry demoted to #8).
    """
    data = _load_csv("top10_rr_bowlers_ipl2027.csv")
    return {"total": len(data), "top10_bowlers": data}


@router.get("/phase5/source_verification_log")
def get_phase5_source_verification_log():
    """
    Returns Phase 5 Source Verification and Provenance Log.
    """
    data = _load_csv("phase5_source_verification_log.csv")
    return {"total": len(data), "source_verification_log": data}


@router.get("/phase5/historical_weakness_report")
def get_phase5_historical_weakness_report():
    """
    Returns Phase 5 Historical Weakness Analysis Report (Markdown).
    """
    file_path = _get_file_path("rr_historical_weakness_analysis.md")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Historical weakness report not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return PlainTextResponse(content, media_type="text/markdown")


@router.get("/phase5/final_recruitment_report")
def get_phase5_final_recruitment_report():
    """
    Returns Phase 5 Final Recruitment Report (10 Answers, Categories, Proposed XI).
    """
    file_path = _get_file_path("rr_ipl2027_final_recruitment_report.md")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Final recruitment report not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return PlainTextResponse(content, media_type="text/markdown")


# ==========================================
# PRE-AUCTION RELEASE INTELLIGENCE ENDPOINTS (AS-OF 12 NOV 2026)
# ==========================================

@router.get("/early_release/tracker")
def get_early_release_tracker():
    """
    Returns Comprehensive 10-Franchise Pre-Auction Release Tracker (48 players across all 10 franchises).
    """
    data = _load_csv("ipl2027_early_release_tracker.csv")
    return {"total": len(data), "release_tracker": data}


@router.get("/early_release/confirmed_released")
def get_confirmed_released_players():
    """
    Returns Officially Confirmed Released Players and completed replacement contracts.
    """
    data = _load_csv("ipl2027_confirmed_released_players.csv")
    return {"total": len(data), "confirmed_released": data}


@router.get("/early_release/reported_release")
def get_reported_release_candidates():
    """
    Returns Credible Media-Reported Release and Trade Candidates across franchises.
    """
    data = _load_csv("ipl2027_reported_release_candidates.csv")
    return {"total": len(data), "reported_candidates": data}


@router.get("/early_release/predicted_release")
def get_predicted_release_candidates():
    """
    Returns Evidence-Based Analytical Release Predictions based on 2026 benching and squad congestion.
    """
    data = _load_csv("ipl2027_predicted_release_candidates.csv")
    return {"total": len(data), "predicted_candidates": data}


@router.get("/early_release/batter_watchlist")
def get_early_release_batter_watchlist():
    """
    Returns Expanded Batting Market Watchlist prioritized by RR historical weakness fit.
    """
    data = _load_csv("rr_batter_market_watchlist.csv")
    return {"total": len(data), "batter_watchlist": data}


@router.get("/early_release/bowler_watchlist")
def get_early_release_bowler_watchlist():
    """
    Returns Expanded Bowling Market Watchlist with Priority 1 Specialist Spinners elevated.
    """
    data = _load_csv("rr_bowler_market_watchlist.csv")
    return {"total": len(data), "bowler_watchlist": data}


@router.get("/early_release/existing_20_reverification")
def get_early_release_existing_20_reverification():
    """
    Returns Complete Reverification of Existing 20 Players with 2026 positions, sample statistics, and contract status.
    """
    data = _load_csv("rr_existing_20_players_reverification.csv")
    return {"total": len(data), "existing_20_reverification": data}


@router.get("/early_release/intelligence_report")
def get_early_release_intelligence_report():
    """
    Returns Comprehensive Pre-Auction Market Intelligence Report as Markdown.
    """
    file_path = _get_file_path("rr_pre_auction_market_intelligence_report.md")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Pre-auction intelligence report not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return PlainTextResponse(content, media_type="text/markdown")


@router.get("/early_release/completed_trades")
def get_early_release_completed_trades():
    """
    Returns Completed IPL 2027 Trade Register (10 verified trades with player IDs and contracts).
    """
    data = _load_csv("ipl2027_completed_trades.csv")
    return {"total": len(data), "completed_trades": data}


@router.get("/early_release/previously_unsold")
def get_early_release_previously_unsold():
    """
    Returns Previously Unsold 2026 Players Pool tracking 2027 auction registration.
    """
    data = _load_csv("ipl2027_previously_unsold_pool.csv")
    return {"total": len(data), "previously_unsold": data}


@router.get("/early_release/verification_audit")
def get_early_release_verification_audit():
    """
    Returns Master Audit Log identifying every correction made and every unresolved claim.
    """
    data = _load_csv("rr_pre_auction_verification_audit.csv")
    return {"total": len(data), "verification_audit": data}


@router.get("/round1/top_10_batters")
def get_round1_top_10_batters():
    """Returns Official Round 1 Top 10 Batters Under Pressure (BPRI)."""
    data = _load_csv("top_10_batters_under_pressure.csv")
    return {"total": len(data), "top_10_batters": data}


@router.get("/round1/top_10_bowlers")
def get_round1_top_10_bowlers():
    """Returns Official Round 1 Top 10 Bowlers Under Pressure (BOWPRI)."""
    data = _load_csv("top_10_bowlers_under_pressure.csv")
    return {"total": len(data), "top_10_bowlers": data}


@router.get("/round1/top_10_overall")
def get_round1_top_10_overall():
    """Returns Primary Round 1 Deliverable: Final Top 10 Overall Recommendations (Calibrated OPRI)."""
    data = _load_csv("top_10_overall_pressure_recommendations.csv")
    return {"total": len(data), "top_10_overall": data}


@router.get("/round1/all_ranked_batters")
def get_round1_all_ranked_batters():
    """Returns all qualified batters evaluated under pressure with bootstrap CIs."""
    data = _load_csv("all_ranked_batters_under_pressure.csv")
    return {"total": len(data), "all_batters": data}


@router.get("/round1/all_ranked_bowlers")
def get_round1_all_ranked_bowlers():
    """Returns all qualified bowlers evaluated under pressure with bootstrap CIs."""
    data = _load_csv("all_ranked_bowlers_under_pressure.csv")
    return {"total": len(data), "all_bowlers": data}


@router.get("/round1/comparison")
def get_round1_player_comparison():
    """Returns side-by-side normal vs pressure comparison metrics."""
    data = _load_csv("player_pressure_comparison.csv")
    return {"total": len(data), "comparison": data}


@router.get("/round1/validation")
def get_round1_match_validation():
    """Returns delivery-by-delivery classification samples across chases & 1st innings."""
    data = _load_csv("pressure_index_match_validation.csv")
    return {"total": len(data), "validation_samples": data}


@router.get("/round1/sensitivity")
def get_round1_sensitivity_analysis():
    """Returns threshold stability (65, 75, 85) and scoring weight variations."""
    data = _load_csv("pressure_model_sensitivity_analysis.csv")
    return {"total": len(data), "sensitivity_analysis": data}


@router.get("/round1/methodology")
def get_round1_methodology():
    """Returns full mathematical methodology documentation as Markdown."""
    path = _get_file_path("pressure_reliability_methodology.md")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Methodology document not found.")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return PlainTextResponse(content, media_type="text/markdown")


@router.get("/round1/rr_insights")
def get_round1_rr_insights():
    """Returns Rajasthan Royals tactical recruitment fit analysis as Markdown."""
    path = _get_file_path("rr_pressure_recruitment_insights.md")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="RR recruitment insights document not found.")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return PlainTextResponse(content, media_type="text/markdown")


@router.get("/round1/data_quality")
def get_round1_data_quality():
    """Returns data quality, governance, and anti-bias report as Markdown."""
    path = _get_file_path("data_quality_and_validation_report.md")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Data quality report not found.")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return PlainTextResponse(content, media_type="text/markdown")


@router.get("/round1/presentation")
def download_round1_presentation():
    """Downloads executive 15-slide PowerPoint deck styled in Rajasthan Royals branding."""
    path = _get_file_path("round1_final_presentation.pptx")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="PowerPoint presentation not found.")
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename="round1_final_presentation.pptx"
    )


@router.get("/round1/report_pdf")
def download_round1_report_pdf():
    """Downloads publication-grade executive scouting report PDF."""
    path = _get_file_path("round1_final_submission_report.pdf")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Submission PDF report not found.")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename="round1_final_submission_report.pdf"
    )







