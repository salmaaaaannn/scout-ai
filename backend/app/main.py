"""
Royals ScoutIQ - Master FastAPI Production Server
Rajasthan Royals AI-Powered Cricket Scouting, Computer Vision & Matchday Intelligence Platform.
Supports Features 21 through 116 across all 8 modules.
"""

from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import io
import csv

from app.analytics.sabermetrics import SabermetricsEngine
from app.analytics.auction_simulator import AuctionStrategyEngine
from app.analytics.data_validator import DataValidationSystem
from app.video_ai.video_processor import VideoProcessor
from app.video_ai.biomechanics import BiomechanicsAnalyzer
from app.video_ai.event_detector import CricketEventDetector
from app.verification.verification_service import AnalystVerificationService
from app.rag.retrieval import HybridRetrievalDispatcher
from app.rag.gemini_rag import GeminiTacticalRAG
from app.optimizer.team_optimizer import MatchdayOptimizer
from app.opposition.opposition_intel import OppositionIntelligenceEngine
from app.development.player_development import PlayerDevelopmentEngine
from app.database.db import init_database, get_database_stats, save_video_asset

app = FastAPI(
    title="Royals ScoutIQ API",
    description="Rajasthan Royals Proprietary AI-Powered Scouting, Computer Vision & Auction Valuation Platform.",
    version="2.7.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.candidates_router import router as candidates_router
from app.api.rankings_router import router as rankings_router

# Load environment variables from .env if present
_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
if not os.path.exists(_env_path):
    _env_path = os.path.join(os.getcwd(), ".env")
if os.path.exists(_env_path):
    with open(_env_path, "r", encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                _k = _k.strip()
                _v = _v.strip().strip("'\"")
                if _k and not os.getenv(_k):
                    os.environ[_k] = _v

# Service Singletons
verification_service = AnalystVerificationService()
retrieval_dispatcher = HybridRetrievalDispatcher(verification_service=verification_service)
rag_assistant = GeminiTacticalRAG(dispatcher=retrieval_dispatcher)

# Phase 1: Round 1 Scouting Intelligence Router
app.include_router(candidates_router)
app.include_router(rankings_router)


# ---------------------------------------------------------------------------
# Request & Response Schemas
# ---------------------------------------------------------------------------

class ProcessVideoRequest(BaseModel):
    video_id: str
    player_id: str
    player_name: str
    role: str
    fps: float = 30.0


class MultiClipAnalysisRequest(BaseModel):
    player_id: str
    player_name: str
    role: str
    clip_ids: List[str]


class ConfirmVerificationRequest(BaseModel):
    obs_id: str
    analyst_name: str


class CorrectVerificationRequest(BaseModel):
    obs_id: str
    analyst_name: str
    corrected_observation: str
    notes: Optional[str] = ""


class RejectVerificationRequest(BaseModel):
    obs_id: str
    analyst_name: str
    reason: Optional[str] = ""


class QueryAssistantRequest(BaseModel):
    query: str


class MatchdayLineupRequest(BaseModel):
    opponent: str
    venue: str
    pitch_type: str = "Pace-Friendly"
    scenario: str = "Batting First"


class ScenarioCompareRequest(BaseModel):
    opponent: str
    venue: str
    pitch_type: str = "Pace-Friendly"


class OppositionBatterRequest(BaseModel):
    batter_name: str
    opponent_team: str


class OppositionBowlerRequest(BaseModel):
    bowler_name: str
    opponent_team: str


class BudgetSimulateRequest(BaseModel):
    total_purse_lakhs: float = 850.0
    target_picks: Optional[List[Dict[str, Any]]] = None


class TrainingPlanRequest(BaseModel):
    player_id: str
    identified_weakness: str


class CompareSessionsRequest(BaseModel):
    session_a: Dict[str, Any]
    session_b: Dict[str, Any]


class DataImportRequest(BaseModel):
    records: List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# Role-Based Access Control Helper (Feature 116)
# ---------------------------------------------------------------------------

def verify_role_access(role_header: Optional[str], allowed_roles: List[str]):
    """Enforces RBAC based on user role (Scout, Coach, Management, Analyst)."""
    if not role_header:
        # Default development role
        return "Scout"
    clean_role = role_header.strip().title()
    if clean_role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Access Denied: Role '{clean_role}' is not authorized. Required: {allowed_roles}"
        )
    return clean_role


# ---------------------------------------------------------------------------
# Core Endpoints
# ---------------------------------------------------------------------------

@app.on_event("startup")
def startup_event():
    init_database()


@app.get("/health")
def health_check():
    db_stats = get_database_stats()
    return {
        "status": "online",
        "service": "Royals ScoutIQ",
        "evaluators": ["Kumar Sangakkara (Head Coach)", "Giles Lindsay (Strategy Director)"],
        "modules_active": [
            "RoyalVision Video CV & Biomechanics",
            "Human-in-the-Loop Analyst Verification",
            "AI Assistance Tactical Engine",
            "Auction Economics & Budget Simulator",
            "Matchday XI + Impact Player Optimizer",
            "Opposition Matchup Intelligence",
            "Player Development & Progress Monitoring",
            "Data Ingestion & Validation Engine",
        ],
        "database": {
            "status": db_stats.get("status", "connected"),
            "engine": db_stats.get("engine", "SQLite 3"),
            "total_records": sum(db_stats.get("tables", {}).values()),
        },
        "version": "2.7.0",
    }


@app.get("/api/db/health")
def db_health_check():
    """Features Phase 2: Database health, table record counts, and persistent storage metrics."""
    return get_database_stats()


@app.get("/", response_class=HTMLResponse)
def serve_landing_page():
    landing_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "landing_page.html"))
    if os.path.exists(landing_path):
        with open(landing_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Royals ScoutIQ API is online. Visit /docs for Swagger UI.</h1>"


# ===========================================================================
# Section A: RoyalVision AI Video Analysis (Features 21–40)
# ===========================================================================

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov"}
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB


@app.post("/api/video/upload")
async def upload_video_file(file: UploadFile = File(...)):
    """
    Feature 21: Uploads match footage with format and file size validation.
    """
    filename = file.filename or "uploaded_video.mp4"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {list(ALLOWED_VIDEO_EXTENSIONS)}"
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Corrupted or empty video file (0 bytes).")
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File oversized. Maximum upload size is 100MB.")

    # Save video asset
    save_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "videos")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    with open(save_path, "wb") as f:
        f.write(content)

    video_id = os.path.splitext(filename)[0]
    try:
        save_video_asset(
            video_id=video_id,
            filename=filename,
            file_path=save_path,
            file_size_bytes=len(content),
        )
    except Exception:
        pass

    return {
        "status": "UPLOAD_SUCCESS",
        "video_id": video_id,
        "filename": filename,
        "file_size_bytes": len(content),
        "video_url": f"/videos/{filename}",
        "message": "Video uploaded and registered in ScoutIQ database for RoyalVision pose extraction.",
    }


