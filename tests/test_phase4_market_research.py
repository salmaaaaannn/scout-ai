"""
tests/test_phase4_market_research.py
====================================
Automated test suite for Royals ScoutIQ Phase 4:
- Verified IPL 2027 Player Market Research
- Audit of previous classification errors (Priyansh Arya, Hazlewood, Chahal, Arshdeep, etc.)
- Top 10 Batters (Verified Free Agents / Released / Unsold)
- Top 10 Bowlers (Verified Free Agents / Released / Unsold)
- Rigorous elimination of players contracted to other franchises
- Multi-source cross-checking (Cricbuzz, ESPNcricinfo, BCCI/IPLT20)
"""

import csv
import os
import pytest

AS_OF_DATE = "2026-11-11"

PHASE4_DELIVERABLES = [
    "phase4_previous_errors.csv",
    "ipl2027_market_status.csv",
    "top10_batters_ipl2027.csv",
    "top10_bowlers_ipl2027.csv",
    "rr_existing_player_exclusions_phase4.csv",
    "phase4_player_evidence_sources.csv",
    "phase4_market_research_report.md",
    "phase4_verification_report.md"
]

PAKISTAN_PLAYER_IDS = {"8741", "2921", "2485", "3024", "8049"}
OTHER_FRANCHISE_CONTRACTED_IDS = {
    "25669",  # Priyansh Arya (PBKS)
    "830",    # Josh Hazlewood (RCB)
    "8221",   # Nitish Kumar Reddy (SRH)
    "1612",   # Yuzvendra Chahal (PBKS)
    "6464",   # Arshdeep Singh (PBKS)
    "4853",   # Glenn Phillips (GT)
    "7446",   # Abdul Samad (LSG)
    "4636",   # Anrich Nortje (KKR)
    "2639",   # Marcus Stoinis (PBKS)
    "4007",   # Ryan Rickelton (MI)
    "46066",  # Vipraj Nigam (DC)
    "3641",   # Ben Dwarshuis (PBKS)
}
RETIRED_PLAYER_IDS = {"2878", "109"}  # Mohit Sharma, Wriddhiman Saha


@pytest.mark.parametrize("filename", PHASE4_DELIVERABLES)
def test_phase4_deliverables_exist_and_non_empty(filename):
    """Quality Gate: All 8 required Phase 4 deliverable files must exist and not be empty."""
    assert os.path.exists(filename), f"Missing required file: {filename}"
    assert os.path.getsize(filename) > 100, f"File {filename} is too small or empty"


def test_previous_errors_audit_correctness():
    """Verify previous errors are audited with exact franchise reconciliations."""
    with open("phase4_previous_errors.csv", "r", encoding="utf-8") as f:
        errors = {r["player_id"]: r for r in csv.DictReader(f)}

    # Priyansh Arya
    assert "25669" in errors
    assert "Punjab Kings" in errors["25669"]["correction"]
    assert errors["25669"]["verified_status"] == "CONTRACTED_OTHER_FRANCHISE"

    # Josh Hazlewood
    assert "830" in errors
    assert "Royal Challengers" in errors["830"]["correction"]
    assert errors["830"]["verified_status"] == "CONTRACTED_OTHER_FRANCHISE"

    # Nitish Reddy
    assert "8221" in errors
    assert "Sunrisers Hyderabad" in errors["8221"]["correction"]
    assert "RETAINED" in errors["8221"]["verified_status"]

    # Yuzvendra Chahal
    assert "1612" in errors
    assert "Punjab Kings" in errors["1612"]["correction"]

    # Arshdeep Singh
    assert "6464" in errors
    assert "Punjab Kings" in errors["6464"]["correction"]
    assert "RTM" in errors["6464"]["correction"]

    # Mohit Sharma
    assert "2878" in errors
    assert errors["2878"]["verified_status"] == "RETIRED"


