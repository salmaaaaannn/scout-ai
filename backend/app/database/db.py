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
    seed_shortlisted_players()


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


# ---------------------------------------------------------------------------
# Player and Scenario Persistence & Seeding
# ---------------------------------------------------------------------------

SHORTLISTED_20_PLAYERS = [
    # Top 10 Batters
    {
        "player_id": "37052",
        "full_name": "Naman Dhir",
        "dob": "1999-12-31",
        "age": 25.0,
        "role": "Top-Order Batter",
        "batting_style": "Right-hand bat",
        "bowling_style": "Right-arm off-break",
        "state_team": "Punjab / Mumbai Indians",
        "is_uncapped": 1,
        "eligibility_status": "ELIGIBLE_UNCAPPED",
    },
    {
        "player_id": "4369",
        "full_name": "Shai Hope",
        "dob": "1993-11-10",
        "age": 31.0,
        "role": "Wicketkeeper-Batter",
        "batting_style": "Right-hand bat",
        "bowling_style": "None",
        "state_team": "West Indies / Delhi Capitals",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
    {
        "player_id": "4853",
        "full_name": "Glenn Phillips",
        "dob": "1996-12-06",
        "age": 28.0,
        "role": "Middle-Order Finisher / WK",
        "batting_style": "Right-hand bat",
        "bowling_style": "Right-arm off-break",
        "state_team": "New Zealand / Gujarat Titans",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
    {
        "player_id": "4106",
        "full_name": "Daryl Mitchell",
        "dob": "1991-05-20",
        "age": 33.0,
        "role": "Middle-Order Anchor / Pace AR",
        "batting_style": "Right-hand bat",
        "bowling_style": "Right-arm medium",
        "state_team": "New Zealand / Chennai Super Kings",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
    {
        "player_id": "2984",
        "full_name": "Sikandar Raza",
        "dob": "1986-04-24",
        "age": 38.0,
        "role": "Spin-Bowling All-Rounder",
        "batting_style": "Right-hand bat",
        "bowling_style": "Right-arm off-break",
        "state_team": "Zimbabwe / Punjab Kings",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
    {
        "player_id": "6931",
        "full_name": "Pathum Nissanka",
        "dob": "1998-05-18",
        "age": 26.0,
        "role": "Top-Order Anchor",
        "batting_style": "Right-hand bat",
        "bowling_style": "None",
        "state_team": "Sri Lanka / Delhi Capitals",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
    {
        "player_id": "2860",
        "full_name": "KS Bharat",
        "dob": "1993-10-03",
        "age": 31.0,
        "role": "Wicketkeeper-Batter",
        "batting_style": "Right-hand bat",
        "bowling_style": "None",
        "state_team": "Andhra / Kolkata Knight Riders",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_CAPPED",
    },
    {
        "player_id": "3645",
        "full_name": "Sarfaraz Khan",
        "dob": "1997-10-22",
        "age": 27.0,
        "role": "Middle-Order Batter",
        "batting_style": "Right-hand bat",
        "bowling_style": "Right-arm leg-break",
        "state_team": "Mumbai / Delhi Capitals",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_CAPPED",
    },
    {
        "player_id": "23311",
        "full_name": "Jacob Bethell",
        "dob": "2003-10-23",
        "age": 21.0,
        "role": "Explosive Pace Finisher / SLA",
        "batting_style": "Left-hand bat",
        "bowling_style": "Slow left-arm orthodox",
        "state_team": "England / Royal Challengers Bengaluru",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
    {
        "player_id": "2416",
        "full_name": "Kyle Mayers",
        "dob": "1992-09-08",
        "age": 32.0,
        "role": "Opening Power-Hitter / Medium",
        "batting_style": "Left-hand bat",
        "bowling_style": "Right-arm medium",
        "state_team": "West Indies / Lucknow Super Giants",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
    # Top 10 Bowlers
    {
        "player_id": "479",
        "full_name": "Adil Rashid",
        "dob": "1988-02-17",
        "age": 36.0,
        "role": "Elite Wrist Spinner",
        "batting_style": "Right-hand bat",
        "bowling_style": "Right-arm legbreak",
        "state_team": "England / Sunrisers Hyderabad",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
    {
        "player_id": "6450",
        "full_name": "Mujeeb Ur Rahman",
        "dob": "2001-03-28",
        "age": 23.0,
        "role": "Mystery Off-Spinner",
        "batting_style": "Right-hand bat",
        "bowling_style": "Right-arm offbreak",
        "state_team": "Afghanistan / Mumbai Indians",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
    {
        "player_id": "8661",
        "full_name": "Matheesha Pathirana",
        "dob": "2002-12-18",
        "age": 22.0,
        "role": "Sling Death Pacer",
        "batting_style": "Right-hand bat",
        "bowling_style": "Right-arm fast",
        "state_team": "Sri Lanka / Kolkata Knight Riders",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
    {
        "player_id": "3697",
        "full_name": "Kyle Jamieson",
        "dob": "1994-12-30",
        "age": 30.0,
        "role": "Tall Bounce Express Pacer",
        "batting_style": "Right-hand bat",
        "bowling_style": "Right-arm fast-medium",
        "state_team": "New Zealand / Delhi Capitals",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
    {
        "player_id": "6286",
        "full_name": "Shivam Mavi",
        "dob": "1998-11-26",
        "age": 26.0,
        "role": "Domestic Powerplay / Death Pacer",
        "batting_style": "Right-hand bat",
        "bowling_style": "Right-arm fast-medium",
        "state_team": "Uttar Pradesh / Sunrisers Hyderabad",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_CAPPED",
    },
    {
        "player_id": "3469",
        "full_name": "Shreyas Gopal",
        "dob": "1993-09-04",
        "age": 31.0,
        "role": "Domestic Leg-Spin Specialist",
        "batting_style": "Right-hand bat",
        "bowling_style": "Right-arm legbreak",
        "state_team": "Karnataka / Mumbai Indians",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_CAPPED",
    },
    {
        "player_id": "4101",
        "full_name": "Mitchell Santner",
        "dob": "1992-02-05",
        "age": 32.0,
        "role": "Economy Finger Spinner",
        "batting_style": "Left-hand bat",
        "bowling_style": "Slow left-arm orthodox",
        "state_team": "New Zealand / Mumbai Indians",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
    {
        "player_id": "22471",
        "full_name": "Matthew Humphreys",
        "dob": "2002-09-28",
        "age": 22.0,
        "role": "Emerging Left-Arm Finger Spinner",
        "batting_style": "Right-hand bat",
        "bowling_style": "Slow left-arm orthodox",
        "state_team": "Ireland",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
    {
        "player_id": "25048",
        "full_name": "Umran Malik",
        "dob": "1999-11-22",
        "age": 25.0,
        "role": "150+ kph Express Pacer",
        "batting_style": "Right-hand bat",
        "bowling_style": "Right-arm fast",
        "state_team": "Jammu & Kashmir / Sunrisers Hyderabad",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_CAPPED",
    },
    {
        "player_id": "6643",
        "full_name": "Hasan Mahmud",
        "dob": "1999-09-24",
        "age": 25.0,
        "role": "Death Overs Yorker Specialist",
        "batting_style": "Right-hand bat",
        "bowling_style": "Right-arm fast-medium",
        "state_team": "Bangladesh",
        "is_uncapped": 0,
        "eligibility_status": "ELIGIBLE_OVERSEAS",
    },
]


def save_player(
    player_id: str,
    full_name: str,
    dob: Optional[str] = None,
    age: Optional[float] = None,
    role: Optional[str] = None,
    batting_style: Optional[str] = None,
    bowling_style: Optional[str] = None,
    state_team: Optional[str] = None,
    is_uncapped: int = 1,
    eligibility_status: str = "ELIGIBLE_UNCAPPED",
) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO players (
            player_id, full_name, dob, age, role,
            batting_style, bowling_style, state_team,
            is_uncapped, eligibility_status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_id, full_name, dob, age, role,
            batting_style, bowling_style, state_team,
            is_uncapped, eligibility_status, datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
    return {
        "player_id": player_id,
        "full_name": full_name,
        "dob": dob,
        "age": age,
        "role": role,
        "batting_style": batting_style,
        "bowling_style": bowling_style,
        "state_team": state_team,
        "is_uncapped": is_uncapped,
        "eligibility_status": eligibility_status,
    }


def get_player(player_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_players() -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players ORDER BY full_name ASC")
        return [dict(r) for r in cursor.fetchall()]


def seed_shortlisted_players():
    """Seeds the 20 approved shortlisted players into the database if missing."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM players")
        count = cursor.fetchone()["cnt"]
        if count < 20:
            for p in SHORTLISTED_20_PLAYERS:
                cursor.execute("""
                INSERT OR REPLACE INTO players (
                    player_id, full_name, dob, age, role,
                    batting_style, bowling_style, state_team,
                    is_uncapped, eligibility_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    p["player_id"], p["full_name"], p.get("dob"), p.get("age"),
                    p.get("role"), p.get("batting_style"), p.get("bowling_style"),
                    p.get("state_team"), p.get("is_uncapped", 1),
                    p.get("eligibility_status", "ELIGIBLE_UNCAPPED"),
                    datetime.now(timezone.utc).isoformat()
                ))
            conn.commit()
            logger.info("Successfully seeded 20 shortlisted players into ScoutIQ persistent database.")


def save_playing_xi_scenario(
    opponent: str,
    venue: str,
    pitch_type: str,
    scenario_type: str,
    selected_xi: List[Dict[str, Any]],
    impact_player: Dict[str, Any],
    team_rating: float,
) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO playing_xi_scenarios (
            opponent, venue, pitch_type, scenario_type,
            selected_xi_json, impact_player_json, team_rating, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            opponent, venue, pitch_type, scenario_type,
            json.dumps(selected_xi), json.dumps(impact_player),
            team_rating, datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
        return cursor.lastrowid


def get_all_playing_xi_scenarios() -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM playing_xi_scenarios ORDER BY created_at DESC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["selected_xi"] = json.loads(d["selected_xi_json"])
            d["impact_player"] = json.loads(d["impact_player_json"])
            result.append(d)
        return result

