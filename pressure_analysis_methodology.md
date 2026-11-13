# Royals ScoutIQ — Phase 2 Pressure Analysis Methodology

**As-of Date:** 2026-11-11 (UTC)  
**Tooling Environment:** Python 3.14.7 | Pure Standard Library Engine (`math`, `statistics`, `random`, `collections`, `csv`)  
**Bootstrap Seed:** `42` (Fixed for 100% deterministic reproducibility)  
**Resamples:** `1000` cluster bootstrap iterations per player  

---

## 1. Delivery Reconstruction & Match State Accounting

Match state is evaluated immediately **prior** to each legal delivery:
1. **Legal Ball Counting:**
   - Over numbers are computed deterministically from completed legal deliveries:
     $$\text{over\_number} = \lfloor \text{legal\_balls\_completed} / 6 \rfloor + 1$$
   - Illegal deliveries (`wide`, `Overstep`) do not increment legal balls completed.
2. **Revised Overs Handling (Critical Fix):**
   - In `matches.csv`, revised overs fields (`first_inn_revised_overs`, `second_inn_revised_overs`) store integer **balls**, not decimal overs.
   - For example, IPL 2023 Final CSK vs GT has `second_inn_revised_overs = 90` (15 overs $\times$ 6 balls = 90 balls).
   - Our engine divides by 6.0 when calculating required run rates ($RRR = \text{runs} / (\text{balls\_remaining} / 6.0)$).
3. **Extras Model:**
   - Total team delivery runs = `runs + extras1_runs + extras_2_runs`.
   - Bowler conceded runs = `runs + (extras1_runs if wide/overstep else 0) + extras_2_runs`. Byes and leg-byes are fielding extras and not charged to the bowler.
   - A **dot ball** is strictly defined as any delivery where `team_delivery_runs == 0` (Section 4.3).

---

## 2. Pressure Classification Rules (§5)

Evaluated in strict precedence order:

### Batter Pressure (ANY of):
1. `BAT_RRR_HIGH`: Chasing (Innings 2) AND Required Run Rate ($RRR$) $\ge 9.0$
2. `BAT_WICKETS_LOST`: Overs 7–20 AND $\ge 3$ wickets lost
3. `BAT_RRR_VS_CRR`: Chasing (Innings 2) AND $RRR \ge 1.5 \times CRR$

### Bowler Pressure (ANY of):
1. `BOWL_RRR_HIGH`: Defending (Innings 2) AND batting side $RRR \ge 9.0$
2. `BOWL_DEATH_OVERS`: Overs 17–20 AND match undecided ($6.0 \le RRR \le 18.0$ in Innings 2, or Innings 1 death overs)

---

## 3. Direction-Adjusted Delta Scoring & Noise Control (§7)

Positive delta ALWAYS represents improvement under pressure:
- **Batter:**
  - $\Delta SR = SR_{\text{pressure}} - SR_{\text{baseline}}$
  - $\Delta \text{Boundary}\% = \text{Boundary}\%_{\text{pressure}} - \text{Boundary}\%_{\text{baseline}}$
  - $\Delta \text{Dot}\% = \text{Dot}\%_{\text{baseline}} - \text{Dot}\%_{\text{pressure}}$ (fewer dots is better)
  - $\Delta \text{Dismissal Rate} = \text{Dismissal Rate}_{\text{baseline}} - \text{Dismissal Rate}_{\text{pressure}}$ (lower dismissal rate is better)
  - Composite = Mean($z(\Delta SR), z(\Delta \text{Boundary}\%), z(\Delta \text{Dot}\%), z(\Delta \text{Dismissal})$)
- **Bowler:**
  - $\Delta \text{Econ} = \text{Econ}_{\text{baseline}} - \text{Econ}_{\text{pressure}}$ (lower economy is better)
  - $\Delta \text{Wicket Rate} = \text{Wicket Rate}_{\text{pressure}} - \text{Wicket Rate}_{\text{baseline}}$
  - $\Delta \text{Dot}\% = \text{Dot}\%_{\text{pressure}} - \text{Dot}\%_{\text{baseline}}$ (more dots is better)
  - **Wicket-Rate Noise Control:** If pressure wickets $< 3$ OR baseline wickets $< 2$, $\Delta \text{Wicket Rate}$ is excluded from composite and remaining metrics are renormalised (`metrics_used = 'econ,dot'`).
- **Winsorization:** All deltas winsorized at 1st and 99th percentiles across qualified pool prior to z-scoring.

---

## 4. Match-Cluster Bootstrap (§8)

- Deliveries are clustered by `match_id`.
- 1000 resamples with replacement of each player's match clusters.
- 95% Percentile Confidence Interval ($2.5^{\text{th}}$ to $97.5^{\text{th}}$ percentile).
- Players with $< 5$ pressure match clusters are marked `ci_low = ci_high = 'NA'` and `robustness_flag = 'fragile'`.

---

## 5. Pre-Registered Robustness Families (§8.4)

- **Family A (Alternative Thresholds):** Batters $\ge 80 / 250$; Bowlers $\ge 64 / 225$.
- **Family B (Alternative Weights):** 50% core metric, 25% secondary, 25% tertiary.
- **Family C (Leave-One-Out):** Exclude IPL; exclude T20I.
- **Stability Rule:** `robustness_flag = 'stable'` if surviving in Top 10 in $\ge 2$ of the 3 families.

---

## 6. Long-Term Investment Scoring Framework (§9)

Category weights:
- Age / Development Potential: 15%
- Multi-Format Ability: 20%
- Role Flexibility: 10%
- Pressure Score (Normalized 0–100): 20%
- Fielding: 10%
- Consistency (Season Variance): 10%
- Fitness / Availability: 5%
- Rajasthan Royals Squad-Need Fit: 10%

All existing Rajasthan Royals players and retired players are strictly excluded from the shortlist per Section 10.
