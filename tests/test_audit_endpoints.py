"""
Royals ScoutIQ - Comprehensive Automated Audit & Verification Test Suite
Tests all endpoints, services, business rules, and constraints for Features 21-116.
Uses FastAPI TestClient with httpx.
"""

import os
import sys
import io
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.main import app
from app.analytics.sabermetrics import SabermetricsEngine
from app.analytics.auction_simulator import AuctionStrategyEngine
from app.analytics.data_validator import DataValidationSystem
from app.video_ai.biomechanics import BiomechanicsAnalyzer
from app.video_ai.event_detector import CricketEventDetector
from app.video_ai.video_processor import VideoProcessor
from app.optimizer.team_optimizer import MatchdayOptimizer
from app.opposition.opposition_intel import OppositionIntelligenceEngine
from app.development.player_development import PlayerDevelopmentEngine

client = TestClient(app)


# ===========================================================================
# 1. Health & Server Smoke Test
# ===========================================================================

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Royals ScoutIQ" in data["service"]
    assert "Kumar Sangakkara (Head Coach)" in data["evaluators"]
    assert len(data["modules_active"]) == 8


def test_landing_page_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Rajasthan Royals" in response.text or "Royals ScoutIQ" in response.text


# ===========================================================================
# 2. Module 2: RoyalVision Video CV & Biomechanics (Features 21-40)
# ===========================================================================

