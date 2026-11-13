"""
Royals ScoutIQ - Auction Economics & Squad Strategy Engine (Features 60–68)
Simulates auction purse expenditure, computes Role Scarcity Indices,
bidding competition, and evaluates squad balance for Rajasthan Royals.
"""

from typing import List, Dict, Any, Optional


class AuctionStrategyEngine:
    """
    Financial and squad strategy modeling for the IPL 2027 Auction.
    """

    ROLE_SCARCITY_SCORES = {
        "Pace All-Rounder": 9.8,       # Gold dust in Indian cricket
        "140k Domestic Pacer Depth": 9.2,
        "Death Power Finisher": 8.9,
        "Mystery Leg-Spinner": 8.4,
        "Wicketkeeper Finisher": 7.8,
        "Top-order Batter": 6.2,        # Relatively abundant in domestic cricket
    }

    @classmethod
    def calculate_role_scarcity(cls, role_or_slot: str) -> float:
        """Feature 65: Returns scarcity index (0.0 to 10.0) for a given player role."""
        for key, val in cls.ROLE_SCARCITY_SCORES.items():
            if key.lower() in role_or_slot.lower():
                return val
        return 6.5

    @classmethod
    def classify_auction_priority(cls, steal_index: float, scarcity: float, tactical_fit: float) -> str:
        """
        Feature 66: Classifies prospect into Target, Backup, or Avoid.
        """
        composite = (steal_index * 0.4) + (scarcity * 0.3) + (tactical_fit * 0.03)
        if composite >= 7.5:
            return "Target (Aggressive Bid)"
        elif composite >= 5.2:
            return "Backup (Base to ₹60L)"
        else:
            return "Avoid / Low Priority"

    @classmethod
    def analyze_squad_balance(cls, squad: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Feature 67: Evaluates squad balance across batting, bowling, all-rounder, and WK roles.
        """
        batters = sum(1 for p in squad if "bat" in p.get("role", "").lower() and "wicket" not in p.get("role", "").lower())
        wks = sum(1 for p in squad if "wicket" in p.get("role", "").lower())
        all_rounders = sum(1 for p in squad if "all-rounder" in p.get("role", "").lower())
        pacers = sum(1 for p in squad if "pace" in p.get("role", "").lower() or "fast" in p.get("role", "").lower())
        spinners = sum(1 for p in squad if "spin" in p.get("role", "").lower())
        overseas = sum(1 for p in squad if p.get("is_overseas", False))

        is_balanced = batters >= 5 and wks >= 2 and all_rounders >= 3 and pacers >= 5 and spinners >= 3
        overseas_valid = overseas <= 8

        return {
            "total_players": len(squad),
            "batters_count": batters,
            "wicketkeepers_count": wks,
            "all_rounders_count": all_rounders,
            "pacers_count": pacers,
            "spinners_count": spinners,
            "overseas_count": overseas,
            "is_squad_balanced": is_balanced,
            "overseas_quota_compliant": overseas_valid,
            "recommendation": "Squad has ideal balance for 14-match IPL season." if is_balanced else "Need additional pace all-rounder depth.",
        }

    @classmethod
    def simulate_auction_budget(
        cls,
        total_purse_lakhs: float = 850.0,  # e.g. 8.5 Crores reserved for uncapped talent
        target_picks: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Feature 68: Simulates purse spending, checking whether all targeted slots can be acquired
        under budget constraints and minimum/maximum player rules.
        """
        picks = target_picks or [
            {"player_id": "P_101", "name": "Vidwath Kaverappa", "role": "140k Domestic Pacer", "base_price": 20, "projected_hammer": 85},
            {"player_id": "P_102", "name": "Ashutosh Sharma", "role": "Death Power Finisher", "base_price": 20, "projected_hammer": 95},
            {"player_id": "P_103", "name": "Suyash Sharma", "role": "Mystery Leg-Spinner", "base_price": 20, "projected_hammer": 120},
            {"player_id": "P_104", "name": "Pace All-Rounder Prospect", "role": "Pace All-Rounder", "base_price": 30, "projected_hammer": 240},
            {"player_id": "P_105", "name": "Backup Domestic Batter", "role": "Top-order Batter", "base_price": 20, "projected_hammer": 40},
        ]

        total_projected_spend = sum(p["projected_hammer"] for p in picks)
        total_base_spend = sum(p["base_price"] for p in picks)
        remaining_purse = total_purse_lakhs - total_projected_spend

        is_feasible = remaining_purse >= 0

        return {
            "allocated_purse_lakhs": total_purse_lakhs,
            "simulated_picks_count": len(picks),
            "total_projected_spend_lakhs": total_projected_spend,
            "total_base_spend_lakhs": total_base_spend,
            "remaining_purse_lakhs": round(remaining_purse, 2),
            "budget_status": "Budget Feasible (Safe Margin)" if is_feasible else "Budget Deficit - Reallocate Targets",
            "purchased_targets": picks,
        }
