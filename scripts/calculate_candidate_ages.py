"""
Candidate Age Calculation & Verification Routing (Protocol v1.1)
Royals ScoutIQ | SupeRR Selector Season 2 - Round 1
Opportunity ID: 1792758

Enforces 5 Sequential Verification Gates:
  Gate 1: Identity Resolution (Rejects PENDING_DISAMBIGUATION, e.g. duplicate Himanshu Singh)
  Gate 2: Eligibility & Cap Status (Excludes Capped and Overseas)
  Gate 3: DOB Precision & Verification (Requires verified FULL_DATE from Priority 1-3 source)
  Gate 4: Deterministic Age Arithmetic (2026-11-08 Primary, 2027-04-01 Secondary)
  Gate 5: Primary Age Ranking (Strict total_days sort key ascending)

Supports:
  --dry-run: Output routing statistics without writing files
  --registry: Custom registry JSON path
  --output-dir: Custom output directory
"""

import argparse
import calendar
import json
import sys
from datetime import date, datetime
from pathlib import Path


PRIMARY_CUTOFF = date(2026, 11, 8)
SECONDARY_CUTOFF = date(2027, 4, 1)


def calculate_calendar_age(dob: date, cutoff: date) -> tuple[int, int, int, int]:
    """
    Computes exact calendar (years, months, days, total_days) between DOB and cutoff date.
    Follows Protocol v1.1:
      - Deterministic calendar month progression
      - Feb 29 birthdates use Feb 28 in non-leap reference years
      - total_days is the exact (cutoff - dob).days
    """
    if cutoff < dob:
        raise ValueError(f"Cutoff date {cutoff} cannot be earlier than DOB {dob}")

    dob_day = dob.day
    dob_month = dob.month

    # If born on Feb 29 and cutoff year is not a leap year, use Feb 28 as anchor
    effective_dob_day = dob_day
    if dob_month == 2 and dob_day == 29 and not calendar.isleap(cutoff.year):
        effective_dob_day = 28

    years = cutoff.year - dob.year
    try:
        birthday_this_year = date(cutoff.year, dob_month, effective_dob_day)
    except ValueError:
        birthday_this_year = date(cutoff.year, 2, 28)

    if cutoff < birthday_this_year:
        years -= 1
        anchor_year = cutoff.year - 1
    else:
        anchor_year = cutoff.year

    # Determine starting anchor date for month/day accumulation
    if dob_month == 2 and dob_day == 29 and not calendar.isleap(anchor_year):
        anchor_date = date(anchor_year, 2, 28)
        month_anchor_day = 28
    else:
        anchor_date = date(anchor_year, dob_month, dob_day)
        month_anchor_day = dob_day

    months = 0
    cur_y = anchor_year
    cur_m = dob_month

    while True:
        next_m = cur_m + 1
        next_y = cur_y
        if next_m > 12:
            next_m = 1
            next_y += 1

        max_days_in_next_m = calendar.monthrange(next_y, next_m)[1]
        target_day = min(month_anchor_day, max_days_in_next_m)
        next_date = date(next_y, next_m, target_day)

        if next_date <= cutoff:
            months += 1
            cur_y = next_y
            cur_m = next_m
            anchor_date = next_date
        else:
            break

    days = (cutoff - anchor_date).days
    total_days = (cutoff - dob).days
    return years, months, days, total_days


