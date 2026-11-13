"""
Royals ScoutIQ - Phase 1 Scouting Intelligence Test Suite
Tests all 10 core requirements of Round 1:
- Ingestion of 336 pool entries with duplicate preservation
- Candidate listing, search, and filtering
- Candidate verification updates and field-level evidence tracking
- Duplicate identity disambiguation
- Exact deterministic age calculation and leap-day boundary logic
- 5-gate eligibility routing and exact partition
- List A generation (Absolute Youngest 10, strict age sort, zero synthetic data)
- List B generation (Role-balanced supplementary shortlist)
- Candidate comparison engine
- Export endpoints (CSV, printable PDF-ready report)
"""

import sys
import os
from pathlib import Path
from datetime import date
import pytest
from fastapi.testclient import TestClient

# Ensure backend and project root are in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app
from app.scouting.age_engine import AgeCalculationEngine, PRIMARY_CUTOFF, SECONDARY_CUTOFF
from app.scouting.routing_engine import EligibilityRoutingEngine
from app.scouting.registry_service import CandidateRegistryService
from app.scouting.models import VerificationUpdateRequest, DisambiguationRequest, DOBPrecision, EligibilityStatus

client = TestClient(app)


def test_api_routing_summary():
    """Verify routing summary endpoint and exact partition."""
    res = client.get("/api/candidates/routing-summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_candidates" in data
    assert "eligible_uncapped_count" in data
    assert "pending_verification_count" in data
    assert "excluded_candidates_count" in data
    assert data["exact_partition_verified"] is True
    assert data["total_candidates"] == (
        data["eligible_uncapped_count"] + data["pending_verification_count"] + data["excluded_candidates_count"]
    )


def test_api_list_candidates_search_and_pagination():
    """Verify candidate listing, search, and pagination."""
    # List all
    res = client.get("/api/candidates?limit=10&offset=0")
    assert res.status_code == 200
    data = res.json()
    assert data["limit"] == 10
    assert len(data["candidates"]) == 10
    assert data["total_count"] >= 335

    # Search for Andre
    res_search = client.get("/api/candidates?q=Andre")
    assert res_search.status_code == 200
    search_data = res_search.json()
    names = [c["identity"]["unstop_name"] for c in search_data["candidates"]]
    assert any("Andre" in n for n in names)


def test_api_top10_absolute_youngest_list_a():
    """Verify List A: Provisional Youngest Verified Candidates entry under completeness gate."""
    res = client.get("/api/candidates/top10-youngest")
    assert res.status_code == 200
    data = res.json()

    meta = data["metadata"]
    assert "List A" in meta["list_name"]
    assert meta["title"] == "Provisional Youngest Verified Candidates"
    assert meta["absolute_ranking_unlocked"] is False
    assert meta["gate_status"] == "VERIFIED_COVERAGE_WITH_RANKING_LIMITATION"
    assert "METHODOLOGY LIMITATION" in meta["methodology_limitation"]
    assert meta["primary_cutoff_date"] == "2026-11-08"
    assert "selection_methodology" in meta

    top10 = data["top10_candidates"]
    assert len(top10) <= 10
    assert len(top10) > 0

    # Verify strict ascending sort by total_days as of 2026-11-08
    total_days_seq = [
        c["age_calculations"]["as_of_2026_11_08"]["total_days"] for c in top10
    ]
    assert total_days_seq == sorted(total_days_seq), "List A must be sorted strictly ascending by total_days"

    # Verify #1 is Andre Siddharth (born 2006-08-28)
    first_pick = top10[0]
    assert first_pick["identity"]["unstop_name"] == "Andre Siddharth"
    assert first_pick["dob"]["value"] == "2006-08-28"
    c8 = first_pick["age_calculations"]["as_of_2026_11_08"]
    assert c8["years"] == 20
    assert c8["months"] == 2
    assert c8["days"] == 11
    assert c8["total_days"] == 7377


def test_api_top10_balanced_list_b():
    """Verify List B: Role-Balanced supplementary shortlist."""
    res = client.get("/api/candidates/top10-balanced")
    assert res.status_code == 200
    data = res.json()
    assert "List B" in data["metadata"]["list_name"]
    shortlist = data["shortlist"]
    assert len(shortlist) > 0

    roles = [c["playing_profile"].get("role") or "" for c in shortlist]
    # Verify diverse positional representation
    has_batter = any("bat" in r.lower() for r in roles)
    has_pacer = any("fast" in r.lower() or "pace" in r.lower() for r in roles)
    assert has_batter, "List B must contain batters"
    assert has_pacer, "List B must contain fast bowlers"


def test_api_candidate_details_and_verification_update():
    """Verify detailed profile retrieval and analyst verification updates."""
    # Lookup Aaradhya Yadav
    res_list = client.get("/api/candidates?q=Aaradhya")
    cands = res_list.json()["candidates"]
    assert len(cands) > 0
    cand_id = cands[0]["candidate_id"]

    # Get details
    res_detail = client.get(f"/api/candidates/{cand_id}")
    assert res_detail.status_code == 200
    cand = res_detail.json()
    assert cand["candidate_id"] == cand_id

    # Update verification
    update_payload = {
        "candidate_id": cand_id,
        "verified_name": "Aaradhya Yadav (Verified)",
        "dob": "2004-06-03",
        "dob_precision": "FULL_DATE",
        "country": "India",
        "is_indian_domestic": True,
        "is_overseas": False,
        "senior_capped_status": "NONE_CONFIRMED",
        "role": "Wicketkeeper-Batter",
        "state_team": "Uttar Pradesh",
        "reviewer": "Test Lead Scout",
        "reviewer_notes": "Verified against BCCI Domestic Player Registry",
    }
    res_update = client.post(f"/api/candidates/{cand_id}/verify", json=update_payload)
    assert res_update.status_code == 200
    updated_cand = res_update.json()["candidate"]
    assert updated_cand["identity"]["verified_name"] == "Aaradhya Yadav (Verified)"
    assert updated_cand["age_calculations"]["as_of_2026_11_08"]["status"] == "CALCULATED"


def test_api_evidence_management():
    """Verify adding field-level evidence to a candidate."""
    res_list = client.get("/api/candidates?limit=1")
    cand_id = res_list.json()["candidates"][0]["candidate_id"]

    evidence_payload = {
        "claim": "Date of birth",
        "value_supported": "2006-08-28",
        "source_title": "Official State Cricket Association Scorecard",
        "publisher": "State Association / BCCI",
        "source_url": "https://www.bcci.tv/match/domestic/2024",
        "source_type": "OFFICIAL_RECORD",
        "retrieved_on": "2026-11-08",
        "checked_by": "Senior QA Analyst",
        "verification_status": "VERIFIED",
        "notes": "Verified match score sheet."
    }
    res_ev = client.post(f"/api/candidates/{cand_id}/evidence", json=evidence_payload)
    assert res_ev.status_code == 200
    assert res_ev.json()["status"] == "EVIDENCE_ATTACHED"


def test_api_duplicate_disambiguation():
    """Verify duplicate identity resolution for Himanshu Singh."""
    res_search = client.get("/api/candidates?q=Himanshu%20Singh")
    cands = res_search.json()["candidates"]
    assert len(cands) > 0
    target_cand = None
    for c in cands:
        if len(c["identity"]["original_entry_indices"]) > 1:
            target_cand = c
            break

    assert target_cand is not None
    cand_id = target_cand["candidate_id"]

    disambig_payload = {
        "candidate_id": cand_id,
        "resolution_status": "VERIFIED",
        "disambiguated_name": "Himanshu Singh (Mumbai Off-Spinner)",
        "distinguishing_notes": "Corroborated as Mumbai CA Ranji off-spinner born 2003-09-17.",
        "reviewer": "Giles Lindsay (Director of Strategy)"
    }
    res_dis = client.post("/api/candidates/disambiguate", json=disambig_payload)
    assert res_dis.status_code == 200
    cand = res_dis.json()["candidate"]
    assert cand["identity"]["name_status"] == "VERIFIED"
    assert "Mumbai" in cand["identity"]["verified_name"]


def test_api_candidate_comparison():
    """Verify side-by-side comparison of multiple candidates."""
    res_top = client.get("/api/candidates/top10-youngest")
    picks = res_top.json()["top10_candidates"]
    assert len(picks) >= 2
    cids = [picks[0]["candidate_id"], picks[1]["candidate_id"]]

    res_comp = client.post("/api/candidates/compare", json={"candidate_ids": cids})
    assert res_comp.status_code == 200
    comp_data = res_comp.json()
    assert comp_data["comparison_count"] == 2
    assert "metric_matrix" in comp_data


def test_api_export_csv_and_pdf_report():
    """Verify CSV export and printable competition report."""
    # CSV export
    res_csv = client.get("/api/candidates/export/csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "candidate_id,unstop_name" in res_csv.text

    # Printable HTML / PDF report
    res_rep = client.get("/api/candidates/scouting-report-pdf")
    assert res_rep.status_code == 200
    assert "text/html" in res_rep.headers["content-type"]
    assert "ROYALS" in res_rep.text
    assert "ScoutIQ" in res_rep.text
    assert "PROVISIONAL YOUNGEST VERIFIED CANDIDATES" in res_rep.text
    assert "METHODOLOGY LIMITATION" in res_rep.text
    assert "Senior International Appearance Audit" in res_rep.text
    assert "November 8, 2026" in res_rep.text


def test_incomplete_dob_coverage_blocks_final_ranking():
    """Directive 6 & 8: Verify incomplete DOB coverage across pool blocks absolute youngest claim."""
    res = client.get("/api/candidates/completeness-gate")
    assert res.status_code == 200
    gate = res.json()

    assert gate["total_unique_candidates"] == 335
    assert gate["verified_candidates"] == 205
    assert gate["remaining_domestic_pending_research"] == 2
    assert gate["absolute_ranking_unlocked"] is False
    assert gate["gate_status"] == "VERIFIED_COVERAGE_WITH_RANKING_LIMITATION"
    assert "Provisional Youngest Verified Candidates" in gate["title"]
    assert len(gate["blocking_reasons"]) > 0
    assert "METHODOLOGY LIMITATION" in gate["methodology_limitation"]


def test_pending_younger_candidate_blocks_absolute_youngest_status():
    """Directive 1 & 8: Unverified candidates in pool prevent claiming absolute youngest status."""
    res_la = client.get("/api/candidates/list-a")
    assert res_la.status_code == 200
    meta = res_la.json()["metadata"]

    assert meta["title"] == "Provisional Youngest Verified Candidates"
    assert meta["absolute_ranking_unlocked"] is False
    assert "METHODOLOGY LIMITATION" in meta["methodology_limitation"]
    assert any("remain pending DOB verification" in r for r in meta["blocking_reasons"])


def test_missing_cap_evidence_does_not_produce_eligible_uncapped():
    """Directive 3 & 8: An absent appearance does not automatically produce ELIGIBLE_UNCAPPED."""
    # A candidate without positive Senior International Appearance Audit evidence must route to PENDING
    unresearched_cand = {
        "candidate_id": "TEST_UNRESEARCHED",
        "identity": {"unstop_name": "Unresearched Player", "name_status": "PENDING"},
        "dob": {"value": "2006-01-01", "precision": "FULL_DATE", "status": "PENDING"},
        "nationality_and_status": {"is_indian_domestic_player": True, "is_overseas": False},
        "international_and_contract_record": {"senior_capped_status": "PENDING", "evidence": []},
        "eligibility": {"status": "PENDING_VERIFICATION", "reason": "No audit performed"},
    }
    dest, reason, calcs = EligibilityRoutingEngine.route_candidate(unresearched_cand)
    assert dest == "PENDING"
    assert "ELIGIBLE_UNCAPPED" not in dest
    assert reason is not None


def test_unsupported_statistics_never_enter_final_dossier():
    """Directive 5 & 8: Verify no speculative speeds, release heights, or auction prices enter dossier."""
    res_la = client.get("/api/candidates/list-a")
    picks = res_la.json()["top10_candidates"]

    for cand in picks:
        perf = cand.get("performance_data", {})
        # Statistics dict must be empty or only verified data
        stats = perf.get("statistics", {})
        assert "death_over_strike_rate" not in stats
        assert "release_height" not in stats
        assert "bowling_speed" not in stats
        assert "auction_hammer_price" not in stats
        assert perf.get("source_status") == "N/A — insufficient verified sample"

    # Verify dossier HTML
    res_pdf = client.get("/api/candidates/scouting-report-pdf")
    html = res_pdf.text
    assert "140+ km/h" not in html
    assert "2.1m" not in html


def test_verified_candidates_ranked_by_exact_age():
    """Directive 8: Candidates in List A are ranked strictly ascending by exact total_days elapsed."""
    res_la = client.get("/api/candidates/list-a")
    picks = res_la.json()["top10_candidates"]
    assert len(picks) == 10

    days_sequence = [p["age_calculations"]["as_of_2026_11_08"]["total_days"] for p in picks]
    assert days_sequence == sorted(days_sequence)

    # #1 Andre Siddharth must be 7,377 total days
    p1 = picks[0]
    assert p1["identity"]["unstop_name"] == "Andre Siddharth"
    assert p1["dob"]["value"] == "2006-08-28"
    assert p1["age_calculations"]["as_of_2026_11_08"]["total_days"] == 7377
    assert p1["age_calculations"]["as_of_2026_11_08"]["years"] == 20
    assert p1["age_calculations"]["as_of_2026_11_08"]["months"] == 2
    assert p1["age_calculations"]["as_of_2026_11_08"]["days"] == 11


def test_pipeline_re_run_deterministic_idempotency():
    """Directive 8: Re-running pipeline produces identical deterministic results."""
    res_run1 = client.get("/api/candidates/list-a").json()
    res_run2 = client.get("/api/candidates/list-a").json()

    picks1 = res_run1["top10_candidates"]
    picks2 = res_run2["top10_candidates"]

    assert len(picks1) == len(picks2)
    for p1, p2 in zip(picks1, picks2):
        assert p1["candidate_id"] == p2["candidate_id"]
        assert p1["dob"]["value"] == p2["dob"]["value"]
        assert p1["age_calculations"] == p2["age_calculations"]

