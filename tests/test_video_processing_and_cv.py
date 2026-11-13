"""
Royals ScoutIQ - Computer Vision & Video Processing Test Suite
Validates YOLO11-Pose inference, COCO keypoint extraction, pitch homography calibration,
kinematic event detection (release frame, trigger latency), and biomechanical analysis.
"""

import pytest
import os
import cv2
import numpy as np

from backend.app.video_ai.event_detector import CricketEventDetector
from backend.app.video_ai.biomechanics import BiomechanicsAnalyzer
from backend.app.video_ai.video_processor import (
    CricketPitchCalibrator,
    VideoProcessor,
    get_yolo_model,
)


def test_cricket_event_detector_ball_release():
    # Empty series
    empty_res = CricketEventDetector.detect_ball_release_frame([])
    assert empty_res["release_frame"] == 0
    assert empty_res["confidence"] == 0.0

    # Normal trajectory: wrist reaches peak elevation (minimum Y) at index 15
    y_series = [500 - (i * 10) for i in range(15)] + [350 + (i * 12) for i in range(15)]
    res = CricketEventDetector.detect_ball_release_frame(y_series, fps=30.0)
    assert res["release_frame"] == 15
    assert res["timestamp_seconds"] == round(15 / 30.0, 3)
    assert res["confidence"] == 0.92


def test_cricket_event_detector_trigger_movement():
    # Short series
    short_res = CricketEventDetector.detect_trigger_movement([100.0, 101.0, 100.5])
    assert short_res["trigger_frame"] == 0
    assert short_res["trigger_latency_ms"] == 45.0

    # Normal series with distinct shift around frame 6
    hip_x = [200.0, 200.1, 200.2, 200.1, 200.0, 201.0, 215.0, 225.0, 230.0, 232.0]
    res = CricketEventDetector.detect_trigger_movement(hip_x, fps=30.0)
    assert res["trigger_frame"] > 0
    assert "trigger_latency_ms" in res
    assert "is_elite_reaction" in res


def test_cricket_event_detector_classify_shot_execution():
    # Lofted attack
    lofted = CricketEventDetector.classify_shot_execution(bat_angle_deg=10.0, swing_plane=35.0)
    assert lofted["classified_shot"] == "Lofted Attack (Overs 17-20)"

    # Cover Drive
    drive = CricketEventDetector.classify_shot_execution(bat_angle_deg=-25.0, swing_plane=15.0, front_foot_forward=True)
    assert drive["classified_shot"] == "Cover Drive"

    # Pull Shot
    pull = CricketEventDetector.classify_shot_execution(bat_angle_deg=50.0, swing_plane=10.0)
    assert pull["classified_shot"] == "Pull Shot"

    # Cut Shot
    cut = CricketEventDetector.classify_shot_execution(bat_angle_deg=-40.0, swing_plane=10.0, front_foot_forward=False)
    assert cut["classified_shot"] == "Cut Shot"

    # Straight Drive
    straight = CricketEventDetector.classify_shot_execution(bat_angle_deg=0.0, swing_plane=10.0)
    assert straight["classified_shot"] == "Straight Drive"


def test_biomechanics_head_stillness():
    # Empty / single frame
    assert BiomechanicsAnalyzer.calculate_head_stillness([]) == 1.0
    assert BiomechanicsAnalyzer.calculate_head_stillness([{"keypoints": [[100, 200]]}]) == 1.0

    # Perfectly still frames (drift ~ 0)
    still_frames = [{"keypoints": [[100.0, 200.0]] * 17} for _ in range(10)]
    still_score = BiomechanicsAnalyzer.calculate_head_stillness(still_frames)
    assert still_score >= 0.99

    # Highly erratic frames (drift ~ 20px per frame)
    erratic_frames = [{"keypoints": [[100.0 + i * 20.0, 200.0 + i * 20.0]] * 17} for i in range(10)]
    erratic_score = BiomechanicsAnalyzer.calculate_head_stillness(erratic_frames)
    assert erratic_score < 0.5


def test_biomechanics_bowling_arm_angle():
    # High-Arm (wrist directly above shoulder, elevation angle ~ 88.6 deg >= 75 deg)
    high_arm = BiomechanicsAnalyzer.calculate_bowling_arm_angle(shoulder=(200.0, 400.0), wrist=(205.0, 150.0))
    assert high_arm["action_classification"] == "High-Arm"
    assert high_arm["elevation_angle_degrees"] >= 75.0

    # 3/4 Round-Arm (elevation angle ~ 60.0 deg between 48 and 75 deg)
    round_arm = BiomechanicsAnalyzer.calculate_bowling_arm_angle(shoulder=(200.0, 400.0), wrist=(300.0, 226.8))
    assert round_arm["action_classification"] == "3/4 Round-Arm"
    assert 48.0 <= round_arm["elevation_angle_degrees"] < 75.0

    # Sling / Lasith Malinga Mold (wrist low, side-arm < 48 deg)
    sling = BiomechanicsAnalyzer.calculate_bowling_arm_angle(shoulder=(200.0, 400.0), wrist=(400.0, 360.0))
    assert sling["action_classification"] == "Sling / Lasith Malinga Mold"
    assert sling["elevation_angle_degrees"] < 48.0


