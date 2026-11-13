# ROYALS SCOUTIQ — ROUND 1 METHODOLOGY
## Identify the Most Reliable Players Under Pressure
### Rajasthan Royals | IPL 2027 Auction Strategy
**Client & Target Evaluators:** Giles Lindsay (Director of Strategy & Analytics) & Kumar Sangakkara (Head Coach)  
**As-of Date:** 12 November 2026 | **Bootstrap Resamples:** 1,000 (Seed: 42)

---

## 1. Executive Overview & Challenge Philosophy

The official mandate of **SupeRR Selector Season 2, Round 1** is to identify the most reliable cricket players under match pressure ahead of the IPL 2027 auction cycle.

Rather than looking at aggregate career statistics, raw boundaries, or tournament runs, our methodology measures **performance relative to leverage**. In modern T20 cricket, scoring 30 runs when chasing 12.0 RRR against elite bowling after a top-order collapse has vastly higher expected win probability value than scoring 50 runs in an unpressured dead rubber.

Our system reconstructs every delivery in chronological order and assigns a **pre-delivery Pressure Index** between 0 and 100 based strictly on match state immediately before the ball is bowled.

---

## 2. Pre-Delivery Pressure Index Formulation

Pressure is computed ball-by-ball. **Zero future information is utilized.**

### A. Innings 2 (Chasing Match Context)
Let $T$ be the effective target, $S$ cumulative score, $R = \max(0, T - S)$ runs required, $L$ legal balls completed, $B = \max(0, 120 - L)$ balls remaining, and $W_{\text{rem}} = 10 - W_{\text{lost}}$ wickets in hand.

1. **Required Run Rate (RRR) Logistic Scaling:**
   $$\text{RRR} = \frac{R}{B / 6.0}$$
   $$P_{\text{base}} = \frac{100}{1 + \exp(-0.52 \cdot (\text{RRR} - 8.8))}$$
   - When $\text{RRR} = 6.0$, $P_{\text{base}} \approx 20$ (Comfortable chase)
   - When $\text{RRR} = 8.8$, $P_{\text{base}} = 50$ (Par balance)
   - When $\text{RRR} = 11.5$, $P_{\text{base}} \approx 80$ (High pressure)
   - When $\text{RRR} \ge 14.0$, $P_{\text{base}} \ge 92$ (Extreme pressure)

2. **Resource & Wicket Deficit Multiplier:**
   Expected wickets lost at ball $L$:
   $$E[W_{\text{lost}}] = 10 \cdot \left(\frac{L}{120}\right)^{0.75}$$
   If actual wickets lost exceeds expected wickets lost:
   $$\Delta W = W_{\text{lost}} - E[W_{\text{lost}}] > 0 \implies P = P + \min(20.0, 4.0 \cdot \Delta W)$$

3. **Collapse Shock Factor:**
   If $\ge 2$ wickets have fallen within the last 12 legal balls, shock penalty: $+8.0$.

4. **Death Urgency & Closeness Floor:**
   - In overs 16–20 ($L \ge 90$), if $R > 0$ and $\text{RRR} \ge 7.5$: $+10.0$.
   - If $R \le 25$ runs and $B \le 18$ balls: Floor $P = 78.0$.
   - If chase is virtually completed ($R \le 15$ with $B \ge 36$ and $W_{\text{rem}} \ge 6$): Dampener $P \le 35.0$.

### B. Innings 1 (First Innings Scoring Context)
1. **Par Benchmark:** Calibrated at $168.0$ across tournament conditions.
2. **Projected Deficit:**
   $$\text{Proj} = S + \left(\text{CRR} \cdot 0.4 + 8.4 \cdot 0.6\right) \cdot \frac{B}{6.0}$$
   $$\text{Deficit} = \max(0, 168.0 - \text{Proj})$$
   $$P_{\text{base}} = 35.0 + \min(30.0, \text{Deficit} \cdot 1.0)$$
3. **Innings 1 Collapse Penalties:**
   - Powerplay ($L \le 36$): if $\ge 2$ wickets lost: $+20$; if $\ge 3$ wickets lost: $+35$.
   - Middle Overs ($36 < L \le 96$): if $\ge 4$ wickets lost: $+22$; if $\ge 5$ wickets lost: $+35$.