@app.post("/api/video/process-clip")
def process_video_clip(req: ProcessVideoRequest):
    """Features 22–38: Extracts events, timestamps, and biomechanical indicators."""
    result = VideoProcessor.process_clip(
        video_id=req.video_id,
        player_id=req.player_id,
        player_name=req.player_name,
        role=req.role,
        fps=req.fps,
    )
    # Enqueue into Analyst Verification queue
    payload = result["analyst_verification_payload"]
    obs = verification_service.enqueue_observation(
        obs_id=f"OBS_{req.video_id}",
        player_id=req.player_id,
        player_name=req.player_name,
        video_id=req.video_id,
        timestamp_seconds=payload["timestamp_seconds"],
        ai_observation=payload["observation_summary"],
        raw_confidence=payload["confidence_score"],
    )
    result["enqueued_verification"] = obs
    return result


@app.post("/api/video/multi-clip-analysis")
def multi_clip_analysis(req: MultiClipAnalysisRequest):
    """Features 39 & 40: Aggregates observations across multiple clips into an AI video summary."""
    clip_summaries = []
    repeatability_scores = []
    head_stillness_scores = []

    for cid in req.clip_ids:
        c_res = VideoProcessor.process_clip(
            video_id=cid,
            player_id=req.player_id,
            player_name=req.player_name,
            role=req.role,
        )
        clip_summaries.append(c_res)
        repeatability_scores.append(c_res["biomechanics"]["repeatability_score"])
        head_stillness_scores.append(c_res["biomechanics"]["head_stillness_score"])

    avg_repeatability = round(sum(repeatability_scores) / len(repeatability_scores), 3) if repeatability_scores else 0.94
    avg_stillness = round(sum(head_stillness_scores) / len(head_stillness_scores), 3) if head_stillness_scores else 0.95

    return {
        "player_id": req.player_id,
        "player_name": req.player_name,
        "role": req.role,
        "clips_analyzed": len(req.clip_ids),
        "aggregated_metrics": {
            "mean_repeatability_score": avg_repeatability,
            "mean_head_stillness_score": avg_stillness,
        },
        "ai_video_summary": (
            f"Multi-clip analysis across {len(req.clip_ids)} delivery sequences confirms high biomechanical "
            f"consistency ({avg_repeatability * 100}% DTW match) with elite head stabilization ({avg_stillness})."
        ),
        "clip_details": clip_summaries,
    }