def route_candidate(candidate: dict) -> tuple[str, str | None, dict | None]:
    """
    Evaluates candidate against sequential gates.
    Returns:
      (routing_destination, routing_reason, age_calculations_dict_or_None)
      where routing_destination is one of: 'ELIGIBLE', 'PENDING', 'EXCLUDED'
    """
    ident = candidate.get("identity", {})
    dob_data = candidate.get("dob", {})
    nat_data = candidate.get("nationality_and_status", {})
    cap_data = candidate.get("international_and_contract_record", {})
    elig_data = candidate.get("eligibility", {})

    # Gate 1: Candidate Identity Resolution
    if ident.get("name_status") == "PENDING_DISAMBIGUATION":
        return "PENDING", "Candidate identity unresolved (PENDING_DISAMBIGUATION - duplicate dropdown name)", None

    original_indices = ident.get("original_entry_indices", [])
    if len(original_indices) > 1 and ident.get("name_status") != "VERIFIED":
        return "PENDING", f"Duplicate dropdown entries at indices {original_indices}; disambiguation required", None

    # Gate 2: Eligibility & Senior Cap Status
    # Direct Exclusion rules:
    if elig_data.get("status") == "EXCLUDED_CAPPED":
        return "EXCLUDED", elig_data.get("reason", "Senior International Capped player"), None

    if elig_data.get("status") == "EXCLUDED_OVERSEAS":
        return "EXCLUDED", elig_data.get("reason", "Overseas player excluded from domestic uncapped pool"), None

    if nat_data.get("is_overseas") is True:
        return "EXCLUDED", f"Overseas player ({nat_data.get('country', 'International')}) excluded from Indian uncapped pool", None

    if cap_data.get("senior_capped_status") == "CAPPED":
        return "EXCLUDED", "Confirmed senior international appearance (BCCI/ICC record)", None

    if elig_data.get("status") != "ELIGIBLE_UNCAPPED":
        return "PENDING", elig_data.get("reason", "Uncapped domestic eligibility status is PENDING_VERIFICATION"), None

    # Gate 3: DOB Precision & Evidence Gate
    dob_status = dob_data.get("status")
    dob_val_str = dob_data.get("value")
    precision = dob_data.get("precision", "FULL_DATE" if dob_val_str and len(dob_val_str) == 10 else "UNKNOWN")

    if dob_status != "VERIFIED":
        return "PENDING", f"DOB status is {dob_status}; requires VERIFIED Priority 1-3 inspected source", None

    if not dob_val_str:
        return "PENDING", "Missing DOB value", None

    if precision != "FULL_DATE":
        return "PENDING", f"DOB precision is {precision}; Protocol requires FULL_DATE (YYYY-MM-DD) for exact age ranking", None

    # Parse Date
    try:
        dob_parsed = datetime.strptime(dob_val_str, "%Y-%m-%d").date()
    except ValueError:
        return "PENDING", f"Malformed DOB string '{dob_val_str}'; expected YYYY-MM-DD", None

    # Gate 4: Deterministic Age Calculation
    try:
        y1, m1, d1, tot1 = calculate_calendar_age(dob_parsed, PRIMARY_CUTOFF)
        y2, m2, d2, tot2 = calculate_calendar_age(dob_parsed, SECONDARY_CUTOFF)
    except Exception as e:
        return "PENDING", f"Age calculation failed: {str(e)}", None

    age_calcs = {
        "as_of_2026_11_08": {
            "years": y1,
            "months": m1,
            "days": d1,
            "total_days": tot1,
            "status": "CALCULATED",
        },
        "as_of_2027_04_01": {
            "years": y2,
            "months": m2,
            "days": d2,
            "total_days": tot2,
            "status": "CALCULATED",
        },
    }

    return "ELIGIBLE", None, age_calcs