4. **Death Overs Acceleration:**
   Overs 17–20: Floor $P = 76.0 + 1.5 \cdot (W_{\text{rem}} - 3)$.

### C. Pressure Bands
- **Low (< 50):** 76,702 balls (39.8%)
- **Medium (50–74):** 47,154 balls (24.5%)
- **High (75–89):** 41,875 balls (21.7%)
- **Extreme (90–100):** 26,944 balls (14.0%)
**Primary Pressure Sample:** $P \ge 75.0$ (68,819 balls, 35.7% of all deliveries).

---

## 3. Reliability & Sample-Size Governance

1. **Qualification Thresholds:**
   - **Batters:** Minimum 60 pressure balls ($P \ge 75$) and 200 baseline balls ($P < 75$). (126 qualified, 105 eligible).
   - **Bowlers:** Minimum 48 pressure legal balls ($P \ge 75$) and 180 baseline legal balls ($P < 75$). (191 qualified, 152 eligible).
2. **Empirical-Bayes Shrinkage:**
   To prevent small samples from dominating the rankings, observed deltas are shrunk toward the population baseline:
   $$\hat{\theta}_i = \lambda_i \theta_i + (1 - \lambda_i) \mu_{\text{pop}}, \quad \lambda_i = \frac{N_i}{N_i + K}$$
   Where $K=40$ for batters and $K=36$ for bowlers.
3. **Match-Cluster Bootstrap Resampling:**
   1,000 resamples of match clusters with replacement (Seed 42) to establish 95% percentile confidence intervals $[CI_{\text{low}}, CI_{\text{high}}]$.
4. **Confidence Grades:**
   - **Grade A:** $N \ge 150$ balls (batters) / $N \ge 120$ balls (bowlers) with tight confidence bounds.
   - **Grade B:** $N \ge 90$ balls (batters) / $N \ge 75$ balls (bowlers).
   - **Grade C:** Threshold qualification ($60 \le N < 90$ / $48 \le N < 75$).

---

## 4. Rating Formulas: BPRI & BOWPRI

### A. Batter Pressure Reliability Index (BPRI, 0–100)
$$BPRI_{\text{raw}} = 0.30 \cdot z_{\Delta SR} + 0.20 \cdot z_{\Delta Avg} + 0.20 \cdot z_{\text{bound}} + 0.15 \cdot z_{\text{dot}} + 0.15 \cdot z_{\text{ci\_low}}$$
$$BPRI = \text{clamp}(50.0 + 15.0 \cdot z(BPRI_{\text{raw}}), 30.0, 99.0)$$

### B. Bowler Pressure Reliability Index (BOWPRI, 0–100)
$$BOWPRI_{\text{raw}} = 0.25 \cdot z_{\Delta Econ} + 0.25 \cdot z_{pEcon} + 0.20 \cdot z_{pWkt} + 0.15 \cdot z_{pDot} + 0.15 \cdot z_{\text{ci\_high}}$$
$$BOWPRI = \text{clamp}(50.0 + 15.0 \cdot z(BOWPRI_{\text{raw}}), 30.0, 99.0)$$

---

## 5. Unified Common Scale: Overall Pressure Reliability Index (OPRI)

To create the **Final Top 10 Overall Recommendations** without an arbitrary 5–5 quota:
1. Standardize qualified eligible batters' BPRI scores to $Z_{\text{BPRI}}$.
2. Standardize qualified eligible bowlers' BOWPRI scores to $Z_{\text{BOWPRI}}$.
3. Map $Z$-scores through the standard normal Cumulative Distribution Function (CDF):
   $$\text{OPRI} = 100 \cdot \Phi(Z) = 100 \cdot \frac{1}{2} \left[1 + \text{erf}\left(\frac{Z}{\sqrt{2}}\right)\right]$$
4. An OPRI score of 98.4 represents the exact same statistical extremity (~98.4th percentile) whether achieved by a batter or a bowler.
5. Sorted strictly descending by OPRI.