def test_top10_batters_purity_and_availability():
    """Verify top 10 batters contains exactly 10 genuine free agents with zero conflicts."""
    with open("top10_batters_ipl2027.csv", "r", encoding="utf-8") as f:
        batters = list(csv.DictReader(f))

    assert len(batters) == 10, f"Expected 10 batters, got {len(batters)}"

    # Check master player registry
    with open("data/cleaned/player_master.csv", "r", encoding="utf-8") as f:
        master_ids = {r["player_id"] for r in csv.DictReader(f)}

    # Check RR exclusions
    with open("rr_existing_player_exclusions_phase4.csv", "r", encoding="utf-8") as f:
        rr_ids = {r["player_id"] for r in csv.DictReader(f)}

    for b in batters:
        pid = b["player_id"]
        # Must exist in master or be external
        assert pid in master_ids or pid == "NOT_IN_SUPPLIED_MASTER"
        # Must be verified free agent
        assert b["availability_status"] == "FREE_AGENT_CONFIRMED"
        assert b["release_status"] == "RELEASED_CONFIRMED"
        assert b["auction_eligibility"] == "ELIGIBLE"
        # Must NOT be contracted to other franchise
        assert pid not in OTHER_FRANCHISE_CONTRACTED_IDS, f"Player {b['player_name']} ({pid}) is contracted elsewhere!"
        # Must NOT be Pakistani
        assert pid not in PAKISTAN_PLAYER_IDS
        # Must NOT be retired
        assert pid not in RETIRED_PLAYER_IDS
        # Must NOT be in RR existing squad
        assert pid not in rr_ids

    # Shai Hope is #1 target
    assert batters[0]["player_id"] == "4369"
    assert "Shai Hope" in batters[0]["player_name"]


def test_top10_bowlers_purity_and_availability():
    """Verify top 10 bowlers contains exactly 10 genuine free agents with zero conflicts."""
    with open("top10_bowlers_ipl2027.csv", "r", encoding="utf-8") as f:
        bowlers = list(csv.DictReader(f))

    assert len(bowlers) == 10, f"Expected 10 bowlers, got {len(bowlers)}"

    # Check master player registry
    with open("data/cleaned/player_master.csv", "r", encoding="utf-8") as f:
        master_ids = {r["player_id"] for r in csv.DictReader(f)}

    # Check RR exclusions
    with open("rr_existing_player_exclusions_phase4.csv", "r", encoding="utf-8") as f:
        rr_ids = {r["player_id"] for r in csv.DictReader(f)}

    for b in bowlers:
        pid = b["player_id"]
        assert pid in master_ids or pid == "NOT_IN_SUPPLIED_MASTER"
        assert b["availability_status"] == "FREE_AGENT_CONFIRMED"
        assert b["release_status"] == "RELEASED_CONFIRMED"
        assert b["auction_eligibility"] == "ELIGIBLE"
        assert pid not in OTHER_FRANCHISE_CONTRACTED_IDS, f"Player {b['player_name']} ({pid}) is contracted elsewhere!"
        assert pid not in PAKISTAN_PLAYER_IDS
        assert pid not in RETIRED_PLAYER_IDS
        assert pid not in rr_ids

    # Matt Henry is #1 bowling target
    assert bowlers[0]["player_id"] == "3174"
    assert "Matt Henry" in bowlers[0]["player_name"]


def test_multi_source_evidence_cross_checks():
    """Verify evidence file contains Cricbuzz, ESPNcricinfo, and official sources."""
    with open("phase4_player_evidence_sources.csv", "r", encoding="utf-8") as f:
        evidence = list(csv.DictReader(f))

    publishers = {r["publisher"] for r in evidence}
    assert any("Cricbuzz" in p for p in publishers), "Cricbuzz cross-check required"
    assert any("ESPNcricinfo" in p for p in publishers), "ESPNcricinfo cross-check required"
    assert any("IPLT20" in p or "BCCI" in p for p in publishers), "Official source required"
