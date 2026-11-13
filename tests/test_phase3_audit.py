"""
tests/test_phase3_audit.py
==========================
Automated test suite for Royals ScoutIQ Phase 3:
- IPL 2027 eligibility verification & policy enforcement
- Franchise affiliation, trade verification (Arshdeep Singh -> MI swap for Hardik Pandya)
- Strict Pakistani player exclusion from RR acquisition shortlist
- Shai Hope multi-format reassessment & 2026 series verification
- Recalculated 20-player Long-Term Investment Shortlist
- Deliverable schema, governance quality gates & evidence provenance
"""

import csv
import os
import pytest

AS_OF_DATE = "2026-11-11"

PHASE3_DELIVERABLES = [
    "phase3_audit_findings.csv",
    "ipl_eligibility_and_trade_audit.csv",
    "shai_hope_format_statistics.csv",
    "shai_hope_multi_format_report.md",
    "updated_long_term_investment_shortlist.csv",
    "updated_multi_format_player_research.csv",
    "updated_player_evidence_sources.csv",
    "phase3_verification_report.md",
]

PAKISTAN_PLAYER_IDS = {"8741", "2921", "2485", "3024", "8049"}


@pytest.mark.parametrize("filename", PHASE3_DELIVERABLES)
def test_phase3_deliverable_exists_and_non_empty(filename):
    """Quality Gate: All 8 required Phase 3 deliverable files must exist and not be empty."""
    assert os.path.exists(filename), f"Missing required Phase 3 file: {filename}"
    assert os.path.getsize(filename) > 100, f"File {filename} is too small or empty"


def test_updated_shortlist_candidate_count_and_composition():
    """Verify the revised RR 2027 Long-Term Investment Shortlist contains exactly 20 vetted players."""
    with open("updated_long_term_investment_shortlist.csv", "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) == 20, f"Expected 20 shortlisted candidates, found {len(reader)}"

    shortlisted_ids = {row["player_id"] for row in reader}

    # 1. Zero Pakistani players
    pak_overlap = shortlisted_ids.intersection(PAKISTAN_PLAYER_IDS)
    assert not pak_overlap, f"Pakistani players must NOT be in RR investment shortlist: {pak_overlap}"

    # 2. Arshdeep Singh excluded (contracted to MI)
    assert "6464" not in shortlisted_ids, "Arshdeep Singh is contracted to MI and cannot be shortlisted"

    # 3. Wriddhiman Saha excluded (retired)
    assert "109" not in shortlisted_ids, "Wriddhiman Saha is retired and cannot be shortlisted"

    # 4. Zero RR existing players
    with open("rr_existing_player_exclusions.csv", "r", encoding="utf-8") as f:
        rr_excl_ids = {r["player_id"] for r in csv.DictReader(f)}
    rr_overlap = shortlisted_ids.intersection(rr_excl_ids)
    assert not rr_overlap, f"Shortlist contains current RR players: {rr_overlap}"


def test_shai_hope_target_one_and_stats():
    """Verify Shai Hope is reassessed, ranked #1 target, and his 2026 performance is verified."""
    with open("updated_long_term_investment_shortlist.csv", "r", encoding="utf-8") as f:
        shortlist = list(csv.DictReader(f))

    # Top ranked candidate is Shai Hope
    top_candidate = shortlist[0]
    assert top_candidate["player_id"] == "4369"
    assert "Shai Hope" in top_candidate["player_name"]
    assert float(top_candidate["investment_score"]) >= 85.0
    assert top_candidate["availability_status"] == "AUCTION_ELIGIBLE_2027"

    # Verify format statistics
    with open("shai_hope_format_statistics.csv", "r", encoding="utf-8") as f:
        format_stats = list(csv.DictReader(f))

    formats = {r["format"]: r for r in format_stats}
    assert "T20I (Recent 2026)" in formats or any("T20I" in k for k in formats)
    assert "ODI (Career)" in formats or any("ODI" in k for k in formats)
    assert "Test (Career / Recent Status)" in formats or any("Test" in k for k in formats)

    # Check 2026 series mention
    with open("shai_hope_multi_format_report.md", "r", encoding="utf-8") as f:
        report_text = f.read()
    assert "261" in report_text
    assert "190.51" in report_text
    assert "Player of the Series" in report_text
    assert "comp_id: '3450'" in report_text or "3450" in report_text


def test_arshdeep_singh_trade_audit():
    """Verify Arshdeep Singh's trade from PBKS to Mumbai Indians is audited and classified."""
    with open("ipl_eligibility_and_trade_audit.csv", "r", encoding="utf-8") as f:
        audit_rows = {r["player_id"]: r for r in csv.DictReader(f)}

    assert "6464" in audit_rows, "Arshdeep Singh must be audited in ipl_eligibility_and_trade_audit.csv"
    arshdeep = audit_rows["6464"]
    assert "Mumbai Indians" in arshdeep["current_franchise"]
    assert "Hardik Pandya" in arshdeep["notes"]
    assert "UNAVAILABLE" in arshdeep["auction_availability"]


def test_pakistani_players_ineligible_classification():
    """Verify Pakistani players are audited and classified as ineligible for IPL acquisition."""
    with open("ipl_eligibility_and_trade_audit.csv", "r", encoding="utf-8") as f:
        audit_rows = {r["player_id"]: r for r in csv.DictReader(f)}

    for pak_id in PAKISTAN_PLAYER_IDS:
        assert pak_id in audit_rows, f"Player {pak_id} must be in the audit table"
        row = audit_rows[pak_id]
        assert "INELIGIBLE" in row["ipl_eligibility"]
        assert row["rr_candidate_eligible"] == "False"


def test_phase3_audit_findings_completeness():
    """Verify all 10 core audit claims are cataloged with specific corrections."""
    with open("phase3_audit_findings.csv", "r", encoding="utf-8") as f:
        findings = list(csv.DictReader(f))

    assert len(findings) >= 10, f"Expected at least 10 audit findings, got {len(findings)}"
    player_ids = {r["player_id"] for r in findings}
    assert "6464" in player_ids  # Arshdeep
    assert "4369" in player_ids  # Shai Hope
    assert "8741" in player_ids  # Mohammad Haris
    assert "2921" in player_ids  # Fakhar Zaman
    assert "109" in player_ids   # Wriddhiman Saha


def test_phase3_verification_report_quality_gates():
    """Verify Phase 3 verification report includes all quality gates and as-of date."""
    with open("phase3_verification_report.md", "r", encoding="utf-8") as f:
        report = f.read()

    assert AS_OF_DATE in report
    for gate in ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10"]:
        assert gate in report, f"Quality gate {gate} missing from verification report"