def process_registry(registry_path: Path, output_dir: Path, dry_run: bool = False):
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    candidates = registry.get("candidates", [])
    print(f"Loaded {len(candidates)} candidates from {registry_path}")

    eligible_list = []
    pending_list = []
    excluded_list = []

    for cand in candidates:
        dest, reason, calcs = route_candidate(cand)
        cand_id = cand.get("candidate_id")
        cand_name = cand.get("identity", {}).get("unstop_name")

        if dest == "ELIGIBLE":
            cand["age_calculations"] = calcs
            eligible_list.append(cand)
        elif dest == "EXCLUDED":
            record = {
                "candidate_id": cand_id,
                "name": cand_name,
                "exclusion_reason": reason,
                "details": cand,
            }
            excluded_list.append(record)
        else:  # PENDING
            record = {
                "candidate_id": cand_id,
                "name": cand_name,
                "pending_reason": reason,
                "details": cand,
            }
            pending_list.append(record)

    # Sort eligible by total_days ascending as of 2026-11-08
    eligible_list.sort(key=lambda c: c["age_calculations"]["as_of_2026_11_08"]["total_days"])

    print("\n--- Verification Pipeline Routing Summary ---")
    print(f"Total candidates evaluated: {len(candidates)}")
    print(f"Verified Eligible (Rankable): {len(eligible_list)}")
    print(f"Pending Verification:        {len(pending_list)}")
    print(f"Excluded (Capped/Overseas):   {len(excluded_list)}")
    total_routed = len(eligible_list) + len(pending_list) + len(excluded_list)
    assert total_routed == len(candidates), f"Routing mismatch! {total_routed} != {len(candidates)}"
    print(f"Exact-partition assertion passed: Every candidate routed exactly once ({total_routed}/{len(candidates)}).")

    if dry_run:
        print("\n[DRY RUN MODE ENABLED] No output files written to disk.")
        if eligible_list:
            print("\nTop 5 Eligible Previews:")
            for idx, c in enumerate(eligible_list[:5], 1):
                name = c["identity"]["unstop_name"]
                c8 = c["age_calculations"]["as_of_2026_11_08"]
                print(f"  {idx}. {name} | {c8['years']}y {c8['months']}m {c8['days']}d ({c8['total_days']} total days)")
        return

    # Write Outputs
    output_dir.mkdir(parents=True, exist_ok=True)

    # Research Completeness Gate Evaluation
    classification_resolved = len(eligible_list) + len(excluded_list)
    classification_coverage_pct = round((classification_resolved / len(candidates)) * 100, 2)
    absolute_ranking_unlocked = len(pending_list) == 0
    list_title = "Top 10 Absolute Youngest Verified Uncapped Players" if absolute_ranking_unlocked else "Provisional Youngest Verified Candidates"
    
    if absolute_ranking_unlocked:
        gate_status = "UNLOCKED_ABSOLUTE_MODE"
    elif classification_coverage_pct >= 99.0:
        gate_status = "VERIFIED_COVERAGE_WITH_RANKING_LIMITATION"
    else:
        gate_status = "LOCKED_PROVISIONAL_MODE"

    methodology_limitation = (
        f"METHODOLOGY LIMITATION: Candidate classification coverage: {classification_coverage_pct}% "
        f"({classification_resolved} of {len(candidates)} unique candidates). Of these, {len(eligible_list)} are currently verified "
        f"as eligible uncapped candidates, {len(excluded_list)} are classified as excluded under the documented eligibility audit, "
        f"and {len(pending_list)} remain in manual review. "
        "List A presents the 10 youngest candidates among the verified eligible pool. "
        "It is not represented as the absolute youngest across all 335 until unresolved candidates are cleared."
        if not absolute_ranking_unlocked
        else "Complete candidate pool verified under Protocol v1.2."
    )

    # List A: Provisional or Absolute
    top10_file = output_dir / "top10_absolute_youngest.json"
    top10_payload = {
        "metadata": {
            "list_type": "List A (Primary Round 1 Entry)",
            "title": list_title,
            "absolute_ranking_unlocked": absolute_ranking_unlocked,
            "gate_status": gate_status,
            "methodology_limitation": methodology_limitation,
            "blocking_reasons": [
                f"{len(pending_list)} domestic candidates remain pending DOB / appearance audit. Unverified candidates may be younger."
            ] if not absolute_ranking_unlocked else [],
            "primary_cutoff": str(PRIMARY_CUTOFF),
            "secondary_cutoff": str(SECONDARY_CUTOFF),
            "total_verified_eligible_pool": len(eligible_list),
            "generated_on": datetime.now().isoformat(),
        },
        "ranked_candidates": eligible_list[:10],
    }
    with open(top10_file, "w", encoding="utf-8") as f:
        json.dump(top10_payload, f, indent=2, ensure_ascii=False)
    print(f"Written List A ({list_title}) to {top10_file}")

    # Full DOB Verification Campaign Queue
    campaign_file = output_dir / "dob_verification_campaign.json"
    campaign_queue = []
    for c in candidates:
        cid = c["candidate_id"]
        uname = c["identity"]["unstop_name"]
        vname = c["identity"].get("verified_name")
        dob_val = c["dob"].get("value")
        dob_prec = c["dob"].get("precision")
        dob_stat = c["dob"].get("status")
        ev_list = c["dob"].get("evidence", [])
        src_title = ev_list[0].get("source_title") if ev_list else None
        src_url = ev_list[0].get("source_url") if ev_list else None
        checked_dt = c["verification"].get("checked_on")
        rev_notes = "; ".join(c["verification"].get("review_notes", [])) if c["verification"].get("review_notes") else None
        elig = c["eligibility"]["status"]
        name_stat = c["identity"].get("name_status")

        if elig == "ELIGIBLE_UNCAPPED":
            tier = "TIER_1_VERIFIED_UNCAPPED"
        elif name_stat == "PENDING_DISAMBIGUATION":
            tier = "TIER_2_DISAMBIGUATION_REQUIRED"
        elif "EXCLUDED" in elig:
            tier = "TIER_5_AUDITED_EXCLUSION"
        elif c["playing_profile"].get("state_team") or c["playing_profile"].get("role"):
            tier = "TIER_3_DOMESTIC_ACTIVE_ROSTER"
        else:
            tier = "TIER_4_UNRESEARCHED_DOMESTIC"

        campaign_queue.append({
            "candidate_id": cid,
            "unstop_name": uname,
            "verified_name": vname,
            "dob": dob_val,
            "dob_precision": dob_prec,
            "dob_source_title": src_title,
            "dob_source_url": src_url,
            "checked_date": checked_dt,
            "verification_status": dob_stat if dob_stat != "PENDING" else "PENDING_INSPECTION",
            "priority_tier": tier,
            "eligibility_status": elig,
            "playing_role": c["playing_profile"].get("role"),
            "state_team": c["playing_profile"].get("state_team"),
            "reviewer_notes": rev_notes or (
                "Awaiting primary source birth certificate or state association registration inspection."
                if dob_stat == "PENDING" else "Inspected and verified."
            )
        })

    tier_order = {
        "TIER_1_VERIFIED_UNCAPPED": 1,
        "TIER_2_DISAMBIGUATION_REQUIRED": 2,
        "TIER_3_DOMESTIC_ACTIVE_ROSTER": 3,
        "TIER_4_UNRESEARCHED_DOMESTIC": 4,
        "TIER_5_AUDITED_EXCLUSION": 5,
    }
    campaign_queue.sort(key=lambda x: (tier_order.get(x["priority_tier"], 99), x["candidate_id"]))

    campaign_payload = {
        "campaign_summary": {
            "total_candidates": len(candidates),
            "verified_candidates": len(eligible_list),
            "pending_candidates": len(pending_list),
            "excluded_candidates": len(excluded_list),
            "absolute_ranking_unlocked": absolute_ranking_unlocked,
            "gate_status": gate_status,
            "methodology_limitation": methodology_limitation,
        },
        "prioritized_queue": campaign_queue,
    }
    with open(campaign_file, "w", encoding="utf-8") as f:
        json.dump(campaign_payload, f, indent=2, ensure_ascii=False)
    print(f"Written DOB verification campaign ({len(campaign_queue)} records) to {campaign_file}")

    # Pending List
    pending_file = output_dir / "pending_verification.json"
    with open(pending_file, "w", encoding="utf-8") as f:
        json.dump({"total_pending": len(pending_list), "pending_candidates": pending_list}, f, indent=2, ensure_ascii=False)
    print(f"Written Pending register to {pending_file}")

    # Excluded List
    excluded_file = output_dir / "excluded_candidates.json"
    with open(excluded_file, "w", encoding="utf-8") as f:
        json.dump({"total_excluded": len(excluded_list), "excluded_candidates": excluded_list}, f, indent=2, ensure_ascii=False)
    print(f"Written Excluded register to {excluded_file}")

    # Supplementary List B (explicitly marked NOT_GENERATED)
    balanced_file = output_dir / "top10_balanced.json"
    balanced_payload = {
        "metadata": {
            "list_type": "List B (Supplementary War Room Recommendation)",
            "title": "Role-Balanced Young Uncapped Stars",
            "status": "NOT_GENERATED",
            "rationale": "Marked NOT_GENERATED until a transparent role-balancing quota policy and verified positional data are formally ratified.",
        },
        "ranked_candidates": [],
    }
    with open(balanced_file, "w", encoding="utf-8") as f:
        json.dump(balanced_payload, f, indent=2, ensure_ascii=False)
    print(f"Written List B placeholder to {balanced_file}")


def main():
    parser = argparse.ArgumentParser(description="Calculate candidate ages and route candidates under Protocol v1.1")
    parser.add_argument("--registry", default="data/processed/candidate_verification_registry.json", help="Path to registry JSON")
    parser.add_argument("--output-dir", default="data/processed", help="Directory for output files")
    parser.add_argument("--dry-run", action="store_true", help="Report routing counts without writing files")
    args = parser.parse_args()

    registry_path = Path(args.registry)
    output_dir = Path(args.output_dir)

    if not registry_path.exists():
        print(f"Error: Registry file not found at {registry_path}", file=sys.stderr)
        sys.exit(1)

    process_registry(registry_path, output_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
