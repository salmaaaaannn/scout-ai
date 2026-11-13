"""
Royals ScoutIQ - Database Persistence Layer Test Suite
Validates SQLite database initialization, table creation, CRUD operations,
data integrity, and scenario persistence across system lifecycles.
"""

import pytest
import os
from backend.app.database.db import (
    init_database,
    get_db,
    get_db_path,
    save_video_asset,
    get_video_asset,
    save_biomechanical_record,
    save_verification_item,
    get_all_verifications,
    update_verification_status,
    get_database_stats,
    save_player,
    get_player,
    get_all_players,
    seed_shortlisted_players,
    save_playing_xi_scenario,
    get_all_playing_xi_scenarios,
    SHORTLISTED_20_PLAYERS,
)


def test_init_database_and_stats():
    init_database()
    stats = get_database_stats()
    assert stats["engine"] == "SQLite 3"
    assert stats["status"] == "connected"
    assert "players" in stats["tables"]
    assert "video_assets" in stats["tables"]
    assert "cv_biomechanical_records" in stats["tables"]
    assert "analyst_verifications" in stats["tables"]
    assert "playing_xi_scenarios" in stats["tables"]
    assert stats["tables"]["players"] >= 20


def test_shortlisted_players_seeding_and_retrieval():
    seed_shortlisted_players()
    players = get_all_players()
    assert len(players) >= 20

    # Test retrieval of specific shortlisted player
    naman = get_player("37052")
    assert naman is not None
    assert naman["full_name"] == "Naman Dhir"
    assert naman["is_uncapped"] == 1

    shai = get_player("4369")
    assert shai is not None
    assert shai["full_name"] == "Shai Hope"
    assert shai["eligibility_status"] == "ELIGIBLE_OVERSEAS"

    # Non-existent player
    unknown = get_player("9999999")
    assert unknown is None


def test_save_and_retrieve_player_crud():
    custom_player = save_player(
        player_id="TEST_P_001",
        full_name="Test Scout Candidate",
        dob="2004-05-15",
        age=22.5,
        role="Pace Bowler",
        batting_style="Right-hand bat",
        bowling_style="Right-arm fast",
        state_team="Rajasthan",
        is_uncapped=1,
        eligibility_status="ELIGIBLE_UNCAPPED",
    )
    assert custom_player["player_id"] == "TEST_P_001"

    fetched = get_player("TEST_P_001")
    assert fetched is not None
    assert fetched["full_name"] == "Test Scout Candidate"
    assert fetched["age"] == 22.5


def test_save_and_get_video_asset():
    asset = save_video_asset(
        video_id="TEST_VID_001",
        filename="test_clip.mp4",
        file_path="/path/to/test_clip.mp4",
        file_size_bytes=2048576,
        player_id="37052",
        fps=30.0,
        total_frames=120,
        duration_seconds=4.0,
        resolution="1920x1080",
    )
    assert asset["video_id"] == "TEST_VID_001"

    fetched = get_video_asset("TEST_VID_001")
    assert fetched is not None
    assert fetched["filename"] == "test_clip.mp4"
    assert fetched["total_frames"] == 120

    assert get_video_asset("NON_EXISTENT_VID") is None


def test_save_biomechanical_record():
    bio_id = save_biomechanical_record(
        video_id="TEST_VID_001",
        player_id="37052",
        player_name="Naman Dhir",
        role="Top-Order Batter",
        timestamp_seconds=1.85,
        head_stillness_score=0.96,
        bat_speed_rad_s=85.4,
        bat_speed_kph=75.2,
        arm_release_angle=72.0,
        spine_stress_index=14.5,
        shot_classification="Cover Drive",
        action_classification="3/4 Round-Arm",
        raw_keypoints=[[100, 200, 0.95], [105, 205, 0.92]],
    )
    assert isinstance(bio_id, int)
    assert bio_id > 0


def test_verification_item_lifecycle():
    item = save_verification_item(
        obs_id="OBS_TEST_DB_LIFECYCLE",
        player_id="37052",
        player_name="Naman Dhir",
        video_id="TEST_VID_001",
        timestamp_seconds=2.1,
        ai_observation="Bat downswing velocity 85.4 rad/s with high head stillness.",
        raw_confidence=0.92,
        review_status="PENDING",
    )
    assert item["obs_id"] == "OBS_TEST_DB_LIFECYCLE"
    assert item["review_status"] == "PENDING"

    # List pending
    pending = get_all_verifications(status="PENDING")
    obs_ids = [p["obs_id"] for p in pending]
    assert "OBS_TEST_DB_LIFECYCLE" in obs_ids

    # Update to CONFIRMED
    updated = update_verification_status(
        obs_id="OBS_TEST_DB_LIFECYCLE",
        status="CONFIRMED",
        analyst_name="Kumar Sangakkara",
        confidence_multiplier=1.0,
        corrected_observation="Verified excellent head stillness and high downswing velocity.",
    )
    assert updated is not None
    assert updated["review_status"] == "CONFIRMED"
    assert updated["analyst_name"] == "Kumar Sangakkara"
    assert updated["confidence_multiplier"] == 1.0


def test_playing_xi_scenario_persistence():
    xi_players = [
        {"player_id": "7915", "player_name": "Yashasvi Jaiswal", "role": "Opening Batter"},
        {"player_id": "37052", "player_name": "Naman Dhir", "role": "Top-Order Batter"},
    ]
    impact = {"player_id": "8661", "player_name": "Matheesha Pathirana", "role": "Death Bowler"}

    scen_id = save_playing_xi_scenario(
        opponent="Chennai Super Kings",
        venue="Sawai Mansingh Stadium, Jaipur",
        pitch_type="Dry Turning Track",
        scenario_type="Defending Total",
        selected_xi=xi_players,
        impact_player=impact,
        team_rating=91.5,
    )
    assert isinstance(scen_id, int)
    assert scen_id > 0

    scenarios = get_all_playing_xi_scenarios()
    assert len(scenarios) > 0
    latest = scenarios[0]
    assert latest["opponent"] == "Chennai Super Kings"
    assert len(latest["selected_xi"]) == 2
    assert latest["impact_player"]["player_name"] == "Matheesha Pathirana"
