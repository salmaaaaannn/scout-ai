'use client';

import React, { useState } from 'react';
import {
  Video,
  Upload,
  Play,
  Activity,
  ShieldAlert,
  Award,
  Zap,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  RefreshCw,
  Compass
} from 'lucide-react';

interface BiomechanicsResult {
  video_id: string;
  player_id: string;
  player_name: string;
  role: string;
  fps: number;
  is_synthetic: boolean;
  detection_confidence: number;
  total_frames_analyzed: number;
  events: {
    release_event: {
      release_frame: number;
      timestamp_seconds: number;
      confidence: number;
    };
    trigger_event: {
      trigger_frame: number;
      trigger_latency_ms: number;
      is_elite_reaction: boolean;
    };
    shot_classification: {
      classified_shot: string;
      scoring_zone: string;
      swing_plane_degrees: number;
      confidence: number;
    };
  };
  biomechanics: {
    head_stillness_score: number;
    arm_release: {
      elevation_angle_degrees: number;
      action_classification: string;
    };
    spine_stress: {
      lateral_flexion_degrees: number;
      stress_index: number;
      risk_category: string;
    };
    bat_speed_proxy: {
      rad_s: number;
      estimated_speed_kph: number;
    };
    repeatability_score: number;
  };
  pitch_calibration?: {
    homography_calibrated: boolean;
    projected_release_coords_meters?: [number, number];
  };
  analyst_verification_payload: {
    observation_summary: string;
    confidence_score: number;
    status: string;
    timestamp_seconds: number;
  };
}

