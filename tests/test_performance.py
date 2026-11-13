"""
Royals ScoutIQ - Performance & Latency Benchmark Suite
Measures execution latency across key compute paths:
- RoyalVision Video Pose & Biomechanics Ingestion
- Gemini Hybrid RAG Tactical Synthesis
- Constrained Matchday XI Optimizer
- Opposition Batter Matchup Engine
- Data Import & Validation Pipeline
"""

import time
import os
import sys
import statistics
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.main import app

client = TestClient(app)


def benchmark_endpoint(name: str, method: str, url: str, payload=None, runs: int = 10):
    latencies = []
    for _ in range(runs):
        start = time.perf_counter()
        if method == "POST":
            res = client.post(url, json=payload)
        else:
            res = client.get(url)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        assert res.status_code in [200, 201], f"Failed: {res.text}"
        latencies.append(elapsed_ms)

    mean_ms = statistics.mean(latencies)
    p95_ms = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
    min_ms = min(latencies)
    max_ms = max(latencies)

    print(f"{name:<45} | Mean: {mean_ms:>6.2f} ms | Min: {min_ms:>6.2f} ms | Max: {max_ms:>6.2f} ms")
    return {"endpoint": name, "mean_ms": round(mean_ms, 2), "min_ms": round(min_ms, 2), "max_ms": round(max_ms, 2)}


if __name__ == "__main__":
    print("=========================================================================================")
    print("      ROYALS ScoutIQ - LATENCY BENCHMARK AUDIT (10 Iterations Per Endpoint)")
    print("=========================================================================================")
    
    b1 = benchmark_endpoint(
        "RoyalVision Video Clip Processing (30 frames)",
        "POST",
        "/api/video/process-clip",
        {"video_id": "BENCH_01", "player_id": "P_101", "player_name": "Vidwath Kaverappa", "role": "Right-Arm Fast Medium"},
    )
    b2 = benchmark_endpoint(
        "Gemini Hybrid RAG Tactical Query",
        "POST",
        "/api/assistant/ask",
        {"query": "Find an uncapped domestic death pacer with high steal index"},
    )
    b3 = benchmark_endpoint(
        "Matchday XI + Impact Player Optimizer",
        "POST",
        "/api/team/recommend-lineup",
        {"opponent": "Mumbai Indians", "venue": "Wankhede Stadium, Mumbai", "pitch_type": "Pace-Friendly", "scenario": "Bowling First"},
    )
    b4 = benchmark_endpoint(
        "Opposition Batter Matchup & Field Setting",
        "POST",
        "/api/opposition/analyze-batter",
        {"batter_name": "Suryakumar Yadav", "opponent_team": "Mumbai Indians"},
    )
    b5 = benchmark_endpoint(
        "Player Development Longitudinal History",
        "GET",
        "/api/development/P_101/trends",
    )
    b6 = benchmark_endpoint(
        "Auction Shortlist Export (CSV)",
        "GET",
        "/api/auction/export-shortlist?format=csv",
    )
    b7 = benchmark_endpoint(
        "Data Validation Engine (5 records)",
        "POST",
        "/api/data/import",
        {"records": [{"player_id": f"P_{i}", "name": f"Prospect {i}", "age": 22, "role": "Batter"} for i in range(5)]},
    )
    print("=========================================================================================")
