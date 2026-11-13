"""
Royals ScoutIQ - Analytics, Opposition Intel & Player Development Test Suite
Covers DataValidationSystem, OppositionIntelligenceEngine,
PlayerDevelopmentEngine, and AuctionStrategyEngine.
"""

import pytest
from backend.app.analytics.data_validator import DataValidationSystem
from backend.app.opposition.opposition_intel import OppositionIntelligenceEngine
from backend.app.development.player_development import PlayerDevelopmentEngine
from backend.app.analytics.auction_simulator import AuctionStrategyEngine


def test_data_validator_comprehensive():
    # Valid records
    valid_batch = [
        {"player_id": "P_01", "full_name": "Aaradhya Yadav", "age": 20, "role": "Wicketkeeper-Batter", "runs": 120},
        {"player_id": "P_02", "full_name": "Aaqib Khan", "age": 21, "role": "Pace Bowler", "wickets": 15},
    ]
    res_valid = DataValidationSystem.validate_player_records(valid_batch)
    assert res_valid["is_dataset_clean"] is True
    assert res_valid["valid_records_count"] == 2
    assert res_valid["rejected_records_count"] == 0

    # Invalid batch with multiple edge cases
    invalid_batch = [
        {"player_id": "P_03", "age": 22, "role": "Batter"},  # missing full_name
        {"player_id": "P_04", "full_name": "Too Young", "age": 12, "role": "Batter"},  # age < 14
        {"player_id": "P_05", "full_name": "Too Old", "age": 48, "role": "Batter"},  # age > 45
        {"player_id": "P_06", "full_name": "Invalid Age", "age": "Unknown", "role": "Batter"},  # non-numeric age
        {"player_id": "P_07", "full_name": "Negative Runs", "age": 25, "role": "Batter", "runs": -10},  # negative runs
        {"player_id": "P_08", "full_name": "Negative Wickets", "age": 24, "role": "Bowler", "wickets": -3},  # negative wickets
        {"player_id": "P_09", "full_name": "Negative Balls", "age": 24, "role": "Batter", "balls_faced": -5},  # negative balls
        {"player_id": "P_09", "full_name": "Duplicate ID", "age": 24, "role": "Bowler"},  # duplicate id P_09
        {"player_id": "P_10", "full_name": "Duplicate ID", "age": 24, "role": "Bowler"},  # duplicate name
    ]
    res_invalid = DataValidationSystem.validate_player_records(invalid_batch)
    assert res_invalid["is_dataset_clean"] is False
    assert res_invalid["rejected_records_count"] == len(invalid_batch)
    assert len(res_invalid["errors"]) > 0


def test_opposition_intelligence_engine():
    # Analyze batter with default mock splits
    batter_intel = OppositionIntelligenceEngine.analyze_opponent_batter(
        batter_name="Heinrich Klaasen",
        opponent_team="Sunrisers Hyderabad",
    )
    assert batter_intel["batter_name"] == "Heinrich Klaasen"
    assert "matchup_matrix" in batter_intel
    assert "primary_weakness" in batter_intel
    assert "primary_strength" in batter_intel
    assert "field_placement_plan" in batter_intel
    assert "coach_summary" in batter_intel

    # Analyze batter with custom splits
    custom_splits = {
        "Left-Arm Express Pace": {"strike_rate": 95.0, "dot_pct": 55.0},
        "Right-Arm Hit-the-Deck Pace": {"strike_rate": 180.0, "dot_pct": 20.0},
    }
    custom_intel = OppositionIntelligenceEngine.analyze_opponent_batter(
        batter_name="Travis Head",
        opponent_team="Sunrisers Hyderabad",
        custom_splits=custom_splits,
    )
    assert custom_intel["primary_weakness"]["bowling_type"] == "Left-Arm Express Pace"
    assert custom_intel["primary_strength"]["bowling_type"] == "Right-Arm Hit-the-Deck Pace"

    # Analyze bowler
    bowler_intel = OppositionIntelligenceEngine.analyze_opponent_bowler(
        bowler_name="Anrich Nortje",
        opponent_team="Delhi Capitals",
    )
    assert bowler_intel["bowler_name"] == "Anrich Nortje"
    assert "phase_performance" in bowler_intel
    assert "Powerplay" in bowler_intel["phase_performance"]
    assert "tactical_assault_plan" in bowler_intel


