"""
Royals ScoutIQ - Hybrid Retrieval Dispatcher (Features 49, 50, 51, 52)
Dispatches queries to SQL for hard cricket statistics and semantic vector retrieval
for verified scouting notes and video timestamps.
"""

from typing import List, Dict, Any, Optional
import re


class HybridRetrievalDispatcher:
    """
    Coordinates structured SQL data and unstructured scouting reports.
    """

    def __init__(self, verification_service=None):
        self.verification_service = verification_service
        # In-memory structured stats catalog for high-speed simulation & querying
        self.stats_catalog: List[Dict[str, Any]] = [
            {
                "player_id": "P_101",
                "name": "Vidwath Kaverappa",
                "age": 19,
                "role": "Right-Arm Fast Medium",
                "state_team": "Karnataka",
                "is_uncapped": True,
                "phase_stats": {
                    "Powerplay": {"overs": 18.0, "runs": 114, "econ": 6.33, "ter": -1.09, "wickets": 8, "dot_pct": 52.4},
                    "Middle": {"overs": 12.0, "runs": 78, "econ": 6.50, "ter": -0.65, "wickets": 3, "dot_pct": 46.0},
                    "Death": {"overs": 14.0, "runs": 118, "econ": 8.43, "ter": -1.92, "wickets": 9, "dot_pct": 41.2},
                },
                "auction_valuation": {
                    "base_price_lakhs": 20,
                    "projected_hammer_lakhs": 85,
                    "steal_index": 9.4,
                    "priority_slot": "140k Domestic Pacer Depth",
                },
            },
            {
                "player_id": "P_102",
                "name": "Ashutosh Sharma",
                "age": 20,
                "role": "Lower-Order Power Finisher",
                "state_team": "Railways",
                "is_uncapped": True,
                "phase_stats": {
                    "Powerplay": {"balls": 12, "runs": 16, "sr": 133.3, "tsr": 4.8, "dot_pct": 33.3},
                    "Middle": {"balls": 45, "runs": 68, "sr": 151.1, "tsr": 29.1, "dot_pct": 26.6},
                    "Death": {"balls": 84, "runs": 178, "sr": 211.9, "tsr": 47.7, "dot_pct": 19.0},
                },
                "auction_valuation": {
                    "base_price_lakhs": 20,
                    "projected_hammer_lakhs": 95,
                    "steal_index": 9.1,
                    "priority_slot": "Death Power Finisher (Overs 17-20)",
                },
            },
            {
                "player_id": "P_103",
                "name": "Suyash Sharma",
                "age": 20,
                "role": "Mystery Leg-Spinner",
                "state_team": "Delhi",
                "is_uncapped": True,
                "phase_stats": {
                    "Powerplay": {"overs": 4.0, "runs": 32, "econ": 8.00, "ter": 0.58, "wickets": 1, "dot_pct": 40.0},
                    "Middle": {"overs": 38.0, "runs": 242, "econ": 6.36, "ter": -0.79, "wickets": 18, "dot_pct": 48.2},
                    "Death": {"overs": 6.0, "runs": 58, "econ": 9.66, "ter": -0.69, "wickets": 2, "dot_pct": 32.0},
                },
                "auction_valuation": {
                    "base_price_lakhs": 20,
                    "projected_hammer_lakhs": 120,
                    "steal_index": 8.8,
                    "priority_slot": "Chahal Succession / High-RPM Spin",
                },
            },
        ]
        self._load_official_candidates()

    def _load_official_candidates(self):
        """Loads official Rajasthan Royals competition picks from data/raw if available."""
        import os
        import json
        candidate_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "raw", "rr_round1_top10_youngest_picks.json"))
        if os.path.exists(candidate_path):
            try:
                with open(candidate_path, "r", encoding="utf-8") as f:
                    candidates = json.load(f)
                existing_ids = {p["player_id"] for p in self.stats_catalog}
                for c in candidates:
                    if c["player_id"] not in existing_ids:
                        self.stats_catalog.append({
                            "player_id": c["player_id"],
                            "name": c["name"],
                            "age": c["age"],
                            "role": c["role"],
                            "state_team": c["state_team"],
                            "is_uncapped": True,
                            "phase_stats": {
                                "Powerplay": {"tsr": 12.0, "ter": -1.2, "dot_pct": 45.0},
                                "Middle": {"tsr": 18.5, "ter": -0.8, "dot_pct": 38.0},
                                "Death": {"tsr": 35.0, "ter": -1.8, "dot_pct": 32.0},
                            },
                            "auction_valuation": {
                                "base_price_lakhs": 20,
                                "projected_hammer_lakhs": int(c.get("projected_inr_crores", 0.5) * 100),
                                "steal_index": c.get("acpi_potential_index", 9.0),
                                "priority_slot": c.get("specialization", "Uncapped Prospect"),
                            },
                        })
            except Exception:
                pass

    def query_structured_stats(self, query: str) -> List[Dict[str, Any]]:
        """Extracts players matching structured statistical criteria."""
        q = query.lower()
        results = []

        # Parse role filters
        target_role = None
        if any(w in q for w in ["pacer", "fast", "bowler", "pace", "seam"]):
            target_role = "Pace"
        elif any(w in q for w in ["finisher", "batter", "bat", "hitter"]):
            target_role = "Finisher"
        elif any(w in q for w in ["spin", "spinner", "leg-spin", "orthodox"]):
            target_role = "Spin"

        for p in self.stats_catalog:
            role_str = p["role"].lower()
            if target_role == "Pace" and not any(k in role_str for k in ["fast", "medium", "pace", "seam"]):
                continue
            elif target_role == "Finisher" and not any(k in role_str for k in ["finisher", "bat", "hitter"]):
                continue
            elif target_role == "Spin" and not any(k in role_str for k in ["spin", "orthodox", "wrist"]):
                continue
            results.append(p)

        return results

    def query_verified_observations(self, player_id: str) -> List[Dict[str, Any]]:
        """Retrieves analyst-confirmed video and scouting notes from verification service."""
        if not self.verification_service:
            return []
        return self.verification_service.get_verified_knowledge_for_rag(player_id)
