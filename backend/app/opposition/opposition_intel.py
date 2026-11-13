"""
Royals ScoutIQ - Opposition Intelligence & Coaching Engine (Features 82–94)
Analyzes opponent batters, bowling matchups, weakness vectors,
and generates tactical field sets for Rajasthan Royals coaching staff.
"""

from typing import List, Dict, Any, Optional


class OppositionIntelligenceEngine:
    """
    Tactical intelligence module translating statistical matchups and video observations
    into actionable coaching game plans for Kumar Sangakkara.
    """

    BOWLING_ARCHETYPES = [
        "Left-Arm Express Pace",
        "Right-Arm Hit-the-Deck Pace",
        "Right-Arm Leg-Spin / Googly",
        "Left-Arm Orthodox Spin",
        "Off-Spin",
    ]

    @classmethod
    def analyze_opponent_batter(
        cls,
        batter_name: str,
        opponent_team: str,
        recent_dismissals: Optional[List[str]] = None,
        custom_splits: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive opposition batter dossier with matchup recommendations.
        """
        splits = custom_splits or cls._get_mock_batter_splits(batter_name)

        # 1. Identify Primary Weakness Vector
        # Find bowling type with lowest SR and highest dot %
        weakness_bowling_type = min(splits.items(), key=lambda x: x[1]["strike_rate"])
        strength_bowling_type = max(splits.items(), key=lambda x: x[1]["strike_rate"])

        # 2. Formulate Matchup Game Plan
        bowler_recommendation = (
            f"Deploy {weakness_bowling_type[0]} immediately upon arrival. "
            f"Batter records a suppressed Strike Rate of {weakness_bowling_type[1]['strike_rate']} "
            f"and high dot-ball percentage of {weakness_bowling_type[1]['dot_pct']}%."
        )

        # 3. Tactical Field Setting Suggestions
        field_setting = {
            "primary_trap": "Wide Line & Deep Cover Sweeper" if "Pace" in weakness_bowling_type[0] else "Packed Leg-Side Ring & Deep Mid-Wicket",
            "fielders": [
                "Deep Backward Point (Boundary Protection)",
                "Deep Extra Cover (Aerial Drive Interception)",
                "Short Mid-Wicket (Leading Edge Catching)",
                "Long-Off (Straight Hit Prevention)",
            ],
            "choke_point_strategy": f"Bowler must avoid slot deliveries. Target hard lengths at 6-8m against {strength_bowling_type[0]} strength zone.",
        }

        return {
            "batter_name": batter_name,
            "opponent_team": opponent_team,
            "matchup_matrix": splits,
            "primary_weakness": {
                "bowling_type": weakness_bowling_type[0],
                "strike_rate": weakness_bowling_type[1]["strike_rate"],
                "dot_pct": weakness_bowling_type[1]["dot_pct"],
                "tactical_plan": bowler_recommendation,
            },
            "primary_strength": {
                "bowling_type": strength_bowling_type[0],
                "strike_rate": strength_bowling_type[1]["strike_rate"],
            },
            "field_placement_plan": field_setting,
            "coach_summary": (
                f"Sangakkara Tactical Plan vs {batter_name}: Neutralize powerplay boundary threat by holding back "
                f"orthodox lines. Use {weakness_bowling_type[0]} during overs 7-11 to build dot-ball pressure."
            ),
        }

    @staticmethod
    def _get_mock_batter_splits(batter_name: str) -> Dict[str, Dict[str, float]]:
        """Simulated matchup split matrix across 5 bowling types."""
        return {
            "Left-Arm Express Pace": {"strike_rate": 112.4, "dot_pct": 48.0, "balls_faced": 55},
            "Right-Arm Hit-the-Deck Pace": {"strike_rate": 146.2, "dot_pct": 31.0, "balls_faced": 120},
            "Right-Arm Leg-Spin / Googly": {"strike_rate": 108.5, "dot_pct": 51.5, "balls_faced": 62},
            "Left-Arm Orthodox Spin": {"strike_rate": 138.0, "dot_pct": 34.0, "balls_faced": 80},
            "Off-Spin": {"strike_rate": 154.5, "dot_pct": 28.0, "balls_faced": 90},
        }

    @classmethod
    def analyze_opponent_bowler(
        cls,
        bowler_name: str,
        opponent_team: str,
    ) -> Dict[str, Any]:
        """
        Feature 84: Analyzes opponent bowler phase effectiveness and tactical counter-plans.
        """
        return {
            "bowler_name": bowler_name,
            "opponent_team": opponent_team,
            "phase_performance": {
                "Powerplay": {"economy": 6.80, "dot_pct": 52.0, "threat_level": "High (Swing Threat)"},
                "Middle": {"economy": 7.45, "dot_pct": 42.0, "threat_level": "Moderate"},
                "Death": {"economy": 11.20, "dot_pct": 24.0, "threat_level": "Vulnerable to Aerial Attack"},
            },
            "primary_vulnerability": "Leaks runs against straight lofted shots in death overs (Economy 11.20 in overs 17-20).",
            "tactical_assault_plan": (
                f"Respect {bowler_name}'s new-ball swing in overs 1-3. Target and attack during his second spell "
                f"at the death with straight-bat lofted drives."
            ),
            "coach_summary": f"Sangakkara Tactical Brief: Target {bowler_name} in overs 18 & 20; boundary frequency jumps to 28% under pressure.",
        }
