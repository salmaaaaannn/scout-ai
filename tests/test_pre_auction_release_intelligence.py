"""
tests/test_pre_auction_release_intelligence.py
===============================================
Comprehensive Automated Test Suite for IPL 2027 Pre-Auction Release Intelligence & Early Market Scouting.
Verifies all deliverables, 8 strict status labels, canonical player ID mappings,
10-franchise coverage, 10 completed trades, spinner shootout (Mujeeb vs Motie vs Rashid),
Shai Hope 4-match sample verification, Linde/Saini replacement caveats, and FastAPI endpoints.
"""

import os
import sys
import csv
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.main import app

client = TestClient(app)

PHASE5_DIR = "phase5_rr_weakness_based_recruitment"
DELIVERABLE_FILES = [
    "ipl2027_early_release_tracker.csv",
    "ipl2027_completed_trades.csv",
    "ipl2027_previously_unsold_pool.csv",
    "ipl2027_confirmed_released_players.csv",
    "ipl2027_reported_release_candidates.csv",
    "ipl2027_predicted_release_candidates.csv",
    "rr_batter_market_watchlist.csv",
    "rr_bowler_market_watchlist.csv",
    "rr_existing_20_players_reverification.csv",
    "rr_pre_auction_verification_audit.csv",
    "rr_pre_auction_market_intelligence_report.md"
]

STRICT_STATUS_LABELS = {
    "RELEASED_CONFIRMED",
    "RELEASE_REPORTED",
    "RELEASE_CANDIDATE_ANALYTICAL",
    "PREVIOUSLY_UNSOLD_2026",
    "RETAINED_OR_CONTRACTED",
    "TRADED_CONFIRMED",
    "AUCTION_REGISTERED_CONFIRMED",
    "UNVERIFIED"
}

ALL_10_FRANCHISES = {"CSK", "MI", "RCB", "KKR", "SRH", "RR", "DC", "PBKS", "LSG", "GT"}


def test_all_deliverables_exist_and_non_empty():
    for fname in DELIVERABLE_FILES:
        p5_path = os.path.join(PHASE5_DIR, fname)
        root_path = fname
        assert os.path.isfile(p5_path), f"File {p5_path} does not exist"
        assert os.path.isfile(root_path), f"File {root_path} does not exist"
        assert os.path.getsize(p5_path) > 100, f"File {p5_path} is too small"
        assert os.path.getsize(root_path) > 100, f"File {root_path} is too small"


