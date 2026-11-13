"""
Unit Tests for Candidate Verification Protocol v1.1
Royals ScoutIQ | calculate_candidate_ages.py

Tests:
  1. test_known_dob_calculation: Verifies exact calendar arithmetic (Andre Siddharth 2006-08-28)
  2. test_leap_day_handling: Verifies Feb 29 birthdate handling in non-leap reference years
  3. test_duplicate_identity_routing: Verifies that unresolved names route to PENDING
  4. test_year_only_dob_routing: Verifies that YEAR_ONLY DOB precision routes to PENDING
"""

import sys
from pathlib import Path
from datetime import date
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.calculate_candidate_ages import (
    calculate_calendar_age,
    route_candidate,
    PRIMARY_CUTOFF,
    SECONDARY_CUTOFF,
)


def test_known_dob_calculation():
    """
    Test 1: Known DOB verification against Andre Siddharth (DOB: 2006-08-28).
    Expected:
      - As of 2026-11-08: 20 years, 2 months, 11 days (7377 total days)
      - As of 2027-04-01: 20 years, 7 months, 4 days (7521 total days)
    """
    dob = date(2006, 8, 28)

    y1, m1, d1, tot1 = calculate_calendar_age(dob, PRIMARY_CUTOFF)
    assert y1 == 20
    assert m1 == 2
    assert d1 == 11
    assert tot1 == (PRIMARY_CUTOFF - dob).days
    assert tot1 == 7377

    y2, m2, d2, tot2 = calculate_calendar_age(dob, SECONDARY_CUTOFF)
    assert y2 == 20
    assert m2 == 7
    assert d2 == 4
    assert tot2 == (SECONDARY_CUTOFF - dob).days
    assert tot2 == 7521


def test_leap_day_handling():
    """
    Test 2: Leap-day candidate handling (DOB: 2004-02-29).
    In non-leap year (2026 / 2027), birthday anniversary uses Feb 28.
    """
    dob = date(2004, 2, 29)

    y1, m1, d1, tot1 = calculate_calendar_age(dob, PRIMARY_CUTOFF)
    assert y1 == 22
    assert tot1 == (PRIMARY_CUTOFF - dob).days
    assert tot1 == 8288

    y2, m2, d2, tot2 = calculate_calendar_age(dob, SECONDARY_CUTOFF)
    assert y2 == 23
    assert tot2 == (SECONDARY_CUTOFF - dob).days
    assert tot2 == 8432


def test_duplicate_identity_routing():
    """
    Test 3: Duplicate identity routing (Himanshu Singh at indices [105, 106]).
    Must route to PENDING under PENDING_DISAMBIGUATION. Must NOT enter eligible list.
    """
    mock_candidate = {
        "candidate_id": "UNSTOP_0106",
        "identity": {
            "unstop_name": "Himanshu Singh",
            "verified_name": None,
            "name_status": "PENDING_DISAMBIGUATION",
            "original_entry_indices": [105, 106],
        },
        "dob": {
            "value": "2003-09-17",
            "status": "VERIFIED",
            "precision": "FULL_DATE",
        },
        "nationality_and_status": {
            "country": "India",
            "is_indian_domestic_player": True,
            "is_overseas": False,
            "status": "VERIFIED",
        },
        "international_and_contract_record": {
            "senior_capped_status": "NONE_CONFIRMED",
            "status": "VERIFIED",
        },
        "eligibility": {
            "status": "ELIGIBLE_UNCAPPED",
        },
    }

    destination, reason, calcs = route_candidate(mock_candidate)
    assert destination == "PENDING"
    assert "PENDING_DISAMBIGUATION" in reason
    assert calcs is None


def test_year_only_dob_routing():
    """
    Test 4: Candidate with unverified or YEAR_ONLY precision DOB.
    Must route to PENDING and be excluded from exact age ranking.
    """
    mock_candidate = {
        "candidate_id": "UNSTOP_0099",
        "identity": {
            "unstop_name": "Sample Prospect",
            "verified_name": "Sample Prospect",
            "name_status": "VERIFIED",
            "original_entry_indices": [98],
        },
        "dob": {
            "value": "2004",
            "status": "NEEDS_VERIFICATION",
            "precision": "YEAR_ONLY",
        },
        "nationality_and_status": {
            "country": "India",
            "is_indian_domestic_player": True,
            "is_overseas": False,
            "status": "VERIFIED",
        },
        "international_and_contract_record": {
            "senior_capped_status": "NONE_CONFIRMED",
            "status": "VERIFIED",
        },
        "eligibility": {
            "status": "ELIGIBLE_UNCAPPED",
        },
    }

    destination, reason, calcs = route_candidate(mock_candidate)
    assert destination == "PENDING"
    assert "YEAR_ONLY" in reason or "VERIFIED" in reason
    assert calcs is None
