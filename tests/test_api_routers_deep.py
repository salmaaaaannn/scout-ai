"""
Royals ScoutIQ - API Routers Deep Integration Test Suite
Validates Candidates Router and Rankings Router endpoints with query parameters,
filters, pagination, error paths, and data export formats.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_candidates_router_queries_and_filters():
    # List with search query
    res = client.get("/api/candidates?q=Yash&limit=5")
    assert res.status_code == 200
    assert "candidates" in res.json()

    # Filter by eligibility status
    res_elig = client.get("/api/candidates?eligibility=ELIGIBLE_UNCAPPED&limit=10")
    assert res_elig.status_code == 200

    # Filter by role
    res_role = client.get("/api/candidates?role=Top-Order Batter&limit=10")
    assert res_role.status_code == 200

    # Summary and queue endpoints
    res_summary = client.get("/api/candidates/routing-summary")
    assert res_summary.status_code == 200
    assert "total_candidates" in res_summary.json()

    res_camp = client.get("/api/candidates/verification-campaign")
    assert res_camp.status_code == 200

    res_pending = client.get("/api/candidates/pending-queue")
    assert res_pending.status_code == 200

    res_excl = client.get("/api/candidates/exclusions")
    assert res_excl.status_code == 200

    # Youngest / List A and List B
    res_a = client.get("/api/candidates/top10-youngest")
    assert res_a.status_code == 200
    assert "top10_candidates" in res_a.json()

    res_b = client.get("/api/candidates/top10-balanced")
    assert res_b.status_code == 200
    assert "shortlist" in res_b.json()

    # Completeness gate
    res_gate = client.get("/api/candidates/completeness-gate")
    assert res_gate.status_code == 200

    # Export endpoints
    res_csv = client.get("/api/candidates/export/csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers.get("content-type", "")

    res_pdf_html = client.get("/api/candidates/scouting-report-pdf")
    assert res_pdf_html.status_code == 200
    assert "text/html" in res_pdf_html.headers.get("content-type", "")


def test_candidates_router_single_and_calculate_ages():
    # Get candidate by valid ID
    cands_res = client.get("/api/candidates?limit=1").json()
    cid = cands_res["candidates"][0]["candidate_id"]

    res_single = client.get(f"/api/candidates/{cid}")
    assert res_single.status_code == 200
    assert res_single.json()["candidate_id"] == cid

    # Non-existent ID returns 404
    res_404 = client.get("/api/candidates/NON_EXISTENT_ID_99999")
    assert res_404.status_code == 404

    # Calculate ages endpoint
    res_age = client.post("/api/candidates/calculate-ages")
    assert res_age.status_code == 200
    age_data = res_age.json()
    assert age_data["status"] == "CALCULATION_COMPLETE"
    assert age_data["primary_cutoff"] == "2026-11-08"


def test_rankings_router_players_and_pressure():
    # List players
    res = client.get("/api/rankings/players?limit=10")
    assert res.status_code == 200
    players = res.json()["players"]
    assert len(players) > 0

    # Search player by name
    res_search = client.get("/api/rankings/players?q=Naman")
    assert res_search.status_code == 200

    # Filter by role
    res_role = client.get("/api/rankings/players?role=Batter")
    assert res_role.status_code == 200

    # Single player lookup
    p1_id = players[0]["player_id"]
    res_p1 = client.get(f"/api/rankings/players/{p1_id}")
    assert res_p1.status_code == 200
    assert res_p1.json()["player_id"] == p1_id


def test_rankings_router_phase_endpoints():
    # Phase 4 endpoints
    res_p4_stat = client.get("/api/rankings/phase4/market_status")
    assert res_p4_stat.status_code == 200

    res_p4_bat = client.get("/api/rankings/phase4/top10_batters")
    assert res_p4_bat.status_code == 200

    res_p4_bowl = client.get("/api/rankings/phase4/top10_bowlers")
    assert res_p4_bowl.status_code == 200

    res_p4_rep = client.get("/api/rankings/phase4/market_report")
    assert res_p4_rep.status_code == 200

    # Phase 5 endpoints
    res_p5_mat = client.get("/api/rankings/phase5/weakness_matrix")
    assert res_p5_mat.status_code == 200

    res_p5_bat = client.get("/api/rankings/phase5/top10_batters")
    assert res_p5_bat.status_code == 200

    res_p5_bowl = client.get("/api/rankings/phase5/top10_bowlers")
    assert res_p5_bowl.status_code == 200

    res_p5_squad = client.get("/api/rankings/phase5/current_squad")
    assert res_p5_squad.status_code == 200

    res_p5_rep = client.get("/api/rankings/phase5/final_recruitment_report")
    assert res_p5_rep.status_code == 200


def test_rankings_router_early_release_endpoints():
    res_tracker = client.get("/api/rankings/early_release/tracker")
    assert res_tracker.status_code == 200

    res_conf = client.get("/api/rankings/early_release/confirmed_released")
    assert res_conf.status_code == 200

    res_rep = client.get("/api/rankings/early_release/reported_release")
    assert res_rep.status_code == 200

    res_pred = client.get("/api/rankings/early_release/predicted_release")
    assert res_pred.status_code == 200

    res_trades = client.get("/api/rankings/early_release/completed_trades")
    assert res_trades.status_code == 200

    res_unsold = client.get("/api/rankings/early_release/previously_unsold")
    assert res_unsold.status_code == 200


def test_rankings_router_round1_endpoints():
    res_batters = client.get("/api/rankings/round1/top_10_batters")
    assert res_batters.status_code == 200
    assert res_batters.json()["total"] == 10

    res_bowlers = client.get("/api/rankings/round1/top_10_bowlers")
    assert res_bowlers.status_code == 200
    assert res_bowlers.json()["total"] == 10

    res_overall = client.get("/api/rankings/round1/top_10_overall")
    assert res_overall.status_code == 200
    assert res_overall.json()["total"] == 10

    res_all_bat = client.get("/api/rankings/round1/all_ranked_batters")
    assert res_all_bat.status_code == 200

    res_all_bowl = client.get("/api/rankings/round1/all_ranked_bowlers")
    assert res_all_bowl.status_code == 200

    res_comp = client.get("/api/rankings/round1/comparison")
    assert res_comp.status_code == 200

    res_dq = client.get("/api/rankings/round1/data_quality")
    assert res_dq.status_code == 200