export default function VideoStudioPage() {
  const [selectedRole, setSelectedRole] = useState('Pace Bowler');
  const [playerName, setPlayerName] = useState('Vidwath Kaverappa');
  const [playerId, setPlayerId] = useState('P_101');
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [uploadedVideoUrl, setUploadedVideoUrl] = useState<string | null>(null);
  const [uploadedVideoId, setUploadedVideoId] = useState<string>('CLIP_SMAT_P101');
  const [analysisResult, setAnalysisResult] = useState<BiomechanicsResult | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setStatusMessage('Uploading video footage to ScoutIQ ingestion bucket...');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${apiUrl}/api/video/upload`, {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setUploadedVideoUrl(data.video_url || URL.createObjectURL(file));
        const vId = data.video_id || `VID_${Date.now()}`;
        setUploadedVideoId(vId);
        setStatusMessage(`Upload successful: ${file.name} registered. Ready for RoyalVision YOLO11-Pose analysis.`);
      } else {
        const err = await res.json();
        setStatusMessage(`Upload failed: ${err.detail || 'Server error'}`);
      }
    } catch (err) {
      console.error('Upload error:', err);
      setStatusMessage('Backend network error during upload.');
    } finally {
      setUploading(false);
    }
  }

  async function runBiomechanicsProcessing() {
    setProcessing(true);
    setStatusMessage('Executing OpenCV frame decoding & YOLO11-Pose keypoint inference...');
    try {
      const res = await fetch(`${apiUrl}/api/video/process-clip`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          video_id: uploadedVideoId,
          player_id: playerId,
          player_name: playerName,
          role: selectedRole,
          fps: 30.0,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setAnalysisResult(data);
        setStatusMessage('RoyalVision pose extraction complete. Biomechanical telemetry persisted to SQLite.');
      } else {
        setStatusMessage('Video processing failed on backend.');
      }
    } catch (err) {
      console.error('Processing error:', err);
      setStatusMessage('Network error during video processing.');
    } finally {
      setProcessing(false);
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-pink-500/20 p-2 text-pink-400">
            <Video className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-black tracking-wide text-white">
            RoyalVision AI Video Studio &amp; Biomechanics
          </h1>
        </div>
        <p className="mt-1 text-sm text-slate-400">
          OpenCV frame extraction, YOLO11-Pose skeletal keypoint tracking, batting bat-path &amp; bowling release angle diagnostics.
        </p>
      </div>

      {/* Upload & Controls */}
      <div className="mb-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 rounded-2xl border border-white/10 bg-slate-900/60 p-6 backdrop-blur-md">
          <h3 className="text-sm font-bold text-white mb-4">Ingest Match Clip or Training Video</h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Candidate Name
              </label>
              <input
                type="text"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                className="w-full rounded-lg border border-white/10 bg-slate-950 px-3 py-2 text-xs text-white focus:border-pink-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Candidate ID
              </label>
              <input
                type="text"
                value={playerId}
                onChange={(e) => setPlayerId(e.target.value)}
                className="w-full rounded-lg border border-white/10 bg-slate-950 px-3 py-2 text-xs text-white focus:border-pink-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Playing Discipline
              </label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="w-full rounded-lg border border-white/10 bg-slate-950 px-3 py-2 text-xs text-white focus:border-pink-500 focus:outline-none"
              >
                <option value="Pace Bowler">Pace Bowler (Right-Arm)</option>
                <option value="Left-Arm Pacer">Left-Arm Fast Bowler</option>
                <option value="Spin Bowler">Spin Bowler (Orthodox / Wrist)</option>
                <option value="Top-Order Batter">Top-Order Batter</option>
                <option value="Death Finisher">Death Finisher</option>
              </select>
            </div>
          </div>

          {/* Drag & Drop Upload Box */}
          <div className="relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-white/15 bg-slate-950/40 p-8 text-center hover:border-pink-500/50 transition-colors">
            <Upload className="h-8 w-8 text-slate-400 mb-2" />
            <p className="text-xs font-semibold text-slate-200">
              {uploading ? 'Uploading Video...' : 'Upload MP4, AVI, or MOV match delivery (up to 100MB)'}
            </p>
            <p className="text-[11px] text-slate-500 mt-1">
              Supports broadcast feeds and side-on / front-on high-speed practice cameras.
            </p>
            <input
              type="file"
              accept=".mp4,.avi,.mov"
              onChange={handleFileUpload}
              className="absolute inset-0 opacity-0 cursor-pointer"
            />
          </div>

          {statusMessage && (
            <div className="mt-3 rounded-lg bg-pink-500/10 border border-pink-500/20 px-3 py-2 text-xs text-pink-300">
              {statusMessage}
            </div>
          )}

          <div className="mt-4 flex justify-end">
            <button
              onClick={runBiomechanicsProcessing}
              disabled={processing}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-pink-600 to-rose-600 px-6 py-2.5 text-xs font-bold text-white shadow-lg shadow-pink-500/25 hover:from-pink-500 hover:to-rose-500 transition-all disabled:opacity-50"
            >
              {processing ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
              Extract 17-Keypoint Biomechanics
            </button>
          </div>
        </div>

        {/* Video Preview or Synthetic Tracker */}
        <div className="rounded-2xl border border-white/10 bg-slate-900/60 p-6 backdrop-blur-md flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-white">Video Feed Preview</h3>
              {analysisResult && (
                <span className={`rounded-full px-2 py-0.5 text-[9px] font-bold border ${
                  analysisResult.is_synthetic
                    ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                    : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                }`}>
                  {analysisResult.is_synthetic ? 'SIMULATED KINEMATICS' : 'REAL YOLO11-POSE MODEL'}
                </span>
              )}
            </div>

            {uploadedVideoUrl ? (
              <video
                src={uploadedVideoUrl}
                controls
                className="w-full rounded-xl border border-white/10 bg-black aspect-video object-contain"
              />
            ) : (
              <div className="flex flex-col items-center justify-center rounded-xl border border-white/10 bg-black/60 aspect-video p-6 text-center">
                <Video className="h-10 w-10 text-slate-600 mb-2" />
                <p className="text-xs text-slate-400">No active video stream loaded.</p>
                <p className="text-[10px] text-slate-500 mt-1">
                  Upload a clip or click 'Extract' to run standard kinematic simulation.
                </p>
              </div>
            )}
          </div>

          {analysisResult && (
            <div className="mt-4 pt-3 border-t border-white/10 flex items-center justify-between text-xs text-slate-400">
              <span>Frames Analyzed: <strong className="text-white">{analysisResult.total_frames_analyzed}</strong></span>
              <span>Model Confidence: <strong className="text-emerald-400">{Math.round(analysisResult.detection_confidence * 100)}%</strong></span>
            </div>
          )}
        </div>
      </div>

      {/* Analysis Telemetry Cards */}
      {analysisResult && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Head Stillness */}
          <div className="rounded-2xl border border-white/10 bg-slate-900/50 p-5 backdrop-blur-md">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Head Stability Drift
            </span>
            <div className="mt-2 flex items-baseline justify-between">
              <span className="font-mono text-2xl font-black text-pink-400">
                {analysisResult.biomechanics.head_stillness_score}
              </span>
              <span className="text-xs font-semibold text-emerald-400">
                {analysisResult.biomechanics.head_stillness_score >= 0.9 ? 'ELITE STABILITY' : 'MODERATE DRIFT'}
              </span>
            </div>
            <p className="mt-2 text-xs text-slate-400">
              Measured across 5 frames before and after release point.
            </p>
          </div>

          {/* Bowling Arm Angle */}
          <div className="rounded-2xl border border-white/10 bg-slate-900/50 p-5 backdrop-blur-md">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Arm Release Angle
            </span>
            <div className="mt-2 flex items-baseline justify-between">
              <span className="font-mono text-2xl font-black text-blue-400">
                {analysisResult.biomechanics.arm_release.elevation_angle_degrees}°
              </span>
              <span className="text-xs font-semibold text-slate-200">
                {analysisResult.biomechanics.arm_release.action_classification}
              </span>
            </div>
            <p className="mt-2 text-xs text-slate-400">
              Release frame: #{analysisResult.events.release_event.release_frame} ({analysisResult.events.release_event.timestamp_seconds}s)
            </p>
          </div>

          {/* Spine Stress Index */}
          <div className="rounded-2xl border border-white/10 bg-slate-900/50 p-5 backdrop-blur-md">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Spine Stress &amp; Lateral Flexion
            </span>
            <div className="mt-2 flex items-baseline justify-between">
              <span className="font-mono text-2xl font-black text-amber-400">
                {analysisResult.biomechanics.spine_stress.lateral_flexion_degrees}°
              </span>
              <span className="text-xs font-semibold text-emerald-400">
                {analysisResult.biomechanics.spine_stress.risk_category}
              </span>
            </div>
            <p className="mt-2 text-xs text-slate-400">
              Shoulder-to-hip trunk counter-rotation screening indicator.
            </p>
          </div>

          {/* Bat Speed or Reaction */}
          <div className="rounded-2xl border border-white/10 bg-slate-900/50 p-5 backdrop-blur-md">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Bat Speed / Downswing Velocity
            </span>
            <div className="mt-2 flex items-baseline justify-between">
              <span className="font-mono text-2xl font-black text-emerald-400">
                {analysisResult.biomechanics.bat_speed_proxy.estimated_speed_kph} km/h
              </span>
              <span className="text-xs font-semibold text-slate-300">
                {analysisResult.events.shot_classification.classified_shot}
              </span>
            </div>
            <p className="mt-2 text-xs text-slate-400">
              Reaction latency: {analysisResult.events.trigger_event.trigger_latency_ms} ms
            </p>
          </div>

          {/* Enqueued Analyst Observation */}
          <div className="lg:col-span-4 rounded-2xl border border-pink-500/30 bg-gradient-to-r from-pink-950/20 to-slate-950 p-6 backdrop-blur-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-pink-400" />
                <h4 className="text-sm font-bold text-white">
                  Enqueued for Analyst Verification
                </h4>
              </div>
              <span className="rounded bg-pink-500/20 px-2 py-0.5 text-[10px] font-bold text-pink-400 border border-pink-500/30">
                STATUS: PENDING ANALYST SIGN-OFF
              </span>
            </div>
            <p className="mt-2 text-xs text-slate-300">
              "{analysisResult.analyst_verification_payload.observation_summary}"
            </p>
            <p className="mt-2 text-[11px] text-slate-500">
              Sent to Giles Lindsay &amp; Kumar Sangakkara review dashboard. Weighting will transition from 0.65 to 1.0 upon franchise confirmation.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
