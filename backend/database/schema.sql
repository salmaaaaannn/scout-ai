-- ==============================================================================
-- Royals ScoutIQ Database Schema
-- Targets: PostgreSQL 16 + pgvector Extension
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Core Player Registry
CREATE TABLE IF NOT EXISTS players (
    player_id VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    dob DATE,
    age INT,
    is_uncapped BOOLEAN DEFAULT TRUE,
    batting_hand VARCHAR(20),       -- 'Right-hand bat', 'Left-hand bat'
    bowling_style VARCHAR(50),      -- 'Right-arm fast', 'Slow left-arm orthodox', etc.
    primary_role VARCHAR(50),       -- 'Top-order Batter', 'Finisher', 'Pace Bowler', 'All-Rounder'
    state_team VARCHAR(50),
    competition_tier VARCHAR(20) DEFAULT 'Elite', -- 'Elite' (Ranji/SMAT Elite), 'Plate'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Phase-Wise Ball-by-Ball Analytics
CREATE TABLE IF NOT EXISTS player_phase_stats (
    stat_id SERIAL PRIMARY KEY,
    player_id VARCHAR(50) REFERENCES players(player_id) ON DELETE CASCADE,
    season INT,
    phase VARCHAR(20) NOT NULL,     -- 'Powerplay', 'Middle', 'Death'
    balls_faced INT DEFAULT 0,
    runs_scored INT DEFAULT 0,
    balls_bowled INT DEFAULT 0,
    runs_conceded INT DEFAULT 0,
    wickets INT DEFAULT 0,
    dot_balls INT DEFAULT 0,
    boundaries_hit INT DEFAULT 0,
    true_strike_rate FLOAT DEFAULT 0.0,         -- Context-normalized TSR
    true_economy_rate FLOAT DEFAULT 0.0,        -- Context-normalized TER
    sample_confidence_weight FLOAT DEFAULT 1.0, -- Bayesian shrinkage factor
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Auction Strategy, Purse & Valuations
CREATE TABLE IF NOT EXISTS auction_valuations (
    valuation_id SERIAL PRIMARY KEY,
    player_id VARCHAR(50) REFERENCES players(player_id) ON DELETE CASCADE,
    auction_year INT DEFAULT 2027,
    base_price_lakhs INT DEFAULT 20,
    projected_hammer_lakhs INT DEFAULT 20,
    rr_slot_priority VARCHAR(50),   -- '140k Pacer', 'Death Finisher', 'Mystery Spin', 'Pace All-Rounder'
    rr_tactical_fit_score FLOAT DEFAULT 0.0,    -- 0.0 to 100.0
    steal_index FLOAT DEFAULT 0.0,              -- WAR / Cost ratio
    auction_tier VARCHAR(20) DEFAULT 'Target',  -- 'Target', 'Backup', 'Avoid'
    analyst_notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Computer Vision Video Assets
CREATE TABLE IF NOT EXISTS video_assets (
    video_id VARCHAR(50) PRIMARY KEY,
    player_id VARCHAR(50) REFERENCES players(player_id) ON DELETE CASCADE,
    video_url TEXT NOT NULL,
    source_match VARCHAR(100),
    video_type VARCHAR(50),         -- 'Match Broadcast', 'Net Session'
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Biomechanical Telemetry Records (RoyalVision CV)
CREATE TABLE IF NOT EXISTS cv_biomechanical_records (
    bio_id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) REFERENCES video_assets(video_id) ON DELETE CASCADE,
    player_id VARCHAR(50) REFERENCES players(player_id) ON DELETE CASCADE,
    timestamp_seconds FLOAT NOT NULL,
    head_stillness_score FLOAT,     -- 0.0 to 1.0 (drift in release window)
    bat_speed_proxy FLOAT,          -- rad/s downswing angular velocity
    swing_plane_angle FLOAT,        -- degrees
    trigger_latency_ms FLOAT,       -- milliseconds from bowler foot strike to weight transfer
    release_height_ratio FLOAT,     -- release_height / body_height
    arm_release_angle FLOAT,        -- degrees from vertical
    injury_stress_index FLOAT,      -- 0.0 (safe) to 1.0 (high lateral trunk flexion / mixed action)
    raw_keypoints_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Human-In-The-Loop Verification Queue
CREATE TABLE IF NOT EXISTS analyst_verifications (
    verification_id SERIAL PRIMARY KEY,
    bio_id INT REFERENCES cv_biomechanical_records(bio_id) ON DELETE CASCADE,
    analyst_name VARCHAR(100) NOT NULL,
    review_status VARCHAR(20) DEFAULT 'PENDING', -- 'CONFIRMED', 'CORRECTED', 'REJECTED'
    confidence_multiplier FLOAT DEFAULT 0.65,    -- 1.0 if confirmed, 0.0 if rejected
    corrected_observation TEXT,
    verified_at TIMESTAMP
);

-- 7. Grounded Knowledge Chunks for Gemini Hybrid RAG
CREATE TABLE IF NOT EXISTS scouting_knowledge_chunks (
    chunk_id SERIAL PRIMARY KEY,
    player_id VARCHAR(50) REFERENCES players(player_id) ON DELETE CASCADE,
    chunk_type VARCHAR(50) NOT NULL,             -- 'Scout Note', 'CV Observation', 'Tactical Brief'
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(768)                        -- Gemini Embedding 2 dimension
);

-- 8. Matchday Starting XI & Impact Player Optimization Records
CREATE TABLE IF NOT EXISTS team_selections (
    selection_id SERIAL PRIMARY KEY,
    opponent VARCHAR(100) NOT NULL,
    venue VARCHAR(100) NOT NULL,
    pitch_type VARCHAR(50),                      -- 'Spin-Friendly', 'Pace-Friendly', 'Flat Track'
    starting_xi JSONB NOT NULL,                  -- List of 11 player IDs and roles
    impact_player_candidate VARCHAR(50) REFERENCES players(player_id),
    scenario VARCHAR(50),                        -- 'Batting First', 'Bowling First'
    gemini_tactical_brief TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_players_uncapped_age ON players(is_uncapped, age);
CREATE INDEX IF NOT EXISTS idx_phase_stats_player ON player_phase_stats(player_id, phase);
CREATE INDEX IF NOT EXISTS idx_auction_steal ON auction_valuations(steal_index DESC);

-- ==============================================================================
-- 9. Phase 1: Round 1 Candidate Verification Registry (Protocol v1.1)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS candidate_verification_registry (
    candidate_id VARCHAR(50) PRIMARY KEY,
    unstop_name VARCHAR(150) NOT NULL,
    verified_name VARCHAR(150),
    name_status VARCHAR(50) DEFAULT 'PENDING',  -- 'VERIFIED', 'PENDING', 'PENDING_DISAMBIGUATION', 'REJECTED'
    original_entry_indices INT[] NOT NULL,
    dob DATE,
    dob_precision VARCHAR(20),                   -- 'FULL_DATE', 'YEAR_MONTH_ONLY', 'YEAR_ONLY'
    dob_verification_status VARCHAR(30) DEFAULT 'PENDING',
    country VARCHAR(50) DEFAULT 'India',
    is_indian_domestic BOOLEAN DEFAULT TRUE,
    is_overseas BOOLEAN DEFAULT FALSE,
    senior_capped_status VARCHAR(30) DEFAULT 'PENDING',  -- 'NONE_CONFIRMED', 'CAPPED', 'PENDING'
    senior_india_appearances INT DEFAULT 0,
    bcci_contract_status VARCHAR(30) DEFAULT 'PENDING',
    u19_india_a_representation TEXT,
    role VARCHAR(50),
    batting_hand VARCHAR(30),
    bowling_style VARCHAR(50),
    state_team VARCHAR(50),
    eligibility_status VARCHAR(40) DEFAULT 'PENDING_VERIFICATION', -- 'ELIGIBLE_UNCAPPED', 'PENDING_VERIFICATION', 'EXCLUDED_CAPPED', 'EXCLUDED_OVERSEAS'
    eligibility_reason TEXT,
    overall_verification_status VARCHAR(40) DEFAULT 'PENDING_VERIFICATION',
    checked_by VARCHAR(100),
    checked_on DATE,
    review_notes TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidate_evidence (
    evidence_id SERIAL PRIMARY KEY,
    candidate_id VARCHAR(50) REFERENCES candidate_verification_registry(candidate_id) ON DELETE CASCADE,
    claim VARCHAR(100) NOT NULL,
    value_supported TEXT NOT NULL,
    source_title VARCHAR(200) NOT NULL,
    publisher VARCHAR(150) NOT NULL,
    source_url TEXT NOT NULL,
    source_type VARCHAR(50) DEFAULT 'OFFICIAL_PROFILE', -- 'OFFICIAL_RECORD', 'COMPETITION_PACK', 'OFFICIAL_PROFILE', 'TOURNAMENT_SITE', 'NEWS_LEAD'
    retrieved_on DATE NOT NULL,
    checked_by VARCHAR(100) NOT NULL,
    verification_status VARCHAR(30) DEFAULT 'VERIFIED',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidate_age_calculations (
    calc_id SERIAL PRIMARY KEY,
    candidate_id VARCHAR(50) REFERENCES candidate_verification_registry(candidate_id) ON DELETE CASCADE,
    reference_date DATE NOT NULL,                -- 2026-11-08 or 2027-04-01
    cutoff_label VARCHAR(50) NOT NULL,           -- 'Primary (Nov 8, 2026)' or 'Secondary (Apr 1, 2027)'
    years INT NOT NULL,
    months INT NOT NULL,
    days INT NOT NULL,
    total_days INT NOT NULL,
    calculation_status VARCHAR(30) DEFAULT 'CALCULATED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scouting_shortlists (
    shortlist_id SERIAL PRIMARY KEY,
    list_type VARCHAR(50) NOT NULL,              -- 'List A (Absolute Youngest 10)', 'List B (Role-Balanced)'
    candidate_id VARCHAR(50) REFERENCES candidate_verification_registry(candidate_id) ON DELETE CASCADE,
    rank_order INT NOT NULL,
    age_in_total_days INT NOT NULL,
    selection_rationale TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_candidate_eligibility ON candidate_verification_registry(eligibility_status);
CREATE INDEX IF NOT EXISTS idx_candidate_age_total_days ON candidate_age_calculations(reference_date, total_days ASC);

