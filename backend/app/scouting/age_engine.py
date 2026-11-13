"""
Royals ScoutIQ - Deterministic Exact Age Calculation Engine
Calculates exact calendar (years, months, days, total_days) between DOB and reference cutoffs.
Primary Cutoff: 2026-11-08 (Annexure A Clause 5)
Secondary Cutoff: 2027-04-01 (IPL 2027 Projected Season Start)
"""

import calendar
from datetime import date, datetime
from typing import Tuple, Dict, Any, Optional


PRIMARY_CUTOFF = date(2026, 11, 8)
SECONDARY_CUTOFF = date(2027, 4, 1)


class AgeCalculationEngine:
    @staticmethod
    def calculate_calendar_age(dob: date, cutoff: date) -> Tuple[int, int, int, int]:
        """
        Deterministic calculation of calendar years, months, days, and total days.
        - Leap day rule: Feb 29 birthdates in non-leap reference years use Feb 28 as month anchor.
        - total_days = (cutoff - dob).days
        """
        if cutoff < dob:
            raise ValueError(f"Cutoff date ({cutoff}) cannot be earlier than DOB ({dob})")

        dob_day = dob.day
        dob_month = dob.month

        # Leap day adjustment in non-leap year
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

    @classmethod
    def calculate_candidate_ages(cls, dob_str: str) -> Dict[str, Any]:
        """
        Parses YYYY-MM-DD DOB string and returns dictionary for both cutoffs.
        Flags suspicious or implausible DOBs (e.g. future or age < 14 or > 45).
        """
        try:
            dob = datetime.strptime(dob_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Malformed date '{dob_str}'. Expected format: YYYY-MM-DD.")

        # Flag sanity bounds
        if dob > PRIMARY_CUTOFF:
            raise ValueError(f"Future DOB detected ({dob_str}) - candidate born after cutoff.")

        y1, m1, d1, tot1 = cls.calculate_calendar_age(dob, PRIMARY_CUTOFF)
        y2, m2, d2, tot2 = cls.calculate_calendar_age(dob, SECONDARY_CUTOFF)

        if y1 < 14 or y1 > 45:
            # Suspicious age warning for cricket recruitment
            warning = f"Suspicious age {y1} outside standard professional bounds (14-45)"
        else:
            warning = None

        return {
            "as_of_2026_11_08": {
                "years": y1,
                "months": m1,
                "days": d1,
                "total_days": tot1,
                "status": "CALCULATED",
                "warning": warning,
            },
            "as_of_2027_04_01": {
                "years": y2,
                "months": m2,
                "days": d2,
                "total_days": tot2,
                "status": "CALCULATED",
                "warning": warning,
            },
        }