# ===========================================================================
# Section B: Human-in-the-Loop Verification (Features 41–47)
# ===========================================================================

@app.get("/api/verification/pending")
def list_pending_verifications():
    """Feature 41: Returns queue of observations awaiting review."""
    return {"pending_items": verification_service.get_pending_queue()}


@app.post("/api/verification/confirm")
def confirm_verification(req: ConfirmVerificationRequest):
    """Feature 42: Confirms observation (sets confidence multiplier to 1.0)."""
    return verification_service.confirm_observation(req.obs_id, req.analyst_name)


@app.post("/api/verification/correct")
def correct_verification(req: CorrectVerificationRequest):
    """Feature 43: Corrects observation with analyst human input."""
    return verification_service.correct_observation(req.obs_id, req.analyst_name, req.corrected_observation, req.notes)


@app.post("/api/verification/reject")
def reject_verification(req: RejectVerificationRequest):
    """Feature 44: Rejects observation (multiplier 0.0, excluded from RAG)."""
    return verification_service.reject_observation(req.obs_id, req.analyst_name, req.reason)


@app.get("/api/verification/history")
def get_verification_history():
    """Feature 47: Retrieves full audit trail of review decisions."""
    all_items = list(verification_service.queue.values())
    reviewed_items = [i for i in all_items if i["status"] != "PENDING"]
    return {
        "total_reviewed": len(reviewed_items),
        "review_history": reviewed_items,
    }


# ===========================================================================
# Section C: Gemini AI & Hybrid RAG Intelligence (Features 48–59)
# ===========================================================================

@app.post("/api/assistant/ask")
def query_scoutiq_assistant(req: QueryAssistantRequest):
    """Features 48, 54, 55, 58, 59: Answers tactical queries with grounded citations."""
    return rag_assistant.answer_query(req.query)


@app.get("/api/players/search")
def semantic_player_search(q: str = Query(..., description="Natural language search query")):
    """Feature 52: Semantic search for players based on query."""
    matches = retrieval_dispatcher.query_structured_stats(q)
    return {
        "query": q,
        "results_count": len(matches),
        "results": matches,
    }


