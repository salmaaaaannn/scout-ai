import os
import csv
import pytest
from fastapi.testclient import TestClient
from app.main import app
import pptx
import pypdf

client = TestClient(app)

DELIVERABLES_13 = [
    "top_10_batters_under_pressure.csv",
    "top_10_bowlers_under_pressure.csv",
    "top_10_overall_pressure_recommendations.csv",
    "all_ranked_batters_under_pressure.csv",
    "all_ranked_bowlers_under_pressure.csv",
    "player_pressure_comparison.csv",
    "pressure_index_match_validation.csv",
    "pressure_model_sensitivity_analysis.csv",
    "pressure_reliability_methodology.md",
    "rr_pressure_recruitment_insights.md",
    "round1_final_submission_report.pdf",
    "round1_final_presentation.pptx",
    "data_quality_and_validation_report.md"
]


def test_all_13_deliverables_exist_and_non_empty():
    for fn in DELIVERABLES_13:
        assert os.path.isfile(fn), f"Missing required deliverable: {fn}"
        assert os.path.getsize(fn) > 0, f"Deliverable is empty: {fn}"


def test_top_10_batters_schema_and_content():
    expected_fields = [
        "rank", "player_name", "player_id", "nationality", "primary_batting_role",
        "bpri_score", "pressure_balls", "pressure_runs", "pressure_strike_rate",
        "pressure_average", "normal_strike_rate", "pressure_vs_normal_improvement",
        "death_over_performance", "confidence_grade", "why_reliable_under_pressure",
        "important_limitations"
    ]
    with open("top_10_batters_under_pressure.csv", "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        assert r.fieldnames == expected_fields, f"Field mismatch in top 10 batters: {r.fieldnames}"
        rows = list(r)
        assert len(rows) == 10, f"Expected 10 batters, got {len(rows)}"

        # Check descending BPRI score
        scores = [float(row["bpri_score"]) for row in rows]
        assert scores == sorted(scores, reverse=True), "BPRI scores not in descending order"

        # Check sample sizes meet qualification
        for row in rows:
            assert int(row["pressure_balls"]) >= 60, f"Batter {row['player_name']} has < 60 pressure balls"
            assert float(row["pressure_strike_rate"]) > 100.0, f"Unusually low strike rate: {row}"
            assert row["confidence_grade"] in ("Grade A", "Grade B", "Grade C")


def test_top_10_bowlers_schema_and_content():
    expected_fields = [
        "rank", "player_name", "player_id", "nationality", "bowling_style",
        "bowpri_score", "pressure_legal_balls", "pressure_wickets", "pressure_economy",
        "pressure_bowling_average", "normal_economy", "pressure_vs_normal_improvement",
        "best_performing_phase", "confidence_grade", "why_reliable_under_pressure",
        "important_limitations"
    ]
    with open("top_10_bowlers_under_pressure.csv", "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        assert r.fieldnames == expected_fields, f"Field mismatch in top 10 bowlers: {r.fieldnames}"
        rows = list(r)
        assert len(rows) == 10, f"Expected 10 bowlers, got {len(rows)}"

        # Check descending BOWPRI score
        scores = [float(row["bowpri_score"]) for row in rows]
        assert scores == sorted(scores, reverse=True), "BOWPRI scores not in descending order"

        # Check sample sizes meet qualification
        for row in rows:
            assert int(row["pressure_legal_balls"]) >= 48, f"Bowler {row['player_name']} has < 48 pressure balls"
            assert float(row["pressure_economy"]) < 12.0, f"Excessive economy rate: {row}"
            assert row["confidence_grade"] in ("Grade A", "Grade B", "Grade C")


def test_top_10_overall_recommendations_integrity():
    with open("top_10_overall_pressure_recommendations.csv", "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r)
        assert len(rows) == 10, f"Expected 10 overall recommendations, got {len(rows)}"

        # Scores must be descending
        scores = [float(row["pressure_reliability_score"]) for row in rows]
        assert scores == sorted(scores, reverse=True), "OPRI scores not in descending order"

    # Exclusions check: Zero RR existing players and zero Pakistani players
    rr_excluded = set()
    if os.path.isfile("rr_existing_player_exclusions.csv"):
        with open("rr_existing_player_exclusions.csv", "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rr_excluded.add(r["player_id"].strip())

    pak_excluded = {"8741", "2921", "2485", "3024", "8049", "2490", "6624", "7983", "3160", "8050", "2923", "2495", "6625", "8051", "2924", "3025"}

    for row in rows:
        pid = row["player_id"].strip()
        assert pid not in rr_excluded, f"Found existing RR player in recommendations: {row['player_name']}"
        assert pid not in pak_excluded, f"Found Pakistani player in recommendations: {row['player_name']}"


def test_presentation_and_pdf_structure():
    prs = pptx.Presentation("round1_final_presentation.pptx")
    assert len(prs.slides) == 15, f"Expected 15 slides, got {len(prs.slides)}"

    pdf = pypdf.PdfReader("round1_final_submission_report.pdf")
    assert len(pdf.pages) >= 2, f"Expected at least 2 pages, got {len(pdf.pages)}"
    full_text = "".join(p.extract_text() for p in pdf.pages)
    assert "SupeRR Selector" in full_text
    assert "Pressure" in full_text


def test_fastapi_round1_endpoints():
    r1 = client.get("/api/rankings/round1/top_10_batters")
    assert r1.status_code == 200
    assert r1.json()["total"] == 10

    r2 = client.get("/api/rankings/round1/top_10_bowlers")
    assert r2.status_code == 200
    assert r2.json()["total"] == 10

    r3 = client.get("/api/rankings/round1/top_10_overall")
    assert r3.status_code == 200
    assert r3.json()["total"] == 10

    r4 = client.get("/api/rankings/round1/methodology")
    assert r4.status_code == 200
    assert "Pressure Index" in r4.text

    r5 = client.get("/api/rankings/round1/rr_insights")
    assert r5.status_code == 200
    assert "Rajasthan Royals" in r5.text

    r6 = client.get("/api/rankings/round1/data_quality")
    assert r6.status_code == 200
    assert "192,675" in r6.text
