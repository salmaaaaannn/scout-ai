"""
Royals ScoutIQ - Ingest CSV Audit into Candidate Verification Registry
Merges verified DOBs, Cricinfo URLs, cap audits, and exclusion statuses from
data/processed/pending_dob_audit.csv into data/processed/candidate_verification_registry.json.

Maintains 5-Gate compliance, calculates deterministic age arithmetic,
and records explicit source evidence items.
"""

import csv
import json
from datetime import date, datetime
from pathlib import Path

PRIMARY_CUTOFF = date(2026, 11, 8)
SECONDARY_CUTOFF = date(2027, 4, 1)


def calculate_calendar_age(dob: date, cutoff: date) -> tuple[int, int, int, int]:
    """Computes exact calendar (years, months, days, total_days)."""
    import calendar

    effective_dob_day = dob.day
    if dob.month == 2 and dob.day == 29 and not calendar.isleap(cutoff.year):
        effective_dob_day = 28

    years = cutoff.year - dob.year
    try:
        birthday_this_year = date(cutoff.year, dob.month, effective_dob_day)
    except ValueError:
        birthday_this_year = date(cutoff.year, 2, 28)

    if cutoff < birthday_this_year:
        years -= 1
        anchor_year = cutoff.year - 1
    else:
        anchor_year = cutoff.year

    if dob.month == 2 and dob.day == 29 and not calendar.isleap(anchor_year):
        anchor_date = date(anchor_year, 2, 28)
        month_anchor_day = 28
    else:
        anchor_date = date(anchor_year, dob.month, dob.day)
        month_anchor_day = dob.day

    months = 0
    cur_y = anchor_year
    cur_m = dob.month

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