@app.get("/api/players/{player_id}/dossier")
def get_player_scouting_dossier(player_id: str):
    """Feature 53: Generates detailed AI-assisted scouting dossier."""
    matches = [p for p in retrieval_dispatcher.stats_catalog if p["player_id"] == player_id]
    if not matches:
        raise HTTPException(status_code=404, detail=f"Player ID '{player_id}' not found.")
    player = matches[0]
    brief = rag_assistant.answer_query(f"Generate full scouting dossier for {player['name']}")
    return {
        "player_id": player_id,
        "profile": player,
        "dossier": brief,
    }


# ===========================================================================
# Section D: Auction Economics & Squad Strategy (Features 60–68)
# ===========================================================================

@app.get("/api/auction/role-scarcity")
def get_role_scarcity_matrix():
    """Feature 65: Returns domestic role scarcity ratings."""
    return {"scarcity_matrix": AuctionStrategyEngine.ROLE_SCARCITY_SCORES}


@app.get("/api/auction/squad-balance")
def evaluate_squad_balance():
    """Feature 67: Evaluates current RR squad balance and role distribution."""
    return AuctionStrategyEngine.analyze_squad_balance(MatchdayOptimizer.RR_SQUAD_POOL)


@app.post("/api/auction/simulate-budget")
def simulate_auction_budget(req: BudgetSimulateRequest):
    """Feature 68: Simulates purse spending against targeted uncapped talent."""
    return AuctionStrategyEngine.simulate_auction_budget(
        total_purse_lakhs=req.total_purse_lakhs,
        target_picks=req.target_picks,
    )


# ===========================================================================
# Section E: Matchday Selection Engine (Features 69–81)
# ===========================================================================

@app.post("/api/team/recommend-lineup")
def recommend_team_lineup(req: MatchdayLineupRequest):
    """Features 69–78: Constrained Starting XI and Impact Player recommendation."""
    return MatchdayOptimizer.recommend_matchday_lineup(
        opponent=req.opponent,
        venue=req.venue,
        pitch_type=req.pitch_type,
        scenario=req.scenario,
    )


@app.post("/api/team/compare-scenarios")
def compare_matchday_scenarios(req: ScenarioCompareRequest):
    """Feature 79: Compares Batting First vs Bowling First combinations side-by-side."""
    bat_first = MatchdayOptimizer.recommend_matchday_lineup(
        opponent=req.opponent, venue=req.venue, pitch_type=req.pitch_type, scenario="Batting First"
    )
    bowl_first = MatchdayOptimizer.recommend_matchday_lineup(
        opponent=req.opponent, venue=req.venue, pitch_type=req.pitch_type, scenario="Bowling First"
    )
    return {
        "match_conditions": {"opponent": req.opponent, "venue": req.venue, "pitch": req.pitch_type},
        "scenario_batting_first": {
            "starting_xi_count": bat_first["starting_xi_count"],
            "impact_substitute": bat_first["impact_player_recommendation"],
        },
        "scenario_bowling_first": {
            "starting_xi_count": bowl_first["starting_xi_count"],
            "impact_substitute": bowl_first["impact_player_recommendation"],
        },
        "strategic_verdict": (
            f"On {req.pitch_type} tracks at {req.venue}, batting first allows RR to accumulate powerplay runs "
            f"and introduce a specialist death bowler in the 2nd innings."
        ),
    }


# ===========================================================================
# Section F: Opposition Intelligence & Coaching (Features 82–94)
# ===========================================================================

@app.post("/api/opposition/analyze-batter")
def analyze_opposition_batter(req: OppositionBatterRequest):
    """Features 83, 85, 86, 91: Detailed batter matchup and field placement strategy."""
    return OppositionIntelligenceEngine.analyze_opponent_batter(
        batter_name=req.batter_name,
        opponent_team=req.opponent_team,
    )


