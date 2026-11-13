import json
from pathlib import Path

def enrich_registry():
    reg_path = Path("data/processed/candidate_verification_registry.json")
    with open(reg_path, "r", encoding="utf-8") as f:
        reg = json.load(f)

    profile_updates = {
        "UNSTOP_0098": {  # Hardik Raj
            "role": "Bowling All-Rounder (Left-Arm Orthodox)",
            "batting_hand": "Left-hand bat",
            "bowling_style": "Slow left-arm orthodox",
            "state_team": "Karnataka / India U19",
            "status": "VERIFIED"
        },
        "UNSTOP_0251": {  # Samarth Nagaraj
            "role": "Right-Arm Medium Fast Bowler",
            "batting_hand": "Right-hand bat",
            "bowling_style": "Right-arm medium fast",
            "state_team": "Karnataka / India U19",
            "status": "VERIFIED"
        },
        "UNSTOP_0199": {  # P Vignesh
            "role": "Slow Left-Arm Orthodox Bowler",
            "batting_hand": "Left-hand bat",
            "bowling_style": "Slow left-arm orthodox",
            "state_team": "Tamil Nadu / India U19",
            "status": "VERIFIED"
        },
        "UNSTOP_0258": {  # Saranu Nishanth
            "role": "Right-Arm Fast Medium Bowler",
            "batting_hand": "Right-hand bat",
            "bowling_style": "Right-arm fast medium",
            "state_team": "Hyderabad / India U19 probables",
            "status": "VERIFIED"
        },
        "UNSTOP_0028": {  # Anmol Sharma
            "role": "Middle-Order Batter / Off-Spin",
            "batting_hand": "Right-hand bat",
            "bowling_style": "Right-arm off-break",
            "state_team": "Delhi",
            "status": "VERIFIED"
        },
        "UNSTOP_0248": {  # Sakib Hussain
            "role": "Right-Arm Fast Medium Bowler",
            "batting_hand": "Right-hand bat",
            "bowling_style": "Right-arm fast medium",
            "state_team": "Bihar / KKR",
            "status": "VERIFIED"
        },
        "UNSTOP_0052": {  # Ayush Vartak
            "role": "Pace Bowling All-Rounder",
            "batting_hand": "Right-hand bat",
            "bowling_style": "Right-arm medium fast",
            "state_team": "Mumbai U19/U23",
            "status": "VERIFIED"
        },
        "UNSTOP_0206": {  # Nishunk Birla
            "role": "Slow Left-Arm Orthodox Bowler",
            "batting_hand": "Right-hand bat",
            "bowling_style": "Slow left-arm orthodox",
            "state_team": "Chandigarh",
            "status": "VERIFIED"
        },
        "UNSTOP_0177": {  # Mohamed Ali
            "role": "Top-Order Batter",
            "batting_hand": "Right-hand bat",
            "bowling_style": "Right-arm off-break",
            "state_team": "Tamil Nadu",
            "status": "VERIFIED"
        },
        "UNSTOP_0051": {  # Ayush Pandey
            "role": "Opening Batter",
            "batting_hand": "Left-hand bat",
            "bowling_style": "Right-arm off-break",
            "state_team": "Chhattisgarh",
            "status": "VERIFIED"
        },
        "UNSTOP_0133": {  # Kartik Chadha
            "role": "Leg-Break Bowler",
            "batting_hand": "Left-hand bat",
            "bowling_style": "Leg-break googly",
            "state_team": "Punjab / BCCI",
            "status": "VERIFIED"
        }
    }

    for c in reg["candidates"]:
        cid = c["candidate_id"]
        # Set performance_data status
        if c.get("eligibility", {}).get("status") == "ELIGIBLE_UNCAPPED":
            if not c.get("performance_data"):
                c["performance_data"] = {}
            c["performance_data"]["source_status"] = "N/A — insufficient verified sample"
            c["performance_data"]["statistics"] = {}
            c["performance_data"]["evidence"] = []

            # Update profile if mapped
            if cid in profile_updates:
                c["playing_profile"].update(profile_updates[cid])
            elif not c["playing_profile"].get("role"):
                # Default role fallback to Batter if unspecified
                c["playing_profile"]["role"] = "Domestic Cricketer"

    with open(reg_path, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)

    print("Registry enriched with profile roles and standardized performance_data.")

if __name__ == "__main__":
    enrich_registry()