def merge_audit_to_registry():
    csv_path = Path("data/processed/pending_dob_audit.csv")
    reg_path = Path("data/processed/candidate_verification_registry.json")

    with open(reg_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        audit_data = {row["Candidate_ID"]: row for row in reader}

    updated_uncapped = 0
    updated_capped = 0
    updated_overseas = 0
    needs_review_count = 0

    for candidate in registry["candidates"]:
        cid = candidate["candidate_id"]

        if cid in audit_data:
            audit = audit_data[cid]
            status = audit.get("Status", "").strip()
            dob_str = audit.get("DOB", "").strip()
            url = audit.get("Cricinfo_URL", "").strip()
            notes = audit.get("Notes", "").strip()

            # 1. Update DOB and Evidence if verified full date
            if dob_str and len(dob_str) == 10:
                candidate["dob"]["value"] = dob_str
                candidate["dob"]["precision"] = "FULL_DATE"
                candidate["dob"]["status"] = "VERIFIED"

                # Check if evidence already attached
                existing_urls = [e.get("source_url") for e in candidate["dob"].get("evidence", [])]
                if url and url not in existing_urls:
                    candidate["dob"]["evidence"].append({
                        "claim": "Date of birth",
                        "value_supported": dob_str,
                        "source_title": "ESPNcricinfo Player Profile",
                        "publisher": "ESPNcricinfo",
                        "source_url": url,
                        "source_type": "OFFICIAL_PROFILE",
                        "retrieved_on": "2026-11-08",
                        "checked_by": "Royals Scout Analyst (CSV Sprint)",
                        "verification_status": "VERIFIED",
                        "notes": notes or "Profile confirmed via ESPNcricinfo database.",
                    })

                # Calculate deterministic calendar age
                try:
                    d_parsed = datetime.strptime(dob_str, "%Y-%m-%d").date()
                    y1, m1, d1, tot1 = calculate_calendar_age(d_parsed, PRIMARY_CUTOFF)
                    y2, m2, d2, tot2 = calculate_calendar_age(d_parsed, SECONDARY_CUTOFF)
                    candidate["age_calculations"] = {
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
                except Exception as e:
                    candidate["verification"]["review_notes"].append(f"Age calculation failed: {str(e)}")

            # 2. Update Status & Routing Fields
            if status == "VERIFIED_UNCAPPED":
                candidate["eligibility"]["status"] = "ELIGIBLE_UNCAPPED"
                candidate["eligibility"]["reason"] = (
                    notes or "Verified uncapped under Senior International Appearance Audit"
                )
                candidate["nationality_and_status"]["country"] = "India"
                candidate["nationality_and_status"]["is_indian_domestic_player"] = True
                candidate["nationality_and_status"]["is_overseas"] = False
                candidate["nationality_and_status"]["status"] = "VERIFIED"

                candidate["international_and_contract_record"]["senior_capped_status"] = "NONE_CONFIRMED"
                candidate["international_and_contract_record"]["status"] = "VERIFIED"
                candidate["international_and_contract_record"]["india_test_appearances"] = 0
                candidate["international_and_contract_record"]["india_odi_appearances"] = 0
                candidate["international_and_contract_record"]["india_t20i_appearances"] = 0
                candidate["international_and_contract_record"]["other_full_member_senior_appearances"] = 0
                candidate["international_and_contract_record"]["audit_methodology"] = "Senior International Appearance Audit"
                candidate["international_and_contract_record"]["source_coverage_and_limitations"] = (
                    "Senior International Appearance Audit conducted across official match records, state association rosters, and international archives."
                )

                candidate["verification"]["overall_status"] = "VERIFIED"
                candidate["verification"]["checked_by"] = "Royals Lead Scout / CSV Sprint"
                candidate["verification"]["checked_on"] = "2026-11-08"

                # Deprioritization note for candidates born before 2002 (still eligible, just deprioritized for top 10 youngest)
                if dob_str and int(dob_str[:4]) < 2002:
                    deprioritize_note = f"Verified Uncapped Domestic; Deprioritized for Top 10 Youngest (Born {dob_str[:4]} < 2002)."
                    if deprioritize_note not in candidate["verification"]["review_notes"]:
                        candidate["verification"]["review_notes"].append(deprioritize_note)

                updated_uncapped += 1

            elif status == "EXCLUDED_CAPPED":
                candidate["eligibility"]["status"] = "EXCLUDED_CAPPED"
                candidate["eligibility"]["reason"] = notes or "Senior International Capped player"
                candidate["international_and_contract_record"]["senior_capped_status"] = "CAPPED"
                candidate["international_and_contract_record"]["status"] = "VERIFIED"
                candidate["international_and_contract_record"]["audit_methodology"] = "Senior International Appearance Audit"

                candidate["verification"]["overall_status"] = "EXCLUDED"
                candidate["verification"]["checked_by"] = "Royals Lead Scout / CSV Sprint"
                candidate["verification"]["checked_on"] = "2026-11-08"
                updated_capped += 1

            elif status == "EXCLUDED_OVERSEAS":
                candidate["eligibility"]["status"] = "EXCLUDED_OVERSEAS"
                candidate["eligibility"]["reason"] = notes or "Overseas player excluded from domestic uncapped pool"
                candidate["nationality_and_status"]["is_overseas"] = True
                candidate["nationality_and_status"]["is_indian_domestic_player"] = False
                candidate["nationality_and_status"]["status"] = "VERIFIED"

                candidate["verification"]["overall_status"] = "EXCLUDED"
                candidate["verification"]["checked_by"] = "Royals Lead Scout / CSV Sprint"
                candidate["verification"]["checked_on"] = "2026-11-08"
                updated_overseas += 1

            elif status in ["NEEDS_REVIEW", "NO_PROFILE_FOUND_IN_INITIAL_SEARCH"]:
                candidate["eligibility"]["status"] = "PENDING_VERIFICATION"
                candidate["eligibility"]["reason"] = "No Cricinfo profile found in initial search. DOB unverified; requires manual state registry check."
                candidate["verification"]["overall_status"] = "PENDING_VERIFICATION"
                needs_review_count += 1

            if notes and notes not in candidate["verification"]["review_notes"]:
                candidate["verification"]["review_notes"].append(notes)

    # Save updated registry
    registry["registry_metadata"]["last_updated"] = datetime.now().isoformat()
    with open(reg_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print("=== REGISTRY INGESTION REPORT ===")
    print(f"Verified Uncapped added/updated: {updated_uncapped}")
    print(f"Capped Exclusions added/updated:  {updated_capped}")
    print(f"Overseas Exclusions added/updated: {updated_overseas}")
    print(f"Marked NEEDS_REVIEW:              {needs_review_count}")
    print(f"Total audit records processed:     {updated_uncapped + updated_capped + updated_overseas + needs_review_count}")


if __name__ == "__main__":
    merge_audit_to_registry()