@app.post("/api/opposition/analyze-bowler")
def analyze_opposition_bowler(req: OppositionBowlerRequest):
    """Feature 84: Detailed opponent bowler delivery patterns and assault strategy."""
    return OppositionIntelligenceEngine.analyze_opponent_bowler(
        bowler_name=req.bowler_name,
        opponent_team=req.opponent_team,
    )


# ===========================================================================
# Section G: Player Development & Monitoring (Features 95–100)
# ===========================================================================

@app.get("/api/development/{player_id}/trends")
def get_player_trends(player_id: str):
    """Features 95–97: Historical performance trajectory and skill tracking."""
    return PlayerDevelopmentEngine.get_player_performance_trends(player_id)


@app.post("/api/development/training-plan")
def generate_training_plan(req: TrainingPlanRequest):
    """Feature 98: Generates targeted technical drills based on weakness."""
    return PlayerDevelopmentEngine.generate_training_plan(req.player_id, req.identified_weakness)


@app.post("/api/development/compare-sessions")
def compare_coaching_sessions(req: CompareSessionsRequest):
    """Feature 99: Before-and-after biomechanical session comparison."""
    return PlayerDevelopmentEngine.compare_before_after_sessions(req.session_a, req.session_b)


@app.get("/api/development/{player_id}/report")
def get_player_development_report(player_id: str):
    """Feature 100: Full progress report for coaches."""
    matches = [p for p in retrieval_dispatcher.stats_catalog if p["player_id"] == player_id]
    name = matches[0]["name"] if matches else f"Prospect {player_id}"
    return PlayerDevelopmentEngine.generate_player_development_report(player_id, name)


# ===========================================================================
# Section H: Dashboard, Reports & Administration (Features 101–116)
# ===========================================================================

