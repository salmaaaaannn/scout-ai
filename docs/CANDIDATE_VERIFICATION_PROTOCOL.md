# Candidate Verification Protocol
**Royals ScoutIQ | SupeRR Selector Season 2 — Round 1**  
**Version:** 1.2  
**Status:** Ratified  
**Target Opportunity ID:** 1792758  
**Purpose:** Apply a consistent, auditable, evidence-first verification process to the Unstop candidate pool before producing any age ranking or scouting recommendation.

---

## 1. Source Hierarchy & Field-Level Evidence Standards

Use the strongest available source for each individual claim; **a source that verifies one field does not automatically verify another.**

| Priority | Source Category | Permitted Use |
| :---: | :--- | :--- |
| **1** | **Official BCCI records, state cricket association records, official tournament/squad records** | DOB, team affiliation, senior international/contract records where explicitly stated, and competition statistics. |
| **2** | **Official Rajasthan Royals case/data pack** (if explicitly contains relevant field) | Only the fields actually supplied in the pack; record the pack version and page/section. |
| **3** | **ESPNcricinfo player profiles and scorecards** | Corroboration of DOB, career appearances, and sourced statistics; *absence of a listed appearance alone does not prove a player is uncapped.* |
| **4** | **Official league/tournament sites and scorecards** (e.g., Maharaja Trophy KSCA, TNPL, UP T20, SMAT) | Tournament-specific statistics, squad membership, and role evidence. |
| **5** | **Reputable news reports and secondary databases** | Research leads and corroboration only; *not sufficient on their own for Tier 1 DOB or uncapped eligibility.* |

### Field-Level Evidence Rule
For every verified claim, the registry stores an explicit evidence object:
```json
{
  "claim": "Date of birth",
  "value_supported": "2006-08-28",
  "source_title": "Andre Siddharth Profile",
  "publisher": "ESPNcricinfo / TNCA",
  "source_url": "https://www.espncricinfo.com/cricketers/andre-siddharth-1457814",
  "source_type": "OFFICIAL_PROFILE",
  "retrieved_on": "2026-11-08",
  "checked_by": "Royals ScoutIQ Verification Team",
  "verification_status": "VERIFIED",
  "notes": "Corroborated against Tamil Nadu Cricket Association registration."
}
```

### Senior International Appearance Audit (Uncapped Verification Standard)
Establishing that a player has **no senior international cap** cannot be inferred merely because an online profile lacks an international section. An absent match on an ESPNcricinfo profile is not automatic proof of uncapped status.

Under Protocol v1.2, every verified candidate must undergo an auditable **Senior International Appearance Audit**, recording 7 independent fields:
1. **India Test Appearances** (must be 0)
2. **India ODI Appearances** (must be 0)
3. **India T20I Appearances** (must be 0)
4. **Other Full-Member Senior Appearances** (must be 0)
5. **Under-19 Appearances** (developmental history only; does NOT cap a player)
6. **India A / Emerging Appearances** (developmental history only; does NOT cap a player)
7. **BCCI Central Contract Status** (active central contract Grades A+, A, B, C indicate senior status)

Supporting evidence must be attached, and source coverage and limitations explicitly recorded. If evidence is missing, contradictory, or uninspected, the candidate's status remains strictly `PENDING_VERIFICATION`.

---

## 2. Eligibility & Representative-History Rules

1. **Age-Group and Development Squad Distinction:**
   * Record **Under-19**, **India A**, **India Emerging**, and other developmental representation separately from senior international appearances.
   * **Rule:** These appearances must **NOT**, under any circumstances, be treated as a senior international cap. U-19 World Cup captains (e.g., Uday Saharan, Yash Dhull) remain strictly uncapped domestic players under IPL auction rules.
2. **Nationality and Overseas Classification:**
   * Keep nationality/domestic status, overseas status, senior-cap history, and BCCI contract status as distinct fields.
   * Derive `ELIGIBLE_UNCAPPED`, `EXCLUDED_CAPPED`, `EXCLUDED_OVERSEAS`, or `PENDING_VERIFICATION` only by applying the actual Round 1 eligibility rules.
   * Overseas status must be recorded as an objective fact before applying any exclusion rule.

---

## 3. DOB and Age Calculation Precision

1. **DOB Verification Gate:**
   * A DOB is `VERIFIED` only when supported by an inspected Priority 1–3 source.
   * Record precision explicitly: `FULL_DATE`, `YEAR_MONTH_ONLY`, or `YEAR_ONLY`.
   * **Only a verified `FULL_DATE` may enter the exact-age primary ranking.**
2. **Reference Cutoff Dates:**
   * **Primary Date:** `2026-11-08` (Official Round 1 release date confirmed in Annexure A, Clause 5).
   * **Secondary Date:** `2027-04-01` (Projected IPL 2027 season start date; labeled as a projection reference, not a contest eligibility rule).
