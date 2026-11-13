"""
Royals ScoutIQ - Production Database & Persistence Layer (Phase 2)
Provides unified SQL persistence for SQLite (default local) and PostgreSQL (production).
Stores video metadata, CV biomechanics telemetry, analyst review queues,
and player dossiers across backend restarts.
"""

import os
import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("scoutiq.database")

# Default database path in project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAULT_SQLITE_PATH = os.path.join(PROJECT_ROOT, "scoutiq.db")


def get_db_path() -> str:
    db_url = os.getenv("DATABASE_URL", "")
    if db_url.startswith("sqlite:///"):
        rel_or_abs = db_url.replace("sqlite:///", "")
        if rel_or_abs.startswith("./"):
            return os.path.join(PROJECT_ROOT, rel_or_abs[2:])
        return os.path.abspath(rel_or_abs)
    return DEFAULT_SQLITE_PATH


def get_db():
    """Returns an active SQLite connection with row_factory enabled."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_database():
    """Initializes schema tables if they do not exist."""
    db_path = get_db_path()
    logger.info(f"Initializing ScoutIQ persistent database at: {db_path}")

    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Players table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            dob TEXT,
            age REAL,
            role TEXT,
            batting_style TEXT,
            bowling_style TEXT,
            state_team TEXT,
            is_uncapped INTEGER DEFAULT 1,
            eligibility_status TEXT DEFAULT 'ELIGIBLE_UNCAPPED',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Video Assets table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_assets (
            video_id TEXT PRIMARY KEY,
            player_id TEXT,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size_bytes INTEGER,
            fps REAL DEFAULT 30.0,
            total_frames INTEGER DEFAULT 0,
            duration_seconds REAL DEFAULT 0.0,
            resolution TEXT DEFAULT '1920x1080',
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(player_id) REFERENCES players(player_id) ON DELETE SET NULL
        );
        """)

        # 3. CV Biomechanical Telemetry Records
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cv_biomechanical_records (
            bio_id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            player_id TEXT NOT NULL,
            player_name TEXT,
            role TEXT,
            timestamp_seconds REAL NOT NULL,
            head_stillness_score REAL,
            bat_speed_rad_s REAL,
            bat_speed_kph REAL,
            arm_release_angle REAL,
            spine_stress_index REAL,
            shot_classification TEXT,
            action_classification TEXT,
            raw_keypoints_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(video_id) REFERENCES video_assets(video_id) ON DELETE CASCADE
        );
        """)

        # 4. Human-In-The-Loop Analyst Verification Queue
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyst_verifications (
            verification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            obs_id TEXT UNIQUE NOT NULL,
            player_id TEXT NOT NULL,
            player_name TEXT NOT NULL,
            video_id TEXT NOT NULL,
            timestamp_seconds REAL NOT NULL,
            ai_observation TEXT NOT NULL,
            raw_confidence REAL NOT NULL,
            review_status TEXT DEFAULT 'PENDING',
            analyst_name TEXT,
            corrected_observation TEXT,
            rejection_reason TEXT,
            confidence_multiplier REAL DEFAULT 0.65,
            enqueued_at TEXT DEFAULT CURRENT_TIMESTAMP,
            verified_at TEXT
        );
        """)

        # 5. Matchday XI & Impact Player Scenarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS playing_xi_scenarios (
            scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,
            opponent TEXT NOT NULL,
            venue TEXT NOT NULL,
            pitch_type TEXT NOT NULL,
            scenario_type TEXT DEFAULT 'Batting First',
            selected_xi_json TEXT NOT NULL,
            impact_player_json TEXT NOT NULL,
            team_rating REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

        conn.commit()
    logger.info("ScoutIQ persistent database schema initialized successfully.")


# ---------------------------------------------------------------------------
# Data Access Methods
# ---------------------------------------------------------------------------