def test_video_upload_valid_mp4():
    # 1KB dummy MP4 binary content
    dummy_mp4 = b"\x00\x00\x00\x20ftypmp42" + b"\x00" * 1024
    files = {"file": ("match_clip_01.mp4", io.BytesIO(dummy_mp4), "video/mp4")}
    response = client.post("/api/video/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UPLOAD_SUCCESS"
    assert data["filename"] == "match_clip_01.mp4"
    assert data["file_size_bytes"] == len(dummy_mp4)


def test_video_upload_invalid_extension():
    # Unsupported file extension .txt
    dummy_txt = b"invalid payload text"
    files = {"file": ("malicious_payload.txt", io.BytesIO(dummy_txt), "text/plain")}
    response = client.post("/api/video/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file format '.txt'" in response.json()["detail"]


def test_video_upload_empty_file():
    # Empty file 0 bytes
    empty_file = b""
    files = {"file": ("empty_clip.mp4", io.BytesIO(empty_file), "video/mp4")}
    response = client.post("/api/video/upload", files=files)
    assert response.status_code == 400
    assert "Corrupted or empty video file" in response.json()["detail"]


def test_video_process_clip_bowler():
    payload = {
        "video_id": "CLIP_SMAT_P_101",
        "player_id": "P_101",
        "player_name": "Vidwath Kaverappa",
        "role": "Right-Arm Fast Medium",
        "fps": 30.0,
    }
    response = client.post("/api/video/process-clip", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert "biomechanics" in data
    # Check release event
    release = data["events"]["release_event"]
    assert "release_frame" in release
    assert release["timestamp_seconds"] >= 0
    # Check biomechanics
    bio = data["biomechanics"]
    assert bio["arm_release"]["action_classification"] in ["High-Arm", "3/4 Round-Arm", "Sling / Lasith Malinga Mold"]
    assert 0.0 <= bio["head_stillness_score"] <= 1.0
    assert bio["spine_stress"]["risk_category"] in ["Low Strain", "Moderate Strain", "High Stress Fracture Risk"]
    # Check that item was enqueued into verification queue
    assert "enqueued_verification" in data
    assert data["enqueued_verification"]["status"] == "PENDING"


def test_video_process_clip_batter():
    payload = {
        "video_id": "CLIP_SMAT_P_102",
        "player_id": "P_102",
        "player_name": "Ashutosh Sharma",
        "role": "Right-Hand Batter",
        "fps": 30.0,
    }
    response = client.post("/api/video/process-clip", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["events"]["shot_classification"]["classified_shot"] != ""
    assert data["biomechanics"]["bat_speed_proxy"]["estimated_speed_kph"] > 0


def test_multi_clip_analysis():
    payload = {
        "player_id": "P_101",
        "player_name": "Vidwath Kaverappa",
        "role": "Right-Arm Fast Medium",
        "clip_ids": ["CLIP_01", "CLIP_02", "CLIP_03"],
    }
    response = client.post("/api/video/multi-clip-analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["clips_analyzed"] == 3
    assert "mean_repeatability_score" in data["aggregated_metrics"]
    assert "ai_video_summary" in data
    assert len(data["clip_details"]) == 3


# ===========================================================================
# 3. Module 3: Human-in-the-Loop Analyst Verification (Features 41-47)
# ===========================================================================

def test_analyst_verification_workflow():
    # Step 1: Ingest clip to generate pending item
    payload = {
        "video_id": "CLIP_VERIFY_FLOW_01",
        "player_id": "P_103",
        "player_name": "Suyash Sharma",
        "role": "Right-Arm Legbreak",
    }
    client.post("/api/video/process-clip", json=payload)

    # Step 2: Check pending queue
    pending_resp = client.get("/api/verification/pending")
    assert pending_resp.status_code == 200
    items = pending_resp.json()["pending_items"]
    target_item = next((item for item in items if item["obs_id"] == "OBS_CLIP_VERIFY_FLOW_01"), None)
    assert target_item is not None
    assert target_item["status"] == "PENDING"

    # Step 3: Confirm observation
    confirm_payload = {
        "obs_id": "OBS_CLIP_VERIFY_FLOW_01",
        "analyst_name": "Giles Lindsay",
    }
    confirm_resp = client.post("/api/verification/confirm", json=confirm_payload)
    assert confirm_resp.status_code == 200
    c_data = confirm_resp.json()
    assert c_data["status"] == "CONFIRMED"
    assert c_data["confidence_multiplier"] == 1.0
    assert c_data["analyst_name"] == "Giles Lindsay"

    # Step 4: Correct another observation
    client.post("/api/video/process-clip", json={
        "video_id": "CLIP_VERIFY_CORRECT_02",
        "player_id": "P_102",
        "player_name": "Ashutosh Sharma",
        "role": "Right-Hand Batter",
    })
    correct_payload = {
        "obs_id": "OBS_CLIP_VERIFY_CORRECT_02",
        "analyst_name": "Kumar Sangakkara",
        "corrected_observation": "Trigger movement starts 15ms earlier against high pace.",
        "notes": "Verified against 145kph delivery trajectory.",
    }
    correct_resp = client.post("/api/verification/correct", json=correct_payload)
    assert correct_resp.status_code == 200
    cor_data = correct_resp.json()
    assert cor_data["status"] == "CORRECTED"
    assert cor_data["confidence_multiplier"] == 1.0
    assert "Trigger movement" in cor_data["current_observation"]

    # Step 5: Reject an observation
    client.post("/api/video/process-clip", json={
        "video_id": "CLIP_VERIFY_REJECT_03",
        "player_id": "P_104",
        "player_name": "Sameer Rizvi",
        "role": "Right-Hand Batter",
    })
    reject_payload = {
        "obs_id": "OBS_CLIP_VERIFY_REJECT_03",
        "analyst_name": "Analyst Team",
        "reason": "Camera parallax angle obscured back-lift plane.",
    }
    reject_resp = client.post("/api/verification/reject", json=reject_payload)
    assert reject_resp.status_code == 200
    rej_data = reject_resp.json()
    assert rej_data["status"] == "REJECTED"
    assert rej_data["confidence_multiplier"] == 0.0

    # Step 6: Review audit history
    history_resp = client.get("/api/verification/history")
    assert history_resp.status_code == 200
    hist_data = history_resp.json()
    assert hist_data["total_reviewed"] >= 3


# ===========================================================================
# 4. Module 4: Gemini AI & Hybrid RAG Intelligence (Features 48-59)
# ===========================================================================

def test_rag_assistant_query():
    query_payload = {"query": "Find an uncapped domestic death pacer with high steal index"}
    response = client.post("/api/assistant/ask", json=query_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["matched_players_count"] > 0
    assert len(data["citations"]) > 0
    # Must contain ground truth citation
    top_citation = data["citations"][0]
    assert "player" in top_citation
    assert "player_id" in top_citation
    assert "data_source" in top_citation
    assert "answer" in data


def test_semantic_player_search():
    response = client.get("/api/players/search?q=spin")
    assert response.status_code == 200
    data = response.json()
    assert data["results_count"] > 0
    assert any("Spin" in p["role"] or "Legbreak" in p["role"] for p in data["results"])


def test_player_dossier_endpoint():
    response = client.get("/api/players/P_101/dossier")
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == "P_101"
    assert data["profile"]["name"] == "Vidwath Kaverappa"
    assert "dossier" in data


def test_player_dossier_not_found():
    response = client.get("/api/players/UNKNOWN_ID/dossier")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ===========================================================================
# 5. Module 5: Auction Economics & Squad Strategy (Features 60-68)
# ===========================================================================

def test_role_scarcity_matrix():
    response = client.get("/api/auction/role-scarcity")
    assert response.status_code == 200
    data = response.json()
    assert "140k Domestic Pacer Depth" in data["scarcity_matrix"]
    assert data["scarcity_matrix"]["140k Domestic Pacer Depth"] == 9.2


def test_squad_balance_analysis():
    response = client.get("/api/auction/squad-balance")
    assert response.status_code == 200
    data = response.json()
    assert "total_players" in data
    assert "batters_count" in data
    assert "all_rounders_count" in data
    assert "pacers_count" in data
    assert "is_squad_balanced" in data


def test_auction_budget_simulator():
    payload = {
        "total_purse_lakhs": 850.0,
        "target_picks": [
            {"player_id": "P_101", "name": "Vidwath Kaverappa", "role": "140k Domestic Pacer", "base_price": 20, "projected_hammer": 85},
            {"player_id": "P_102", "name": "Ashutosh Sharma", "role": "Death Power Finisher", "base_price": 20, "projected_hammer": 95},
            {"player_id": "P_103", "name": "Suyash Sharma", "role": "Mystery Leg-Spinner", "base_price": 20, "projected_hammer": 120},
        ]
    }
    response = client.post("/api/auction/simulate-budget", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["simulated_picks_count"] == 3
    assert data["total_projected_spend_lakhs"] == 300
    assert data["remaining_purse_lakhs"] == 550.0
    assert "Budget Feasible" in data["budget_status"]


# ===========================================================================
# 6. Module 6: Matchday Selection Engine (Features 69-81)
# ===========================================================================

def test_matchday_lineup_constraints():
    payload = {
        "opponent": "Mumbai Indians",
        "venue": "Wankhede Stadium, Mumbai",
        "pitch_type": "Pace-Friendly",
        "scenario": "Bowling First",
    }
    response = client.post("/api/team/recommend-lineup", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Rule 1: Exactly 11 starters
    assert data["starting_xi_count"] == 11
    # Rule 2: At most 4 overseas players
    assert data["overseas_count"] <= 4
    # Rule 3: At least 1 wicketkeeper
    assert data["wicket_keepers_count"] >= 1
    # Rule 4: At least 20 bowling overs capacity
    assert data["total_bowling_overs_capacity"] >= 20.0
    # Rule 5: Impact Player designated
    assert data["impact_player_recommendation"] is not None
    assert "name" in data["impact_player_recommendation"]
    assert "role" in data["impact_player_recommendation"]
    assert data["impact_player_recommendation"]["tactical_plan"] != ""


def test_compare_scenarios_bat_first_vs_bowl_first():
    payload = {
        "opponent": "Chennai Super Kings",
        "venue": "Sawai Mansingh Stadium, Jaipur",
        "pitch_type": "Balanced",
    }
    response = client.post("/api/team/compare-scenarios", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scenario_batting_first" in data
    assert "scenario_bowling_first" in data
    assert data["strategic_verdict"] != ""


# ===========================================================================
# 7. Module 7: Opposition Intelligence & Coaching (Features 82-94)
# ===========================================================================

def test_opposition_batter_analysis():
    payload = {
        "batter_name": "Suryakumar Yadav",
        "opponent_team": "Mumbai Indians",
    }
    response = client.post("/api/opposition/analyze-batter", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["batter_name"] == "Suryakumar Yadav"
    assert "primary_weakness" in data
    assert "field_placement_plan" in data
    assert len(data["matchup_matrix"]) == 5
    assert "tactical_plan" in data["primary_weakness"]


def test_opposition_bowler_analysis():
    payload = {
        "bowler_name": "Jasprit Bumrah",
        "opponent_team": "Mumbai Indians",
    }
    response = client.post("/api/opposition/analyze-bowler", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["bowler_name"] == "Jasprit Bumrah"
    assert "phase_performance" in data
    assert "tactical_assault_plan" in data


# ===========================================================================
# 8. Module 8: Player Development & Monitoring (Features 95-100)
# ===========================================================================

def test_player_development_trends():
    response = client.get("/api/development/P_101/trends")
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == "P_101"
    assert len(data["historical_records"]) >= 3
    assert "trajectory" in data


def test_generate_training_plan():
    payload = {
        "player_id": "P_101",
        "identified_weakness": "Excessive lateral spine flexion on release stride",
    }
    response = client.post("/api/development/training-plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["identified_weakness"] == payload["identified_weakness"]
    assert len(data["prescribed_drills"]) >= 2
    assert data["head_coach_guidance"] != ""


def test_compare_coaching_sessions():
    payload = {
        "session_a": {
            "session_id": "SESS_01",
            "date": "2025-10-01",
            "head_stillness": 0.88,
            "bat_speed": 115.0,
            "stress_index": 0.55,
        },
        "session_b": {
            "session_id": "SESS_02",
            "date": "2026-02-15",
            "head_stillness": 0.94,
            "bat_speed": 128.0,
            "stress_index": 0.38,
        },
    }
    response = client.post("/api/development/compare-sessions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["technical_evolution"] == "Significant Technical Improvement"
    assert "+0.06" in data["head_stillness_change"]


def test_player_development_report():
    response = client.get("/api/development/P_101/report")
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == "P_101"
    assert "executive_summary" in data
    assert "acpi_potential_rating" in data


# ===========================================================================
# 9. Module 9: Export, Reports & RBAC Access Control (Features 101-116)
# ===========================================================================

def test_export_auction_shortlist_json():
    # Allowed role: Scout
    headers = {"X-Royals-Role": "Scout"}
    response = client.get("/api/auction/export-shortlist?format=json", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0
    assert len(data["shortlist"]) > 0


def test_export_auction_shortlist_csv():
    headers = {"X-Royals-Role": "Management"}
    response = client.get("/api/auction/export-shortlist?format=csv", headers=headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "player_id,name,age,role" in response.text
    assert "Vidwath Kaverappa" in response.text


def test_export_auction_shortlist_forbidden_role():
    # Unauthorized role: Guest / Intern
    headers = {"X-Royals-Role": "Guest"}
    response = client.get("/api/auction/export-shortlist?format=json", headers=headers)
    assert response.status_code == 403
    assert "Access Denied" in response.json()["detail"]


def test_printable_html_dossier():
    response = client.get("/api/reports/player-dossier/P_101")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Vidwath Kaverappa" in response.text
    assert "KUMAR SANGAKKARA" in response.text


def test_executive_presentation_export():
    headers = {"X-Royals-Role": "Coach"}
    response = client.get("/api/reports/executive-presentation", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "Royals ScoutIQ — IPL 2027 Auction Strategy" in data["presentation_title"]
    assert len(data["deck_structure"]) >= 10


def test_data_import_and_validation():
    headers = {"X-Royals-Role": "Analyst"}
    payload = {
        "records": [
            {
                "player_id": "P_IMPORT_01",
                "name": "Tanush Kotian",
                "age": 26,
                "role": "All-Rounder",
                "state_team": "Mumbai",
                "matches": 24,
                "runs": 450,
                "wickets": 28,
            },
            {
                "player_id": "P_IMPORT_BAD_AGE",
                "name": "Invalid Age Player",
                "age": 12,  # Invalid age (<14)
                "role": "Batter",
            },
            {
                "player_id": "P_IMPORT_NEGATIVE_STAT",
                "name": "Negative Stat Player",
                "age": 22,
                "role": "Bowler",
                "wickets": -5,  # Negative stat error
            },
        ]
    }
    response = client.post("/api/data/import", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 3
    assert data["valid_records"] == 1
    assert data["invalid_records"] == 2
    assert len(data["errors"]) == 2


# ===========================================================================
# 10. Sabermetric Formula Unit Tests
# ===========================================================================

def test_tsr_calculation_normal_and_boundary_conditions():
    # Strike rate of 200 on baseline 130 -> TSR = +70.0
    tsr = SabermetricsEngine.calculate_tsr(runs=40, balls=20, phase="Overall")
    assert tsr == 70.0

    # Zero balls faced returns 0.0 without ZeroDivisionError
    tsr_zero = SabermetricsEngine.calculate_tsr(runs=0, balls=0, phase="Death")
    assert tsr_zero == 0.0


def test_ter_calculation_normal_and_boundary_conditions():
    # Conceded 24 runs in 24 balls (6.0 rpo) in Death phase (baseline 10.35 rpo)
    # TER = 6.0 - 10.35 = -4.35 (saving 4.35 runs per over)
    ter = SabermetricsEngine.calculate_ter(runs_conceded=24, balls_bowled=24, phase="Death")
    assert ter == -4.35

    # Zero balls bowled returns 0.0
    ter_zero = SabermetricsEngine.calculate_ter(runs_conceded=0, balls_bowled=0, phase="Middle")
    assert ter_zero == 0.0


def test_empirical_bayes_shrinkage():
    # Small sample (10 balls) should heavily shrink towards baseline (135.0)
    shrunk_small = SabermetricsEngine.apply_bayesian_shrinkage(observed_rate=250.0, sample_size=10, prior_mean=135.0, prior_weight=50)
    assert abs(shrunk_small - 154.17) < 0.1

    # Large sample (500 balls) should remain close to observed value
    shrunk_large = SabermetricsEngine.apply_bayesian_shrinkage(observed_rate=250.0, sample_size=500, prior_mean=135.0, prior_weight=50)
    assert abs(shrunk_large - 239.55) < 0.1


def test_steal_index_bounds():
    # High projected WAR with low hammer price relative to base price -> High steal index
    steal = SabermetricsEngine.calculate_steal_index(projected_war=4.5, projected_hammer_lakhs=50.0, base_price_lakhs=20.0)
    assert 1.0 <= steal <= 10.0
    assert steal >= 8.0


def test_phase3_api_endpoints():
    # Phase 3 audit findings endpoint
    r_findings = client.get("/api/rankings/phase3_findings")
    assert r_findings.status_code == 200
    assert r_findings.json()["total"] >= 10

    # Trade audit endpoint
    r_trade = client.get("/api/rankings/trade_audit")
    assert r_trade.status_code == 200
    assert r_trade.json()["total"] >= 20

    # Shai Hope markdown report endpoint
    r_shai_md = client.get("/api/rankings/shai_hope_report")
    assert r_shai_md.status_code == 200
    assert "Shai Hope" in r_shai_md.text
    assert "Player of the Series" in r_shai_md.text

    # Shai Hope statistics endpoint
    r_shai_stats = client.get("/api/rankings/shai_hope_statistics")
    assert r_shai_stats.status_code == 200
    assert r_shai_stats.json()["total"] >= 3

    # Phase 3 verification report endpoint
    r_verif = client.get("/api/rankings/phase3_verification_report")
    assert r_verif.status_code == 200
    assert "Phase 3 Governance" in r_verif.text


def test_phase4_api_endpoints():
    # Previous errors endpoint
    r_err = client.get("/api/rankings/phase4/previous_errors")
    assert r_err.status_code == 200
    assert r_err.json()["total"] >= 10

    # Market status endpoint
    r_mkt = client.get("/api/rankings/phase4/market_status")
    assert r_mkt.status_code == 200
    assert r_mkt.json()["total"] >= 30

    # Top 10 batters endpoint
    r_bat = client.get("/api/rankings/phase4/top10_batters")
    assert r_bat.status_code == 200
    assert r_bat.json()["total"] == 10
    assert r_bat.json()["top10_batters"][0]["player_name"] == "Shai Hope"

    # Top 10 bowlers endpoint
    r_bowl = client.get("/api/rankings/phase4/top10_bowlers")
    assert r_bowl.status_code == 200
    assert r_bowl.json()["total"] == 10
    assert r_bowl.json()["top10_bowlers"][0]["player_name"] == "Matt Henry"

    # RR exclusions endpoint
    r_excl = client.get("/api/rankings/phase4/rr_exclusions")
    assert r_excl.status_code == 200
    assert r_excl.json()["total"] >= 10

    # Evidence sources endpoint
    r_evid = client.get("/api/rankings/phase4/evidence_sources")
    assert r_evid.status_code == 200
    assert r_evid.json()["total"] >= 20

    # Market report markdown endpoint
    r_rep = client.get("/api/rankings/phase4/market_report")
    assert r_rep.status_code == 200
    assert "Master Acquisition Intelligence" in r_rep.text

    # Verification report endpoint
    r_verif = client.get("/api/rankings/phase4/verification_report")
    assert r_verif.status_code == 200
    assert "Phase 4 Governance" in r_verif.text


def test_phase5_api_endpoints():
    # Batting phase analysis
    r_bat_ph = client.get("/api/rankings/phase5/batting_phase_analysis")
    assert r_bat_ph.status_code == 200
    assert r_bat_ph.json()["total"] == 9

    # Spin bowling analysis
    r_spin = client.get("/api/rankings/phase5/spin_bowling_analysis")
    assert r_spin.status_code == 200
    assert r_spin.json()["total"] >= 6

    # Pace bowling analysis
    r_pace = client.get("/api/rankings/phase5/pace_bowling_analysis")
    assert r_pace.status_code == 200
    assert r_pace.json()["total"] >= 6

    # Fielding errors
    r_field = client.get("/api/rankings/phase5/fielding_errors")
    assert r_field.status_code == 200
    assert r_field.json()["total"] >= 12

    # Catching efficiency
    r_catch = client.get("/api/rankings/phase5/catching_efficiency")
    assert r_catch.status_code == 200
    assert r_catch.json()["total"] == 3

    # Weakness matrix
    r_matrix = client.get("/api/rankings/phase5/weakness_matrix")
    assert r_matrix.status_code == 200
    assert r_matrix.json()["total"] >= 5

    # Current squad
    r_squad = client.get("/api/rankings/phase5/current_squad")
    assert r_squad.status_code == 200
    assert r_squad.json()["total"] >= 15

    # Top 10 batters
    r_bat = client.get("/api/rankings/phase5/top10_batters")
    assert r_bat.status_code == 200
    assert r_bat.json()["total"] == 10
    assert r_bat.json()["top10_batters"][0]["player_name"] == "Shai Hope"

    # Top 10 bowlers (Spinners elevated, Mujeeb and Shreyas Gopal replacing Henry and Yadav)
    r_bowl = client.get("/api/rankings/phase5/top10_bowlers")
    assert r_bowl.status_code == 200
    assert r_bowl.json()["total"] == 10
    bowl_names = [b["player_name"] for b in r_bowl.json()["top10_bowlers"]]
    assert bowl_names[0] == "Akeal Hosein"
    assert "Mujeeb Ur Rahman" in bowl_names
    assert "Shreyas Gopal" in bowl_names
    assert "Matt Henry" not in bowl_names
    assert "Umesh Yadav" not in bowl_names

    # Markdown reports
    r_hw = client.get("/api/rankings/phase5/historical_weakness_report")
    assert r_hw.status_code == 200
    assert "Historical Weakness Analysis" in r_hw.text

    r_fr = client.get("/api/rankings/phase5/final_recruitment_report")
    assert r_fr.status_code == 200
    assert "Final Strategic Recruitment Report" in r_fr.text



