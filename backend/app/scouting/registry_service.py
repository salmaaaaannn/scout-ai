"""
Royals ScoutIQ - Candidate Registry & Verification Management Service
Handles candidate ingestion, field-level evidence tracking, eligibility routing,
and export generation for Round 1 Scouting Intelligence.
"""

import io
import csv
import json
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.app.scouting.age_engine import AgeCalculationEngine, PRIMARY_CUTOFF, SECONDARY_CUTOFF
from backend.app.scouting.routing_engine import EligibilityRoutingEngine
from backend.app.scouting.models import (
    IdentityStatus,
    DOBPrecision,
    VerificationStatus,
    EligibilityStatus,
    ProvenanceStatus,
    EvidenceItem,
    VerificationUpdateRequest,
    DisambiguationRequest,
)


class CandidateRegistryService:
    def __init__(self, registry_file: Optional[Path] = None, raw_pool_file: Optional[Path] = None):
        self.root_dir = Path(__file__).resolve().parent.parent.parent.parent
        self.registry_file = registry_file or (self.root_dir / "data" / "processed" / "candidate_verification_registry.json")
        self.raw_pool_file = raw_pool_file or (self.root_dir / "data" / "raw" / "unstop_round1_players_pool.json")
        self.metadata: Dict[str, Any] = {}
        self.candidates: Dict[str, Dict[str, Any]] = {}  # candidate_id -> record
        self._load_or_initialize()

    def _load_or_initialize(self):
        """Loads from candidate_verification_registry.json if present, else ingests from raw pool."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.metadata = data.get("registry_metadata", {})
                for c in data.get("candidates", []):
                    self.candidates[c["candidate_id"]] = c
                if self.candidates:
                    return
            except Exception as e:
                print(f"Warning: Failed to load registry file: {e}. Rebuilding from raw pool.")

        self.ingest_from_raw_pool()

    def ingest_from_raw_pool(self, raw_entries: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Ingests 336 entries from raw Unstop pool.
        Preserves original dropdown order, indices, and duplicates (indices [105, 106] for Himanshu Singh).
        """
        if raw_entries is None:
            if not self.raw_pool_file.exists():
                raise FileNotFoundError(f"Raw pool file not found at {self.raw_pool_file}")
            with open(self.raw_pool_file, "r", encoding="utf-8") as f:
                raw_entries = json.load(f)

        now_iso = datetime.now().isoformat()
        name_to_indices: Dict[str, List[int]] = {}
        for idx, entry in enumerate(raw_entries):
            name = entry.get("name", "").strip()
            if name:
                if name not in name_to_indices:
                    name_to_indices[name] = []
                name_to_indices[name].append(idx)

        self.candidates.clear()
        counter = 1

        for name, indices in name_to_indices.items():
            candidate_id = f"UNSTOP_{counter:04d}"
            counter += 1

            is_duplicate = len(indices) > 1
            name_status = "PENDING_DISAMBIGUATION" if is_duplicate else "PENDING"

            record = {
                "candidate_id": candidate_id,
                "identity": {
                    "unstop_name": name,
                    "verified_name": None,
                    "name_status": name_status,
                    "original_entry_indices": indices,
                },
                "dob": {
                    "value": None,
                    "precision": None,
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
                    "other_full_member_senior_appearances": None,
                    "bcci_senior_central_contract_status": "PENDING",
                    "senior_capped_status": "PENDING",
                    "u19_india_a_representation": None,
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
                    "provenance": "UNSUPPORTED",
                    "statistics": {},
                    "evidence": [],
                },
                "age_calculations": {
                    "as_of_2026_11_08": {
                        "years": None, "months": None, "days": None, "total_days": None,
                        "status": "NOT_CALCULATED"
                    },
                    "as_of_2027_04_01": {
                        "years": None, "months": None, "days": None, "total_days": None,
                        "status": "NOT_CALCULATED"
                    }
                },
                "eligibility": {
                    "competition_rule_reference": "Annexure A, Clause 5 (Round 1: Youngest Uncapped Player)",
                    "status": "PENDING_VERIFICATION",
                    "reason": "Initial unresearched state from raw Unstop pool",
                    "evidence": []
                },
                "verification": {
                    "overall_status": "PENDING_VERIFICATION",
                    "checked_by": None,
                    "checked_on": None,
                    "review_notes": []
                }
            }

            if is_duplicate:
                record["verification"]["review_notes"].append(
                    f"Duplicate entry in Unstop dropdown at indices {indices}. Preserved under single identity; flagged PENDING_DISAMBIGUATION."
                )

            self.candidates[candidate_id] = record

        self.metadata = {
            "registry_version": "1.1",
            "competition": "SupeRR Selector Season 2",
            "opportunity_id": "1792758",
            "source_pool": str(self.raw_pool_file),
            "source_pool_count": len(raw_entries),
            "unique_candidate_count": len(self.candidates),
            "created_on": now_iso,
            "last_updated": now_iso,
            "age_cutoffs": {
                "primary": str(PRIMARY_CUTOFF),
                "secondary": str(SECONDARY_CUTOFF),
                "primary_cutoff_basis": "Round 1 release date (2026-11-08) confirmed per Annexure A Clause 5",
            }
        }

        self.save_registry()
        return {
            "total_entries_ingested": len(raw_entries),
            "unique_candidates_registered": len(self.candidates),
            "duplicates_tracked": sum(1 for c in self.candidates.values() if len(c["identity"]["original_entry_indices"]) > 1),
            "status": "INGESTION_COMPLETE"
        }

    def save_registry(self):
        """Persists current state to JSON."""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "registry_metadata": self.metadata,
            "candidates": list(self.candidates.values()),
        }
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        return self.candidates.get(candidate_id)

    def find_candidate_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        clean_name = name.strip().lower()
        for c in self.candidates.values():
            if c["identity"]["unstop_name"].strip().lower() == clean_name:
                return c
            if c["identity"].get("verified_name") and c["identity"]["verified_name"].strip().lower() == clean_name:
                return c
        return None

    def list_candidates(
        self,
        query: Optional[str] = None,
        eligibility: Optional[str] = None,
        verification_status: Optional[str] = None,
        role: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Filtered listing with pagination."""
        results = list(self.candidates.values())

        if query:
            q = query.lower()
            results = [
                c for c in results
                if q in c["identity"]["unstop_name"].lower()
                or (c["identity"].get("verified_name") and q in c["identity"]["verified_name"].lower())
                or q in (c["playing_profile"].get("state_team") or "").lower()
            ]

        if eligibility:
            results = [c for c in results if c["eligibility"]["status"].upper() == eligibility.upper()]

        if verification_status:
            results = [c for c in results if c["verification"]["overall_status"].upper() == verification_status.upper()]

        if role:
            results = [c for c in results if role.lower() in (c["playing_profile"].get("role") or "").lower()]

        total_count = len(results)
        paginated = results[offset : offset + limit]

        return {
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "candidates": paginated,
        }

    def update_verification(self, req: VerificationUpdateRequest) -> Dict[str, Any]:
        """Updates candidate verification fields and recalculates eligibility & age."""
        cand = self.get_candidate(req.candidate_id)
        if not cand:
            raise KeyError(f"Candidate ID '{req.candidate_id}' not found in registry.")

        now_str = datetime.now().strftime("%Y-%m-%d")

        if req.verified_name:
            cand["identity"]["verified_name"] = req.verified_name
            cand["identity"]["name_status"] = "VERIFIED"

        if req.dob:
            cand["dob"]["value"] = req.dob
            cand["dob"]["precision"] = req.dob_precision.value if req.dob_precision else "FULL_DATE"
            cand["dob"]["status"] = "VERIFIED"

            # Recalculate deterministic age
            try:
                ages = AgeCalculationEngine.calculate_candidate_ages(req.dob)
                cand["age_calculations"] = ages
            except Exception as e:
                cand["verification"]["review_notes"].append(f"Age calculation failed: {str(e)}")

        if req.country is not None:
            cand["nationality_and_status"]["country"] = req.country
            cand["nationality_and_status"]["is_indian_domestic_player"] = req.is_indian_domestic
            cand["nationality_and_status"]["is_overseas"] = req.is_overseas
            cand["nationality_and_status"]["status"] = "VERIFIED"

        if req.senior_capped_status:
            cand["international_and_contract_record"]["senior_capped_status"] = req.senior_capped_status
            cand["international_and_contract_record"]["status"] = "VERIFIED"

        cand["international_and_contract_record"]["india_test_appearances"] = getattr(req, "india_test_appearances", 0)
        cand["international_and_contract_record"]["india_odi_appearances"] = getattr(req, "india_odi_appearances", 0)
        cand["international_and_contract_record"]["india_t20i_appearances"] = getattr(req, "india_t20i_appearances", 0)
        cand["international_and_contract_record"]["other_full_member_senior_appearances"] = getattr(req, "other_senior_international_appearances", 0)
        cand["international_and_contract_record"]["u19_appearances"] = getattr(req, "u19_appearances", None)
        cand["international_and_contract_record"]["india_a_appearances"] = getattr(req, "india_a_appearances", None)
        cand["international_and_contract_record"]["bcci_central_contract"] = getattr(req, "bcci_central_contract", "NONE")
        cand["international_and_contract_record"]["audit_methodology"] = "Senior International Appearance Audit"
        if getattr(req, "source_coverage_and_limitations", None):
            cand["international_and_contract_record"]["source_coverage_and_limitations"] = req.source_coverage_and_limitations

        # Remove unsupported statistics - strictly enforce null or N/A
        cand["performance_data"]["statistics"] = {}
        cand["performance_data"]["source_status"] = "N/A — insufficient verified sample"

        if req.role:
            cand["playing_profile"]["role"] = req.role
        if req.batting_hand:
            cand["playing_profile"]["batting_hand"] = req.batting_hand
        if req.bowling_style:
            cand["playing_profile"]["bowling_style"] = req.bowling_style
        if req.state_team:
            cand["playing_profile"]["state_team"] = req.state_team
        cand["playing_profile"]["status"] = "VERIFIED"

        # Apply eligibility status or derive via router
        if req.eligibility_status:
            cand["eligibility"]["status"] = req.eligibility_status.value
        else:
            dest, reason, calcs = EligibilityRoutingEngine.route_candidate(cand)
            if dest == "ELIGIBLE":
                cand["eligibility"]["status"] = "ELIGIBLE_UNCAPPED"
                cand["eligibility"]["reason"] = "Identity, uncapped status, and full DOB verified under Protocol v1.1"
                if calcs:
                    cand["age_calculations"] = calcs
            elif dest == "EXCLUDED":
                if cand["nationality_and_status"].get("is_overseas"):
                    cand["eligibility"]["status"] = "EXCLUDED_OVERSEAS"
                else:
                    cand["eligibility"]["status"] = "EXCLUDED_CAPPED"
                cand["eligibility"]["reason"] = reason
            else:
                cand["eligibility"]["status"] = "PENDING_VERIFICATION"
                cand["eligibility"]["reason"] = reason

        # Attach evidence
        if req.evidence:
            ev_dict = req.evidence.dict() if hasattr(req.evidence, "dict") else dict(req.evidence)
            claim = ev_dict.get("claim", "")
            if "dob" in claim.lower():
                cand["dob"]["evidence"].append(ev_dict)
            elif "cap" in claim.lower() or "international" in claim.lower():
                cand["international_and_contract_record"]["evidence"].append(ev_dict)
            elif "nationality" in claim.lower():
                cand["nationality_and_status"]["evidence"].append(ev_dict)
            else:
                cand["eligibility"]["evidence"].append(ev_dict)

        cand["verification"]["checked_by"] = req.reviewer
        cand["verification"]["checked_on"] = now_str
        if req.reviewer_notes:
            cand["verification"]["review_notes"].append(req.reviewer_notes)

        # Set overall verification status
        if cand["eligibility"]["status"] == "ELIGIBLE_UNCAPPED":
            cand["verification"]["overall_status"] = "VERIFIED"
        elif "EXCLUDED" in cand["eligibility"]["status"]:
            cand["verification"]["overall_status"] = "EXCLUDED"
        else:
            cand["verification"]["overall_status"] = "PENDING_VERIFICATION"

        self.save_registry()
        return cand

    def resolve_disambiguation(self, req: DisambiguationRequest) -> Dict[str, Any]:
        """Resolves duplicate identity review (e.g. Himanshu Singh at indices [105, 106])."""
        cand = self.get_candidate(req.candidate_id)
        if not cand:
            raise KeyError(f"Candidate ID '{req.candidate_id}' not found.")

        cand["identity"]["name_status"] = req.resolution_status.value
        cand["identity"]["verified_name"] = req.disambiguated_name
        cand["verification"]["checked_by"] = req.reviewer
        cand["verification"]["checked_on"] = datetime.now().strftime("%Y-%m-%d")
        cand["verification"]["review_notes"].append(
            f"Disambiguation resolved by {req.reviewer}: {req.distinguishing_notes}"
        )

        self.save_registry()
        return cand

    def execute_routing(self) -> Dict[str, Any]:
        """
        Evaluates every candidate in registry against 5 sequential gates.
        Returns exact-partition summary counts.
        """
        eligible = []
        pending = []
        excluded = []

        for cand in self.candidates.values():
            dest, reason, calcs = EligibilityRoutingEngine.route_candidate(cand)
            if dest == "ELIGIBLE":
                cand["age_calculations"] = calcs
                eligible.append(cand)
            elif dest == "EXCLUDED":
                excluded.append({"candidate_id": cand["candidate_id"], "name": cand["identity"]["unstop_name"], "reason": reason, "details": cand})
            else:
                pending.append({"candidate_id": cand["candidate_id"], "name": cand["identity"]["unstop_name"], "reason": reason, "details": cand})

        # Sort eligible by total_days ascending
        eligible.sort(key=lambda c: c["age_calculations"]["as_of_2026_11_08"]["total_days"])

        total = len(self.candidates)
        assert len(eligible) + len(pending) + len(excluded) == total, "Routing partition mismatch"

        return {
            "total_candidates": total,
            "eligible_count": len(eligible),
            "pending_count": len(pending),
            "excluded_count": len(excluded),
            "eligible": eligible,
            "pending": pending,
            "excluded": excluded,
        }

    def get_research_completeness(self) -> Dict[str, Any]:
        """
        Requirement 6: Computes pool-wide research completeness and evaluates whether the final
        'Top 10 Absolute Youngest' designation is unlocked or locked in Provisional Mode.
        """
        total = len(self.candidates)
        verified_count = 0
        year_only_dob_count = 0
        missing_dob_count = 0
        unresolved_identity_count = 0
        excluded_rules_count = 0
        remaining_domestic_pending = 0

        for cand in self.candidates.values():
            elig = cand["eligibility"]["status"]
            dob_val = cand["dob"].get("value")
            dob_prec = cand["dob"].get("precision")
            dob_stat = cand["dob"].get("status")
            name_stat = cand["identity"].get("name_status")

            if name_stat == "PENDING_DISAMBIGUATION":
                unresolved_identity_count += 1

            if elig in ["EXCLUDED_CAPPED", "EXCLUDED_OVERSEAS"]:
                excluded_rules_count += 1
            elif elig == "ELIGIBLE_UNCAPPED":
                if dob_stat == "VERIFIED" and dob_prec == "FULL_DATE":
                    verified_count += 1
                else:
                    remaining_domestic_pending += 1
            else:  # PENDING_VERIFICATION
                remaining_domestic_pending += 1
                if dob_val is None:
                    missing_dob_count += 1
                elif dob_prec in ["YEAR_ONLY", "YEAR_MONTH_ONLY"]:
                    year_only_dob_count += 1

        blocking_reasons = []
        if remaining_domestic_pending > 0:
            blocking_reasons.append(
                f"{remaining_domestic_pending} potentially eligible domestic candidates remain pending DOB verification in the registry. Unverified candidates could be younger than those currently verified."
            )
        if unresolved_identity_count > 0:
            blocking_reasons.append(
                f"{unresolved_identity_count} candidate(s) remain with unresolved identity (PENDING_DISAMBIGUATION)."
            )
        if year_only_dob_count > 0:
            blocking_reasons.append(
                f"{year_only_dob_count} candidate(s) possess only year-level or partial DOB precision, preventing exact deterministic day-count sorting."
            )

        classification_resolved = verified_count + excluded_rules_count
        classification_coverage_pct = round((classification_resolved / total) * 100, 2)

        absolute_ranking_unlocked = len(blocking_reasons) == 0
        if absolute_ranking_unlocked:
            gate_status = "UNLOCKED_ABSOLUTE_MODE"
            title = "Top 10 Absolute Youngest Verified Uncapped Players"
        elif classification_coverage_pct >= 99.0:
            gate_status = "VERIFIED_COVERAGE_WITH_RANKING_LIMITATION"
            title = "Provisional Youngest Verified Candidates"
        else:
            gate_status = "LOCKED_PROVISIONAL_MODE"
            title = "Provisional Youngest Verified Candidates"

        methodology_limitation = (
            f"METHODOLOGY LIMITATION: Candidate classification coverage: {classification_coverage_pct}% "
            f"({classification_resolved} of {total} unique candidates). Of these, {verified_count} are currently verified "
            f"as eligible uncapped candidates, {excluded_rules_count} are classified as excluded under the documented eligibility audit, "
            f"and {remaining_domestic_pending} remain in manual review. "
            "List A presents the 10 youngest candidates among the verified eligible pool. "
            "It is not represented as the absolute youngest across all 335 until unresolved candidates are cleared."
            if not absolute_ranking_unlocked
            else "Complete candidate pool verified under Protocol v1.2."
        )

        return {
            "total_unique_candidates": total,
            "verified_candidates": verified_count,
            "classification_resolved": classification_resolved,
            "classification_coverage_pct": classification_coverage_pct,
            "year_only_dob_count": year_only_dob_count,
            "missing_dob_count": missing_dob_count,
            "unresolved_identity_count": unresolved_identity_count,
            "excluded_rules_count": excluded_rules_count,
            "remaining_domestic_pending_research": remaining_domestic_pending,
            "absolute_ranking_unlocked": absolute_ranking_unlocked,
            "gate_status": gate_status,
            "title": title,
            "blocking_reasons": blocking_reasons,
            "methodology_limitation": methodology_limitation,
        }

    def get_dob_verification_campaign(self) -> Dict[str, Any]:
        """
        Requirement 2: Full DOB verification campaign queue prioritizing domestic candidates.
        Provides field-level tracking for every candidate in the pool without inventing data.
        """
        completeness = self.get_research_completeness()
        queue = []

        for c in self.candidates.values():
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

            queue.append({
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

        tier_weights = {
            "TIER_1_VERIFIED_UNCAPPED": 1,
            "TIER_2_DISAMBIGUATION_REQUIRED": 2,
            "TIER_3_DOMESTIC_ACTIVE_ROSTER": 3,
            "TIER_4_UNRESEARCHED_DOMESTIC": 4,
            "TIER_5_AUDITED_EXCLUSION": 5,
        }
        queue.sort(key=lambda x: (tier_weights.get(x["priority_tier"], 99), x["candidate_id"]))

        return {
            "campaign_summary": completeness,
            "total_queue_count": len(queue),
            "prioritized_queue": queue,
        }

    def generate_list_a(self) -> Dict[str, Any]:
        """
        List A: Youngest Verified Uncapped Candidates (Round 1 Entry).
        - If research completeness gate is locked (pending domestic candidates exist),
          locks absolute claim and titles list 'Provisional Youngest Verified Candidates'.
        - Includes prominent methodology limitation explaining that unverified candidates could be younger.
        """
        routing = self.execute_routing()
        eligible = routing["eligible"]
        top10 = eligible[:10]
        completeness = self.get_research_completeness()

        list_title = completeness["title"]
        is_unlocked = completeness["absolute_ranking_unlocked"]

        return {
            "metadata": {
                "list_name": "List A (Primary Round 1 Entry)",
                "title": list_title,
                "absolute_ranking_unlocked": is_unlocked,
                "gate_status": completeness["gate_status"],
                "methodology_limitation": completeness["methodology_limitation"],
                "blocking_reasons": completeness["blocking_reasons"],
                "primary_cutoff_date": str(PRIMARY_CUTOFF),
                "secondary_projection_date": str(SECONDARY_CUTOFF),
                "sort_criterion": "Deterministic total_days elapsed since verified DOB (ascending)",
                "verified_eligible_pool_size": len(eligible),
                "total_pool_size": routing["total_candidates"],
                "selection_methodology": (
                    "Strict compliance with Round 1 objective. Candidates must satisfy sequential verification gates: "
                    "(1) Resolved identity, (2) Senior International Appearance Audit confirming uncapped status (0 Tests, 0 ODIs, 0 T20Is, zero full member caps), "
                    "(3) Full DOB verified by Priority 1-3 inspected source, (4) Deterministic age calculation with leap-day logic, "
                    "(5) Sorted strictly ascending by exact elapsed days. "
                    + ("Ranked provisionally while remaining pool candidates complete DOB verification." if not is_unlocked else "Fully ratified across entire pool.")
                ),
                "generated_at": datetime.now().isoformat(),
            },
            "top10_candidates": top10,
        }

    def generate_list_b(self) -> Dict[str, Any]:
        """
        List B: Role-Balanced Supplementary Shortlist.
        Addresses Rajasthan Royals roster depth vacancies across:
        - Batters
        - Wicketkeepers
        - Fast Bowlers
        - Spinners
        - All-Rounders
        Supplementary to List A; never alters List A order.
        """
        routing = self.execute_routing()
        eligible = routing["eligible"]

        if not eligible:
            return {
                "metadata": {
                    "list_name": "List B (Supplementary War Room Recommendation)",
                    "title": "Role-Balanced Young Uncapped Stars",
                    "status": "NOT_GENERATED",
                    "rationale": "Awaiting verified candidate pool population.",
                },
                "shortlist": [],
            }

        role_buckets = {
            "Batters": [],
            "Wicketkeepers": [],
            "Fast Bowlers": [],
            "Spinners": [],
            "All-Rounders": [],
        }

        for c in eligible:
            role = (c["playing_profile"].get("role") or "").lower()
            if "wicket" in role:
                role_buckets["Wicketkeepers"].append(c)
            elif "all-rounder" in role:
                role_buckets["All-Rounders"].append(c)
            elif "fast" in role or "pace" in role:
                role_buckets["Fast Bowlers"].append(c)
            elif "spin" in role or "orthodox" in role or "wrist" in role:
                role_buckets["Spinners"].append(c)
            else:
                role_buckets["Batters"].append(c)

        balanced_picks = []
        # Target quota: 3 Batters, 1 WK, 3 Fast Bowlers, 2 Spinners, 1 All-Rounder
        quota = [
            ("Batters", 3),
            ("Wicketkeepers", 1),
            ("Fast Bowlers", 3),
            ("Spinners", 2),
            ("All-Rounders", 1),
        ]
        for role_name, count in quota:
            picks = role_buckets[role_name][:count]
            balanced_picks.extend(picks)

        # If shortfall, backfill with youngest remaining
        if len(balanced_picks) < 10:
            picked_ids = {p["candidate_id"] for p in balanced_picks}
            for c in eligible:
                if c["candidate_id"] not in picked_ids and len(balanced_picks) < 10:
                    balanced_picks.append(c)

        return {
            "metadata": {
                "list_name": "List B (Supplementary War Room Recommendation)",
                "title": "Role-Balanced Young Uncapped Shortlist for Rajasthan Royals",
                "status": "ACTIVE_SUPPLEMENTARY",
                "quota_specification": "3 Batters, 1 Wicketkeeper, 3 Fast Bowlers, 2 Spinners, 1 All-Rounder",
                "rr_tactical_alignment": (
                    "Targets Rajasthan Royals 2027 roster balance: Indian fast-bowling depth (backup to overseas pacers), "
                    "post-Chahal spin succession, middle-order domestic batting stability, and high-scarcity pace all-rounders."
                ),
                "generated_at": datetime.now().isoformat(),
            },
            "shortlist": balanced_picks,
        }

    def compare_candidates(self, candidate_ids: List[str]) -> Dict[str, Any]:
        """Side-by-side comparison of 2 to 4 candidates."""
        profiles = []
        for cid in candidate_ids:
            c = self.get_candidate(cid)
            if c:
                profiles.append(c)

        return {
            "comparison_count": len(profiles),
            "candidates": profiles,
            "metric_matrix": {
                "candidate_names": [p["identity"]["unstop_name"] for p in profiles],
                "verified_dobs": [p["dob"].get("value") for p in profiles],
                "age_nov_8_2026": [
                    f"{p['age_calculations']['as_of_2026_11_08'].get('years')}y "
                    f"{p['age_calculations']['as_of_2026_11_08'].get('months')}m "
                    f"{p['age_calculations']['as_of_2026_11_08'].get('days')}d"
                    if p['age_calculations']['as_of_2026_11_08'].get('years') is not None else "Pending"
                    for p in profiles
                ],
                "total_days_nov_8": [
                    p["age_calculations"]["as_of_2026_11_08"].get("total_days") for p in profiles
                ],
                "roles": [p["playing_profile"].get("role", "Pending") for p in profiles],
                "state_teams": [p["playing_profile"].get("state_team", "Pending") for p in profiles],
                "eligibility_statuses": [p["eligibility"]["status"] for p in profiles],
            }
        }

    def export_csv(self) -> str:
        """Exports all candidates with full verification provenance as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "candidate_id", "unstop_name", "verified_name", "dob", "dob_precision", "dob_status",
            "age_years_nov8", "age_months_nov8", "age_days_nov8", "total_days_nov8",
            "age_years_apr1", "total_days_apr1", "country", "is_uncapped", "senior_capped_status",
            "role", "state_team", "eligibility_status", "verification_status", "primary_evidence_url"
        ])
        for c in self.candidates.values():
            a8 = c["age_calculations"].get("as_of_2026_11_08", {})
            a1 = c["age_calculations"].get("as_of_2027_04_01", {})
            ev_url = ""
            if c["dob"].get("evidence"):
                ev_url = c["dob"]["evidence"][0].get("source_url", "")
            writer.writerow([
                c["candidate_id"],
                c["identity"]["unstop_name"],
                c["identity"].get("verified_name", ""),
                c["dob"].get("value", ""),
                c["dob"].get("precision", ""),
                c["dob"].get("status", ""),
                a8.get("years", ""),
                a8.get("months", ""),
                a8.get("days", ""),
                a8.get("total_days", ""),
                a1.get("years", ""),
                a1.get("total_days", ""),
                c["nationality_and_status"].get("country", ""),
                c["nationality_and_status"].get("is_indian_domestic_player", ""),
                c["international_and_contract_record"].get("senior_capped_status", ""),
                c["playing_profile"].get("role", ""),
                c["playing_profile"].get("state_team", ""),
                c["eligibility"]["status"],
                c["verification"]["overall_status"],
                ev_url,
            ])
        return output.getvalue()
