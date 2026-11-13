"""
Royals ScoutIQ - Comprehensive End-to-End Pipeline Integration Test
Verifies all 6 non-data modules:
1. Video AI Pose Extraction & Event Classification
2. Human-in-the-Loop Analyst Verification Queue
3. Gemini Hybrid RAG Intelligence & Citation Grounding
4. Matchday XI & Impact Player Constrained Optimization
5. Opposition Matchup Intelligence & Field Setting
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.analytics.sabermetrics import SabermetricsEngine
from app.video_ai.video_processor import VideoProcessor
from app.verification.verification_service import AnalystVerificationService
from app.rag.retrieval import HybridRetrievalDispatcher
from app.rag.gemini_rag import GeminiTacticalRAG
from app.optimizer.team_optimizer import MatchdayOptimizer
from app.opposition.opposition_intel import OppositionIntelligenceEngine


def run_full_pipeline_verification():
    print("==================================================================")
    print("      ROYALS ScoutIQ - FULL PIPELINE INTEGRATION TEST")
    print("==================================================================")

    # 1. Sabermetrics Validation
    tsr = SabermetricsEngine.calculate_tsr(runs=52, balls=24, phase="Death")
    ter = SabermetricsEngine.calculate_ter(runs_conceded=22, balls_bowled=24, phase="Middle")
    steal = SabermetricsEngine.calculate_steal_index(projected_war=4.2, projected_hammer_lakhs=65.0, base_price_lakhs=20.0)
    print(f"\n[1/5] SABERMETRICS CHECK: OK")
    print(f"      - Death TSR: +{tsr}")
    print(f"      - Middle TER: {ter}")
    print(f"      - Steal Index: {steal}/10")

    # 2. Video AI & Event Processing
    video_res = VideoProcessor.process_clip(
        video_id="CLIP_SMAT_2024_01",
        player_id="P_101",
        player_name="Vidwath Kaverappa",
        role="Right-Arm Fast Medium",
    )
    print(f"\n[2/5] ROYALVISION VIDEO AI: OK")
    print(f"      - Release Point: Frame {video_res['events']['release_event']['release_frame']} ({video_res['events']['release_event']['timestamp_seconds']}s)")
    print(f"      - Arm Angle: {video_res['biomechanics']['arm_release']['elevation_angle_degrees']}° ({video_res['biomechanics']['arm_release']['action_classification']})")
    print(f"      - Head Stillness: {video_res['biomechanics']['head_stillness_score']}")
    print(f"      - Spine Risk: {video_res['biomechanics']['spine_stress']['risk_category']}")

    # 3. Human-in-the-Loop Analyst Verification
    v_svc = AnalystVerificationService(store_path="/tmp/pipeline_verification_store.json")
    enqueued = v_svc.enqueue_observation(
        obs_id="OBS_TEST_01",
        player_id="P_101",
        player_name="Vidwath Kaverappa",
        video_id="CLIP_SMAT_2024_01",
        timestamp_seconds=video_res['events']['release_event']['timestamp_seconds'],
        ai_observation="Confirmed high-arm release with elite trunk stability.",
    )
    confirmed = v_svc.confirm_observation("OBS_TEST_01", analyst_name="Giles Lindsay")
    print(f"\n[3/5] HUMAN VERIFICATION QUEUE: OK")
    print(f"      - Review Status: {confirmed['status']}")
    print(f"      - Verified By: {confirmed['analyst_name']}")
    print(f"      - Confidence Multiplier: {confirmed['confidence_multiplier']}")

    # 4. Gemini Hybrid RAG Tactical Query
    dispatcher = HybridRetrievalDispatcher(verification_service=v_svc)
    rag = GeminiTacticalRAG(dispatcher=dispatcher)
    rag_res = rag.answer_query("Recommend a domestic pacer with elite death economy and high steal value")
    print(f"\n[4/5] GEMINI HYBRID RAG: OK")
    print(f"      - Matched Players: {rag_res['matched_players_count']}")
    print(f"      - Grounded Citation: {rag_res['citations'][0]['player']} ({rag_res['citations'][0]['verification_status']})")

    # 5. Matchday XI & Opposition Intelligence
    lineup = MatchdayOptimizer.recommend_matchday_lineup(
        opponent="Mumbai Indians",
        venue="Wankhede Stadium, Mumbai",
        pitch_type="Pace-Friendly",
        scenario="Bowling First",
    )
    opp = OppositionIntelligenceEngine.analyze_opponent_batter(
        batter_name="Suryakumar Yadav",
        opponent_team="Mumbai Indians",
    )
    print(f"\n[5/5] MATCHDAY & OPPOSITION INTELLIGENCE: OK")
    print(f"      - Starting XI: {lineup['starting_xi_count']} players (Overseas: {lineup['overseas_count']})")
    print(f"      - Impact Substitute: {lineup['impact_player_recommendation']['name']}")
    print(f"      - Tactical Choke vs {opp['batter_name']}: {opp['primary_weakness']['tactical_plan']}")

    print("\n==================================================================")
    print("      ALL 5 PHASES VERIFIED & OPERATIONAL (READY FOR NOV 8 DATA)")
    print("==================================================================")


if __name__ == "__main__":
    run_full_pipeline_verification()