3. **Deterministic Age Arithmetic & Leap-Day Rule:**
   * Compute calendar years, months, and days deterministically.
   * **Leap-Day Handling:** For players born on **February 29**, in non-leap reference years, February 28 is used as the month anniversary for calendar-age components.
   * Exact `total_days` is calculated as `(reference_date - dob).days` and serves as the strict, integer sorting key.
   * Partial or unverified DOBs remain in the pending register with status `NOT_CALCULATED`.

---

## 4. Candidate Identity & Duplicate-Name Handling

1. **Raw Pool Immutability:**
   * The raw Unstop candidate pool (`data/raw/unstop_round1_players_pool.json`) is immutable: preserve order, dropdown indices, and duplicate entries.
2. **Name Ambiguity != Identical Person:**
   * A repeated name is not proof of a repeated person. Do not merge records unless identity is corroborated by distinguishing metadata (DOB, state association, playing role, or player ID).
3. **The "Himanshu Singh" Protocol (Indices 105 & 106):**
   * Retain both source indices: `original_entry_indices: [105, 106]`.
   * Mark identity resolution as `PENDING_DISAMBIGUATION`.
   * Any hypothesis (such as the Mumbai Ranji off-spinner) remains an unconfirmed research note.
   * **Rule:** An unresolved identity must NOT enter the final ranked list.

---

## 5. PENDING Policy & Ranking Gates

1. **Zero Guesswork Rule:**
   * Use `PENDING` whenever evidence is missing, uninspected, conflicting, or incomplete.
   * Never substitute guessed values, static defaults, or model estimates into statistical or demographic fields.
2. **Primary Youngest-Player List (List A) Requirements:**
   To qualify for List A, a candidate must satisfy all five gates:
   * **Gate 1 (Identity):** Candidate identity fully resolved against the Unstop dropdown pool (no `PENDING_DISAMBIGUATION`).
   * **Gate 2 (Eligibility):** Conclusively established as an Indian domestic uncapped player under official competition rules.
   * **Gate 3 (DOB):** Full date (`FULL_DATE`) verified by an inspected Priority 1–3 source.
   * **Gate 4 (Age Calculation):** Deterministic exact calendar age and `total_days` calculated for `2026-11-08`.
   * **Gate 5 (Sorting):** Sorted strictly by `total_days` ascending.
3. **Performance Statistics Independence:**
   * Performance statistics are **not** a prerequisite for List A. A player with verified DOB and uncapped status is ranked by age regardless of match tracking availability.
   * Statistical sample size thresholds and empirical Bayes shrinkage apply **only** to performance comparisons and rate metrics in supplementary analyses (List B), never to the primary age sort.
4. **Supplementary Balanced List (List B):**
   * Marked `NOT_GENERATED` until a transparent role-balancing policy and verified positional data are ratified.
5. **Separate Output Partitions:**
   * `data/processed/top10_absolute_youngest.json` (List A)
   * `data/processed/dob_verification_campaign.json` (Prioritized 335-candidate research campaign queue)
   * `data/processed/pending_verification.json` (Incomplete DOB, unresolved identity, or pending appearance audit)
   * `data/processed/excluded_candidates.json` (Verified capped or overseas exclusions with cited reasons)

---

## 6. Research Completeness Gate & Ranking Policy

1. **The Research Completeness Gate:**
   To unlock the definitive designation **"Top 10 Absolute Youngest"**, the evaluation system enforces a pool-wide research completeness gate requiring:
   * Complete identity resolution across all candidate records (zero `PENDING_DISAMBIGUATION`).
   * Verified `FULL_DATE` DOB from inspected Priority 1–3 sources for every potentially eligible domestic candidate.
   * Documented Senior International Appearance Audits for every domestic candidate.
   * Zero unresolved candidates who could potentially be younger than the 10th-ranked candidate.

2. **Provisional Mode Enforcement:**
   * If even a single potentially eligible domestic candidate remains in `PENDING_VERIFICATION` due to uninspected DOB or pending appearance records, the platform **strictly blocks** the absolute-youngest claim.
   * List A is automatically designated: **"Provisional Youngest Verified Candidates"**.
   * A prominent methodology limitation warning must be displayed in all dashboards and dossiers:
     > *"METHODOLOGY LIMITATION: This list represents the youngest candidates among those verified to date. Candidates in the Unstop pool remain in the verification queue awaiting primary source DOB and Senior International Appearance Audits. Because unverified candidates could be younger, this ranking is PROVISIONAL and strictly for internal research."*
   * The designation *"Top 10 Absolute Youngest"* is unlocked only when research completeness reaches 100%.

3. **Prohibition of Unsupported Statistics:**
   * No synthetic, uninspected, or simulated metrics may be presented as verified data.
   * Death-over strike rates, phase metrics, release heights, bowling speeds, and speculative auction hammer prices are strictly excluded unless supported by verified ball-by-ball match tracking data.
   * Use `null` or `"N/A — insufficient verified sample"` for missing statistical fields.

