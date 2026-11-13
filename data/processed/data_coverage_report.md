# Royals ScoutIQ — Phase 2 Data Coverage Pre-Check Report

**As-of Date:** 2026-11-11 (UTC)  
**Status:** **PASSED (SUFFICIENT_SAMPLE)** — Hard Gate §0.4 Satisfied  

---

## 1. Executive Summary & Gate Status

Per Section 0.4 of the Consolidated Brief, this report pre-audits data coverage before finalizing pressure rankings.  
- **Gate Requirement:** Minimum 10 qualified batters AND 10 qualified bowlers passing sample thresholds.
- **Result:** **107 Qualified Batters** and **181 Qualified Bowlers** pass default thresholds.
- **Family A Alternative Sample:** **92 Batters** and **151 Bowlers** pass stricter thresholds.
- **Gate Determination:** **PASS**. Proceeding with primary diagnostic rankings and long-term investment shortlist.

---

## 2. Ingested Dataset Dimensions

| Dimension | Count | Notes |
| :--- | :--- | :--- |
| **Total Matches** | 883 | 883 matches across IPL (371 matches) and T20 International tournaments (512 matches). |
| **Total Innings** | 1,724 | Reconstructed ball-by-ball. |
| **Total Deliveries** | 200,999 | Ingested delivery records from `ball_by_ball.csv`. |
| **Legal Deliveries** | 192,675 | Legal deliveries used for over counting and match state evaluation. |
| **Illegal Deliveries** | 8,286 | Wides and No-balls (Oversteps); accounted for team runs but excluded from legal ball counts. |
| **Super Over Deliveries** | 38 | Logged and segregated from primary 20-over rankings per §3.6. |
| **Derivable Effective Targets** | 867 | Derivable via revised target metadata or Innings 1 aggregate score + 1. |
| **Master Registry Players** | 1,217 | Verified player identities in `player_master.csv`. |
| **Players with ≥ 1 Ball Faced** | 888 | Strikers with recorded deliveries. |
| **Players with ≥ 1 Ball Bowled** | 647 | Bowlers with recorded deliveries. |

---

## 3. Sample Qualification Matrix

| Role | Default Threshold (§4.6) | Qualified Players | Family A Stricter Threshold (§8.4) | Family A Qualified |
| :--- | :--- | :--- | :--- | :--- |
| **Batters** | $\ge 60$ Pressure Balls & $\ge 200$ Baseline Balls | **107** | $\ge 80$ Pressure Balls & $\ge 250$ Baseline Balls | **92** |
| **Bowlers** | $\ge 50$ Pressure Balls & $\ge 180$ Baseline Balls | **181** | $\ge 64$ Pressure Balls & $\ge 225$ Baseline Balls | **151** |

---

## 4. Excluded Innings Register

Total innings excluded from target reconstruction: **0**.