def test_early_release_tracker_integrity_and_status_labels():
    tracker_path = os.path.join(PHASE5_DIR, "ipl2027_early_release_tracker.csv")
    with open(tracker_path, mode="r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) >= 40, f"Expected at least 40 players in tracker, got {len(rows)}"

    franchises_found = set()
    for r in rows:
        assert int(r["player_id"]) > 0
        assert r["player_name"]
        assert r["nationality"]
        assert r["current_franchise"]
        if r["current_franchise"] in ALL_10_FRANCHISES:
            franchises_found.add(r["current_franchise"])

        # Strict 8 status labels enforcement
        assert r["market_status_label"] in STRICT_STATUS_LABELS, (
            f"Invalid status label '{r['market_status_label']}' for player {r['player_name']}"
        )

        # Audit metadata
        assert r["primary_evidence_source"]
        assert r["source_url"].startswith("http")
        assert r["date_checked"] == "2026-11-12"
        assert r["confidence_level"] in {"High", "Medium", "Low"}
        assert r["verification_notes"]

    assert franchises_found == ALL_10_FRANCHISES, f"Missing franchises: {ALL_10_FRANCHISES - franchises_found}"


def test_completed_trades_register():
    fpath = os.path.join(PHASE5_DIR, "ipl2027_completed_trades.csv")
    with open(fpath, mode="r", encoding="utf-8") as f:
        trades = list(csv.DictReader(f))

    assert len(trades) == 10
    trade_names = {t["player_name"]: t for t in trades}

    # Verify Pant: LSG to DC
    assert trade_names["Rishabh Pant"]["from_franchise"] == "LSG"
    assert trade_names["Rishabh Pant"]["to_franchise"] == "DC"
    assert trade_names["Rishabh Pant"]["market_status_label"] == "TRADED_CONFIRMED"
    assert "DC" in trade_names["Rishabh Pant"]["current_contract_status"]

    # Verify Kuldeep: DC to LSG
    assert trade_names["Kuldeep Yadav"]["from_franchise"] == "DC"
    assert trade_names["Kuldeep Yadav"]["to_franchise"] == "LSG"

    # Verify Natarajan: DC to SRH
    assert trade_names["T Natarajan"]["from_franchise"] == "DC"
    assert trade_names["T Natarajan"]["to_franchise"] == "SRH"

    # Verify Ansari: SRH to DC
    assert trade_names["Zeeshan Ansari"]["from_franchise"] == "SRH"
    assert trade_names["Zeeshan Ansari"]["to_franchise"] == "DC"

    # Verify Livingstone: SRH to CSK
    assert trade_names["Liam Livingstone"]["from_franchise"] == "SRH"
    assert trade_names["Liam Livingstone"]["to_franchise"] == "CSK"

    # Verify Edwards: SRH to CSK
    assert trade_names["Jack Edwards"]["from_franchise"] == "SRH"
    assert trade_names["Jack Edwards"]["to_franchise"] == "CSK"

    # Verify Khaleel: CSK to SRH
    assert trade_names["Khaleel Ahmed"]["from_franchise"] == "CSK"
    assert trade_names["Khaleel Ahmed"]["to_franchise"] == "SRH"

    # Verify Ellis: CSK to SRH
    assert trade_names["Nathan Ellis"]["from_franchise"] == "CSK"
    assert trade_names["Nathan Ellis"]["to_franchise"] == "SRH"

    # Verify Hardik: MI to PBKS
    assert trade_names["Hardik Pandya"]["from_franchise"] == "MI"
    assert trade_names["Hardik Pandya"]["to_franchise"] == "PBKS"

    # Verify Arshdeep: PBKS to MI
    assert trade_names["Arshdeep Singh"]["from_franchise"] == "PBKS"
    assert trade_names["Arshdeep Singh"]["to_franchise"] == "MI"


def test_previously_unsold_pool_csv():
    fpath = os.path.join(PHASE5_DIR, "ipl2027_previously_unsold_pool.csv")
    with open(fpath, mode="r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 5
    for r in rows:
        assert r["market_status_label"] == "PREVIOUSLY_UNSOLD_2026"
    names = {r["player_name"] for r in rows}
    assert "Shai Hope" in names
    assert "Mujeeb Ur Rahman" in names
    assert "Daryl Mitchell" in names
    assert "Kyle Mayers" in names
    assert "Mayank Agarwal" in names


def test_shai_hope_4_matches_sample_correction():
    # Check in batter watchlist
    b_path = os.path.join(PHASE5_DIR, "rr_batter_market_watchlist.csv")
    with open(b_path, mode="r", encoding="utf-8") as f:
        b_rows = list(csv.DictReader(f))
    hope_b = [r for r in b_rows if r["player_name"] == "Shai Hope"][0]
    assert "4 T20I matches" in hope_b["sample_specific_stats"] or "4 matches" in hope_b["sample_specific_stats"]
    assert "3 matches" not in hope_b["sample_specific_stats"]
    assert "3 T20Is" not in hope_b["sample_specific_stats"]
    assert "190.51" in hope_b["sample_specific_stats"]

    # Check in reverification csv
    rev_path = os.path.join(PHASE5_DIR, "rr_existing_20_players_reverification.csv")
    with open(rev_path, mode="r", encoding="utf-8") as f:
        rev_rows = list(csv.DictReader(f))
    hope_rev = [r for r in rev_rows if r["player_name"] == "Shai Hope"][0]
    assert "4 T20I matches" in hope_rev["exact_sample_citation"] or "4 matches" in hope_rev["exact_sample_citation"]
    assert "3 matches" not in hope_rev["exact_sample_citation"]
    assert "3 T20Is" not in hope_rev["exact_sample_citation"]

    # Check in markdown report
    rep_path = os.path.join(PHASE5_DIR, "rr_pre_auction_market_intelligence_report.md")
    with open(rep_path, mode="r", encoding="utf-8") as f:
        rep_text = f.read()
    assert "4 T20I matches" in rep_text or "4 matches" in rep_text


def test_george_linde_and_navdeep_saini_replacement_appointments():
    rev_path = os.path.join(PHASE5_DIR, "rr_existing_20_players_reverification.csv")
    with open(rev_path, mode="r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    name_map = {r["player_name"]: r for r in rows}

    linde = name_map["George Linde"]
    assert "LSG" in linde["verified_ipl_2026_position"]
    assert "Hasaranga" in linde["verified_ipl_2026_position"]
    assert "ELIGIBILITY_UNVERIFIED" in linde["auction_2027_registration_status"]

    saini = name_map["Navdeep Saini"]
    assert "KKR" in saini["verified_ipl_2026_position"]
    assert "Replacement" in saini["verified_ipl_2026_position"]
    assert "ELIGIBILITY_UNVERIFIED" in saini["auction_2027_registration_status"]


def test_target_list_vs_watchlist_discipline():
    # Batter watchlist
    b_path = os.path.join(PHASE5_DIR, "rr_batter_market_watchlist.csv")
    with open(b_path, mode="r", encoding="utf-8") as f:
        batters = list(csv.DictReader(f))

    confirmed_batters = [b for b in batters if "CONFIRMED_AVAILABLE" in b["availability_tier"]]
    assert len(confirmed_batters) == 4  # Hope, Mitchell, Mayers, Agarwal
    watchlist_batters = [b for b in batters if "PRE_AUCTION_RELEASE_WATCHLIST" in b["availability_tier"]]
    assert len(watchlist_batters) >= 5

    # Bowler watchlist
    bw_path = os.path.join(PHASE5_DIR, "rr_bowler_market_watchlist.csv")
    with open(bw_path, mode="r", encoding="utf-8") as f:
        bowlers = list(csv.DictReader(f))

    # Mujeeb must be #1 spinner over Motie and Rashid
    assert bowlers[0]["player_name"] == "Mujeeb Ur Rahman"
    assert bowlers[0]["rank"] == "1"
    assert "CONFIRMED_AVAILABLE" in bowlers[0]["availability_tier"]

    assert bowlers[1]["player_name"] == "Gudakesh Motie"
    assert "WATCHLIST" in bowlers[1]["availability_tier"]

    assert bowlers[2]["player_name"] == "Adil Rashid"
    assert "WATCHLIST" in bowlers[2]["availability_tier"]


def test_pre_auction_verification_audit_csv():
    fpath = os.path.join(PHASE5_DIR, "rr_pre_auction_verification_audit.csv")
    with open(fpath, mode="r", encoding="utf-8") as f:
        audits = list(csv.DictReader(f))

    assert len(audits) >= 8
    for a in audits:
        assert a["audit_item_id"]
        assert a["parameter_checked"]
        assert a["previous_value"]
        assert a["corrected_value"]
        assert a["correction_status"] == "CORRECTED_AND_VERIFIED"
        assert a["verification_source"]
        assert a["source_url"].startswith("http")


def test_fastapi_audited_endpoints():
    # Completed trades endpoint
    r_tr = client.get("/api/rankings/early_release/completed_trades")
    assert r_tr.status_code == 200
    data_tr = r_tr.json()
    assert data_tr["total"] == 10
    assert data_tr["completed_trades"][0]["player_name"] == "Rishabh Pant"

    # Previously unsold endpoint
    r_un = client.get("/api/rankings/early_release/previously_unsold")
    assert r_un.status_code == 200
    data_un = r_un.json()
    assert data_un["total"] == 5
    un_names = [r["player_name"] for r in data_un["previously_unsold"]]
    assert "Shai Hope" in un_names
    assert "Mujeeb Ur Rahman" in un_names

    # Verification audit endpoint
    r_aud = client.get("/api/rankings/early_release/verification_audit")
    assert r_aud.status_code == 200
    assert r_aud.json()["total"] >= 8

    # Tracker endpoint
    r_trk = client.get("/api/rankings/early_release/tracker")
    assert r_trk.status_code == 200
    assert r_trk.json()["total"] >= 40

    # Batter watchlist endpoint
    r_bat = client.get("/api/rankings/early_release/batter_watchlist")
    assert r_bat.status_code == 200
    assert r_bat.json()["batter_watchlist"][0]["player_name"] == "Shai Hope"
    assert "4 T20I matches" in r_bat.json()["batter_watchlist"][0]["sample_specific_stats"] or "4 matches" in r_bat.json()["batter_watchlist"][0]["sample_specific_stats"]

    # Bowler watchlist endpoint
    r_bw = client.get("/api/rankings/early_release/bowler_watchlist")
    assert r_bw.status_code == 200
    assert r_bw.json()["bowler_watchlist"][0]["player_name"] == "Mujeeb Ur Rahman"

    # Report markdown endpoint
    r_rep = client.get("/api/rankings/early_release/intelligence_report")
    assert r_rep.status_code == 200
    assert "Completed IPL 2027 Trade Register" in r_rep.text
    assert "Rishabh Pant" in r_rep.text
