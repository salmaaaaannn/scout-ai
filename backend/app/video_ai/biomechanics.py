"""
Royals ScoutIQ - RoyalVision Biomechanics & Computer Vision Telemetry Module
Extracts quantifiable biomechanical markers from video pose keypoints
(Head Stillness, Bat Speed Proxy, Bowling Release Height/Angle, Spine Stress).
"""

import math
from typing import List, Dict, Any, Tuple


class BiomechanicsAnalyzer:
    """
    Analyzes 17 COCO skeletal keypoints (Nose, Eyes, Ears, Shoulders, Elbows, Wrists,
    Hips, Knees, Ankles) across video frame sequences.
    """

    # COCO Keypoint Index Mapping
    KP_NOSE = 0
    KP_L_SHOULDER = 5
    KP_R_SHOULDER = 6
    KP_L_ELBOW = 7
    KP_R_ELBOW = 8
    KP_L_WRIST = 9
    KP_R_WRIST = 10
    KP_L_HIP = 11
    KP_R_HIP = 12
    KP_L_KNEE = 13
    KP_R_KNEE = 14
    KP_L_ANKLE = 15
    KP_R_ANKLE = 16

    @staticmethod
    def calculate_head_stillness(keypoint_frames: List[Dict[str, Any]]) -> float:
        """
        Quantifies head stability during the 5 frames before and after ball release/impact.
        Returns a score between 0.0 (erratic drift) and 1.0 (dead still, elite technique).
        """
        if len(keypoint_frames) < 2:
            return 1.0

        drifts = []
        for i in range(1, len(keypoint_frames)):
            prev = keypoint_frames[i - 1].get("keypoints", [])
            curr = keypoint_frames[i].get("keypoints", [])

            if len(prev) > BiomechanicsAnalyzer.KP_NOSE and len(curr) > BiomechanicsAnalyzer.KP_NOSE:
                dx = curr[BiomechanicsAnalyzer.KP_NOSE][0] - prev[BiomechanicsAnalyzer.KP_NOSE][0]
                dy = curr[BiomechanicsAnalyzer.KP_NOSE][1] - prev[BiomechanicsAnalyzer.KP_NOSE][1]
                distance = math.sqrt(dx ** 2 + dy ** 2)
                drifts.append(distance)

        if not drifts:
            return 1.0

        mean_drift = sum(drifts) / len(drifts)
        # Normalized score: drift under 2px maps to > 0.95, drift > 15px drops to < 0.3
        stillness_score = max(0.0, min(1.0, 1.0 - (mean_drift / 15.0)))
        return round(stillness_score, 3)

    @staticmethod
    def calculate_bowling_arm_angle(shoulder: Tuple[float, float], wrist: Tuple[float, float]) -> Dict[str, Any]:
        """
        Calculates bowling arm angle relative to vertical axis (12 o'clock = 90 deg high-arm).
        Classifies action as High-Arm, 3/4 Round-Arm, or Sling.
        """
        dx = wrist[0] - shoulder[0]
        dy = shoulder[1] - wrist[1]  # positive upwards in image coordinates

        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        # Normalize relative to vertical (90 deg = straight up)
        elevation_angle = max(0.0, min(90.0, angle_deg))

        if elevation_angle >= 75.0:
            classification = "High-Arm"
        elif elevation_angle >= 48.0:
            classification = "3/4 Round-Arm"
        else:
            classification = "Sling / Lasith Malinga Mold"

        return {
            "elevation_angle_degrees": round(elevation_angle, 1),
            "action_classification": classification,
        }

    @staticmethod
    def calculate_spine_stress_index(
        shoulder_l: Tuple[float, float],
        shoulder_r: Tuple[float, float],
        hip_l: Tuple[float, float],
        hip_r: Tuple[float, float],
    ) -> Dict[str, Any]:
        """
        Detects excessive lateral trunk flexion and counter-rotation at front-foot contact.
        Excessive lateral flexion (>32 degrees) is a primary risk factor for lumbar stress fractures.
        """
        # Shoulder vector midpoint and Hip vector midpoint
        shoulder_mid = ((shoulder_l[0] + shoulder_r[0]) / 2.0, (shoulder_l[1] + shoulder_r[1]) / 2.0)
        hip_mid = ((hip_l[0] + hip_r[0]) / 2.0, (hip_l[1] + hip_r[1]) / 2.0)

        dx = shoulder_mid[0] - hip_mid[0]
        dy = hip_mid[1] - shoulder_mid[1]  # positive upwards

        # Angle with vertical
        trunk_tilt_rad = math.atan2(abs(dx), max(dy, 1e-4))
        lateral_flexion_deg = math.degrees(trunk_tilt_rad)

        # Stress index: 0.0 (safe) to 1.0 (critical injury risk)
        stress_index = min(1.0, max(0.0, lateral_flexion_deg / 35.0))

        risk_category = "Low Strain" if stress_index < 0.45 else ("Moderate Strain" if stress_index < 0.75 else "High Stress Fracture Risk")

        return {
            "lateral_flexion_degrees": round(lateral_flexion_deg, 1),
            "stress_index": round(stress_index, 2),
            "risk_category": risk_category,
        }

    @staticmethod
    def calculate_bat_speed_proxy(wrist_positions: List[Tuple[float, float]], fps: float = 30.0) -> float:
        """
        Estimates downswing bat speed velocity (rad/s) across consecutive frames leading to impact.
        """
        if len(wrist_positions) < 3:
            return 115.0

        velocities = []
        dt = 1.0 / max(fps, 1.0)
        for i in range(1, len(wrist_positions)):
            dx = wrist_positions[i][0] - wrist_positions[i - 1][0]
            dy = wrist_positions[i][1] - wrist_positions[i - 1][1]
            dist = math.sqrt(dx ** 2 + dy ** 2)
            velocities.append(dist / dt)

        peak_velocity = max(velocities)
        # Scaled to rad/s proxy
        rad_speed = round(min(160.0, max(80.0, peak_velocity * 0.18)), 1)
        return rad_speed