def test_player_development_engine():
    # Performance trends for existing bowler P_101
    trends_bowler = PlayerDevelopmentEngine.get_player_performance_trends("P_101")
    assert trends_bowler["seasons_analyzed"] == 3
    assert trends_bowler["trajectory"] == "Ascending (High Upside)"
    assert "Death Economy" in trends_bowler["trend_summary"]

    # Performance trends for existing batter P_102
    trends_batter = PlayerDevelopmentEngine.get_player_performance_trends("P_102")
    assert trends_batter["seasons_analyzed"] == 3
    assert trends_batter["trajectory"] == "Ascending (High Upside)"
    assert "Death Strike Rate" in trends_batter["trend_summary"]

    # Unknown player
    trends_unknown = PlayerDevelopmentEngine.get_player_performance_trends("UNKNOWN_PLAYER")
    assert trends_unknown["records_found"] == 0
    assert trends_unknown["trajectory"] == "Flat"

    # Training plans for different weaknesses
    plan_spin = PlayerDevelopmentEngine.generate_training_plan("P_101", "Weak against wrist spin and googly")
    assert len(plan_spin["prescribed_drills"]) >= 2
    assert "wrist spin" in plan_spin["head_coach_guidance"].lower()

    plan_death = PlayerDevelopmentEngine.generate_training_plan("P_101", "Death yorker accuracy issues")
    assert len(plan_death["prescribed_drills"]) >= 2

    plan_default = PlayerDevelopmentEngine.generate_training_plan("P_101", "Short pitch bowling")
    assert len(plan_default["prescribed_drills"]) >= 2

    # Before and after session comparison
    session_a = {"date": "2025-10-01", "head_stillness": 0.82, "bat_speed": 110.0, "stress_index": 0.55}
    session_b = {"date": "2026-02-15", "head_stillness": 0.94, "bat_speed": 128.5, "stress_index": 0.35}
    comp = PlayerDevelopmentEngine.compare_before_after_sessions(session_a, session_b)
    assert comp["technical_evolution"] == "Significant Technical Improvement"
    assert "+" in comp["head_stillness_change"]

    # Full report
    rep = PlayerDevelopmentEngine.generate_player_development_report("P_101", "Vidwath Kaverappa")
    assert rep["report_id"] == "DEV_REP_P_101"
    assert rep["acpi_potential_rating"] > 0.0


def test_auction_strategy_engine():
    # Role scarcity calculations
    assert AuctionStrategyEngine.calculate_role_scarcity("Pace All-Rounder") >= 9.5
    assert AuctionStrategyEngine.calculate_role_scarcity("140k Domestic Pacer Depth") >= 9.0
    assert AuctionStrategyEngine.calculate_role_scarcity("Top-order Batter") <= 7.0
    assert AuctionStrategyEngine.calculate_role_scarcity("Unknown Role") == 6.5

    # Priority classification
    target_prio = AuctionStrategyEngine.classify_auction_priority(steal_index=9.0, scarcity=9.5, tactical_fit=80.0)
    assert "Target" in target_prio

    backup_prio = AuctionStrategyEngine.classify_auction_priority(steal_index=6.0, scarcity=6.0, tactical_fit=50.0)
    assert "Backup" in backup_prio

    avoid_prio = AuctionStrategyEngine.classify_auction_priority(steal_index=2.0, scarcity=3.0, tactical_fit=10.0)
    assert "Avoid" in avoid_prio

    # Squad balance analysis
    mock_squad = [
        {"name": f"Batter {i}", "role": "Top-Order Batter", "is_overseas": False} for i in range(5)
    ] + [
        {"name": f"WK {i}", "role": "Wicketkeeper Batter", "is_overseas": False} for i in range(2)
    ] + [
        {"name": f"AR {i}", "role": "Pace All-Rounder", "is_overseas": False} for i in range(3)
    ] + [
        {"name": f"Pacer {i}", "role": "Pace Bowler", "is_overseas": i < 2} for i in range(5)
    ] + [
        {"name": f"Spinner {i}", "role": "Spin Bowler", "is_overseas": False} for i in range(3)
    ]
    balance_res = AuctionStrategyEngine.analyze_squad_balance(mock_squad)
    assert balance_res["total_players"] == 18
    assert balance_res["is_squad_balanced"] is True
    assert balance_res["overseas_quota_compliant"] is True

    # Auction budget simulation
    budget_sim = AuctionStrategyEngine.simulate_auction_budget(total_purse_lakhs=850.0)
    assert budget_sim["allocated_purse_lakhs"] == 850.0
    assert budget_sim["simulated_picks_count"] == 5
    assert "remaining_purse_lakhs" in budget_sim
    assert "budget_status" in budget_sim