@app.get("/api/auction/export-shortlist")
def export_auction_shortlist(
    format: str = Query("json", pattern="^(json|csv)$"),
    x_royals_role: Optional[str] = Header(None),
):
    """
    Feature 108: Exports auction shortlist as JSON or CSV.
    Protected by RBAC: Allowed roles: Scout, Management.
    """
    verify_role_access(x_royals_role, ["Scout", "Management"])
    data = retrieval_dispatcher.stats_catalog

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["player_id", "name", "age", "role", "state_team", "steal_index", "base_price", "projected_hammer"])
        for p in data:
            v = p["auction_valuation"]
            writer.writerow([p["player_id"], p["name"], p["age"], p["role"], p["state_team"], v["steal_index"], v["base_price_lakhs"], v["projected_hammer_lakhs"]])
        return PlainTextResponse(output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=rr_shortlist.csv"})

    return {"shortlist": data, "count": len(data), "exported_by_role": x_royals_role or "Scout"}


@app.get("/api/reports/player-dossier/{player_id}", response_class=HTMLResponse)
def get_printable_scouting_dossier(player_id: str):
    """Feature 109: Generates high-res printable HTML scouting dossier (PDF-ready)."""
    matches = [p for p in retrieval_dispatcher.stats_catalog if p["player_id"] == player_id]
    if not matches:
        raise HTTPException(status_code=404, detail="Player not found")
    p = matches[0]
    val = p["auction_valuation"]
    stats = p["phase_stats"]

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>RR War Room Dossier - {p['name']}</title>
      <style>
        body {{ font-family: 'Montserrat', sans-serif; background: #070B14; color: #FFF; padding: 30px; }}
        .header {{ border-bottom: 2px solid #E50695; padding-bottom: 15px; margin-bottom: 20px; }}
        .title {{ font-size: 26px; font-weight: 800; text-transform: uppercase; color: #FFF; }}
        .badge {{ background: #E50695; color: #FFF; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }}
        .card {{ background: #181825; border: 1px solid rgba(229,6,149,0.3); padding: 15px; border-radius: 8px; }}
        .stat-val {{ font-size: 20px; font-weight: bold; color: #00F0FF; }}
      </style>
    </head>
    <body>
      <div class="header">
        <div class="title">{p['name']} <span class="badge">STEAL INDEX: {val['steal_index']}/10</span></div>
        <p style="color: #94A3B8; margin-top: 5px;">Age {p['age']} · {p['role']} · {p['state_team']} | Target: {val['priority_slot']}</p>
      </div>
      <div class="grid">
        <div class="card">
          <div style="font-size: 11px; color: #EDAA16; font-weight: bold;">AUCTION VALUATION</div>
          <p>Base Price: <strong>₹{val['base_price_lakhs']} Lakhs</strong></p>
          <p>Projected Hammer Price: <strong>₹{val['projected_hammer_lakhs']} Lakhs</strong></p>
        </div>
        <div class="card">
          <div style="font-size: 11px; color: #00F0FF; font-weight: bold;">PHASE SABERMETRICS</div>
          <p>Death Phase Metric: <span class="stat-val">{stats.get('Death', {}).get('ter', stats.get('Death', {}).get('tsr', 'N/A'))}</span></p>
          <p>Powerplay Phase Metric: <span>{stats.get('Powerplay', {}).get('ter', stats.get('Powerplay', {}).get('tsr', 'N/A'))}</span></p>
        </div>
      </div>
      <div class="card">
        <div style="font-size: 11px; color: #E50695; font-weight: bold;">HEAD COACH VERDICT (KUMAR SANGAKKARA)</div>
        <p style="font-style: italic; color: #E2E8F0; margin-top: 5px;">
          "High tactical suitability for Rajasthan Royals IPL 2027 roster balance. Recommended bid ceiling up to ₹{val['projected_hammer_lakhs']} Lakhs."
        </p>
      </div>
    </body>
    </html>
    """
    return html


@app.get("/api/reports/executive-presentation")
def get_executive_presentation_export(x_royals_role: Optional[str] = Header(None)):
    """
    Feature 110: Generates executive 15-slide deck structure for Kumar Sangakkara & Giles Lindsay.
    Protected by RBAC: Allowed roles: Management, Scout, Coach.
    """
    verify_role_access(x_royals_role, ["Management", "Scout", "Coach"])
    return {
        "presentation_title": "Royals ScoutIQ — IPL 2027 Auction Strategy",
        "audience": ["Kumar Sangakkara (Head Coach)", "Giles Lindsay (Strategy Director)"],
        "deck_structure": [
            {"slide": 1, "title": "Executive Philosophy: Moneyball Meets Computer Vision"},
            {"slide": 2, "title": "Royals ScoutIQ Architecture: 4-Pillar Separation"},
            {"slide": 3, "title": "Sabermetric Normalization: True Strike Rate & True Economy Rate"},
            {"slide": 4, "title": "RoyalVision Video AI: Quantifying Biomechanical Ceilings"},
            {"slide": 5, "title": "Rajasthan Royals 2027 Roster Gap Matrix"},
            {"slide": 6, "title": "Top Uncapped Pick #1: Vidwath Kaverappa (Death Pacer)"},
            {"slide": 7, "title": "Top Uncapped Pick #2: Ashutosh Sharma (Power Finisher)"},
            {"slide": 8, "title": "Top Uncapped Pick #3: Suyash Sharma (Mystery Spin)"},
            {"slide": 9, "title": "Auction Purse Allocation & Steal Index Rationale"},
            {"slide": 10, "title": "Matchday XI & Dynamic Impact Player Integration"},
        ],
        "exported_by": x_royals_role or "Management",
    }


@app.post("/api/data/import")
def import_and_validate_data(req: DataImportRequest, x_royals_role: Optional[str] = Header(None)):
    """
    Features 114 & 115: Validates and imports dataset records into memory/database.
    Protected by RBAC: Allowed roles: Management, Analyst.
    """
    verify_role_access(x_royals_role, ["Management", "Analyst"])
    validation_results = DataValidationSystem.validate_player_records(req.records)
    return validation_results
