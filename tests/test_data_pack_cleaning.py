import os
import csv
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

CLEANED_DIR = "data/cleaned"


def test_cleaned_files_exist():
    required_files = [
        "player_master.csv",
        "player_aliases.csv",
        "player_id_mapping.csv",
        "data_validation_report.csv",
        "cleaning_summary.md",
    ]
    for rf in required_files:
        p = os.path.join(CLEANED_DIR, rf)
        assert os.path.isfile(p), f"Missing cleaned artifact: {p}"
        assert os.path.getsize(p) > 0, f"Artifact is empty: {p}"


def test_player_master_integrity():
    p = os.path.join(CLEANED_DIR, "player_master.csv")
    with open(p, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 1217, f"Expected 1217 players, found {len(rows)}"

    pids = [r["player_id"] for r in rows]
    assert len(pids) == len(set(pids)), "Duplicate player_id detected in player_master.csv"

    # Verify canonical name normalization examples
    dhoni = next((r for r in rows if r["player_id"] == "8"), None)
    assert dhoni is not None
    assert dhoni["canonical_name"] == "MS Dhoni"
    assert dhoni["original_name"] == "Mahendra Singh Dhoni"
    assert dhoni["primary_role"] == "Batter"
    assert dhoni["is_ipl_player"].lower() == "true"

    tilak = next((r for r in rows if r["original_name"] == "Namboori Tilak Varma"), None)
    assert tilak is not None
    assert tilak["canonical_name"] == "Tilak Varma"

    coulter = next((r for r in rows if r["original_name"] == "Nathan Coulter Nile"), None)
    assert coulter is not None
    assert coulter["canonical_name"] == "Nathan Coulter-Nile"

    shahrukh = next((r for r in rows if r["original_name"] == "M Shahrukh Khan"), None)
    assert shahrukh is not None
    assert shahrukh["canonical_name"] == "Shahrukh Khan"


def test_distinct_players_not_merged():
    p = os.path.join(CLEANED_DIR, "player_id_mapping.csv")
    with open(p, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Abdul Samad
    samad_rows = [r for r in rows if "Abdul Samad" in r["original_name"]]
    assert len(samad_rows) == 2, "Abdul Samad identities were merged or lost"
    pids = set(r["player_id"] for r in samad_rows)
    assert pids == {"7446", "6922"}

    # Rashid Khan
    rashid_rows = [r for r in rows if r["original_name"] == "Rashid Khan"]
    assert len(rashid_rows) == 2, "Rashid Khan identities were merged or lost"
    rashid_pids = set(r["player_id"] for r in rashid_rows)
    assert rashid_pids == {"4722", "20172"}

    # Haider Ali
    haider_rows = [r for r in rows if r["original_name"] == "Haider Ali"]
    assert len(haider_rows) == 2, "Haider Ali identities were merged or lost"
    haider_pids = set(r["player_id"] for r in haider_rows)
    assert haider_pids == {"7338", "28756"}


def test_validation_report_issues():
    p = os.path.join(CLEANED_DIR, "data_validation_report.csv")
    with open(p, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) >= 6
    # Verify critical issue for revised overs balls vs overs
    revised_issue = next((r for r in rows if "first_inn_revised_overs" in r["record_identifier"]), None)
    assert revised_issue is not None
    assert revised_issue["severity"] == "CRITICAL"
    assert "integer balls" in revised_issue["description"]


def test_rankings_api_endpoints():
    client = TestClient(app)

    # 1. Search players
    res = client.get("/api/rankings/players?q=Dhoni")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert data["players"][0]["canonical_name"] == "MS Dhoni"

    # 2. Player detail
    res_detail = client.get("/api/rankings/players/8")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["player_id"] == "8"
    assert detail["profile"]["canonical_name"] == "MS Dhoni"
    assert len(detail["aliases"]) >= 1

    # 3. Validation report
    res_val = client.get("/api/rankings/validation_report")
    assert res_val.status_code == 200
    val_data = res_val.json()
    assert val_data["total_issues"] >= 6

    # 4. Cleaning summary markdown
    res_summary = client.get("/api/rankings/cleaning_summary")
    assert res_summary.status_code == 200
    assert "Discovered Dataset Inventory" in res_summary.text
