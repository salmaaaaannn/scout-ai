"""
Royals ScoutIQ - Data Ingestion & Validation Engine (Features 114 & 115)
Validates imported CSV, Excel, and JSON datasets for missing fields,
duplicates, age bounds, and statistical anomalies.
"""

from typing import List, Dict, Any, Tuple
import re


class DataValidationSystem:
    """
    Validates domestic cricket datasets before loading into PostgreSQL / Pandas.
    """

    REQUIRED_PLAYER_COLUMNS = ["player_id", "full_name", "age", "role"]

    @classmethod
    def validate_player_records(cls, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validates player records against business constraints:
        - Required columns must be present
        - Age must be between 14 and 45
        - Duplicates by player_id or full_name must be identified
        - Negative values in stats are rejected
        """
        valid_records = []
        rejected_records = []
        seen_ids = set()
        seen_names = set()

        for idx, row in enumerate(records, start=1):
            errors = []

            # Normalize name / full_name
            if "name" in row and "full_name" not in row:
                row["full_name"] = row["name"]
            elif "full_name" in row and "name" not in row:
                row["name"] = row["full_name"]

            # Check required fields
            for col in cls.REQUIRED_PLAYER_COLUMNS:
                if col not in row or row[col] is None or str(row[col]).strip() == "":
                    errors.append(f"Missing required field '{col}'")

            # Check age bounds
            try:
                age = int(row.get("age", 0))
                if age < 14 or age > 45:
                    errors.append(f"Invalid age '{age}' (must be 14-45)")
            except (ValueError, TypeError):
                errors.append(f"Non-numeric age '{row.get('age')}'")

            # Check duplicates
            pid = str(row.get("player_id", "")).strip()
            name = str(row.get("full_name", "")).strip().lower()

            if pid and pid in seen_ids:
                errors.append(f"Duplicate player_id '{pid}'")
            elif pid:
                seen_ids.add(pid)

            if name and name in seen_names:
                errors.append(f"Duplicate full_name '{row.get('full_name')}'")
            elif name:
                seen_names.add(name)

            # Check statistical anomalies if present
            if "balls_faced" in row and row["balls_faced"] < 0:
                errors.append("Negative balls_faced")
            if "runs_scored" in row and row["runs_scored"] < 0:
                errors.append("Negative runs_scored")
            if "runs" in row and row["runs"] < 0:
                errors.append("Negative runs")
            if "wickets" in row and row["wickets"] < 0:
                errors.append("Negative wickets")
            if "matches" in row and row["matches"] < 0:
                errors.append("Negative matches")

            if errors:
                rejected_records.append({
                    "row_index": idx,
                    "record": row,
                    "validation_errors": errors,
                })
            else:
                valid_records.append(row)

        all_errors = [e for r in rejected_records for e in r["validation_errors"]]

        return {
            "total_records_received": len(records),
            "valid_records_count": len(valid_records),
            "rejected_records_count": len(rejected_records),
            "total_records": len(records),
            "valid_records": len(valid_records),
            "invalid_records": len(rejected_records),
            "errors": all_errors,
            "is_dataset_clean": len(rejected_records) == 0,
            "valid_records_list": valid_records,
            "rejected_records_list": rejected_records,
        }
