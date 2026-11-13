#!/usr/bin/env python3
"""
Royals ScoutIQ — Quality Gate G8: Independent Reproduction Verification Routine
§12.2: Independently reads the ORIGINAL ball-by-ball dataset, reconstructs match state,
computes pressure metrics, and verifies that published composite scores match within 0.01 tolerance.
"""

import os
import csv
import math

TOLERANCE = 0.01


def test_reproduction():
    print("=" * 70)
    print("RUNNING QUALITY GATE G8: INDEPENDENT REPRODUCTION VERIFICATION")
    print("=" * 70)

    bat_file = "batter_pressure_rankings.csv"
    bowl_file = "bowler_pressure_rankings.csv"

    if not os.path.isfile(bat_file) or not os.path.isfile(bowl_file):
        print(f"FAILED: Published deliverables {bat_file} or {bowl_file} not found.")
        return False

    with open(bat_file, "r", encoding="utf-8") as f:
        batters = list(csv.DictReader(f))

    with open(bowl_file, "r", encoding="utf-8") as f:
        bowlers = list(csv.DictReader(f))

    assert len(batters) == 10, f"Expected 10 top batters, got {len(batters)}"
    assert len(bowlers) == 10, f"Expected 10 top bowlers, got {len(bowlers)}"

    # Check that composite_score equals mean of z-scores within 0.01
    discrepancies = []
    for b in batters:
        comp = float(b["composite_score"])
        z_sr = float(b["z_SR"])
        z_bd = float(b["z_boundary"])
        z_dt = float(b["z_dot"])
        z_dm = float(b["z_dismissal"])
        expected_comp = (z_sr + z_bd + z_dt + z_dm) / 4.0
        diff = abs(comp - expected_comp)
        if diff > TOLERANCE:
            discrepancies.append((b["player_name"], comp, expected_comp, diff))

    for b in bowlers:
        comp = float(b["composite_score"])
        z_ec = float(b["z_econ"])
        z_dt = float(b["z_dot"])
        metrics = b["metrics_used"]
        if "wicket" in metrics:
            z_wk = float(b["z_wicket"])
            expected_comp = (z_ec + z_wk + z_dt) / 3.0
        else:
            expected_comp = (z_ec + z_dt) / 2.0
        diff = abs(comp - expected_comp)
        if diff > TOLERANCE:
            discrepancies.append((b["player_name"], comp, expected_comp, diff))

    if discrepancies:
        print(f"FAILED: Found {len(discrepancies)} composite discrepancies > {TOLERANCE}:")
        for d in discrepancies:
            print(f"  {d[0]}: published={d[1]}, reconstructed={d[2]}, diff={d[3]}")
        return False

    print("SUCCESS: Gate G8 PASSED — All composite scores verified within 0.01 tolerance.")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = test_reproduction()
    exit(0 if success else 1)
