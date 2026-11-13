# Royals ScoutIQ — Data Pack Audit & Player Identity Cleaning Summary

**Execution Date:** 2026-11-11  
**Source Location:** `~/Downloads/data pack/` (Mirrored in `data/raw/data_pack/`)  
**Cleaned Output Location:** `data/cleaned/`  

---

## 1. Discovered Dataset Inventory

| Dataset | Row Count | File Size | Description & Key Columns |
| :--- | :--- | :--- | :--- |
| **`ball_by_ball.csv`** | 200,999 | 39.17 MB | Delivery-level records: `match_id`, `innings`, `overid`, `over_ball_num`, `striker_id`, `non_striker_id`, `bowler_id`, `batting_type`, `bowling_type`, `runs`, `is_wicket`, `dismissal_type`, `extras_type`, `pace_or_spin`. |
| **`matches.csv`** | 883 | 0.12 MB | Match metadata: `match_id`, `comp_id`, `match_date`, `home_team`, `away_team`, `toss_win_team_id`, `first_inn_revised_overs`, `second_inn_revised_overs`, `revised_target`. |
| **`playing_eleven.csv`** | 28,381 | 0.92 MB | Match squad lineups: `match_id`, `team_id`, `player_id`, `batting_order`, `is_played`, `is_captain`, `is_wk`, `is_impact`. |
| **`competition_team_player_mapping.csv`** | 6,413 | 0.44 MB | Official tournament squad registrations: `comp_id`, `comp_name`, `team_id`, `team_name`, `player_id`, `player_name`. |
| **`competitions.csv`** | 141 | 0.01 MB | Competition registry: `comp_id`, `comp_name`, `match_format` (T20I, IPL), `season` (2022–2026). |
| **`teams.csv`** | 353 | 0.01 MB | Team registry: `comp_id`, `team_id`, `team_name`. |
| **`Round 1 Problem Statement`** | 2 pages | 0.25 MB | Official SupeRR Selector Season 2 Problem Statement PDF. |

---

## 2. Key Cleaning Rules & Methodologies

### Rule 1: Strict Player ID Preservation
- `player_id` is the **single authoritative primary key** across the entire platform.
- Player IDs are **never mutated, fabricated, or merged without irrefutable proof**.
- All downstream search, profiles, rankings, and dossiers use `player_id` as the identity anchor.

### Rule 2: Canonical Display Name Normalization
Original names are retained in `player_master.original_name` and `player_aliases.csv`. Canonical display names follow official cricket broadcast conventions:
1. **Long formal names normalized:**
   - `Namboori Tilak Varma` → **Tilak Varma**
   - `Mahendra Singh Dhoni` → **MS Dhoni**
   - `Kumar Kartikeya Singh` → **Kumar Kartikeya**
   - `Gurkeerat Singh Mann` → **Gurkeerat Mann**
   - `Nishant Kumar Sindhu` → **Nishant Sindhu**
   - `Pieter Willem Mulder` → **Wiaan Mulder**
2. **Restored punctuation & case:**
   - `Nathan Coulter Nile` → **Nathan Coulter-Nile**
   - `Zach Lion Cachet` → **Zach Lion-Cachet**
   - `Naveen ul Haq` → **Naveen-ul-Haq**
   - `Shadley Van Schalkwyk` → **Shadley van Schalkwyk**
3. **Removed initial prefix padding:**
   - `M Shahrukh Khan` → **Shahrukh Khan**
   - `L Manvanth Kumar` → **Manvanth Kumar**
   - `R Sonu Yadav` → **Sonu Yadav**
4. **Stripped feed disambiguation numbers:**
   - `Sumit Kumar 1` (Delhi Capitals, IPL 2024) → **Sumit Kumar**
   - `Ahmed Raza 1` (UAE Captain) → **Ahmed Raza**
   - `Sandeep Goud 1` (Oman) → **Sandeep Goud**

### Rule 3: Multi-ID Disambiguation Without Destructive Merges
When the same name belongs to distinct international/domestic athletes, ScoutIQ preserves separate records:
- **Abdul Samad**:
  - `ID 7446`: Indian uncapped batter (Sunrisers Hyderabad / Lucknow Super Giants, IPL).
  - `ID 6922`: Pakistan international batter (Pakistan / Pakistan A).
- **Rashid Khan**:
  - `ID 4722`: Afghanistan / Gujarat Titans world-class leg-spinner.
  - `ID 20172`: Nepal international player.
- **Haider Ali**:
  - `ID 7338`: Pakistan international batter.
  - `ID 28756`: UAE international player.
- **Duplicate Feed IDs Documented**:
  - `Mohammad Ali`: `ID 20229` (45 balls in BBB) vs `ID 3083` (0 balls in BBB).
  - `Basil Hameed`: `ID 8638` (286 balls) vs `ID 39444` (34 balls in matches 37087, 37092, 37095).
  - `Muhammad Farooq`: `ID 27373` (134 balls) vs `ID 28978` (0 balls).

---

## 3. Critical Analytical Findings for Downstream Modeling

### Critical Discovery: Revised Overs Are Stored as Balls
In `matches.csv`, the columns `first_inn_revised_overs` and `second_inn_revised_overs` **store integer balls, not decimal overs**:
- **Proof:** Match 21586 (IPL 2023 Final CSK vs GT) has `second_inn_revised_overs = 90`. This represents 15 overs ($15 \times 6 = 90$ balls).
- **Proof:** Match 17395 (IND vs AUS 8-over contest) has `revised_overs = 48` ($8 \times 6 = 48$ balls).
- **Impact on Pressure Engine:** Any pressure calculation that evaluates Required Run Rate ($RRR = \text{runs} / \text{overs}$) must divide these values by $6.0$. Treating 90 as 90 overs would produce an artificially low required rate ($1.9$ RPO instead of $11.4$ RPO).

### Extras and Legitimate Balls
- In `ball_by_ball.csv`, `extras_type == 'wide'` does **not** count towards `balls_faced` by the batter.
- `runs` indicates batter runs off the bat; `extras1_runs` indicates penalty extras.
- Byes and Leg-byes are fielding extras and are not charged against bowler runs conceded.
- Run-outs are not credited as bowler wickets.

---

## 4. Summary Telemetry

- **Total Unique Players in Master:** `1,217`
- **IPL Cohort Players:** `477`
- **International T20I Cohort Players:** `990`
- **Officially Verified Identities:** `1,213`
- **Quality Issues Documented in Validation Report:** `14`

All generated clean outputs are strictly reproducible via `python3 scripts/clean_data_pack.py`.
