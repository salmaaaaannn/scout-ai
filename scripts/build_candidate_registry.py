"""
Build Candidate Verification Registry (Version 1.0)
SupeRR Selector Season 2 - Rajasthan Royals IPL 2027 Auction Strategy
Opportunity ID: 1792758

Ingests raw Unstop pool (336 entries), preserves original dropdown indices
(including duplicate 'Himanshu Singh' at indices [105, 106]), and initializes
every unresearched field to PENDING / NOT_RESEARCHED / NOT_CALCULATED.
Strictly zero synthetic or guessed values.
"""

import json
from datetime import datetime
from pathlib import Path


def build_candidate_registry():
    raw_path = Path("data/raw/unstop_round1_players_pool.json")
    output_path = Path("data/processed/candidate_verification_registry.json")

    with open(raw_path, "r", encoding="utf-8") as f:
        raw_pool = json.load(f)

    now_iso = datetime.now().isoformat()

    # Track indices for each candidate name to preserve dropdown indexing
    name_to_indices = {}
    for idx, entry in enumerate(raw_pool):
        name = entry.get("name", "").strip()
        if name not in name_to_indices:
            name_to_indices[name] = []
        name_to_indices[name].append(idx)

    candidates = []
    candidate_counter = 1

    for name, indices in name_to_indices.items():
        candidate_id = f"UNSTOP_{candidate_counter:04d}"
        candidate_counter += 1

        candidate_record = {
            "candidate_id": candidate_id,
            "identity": {
                "unstop_name": name,
                "verified_name": None,
                "name_status": "PENDING",
                "original_entry_indices": indices,
            },
            "dob": {
                "value": None,
                "status": "PENDING",
                "evidence": [],
            },
            "nationality_and_status": {
                "country": None,
                "is_indian_domestic_player": None,
                "is_overseas": None,
                "status": "PENDING",
                "evidence": [],
            },
            "international_and_contract_record": {
                "senior_india_international_appearances": None,
                "bcci_senior_central_contract_status": "PENDING",
                "senior_capped_status": "PENDING",
                "status": "PENDING",
                "evidence": [],
            },
            "playing_profile": {
                "role": None,
                "batting_hand": None,
                "bowling_style": None,
                "state_team": None,
                "status": "PENDING",
                "evidence": [],
            },
            "performance_data": {
                "source_status": "NOT_RESEARCHED",
                "statistics": {},
                "evidence": [],
            },
            "age_calculations": {
                "as_of_2026_11_08": {
                    "years": None,
                    "months": None,
                    "days": None,
                    "total_days": None,
                    "status": "NOT_CALCULATED",
                },
                "as_of_2027_04_01": {
                    "years": None,
                    "months": None,
                    "days": None,
                    "total_days": None,
                    "status": "NOT_CALCULATED",
                },
            },
            "eligibility": {
                "competition_rule_reference": "Annexure A, Clause 5 (Round 1: Youngest Uncapped Player)",
                "status": "PENDING_VERIFICATION",
                "reason": "Initial unresearched state from raw Unstop pool",
                "evidence": [],
            },
            "verification": {
                "overall_status": "PENDING_VERIFICATION",
                "checked_by": None,
                "checked_on": None,
                "review_notes": [],
            },
        }

        # If duplicate entry in dropdown, add a note to review_notes
        if len(indices) > 1:
            candidate_record["verification"]["review_notes"].append(
                f"Duplicate entry in Unstop raw pool at dropdown indices {indices}. Preserved under single verified identity."
            )

        candidates.append(candidate_record)

    registry = {
        "registry_metadata": {
            "registry_version": "1.0",
            "competition": "SupeRR Selector Season 2",
            "opportunity_id": "1792758",
            "source_pool": "data/raw/unstop_round1_players_pool.json",
            "source_pool_count": len(raw_pool),
            "unique_candidate_count": len(candidates),
            "created_on": now_iso,
            "last_updated": now_iso,
            "age_cutoffs": {
                "primary": "2026-11-08",
                "secondary": "2027-04-01",
                "primary_cutoff_basis": "Round 1 release date (2026-11-08) confirmed per Annexure A Clause 5",
            },
        },
        "candidates": candidates,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {output_path}")
    print(f"Total raw pool entries: {len(raw_pool)}")
    print(f"Unique candidates registered: {len(candidates)}")
    for c in candidates:
        if len(c["identity"]["original_entry_indices"]) > 1:
            print(f"Duplicate mapped: {c['identity']['unstop_name']} -> Indices {c['identity']['original_entry_indices']}")


if __name__ == "__main__":
    build_candidate_registry()
