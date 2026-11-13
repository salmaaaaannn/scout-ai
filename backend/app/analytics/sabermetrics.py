"""
Royals ScoutIQ - Sabermetric & Bayesian Statistical Normalization Engine
Implements True Strike Rate (TSR), True Economy Rate (TER), Bayesian Sample Shrinkage,
and Auction Steal Index calculations.
"""

from typing import Dict, Any


class SabermetricsEngine:
    """
    Mathematical intelligence engine designed to eliminate domestic stat-padding,
    small-sample anomalies, and pitch bias in cricket data.
    """

    # Baseline Phase Expectations (T20 Domestic Standard)
    DEFAULT_PHASE_BASELINES = {
        "Powerplay": {"expected_sr": 128.5, "expected_econ": 7.42},
        "Middle": {"expected_sr": 122.0, "expected_econ": 7.15},
        "Death": {"expected_sr": 164.2, "expected_econ": 10.35},
    }

    # Competition Quality Multipliers (CQM)
    TIER_WEIGHTS = {
        "Elite": 1.0,         # Frontline Ranji / SMAT Elite Groups
        "StateT20": 0.85,     # High-end State T20 (TNPL, UP T20, Maharaja Trophy)
        "Plate": 0.65,        # BCCI Plate division (weaker bowling/batting depth)
    }

    @staticmethod
    def calculate_tsr(runs: int, balls: int, phase: str = "Middle", custom_baseline_sr: float = None) -> float:
        """
        True Strike Rate (TSR):
        Measures the runs scored per 100 balls above/below the expected baseline
        for that exact phase and pitch conditions.
        """
        if balls == 0:
            return 0.0

        raw_sr = (runs / balls) * 100.0
        baseline = custom_baseline_sr or SabermetricsEngine.DEFAULT_PHASE_BASELINES.get(phase, {}).get("expected_sr", 130.0)
        return round(raw_sr - baseline, 2)

    @staticmethod
    def calculate_ter(runs_conceded: int, balls_bowled: int, phase: str = "Middle", custom_baseline_econ: float = None) -> float:
        """
        True Economy Rate (TER):
        Measures runs conceded per 6 balls relative to the phase baseline.
        Negative TER indicates elite run suppression (better than expected).
        """
        if balls_bowled == 0:
            return 0.0

        overs = balls_bowled / 6.0
        raw_econ = runs_conceded / overs
        baseline = custom_baseline_econ or SabermetricsEngine.DEFAULT_PHASE_BASELINES.get(phase, {}).get("expected_econ", 7.8)
        return round(raw_econ - baseline, 2)

    @staticmethod
    def apply_bayesian_shrinkage(observed_rate: float, sample_size: int, prior_mean: float, prior_weight: int = 35) -> float:
        """
        Empirical Bayes Shrinkage:
        Pulls anomalous stats from small sample sizes toward the league prior mean.
        Formula: (n * observed + m * prior) / (n + m)
        """
        if sample_size <= 0:
            return prior_mean

        shrunk_rate = (sample_size * observed_rate + prior_weight * prior_mean) / (sample_size + prior_weight)
        return round(shrunk_rate, 2)

    bayesian_shrinkage = apply_bayesian_shrinkage

    @staticmethod
    def calculate_acpi(age: int, performance_rating: float) -> float:
        """
        Age-Curve Potential Index (ACPI):
        Estimates the 3-year ceiling of a player. A 19-year-old performing at domestic level
        has significantly higher trajectory upside than a 25-year-old with identical stats.
        Baseline peak age in T20 is modeled around 25.5 - 28.0 years.
        """
        if age <= 17:
            age_multiplier = 1.35
        elif age <= 19:
            age_multiplier = 1.25
        elif age <= 21:
            age_multiplier = 1.15
        elif age <= 23:
            age_multiplier = 1.05
        else:
            age_multiplier = 0.95

        acpi_score = min(100.0, performance_rating * age_multiplier)
        return round(acpi_score, 1)

    @staticmethod
    def calculate_steal_index(projected_war: float, projected_hammer_lakhs: float, base_price_lakhs: float = 20.0) -> float:
        """
        Auction Steal Index:
        Measures Value Over Replacement (WAR) relative to projected purse expenditure.
        Identifies high-impact uncapped talent available at value prices (The Vignesh Puthur Index).
        Scale: 0.0 to 10.0
        """
        if projected_hammer_lakhs <= 0:
            return 0.0

        # High WAR with near-base price yield top steal ratings
        cost_ratio = projected_hammer_lakhs / max(base_price_lakhs, 20.0)
        raw_index = (projected_war * 10.0) / (1.0 + (cost_ratio * 0.45))
        return round(min(10.0, max(0.0, raw_index)), 1)