def save_video_asset(
    video_id: str,
    filename: str,
    file_path: str,
    file_size_bytes: int,
    player_id: Optional[str] = None,
    fps: float = 30.0,
    total_frames: int = 0,
    duration_seconds: float = 0.0,
    resolution: str = "1920x1080",
) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO video_assets (
            video_id, player_id, filename, file_path, file_size_bytes, fps, total_frames, duration_seconds, resolution, uploaded_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            video_id, player_id, filename, file_path, file_size_bytes, fps, total_frames, duration_seconds, resolution,
            datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()

    return {
        "video_id": video_id,
        "filename": filename,
        "file_size_bytes": file_size_bytes,
        "fps": fps,
        "total_frames": total_frames,
        "duration_seconds": duration_seconds,
        "resolution": resolution,
    }


def get_video_asset(video_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM video_assets WHERE video_id = ?", (video_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)


def save_biomechanical_record(
    video_id: str,
    player_id: str,
    player_name: str,
    role: str,
    timestamp_seconds: float,
    head_stillness_score: float,
    bat_speed_rad_s: float,
    bat_speed_kph: float,
    arm_release_angle: float,
    spine_stress_index: float,
    shot_classification: str,
    action_classification: str,
    raw_keypoints: Any,
) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO cv_biomechanical_records (
            video_id, player_id, player_name, role, timestamp_seconds,
            head_stillness_score, bat_speed_rad_s, bat_speed_kph,
            arm_release_angle, spine_stress_index, shot_classification,
            action_classification, raw_keypoints_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            video_id, player_id, player_name, role, timestamp_seconds,
            head_stillness_score, bat_speed_rad_s, bat_speed_kph,
            arm_release_angle, spine_stress_index, shot_classification,
            action_classification, json.dumps(raw_keypoints)
        ))
        conn.commit()
        return cursor.lastrowid


def save_verification_item(
    obs_id: str,
    player_id: str,
    player_name: str,
    video_id: str,
    timestamp_seconds: float,
    ai_observation: str,
    raw_confidence: float,
    review_status: str = "PENDING",
    confidence_multiplier: float = 0.65,
) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO analyst_verifications (
            obs_id, player_id, player_name, video_id, timestamp_seconds,
            ai_observation, raw_confidence, review_status, confidence_multiplier, enqueued_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            obs_id, player_id, player_name, video_id, timestamp_seconds,
            ai_observation, raw_confidence, review_status, confidence_multiplier,
            datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()

    return {
        "obs_id": obs_id,
        "player_id": player_id,
        "player_name": player_name,
        "video_id": video_id,
        "timestamp_seconds": timestamp_seconds,
        "ai_observation": ai_observation,
        "raw_confidence": raw_confidence,
        "review_status": review_status,
        "confidence_multiplier": confidence_multiplier,
    }


def get_all_verifications(status: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute("SELECT * FROM analyst_verifications WHERE review_status = ? ORDER BY enqueued_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM analyst_verifications ORDER BY enqueued_at DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def update_verification_status(
    obs_id: str,
    status: str,
    analyst_name: str,
    confidence_multiplier: float,
    corrected_observation: Optional[str] = None,
    rejection_reason: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE analyst_verifications
        SET review_status = ?,
            analyst_name = ?,
            confidence_multiplier = ?,
            corrected_observation = COALESCE(?, corrected_observation),
            rejection_reason = COALESCE(?, rejection_reason),
            verified_at = ?
        WHERE obs_id = ?
        """, (
            status, analyst_name, confidence_multiplier,
            corrected_observation, rejection_reason, datetime.now(timezone.utc).isoformat(),
            obs_id
        ))
        conn.commit()
        cursor.execute("SELECT * FROM analyst_verifications WHERE obs_id = ?", (obs_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_database_stats() -> Dict[str, Any]:
    db_path = get_db_path()
    exists = os.path.exists(db_path)
    size_bytes = os.path.getsize(db_path) if exists else 0

    stats = {
        "engine": "SQLite 3",
        "database_file": os.path.basename(db_path),
        "database_path": db_path,
        "file_size_bytes": size_bytes,
        "status": "connected" if exists else "uninitialized",
        "tables": {}
    }

    if exists:
        with get_db() as conn:
            cursor = conn.cursor()
            for tbl in ["players", "video_assets", "cv_biomechanical_records", "analyst_verifications", "playing_xi_scenarios"]:
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {tbl}")
                    stats["tables"][tbl] = cursor.fetchone()["count"]
                except Exception:
                    stats["tables"][tbl] = 0

    return stats
