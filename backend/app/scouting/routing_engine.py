"""
Royals ScoutIQ - Candidate Eligibility & Routing Engine (Protocol v1.1)
Enforces sequential gates to partition all candidates into:
  - ELIGIBLE_UNCAPPED (Rankable in List A)
  - PENDING_VERIFICATION (Incomplete DOB, unresolved disambiguation, pending cap check)
  - EXCLUDED_CAPPED (Senior international cap confirmed)
  - EXCLUDED_OVERSEAS (Overseas national confirmed)
"""

from typing import Tuple, Dict, Any, Optional
from backend.app.scouting.age_engine import AgeCalculationEngine, PRIMARY_CUTOFF, SECONDARY_CUTOFF


class EligibilityRoutingEngine:
    @staticmethod
    def route_candidate(candidate: Dict[str, Any]) -> Tuple[str, Optional[str], Optional[Dict[str, Any]]]:
        """
        Evaluates candidate against sequential gates.
        Returns: (destination_bucket, routing_reason, age_calculations_dict_or_None)
        destination_bucket is one of:
          'ELIGIBLE', 'PENDING', 'EXCLUDED'
        """
        ident = candidate.get("identity", {})
        dob_data = candidate.get("dob", {})
        nat_data = candidate.get("nationality_and_status", {})
        cap_data = candidate.get("international_and_contract_record", {})
        elig_data = candidate.get("eligibility", {})

        # Gate 1: Candidate Identity Resolution
        name_status = ident.get("name_status")
        if name_status == "PENDING_DISAMBIGUATION":
            return "PENDING", "Candidate identity unresolved (PENDING_DISAMBIGUATION - duplicate dropdown name)", None

        indices = ident.get("original_entry_indices", [])
        if len(indices) > 1 and name_status != "VERIFIED":
            return "PENDING", f"Duplicate dropdown entries at indices {indices}; identity disambiguation required", None

        # Gate 2: Eligibility & Senior Cap Exclusion
        elig_status = elig_data.get("status")
        if elig_status == "EXCLUDED_CAPPED":
            return "EXCLUDED", elig_data.get("reason", "Senior International Capped player"), None

        if elig_status == "EXCLUDED_OVERSEAS":
            return "EXCLUDED", elig_data.get("reason", "Overseas player excluded from domestic uncapped pool"), None

        if nat_data.get("is_overseas") is True:
            country = nat_data.get("country", "International")
            return "EXCLUDED", f"Overseas player ({country}) excluded from Indian domestic uncapped pool", None

        if cap_data.get("senior_capped_status") == "CAPPED":
            return "EXCLUDED", "Confirmed senior international cap (BCCI/ICC registry)", None

        if elig_status != "ELIGIBLE_UNCAPPED":
            return "PENDING", elig_data.get("reason", "Uncapped domestic eligibility status is PENDING_VERIFICATION"), None

        # Gate 3: DOB Precision & Evidence Gate
        dob_status = dob_data.get("status")
        dob_val = dob_data.get("value")
        precision = dob_data.get("precision", "FULL_DATE" if (dob_val and len(dob_val) == 10) else "UNKNOWN")

        if dob_status != "VERIFIED":
            return "PENDING", f"DOB status is '{dob_status}'; requires VERIFIED Priority 1-3 inspected source", None

        if not dob_val:
            return "PENDING", "Missing DOB value", None

        if precision != "FULL_DATE":
            return "PENDING", f"DOB precision is '{precision}'; Protocol requires FULL_DATE (YYYY-MM-DD)", None

        # Gate 4: Deterministic Age Calculation
        try:
            calcs = AgeCalculationEngine.calculate_candidate_ages(dob_val)
        except Exception as e:
            return "PENDING", f"Age calculation failed: {str(e)}", None

        return "ELIGIBLE", None, calcs
