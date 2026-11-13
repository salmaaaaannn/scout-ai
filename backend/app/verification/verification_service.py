"""
Royals ScoutIQ - Human-in-the-Loop Analyst Verification Service (Features 41–47)
Provides the verification queue where franchise scouts & analysts
Confirm (1.0), Correct, or Reject (0.0) AI-generated video and scouting observations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import os
import json

try:
    from app.database.db import save_verification_item, update_verification_status
except Exception:
    save_verification_item = None
    update_verification_status = None


class VerificationStatus:
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CORRECTED = "CORRECTED"
    REJECTED = "REJECTED"


class AnalystVerificationService:
    """
    In-memory and file-backed verification store maintaining verified player features.
    """

    def __init__(self, store_path: Optional[str] = None):
        self.store_path = store_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "data", "processed", "verified_observations.json"
        )
        self.queue: Dict[str, Dict[str, Any]] = {}
        self._load_store()

    def _load_store(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    self.queue = json.load(f)
            except Exception:
                self.queue = {}

    def _save_store(self):
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self.queue, f, indent=2)

    def enqueue_observation(
        self,
        obs_id: str,
        player_id: str,
        player_name: str,
        video_id: str,
        timestamp_seconds: float,
        ai_observation: str,
        raw_confidence: float = 0.65,
    ) -> Dict[str, Any]:
        """Adds a newly extracted video observation to the pending verification queue."""
        item = {
            "obs_id": obs_id,
            "player_id": player_id,
            "player_name": player_name,
            "video_id": video_id,
            "timestamp_seconds": timestamp_seconds,
            "original_ai_observation": ai_observation,
            "current_observation": ai_observation,
            "ai_observation": ai_observation,
            "confidence_multiplier": raw_confidence,
            "status": VerificationStatus.PENDING,
            "analyst_name": None,
            "review_notes": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "verified_at": None,
        }
        self.queue[obs_id] = item
        self._save_store()
        if save_verification_item is not None:
            try:
                save_verification_item(
                    obs_id=obs_id,
                    player_id=player_id,
                    player_name=player_name,
                    video_id=video_id,
                    timestamp_seconds=timestamp_seconds,
                    ai_observation=ai_observation,
                    raw_confidence=raw_confidence,
                    review_status=VerificationStatus.PENDING,
                    confidence_multiplier=raw_confidence,
                )
            except Exception:
                pass
        return item

    def confirm_observation(self, obs_id: str, analyst_name: str) -> Dict[str, Any]:
        """Approves the observation as franchise ground truth (multiplier = 1.0)."""
        if obs_id not in self.queue:
            raise KeyError(f"Observation {obs_id} not found in verification queue.")

        item = self.queue[obs_id]
        item["status"] = VerificationStatus.CONFIRMED
        item["analyst_name"] = analyst_name
        item["confidence_multiplier"] = 1.0
        item["verified_at"] = datetime.now(timezone.utc).isoformat()
        self._save_store()
        if update_verification_status is not None:
            try:
                update_verification_status(
                    obs_id=obs_id,
                    status=VerificationStatus.CONFIRMED,
                    analyst_name=analyst_name,
                    confidence_multiplier=1.0,
                )
            except Exception:
                pass
        return item

    def correct_observation(self, obs_id: str, analyst_name: str, corrected_text: str, notes: str = "") -> Dict[str, Any]:
        """Modifies inaccurate AI predictions and records human correction."""
        if obs_id not in self.queue:
            raise KeyError(f"Observation {obs_id} not found in verification queue.")

        item = self.queue[obs_id]
        item["status"] = VerificationStatus.CORRECTED
        item["analyst_name"] = analyst_name
        item["current_observation"] = corrected_text
        item["ai_observation"] = corrected_text
        item["review_notes"] = notes
        item["confidence_multiplier"] = 1.0
        item["verified_at"] = datetime.now(timezone.utc).isoformat()
        self._save_store()
        if update_verification_status is not None:
            try:
                update_verification_status(
                    obs_id=obs_id,
                    status=VerificationStatus.CORRECTED,
                    analyst_name=analyst_name,
                    confidence_multiplier=1.0,
                    corrected_observation=corrected_text,
                )
            except Exception:
                pass
        return item

    def reject_observation(self, obs_id: str, analyst_name: str, reason: str = "") -> Dict[str, Any]:
        """Rejects the observation, setting multiplier to 0.0 to exclude it from RAG synthesis."""
        if obs_id not in self.queue:
            raise KeyError(f"Observation {obs_id} not found in verification queue.")

        item = self.queue[obs_id]
        item["status"] = VerificationStatus.REJECTED
        item["analyst_name"] = analyst_name
        item["review_notes"] = reason
        item["confidence_multiplier"] = 0.0
        item["verified_at"] = datetime.now(timezone.utc).isoformat()
        self._save_store()
        if update_verification_status is not None:
            try:
                update_verification_status(
                    obs_id=obs_id,
                    status=VerificationStatus.REJECTED,
                    analyst_name=analyst_name,
                    confidence_multiplier=0.0,
                    rejection_reason=reason,
                )
            except Exception:
                pass
        return item

    def get_pending_queue(self) -> List[Dict[str, Any]]:
        """Returns all observations awaiting analyst sign-off."""
        return [item for item in self.queue.values() if item["status"] == VerificationStatus.PENDING]

    def get_verified_knowledge_for_rag(self, player_id: str) -> List[Dict[str, Any]]:
        """Returns only confirmed and corrected observations for safe, hallucination-free RAG."""
        return [
            item
            for item in self.queue.values()
            if item["player_id"] == player_id
            and item["status"] in (VerificationStatus.CONFIRMED, VerificationStatus.CORRECTED)
        ]