def test_biomechanics_spine_stress_index():
    # Symmetrical, upright posture
    low_stress = BiomechanicsAnalyzer.calculate_spine_stress_index(
        shoulder_l=(180.0, 300.0),
        shoulder_r=(220.0, 300.0),
        hip_l=(185.0, 450.0),
        hip_r=(215.0, 450.0),
    )
    assert low_stress["risk_category"] == "Low Strain"
    assert low_stress["stress_index"] < 0.45

    # Severe lateral flexion / rotation (shoulder shifted laterally relative to hips)
    high_stress = BiomechanicsAnalyzer.calculate_spine_stress_index(
        shoulder_l=(300.0, 300.0),
        shoulder_r=(400.0, 300.0),
        hip_l=(185.0, 450.0),
        hip_r=(215.0, 450.0),
    )
    assert high_stress["risk_category"] == "High Stress Fracture Risk"
    assert high_stress["stress_index"] >= 0.75


def test_biomechanics_bat_speed_proxy():
    # Insufficient points default
    assert BiomechanicsAnalyzer.calculate_bat_speed_proxy([]) == 115.0
    assert BiomechanicsAnalyzer.calculate_bat_speed_proxy([(100.0, 100.0)]) == 115.0

    # Fast downswing sequence (5 frames)
    wrists = [(300.0, 100.0 + i * 40.0) for i in range(5)]
    speed = BiomechanicsAnalyzer.calculate_bat_speed_proxy(wrists, fps=30.0)
    assert speed >= 80.0


def test_cricket_pitch_calibrator_homography_and_mapping():
    # Invalid corners
    assert CricketPitchCalibrator.compute_homography([]) is None

    # Valid 4 broadcast crease corners
    corners = [(420.0, 780.0), (860.0, 780.0), (740.0, 320.0), (540.0, 320.0)]
    H = CricketPitchCalibrator.compute_homography(corners)
    assert H is not None
    assert H.shape == (3, 3)

    # Map point
    point_on_pitch = CricketPitchCalibrator.map_pixel_to_pitch((640.0, 550.0), H)
    assert point_on_pitch is not None
    assert len(point_on_pitch) == 2
    assert isinstance(point_on_pitch[0], float)
    assert isinstance(point_on_pitch[1], float)

    # Map with None H
    assert CricketPitchCalibrator.map_pixel_to_pitch((100, 100), None) is None


def test_video_processor_synthetic_clip_execution():
    # Test batter clip
    res_batter = VideoProcessor.process_clip(
        video_id="TEST_CLIP_BATTER",
        player_id="37052",
        player_name="Naman Dhir",
        role="Top-Order Batter",
        fps=30.0,
    )
    assert res_batter["video_id"] == "TEST_CLIP_BATTER"
    assert "head_stillness_score" in res_batter["biomechanics"]
    assert "bat_speed_proxy" in res_batter["biomechanics"]
    assert "shot_classification" in res_batter["events"]

    # Test bowler clip
    res_bowler = VideoProcessor.process_clip(
        video_id="TEST_CLIP_BOWLER",
        player_id="8661",
        player_name="Matheesha Pathirana",
        role="Sling Death Pacer",
        fps=30.0,
    )
    assert res_bowler["video_id"] == "TEST_CLIP_BOWLER"
    assert "arm_release" in res_bowler["biomechanics"]
    assert "spine_stress" in res_bowler["biomechanics"]


def test_yolo_pose_model_presence_and_inference():
    yolo = get_yolo_model()
    assert yolo is not None, "YOLO11-Pose model should be discoverable in backend/app/models/yolo11n-pose.pt"

    video_path = os.path.abspath("data/raw/videos/valid_test_clip.mp4")
    assert os.path.exists(video_path)

    res = VideoProcessor.process_clip(
        video_id="valid_test_clip",
        player_id="P_101",
        player_name="Vidwath Kaverappa",
        role="Pace Bowler",
        video_file_path=video_path,
    )
    assert res["video_id"] == "valid_test_clip"
    assert res["is_synthetic"] is False
    assert res["total_frames_analyzed"] == 15
    assert res["detection_confidence"] > 0.0
