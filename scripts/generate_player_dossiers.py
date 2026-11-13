#!/usr/bin/env python3
"""generate_player_dossiers.py

Creates one‑page PDF dossiers for a list of players (batters + bowlers).

Usage:
    python scripts/generate_player_dossiers.py --players players.json
where `players.json` is a simple JSON array of player IDs, e.g.:
[
    "1187", "6273", "1210", "1596",   # batters
    "3639", "4369", "3125", "778"    # bowlers
]

The script writes PDFs to:
    data/reports/dossiers/<player_id>.pdf
"""

import argparse
import json
import os
import sys
from datetime import datetime

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

# ----------------------------------------------------------------------
# Adjust these imports to match your project’s DB model configuration.
# ----------------------------------------------------------------------
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# ---- Paths -----------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "scripts", "templates")
TEMPLATE_FILE = "dossier_template.html"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "reports", "dossiers")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# Database configuration – the repo ships a SQLite fallback for quick testing.
# Override with your PostgreSQL URI via the DATABASE_URL env var.
# ----------------------------------------------------------------------
DB_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(PROJECT_ROOT, 'backend', 'database', 'scoutiq.db')}"
)
engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def load_template() -> Environment:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    return env.get_template(TEMPLATE_FILE)

def fetch_player_data(session, player_id: str) -> dict:
    """Collects all columns needed for the dossier.
    Expected tables (see README schema):
        players, player_phase_stats, auction_valuations,
        cv_biomechanical_records (latest snapshot per player).
    Returns a flat dictionary ready for the Jinja template.
    """
    # Basic profile
    player_row = session.execute(
        text("SELECT player_id, full_name, primary_role FROM players WHERE player_id = :pid"),
        {"pid": player_id},
    ).fetchone()
    if not player_row:
        raise ValueError(f"Player ID {player_id} not found in players table")
    profile = dict(player_row)

    # Phase‑stats (reliability metrics)
    stats_row = session.execute(
        text(
            """
            SELECT tsr, ter, pressure_sr_pct, baseline_sr_pct,
                   sample_balls, reliability_score, steal_index, acpi,
                   tactical_fit_score, rr_slot_priority
            FROM player_phase_stats
            WHERE player_id = :pid
            """
        ),
        {"pid": player_id},
    ).fetchone()
    if stats_row:
        profile.update(dict(stats_row))
    else:
        # Fill with N/A placeholders if stats are missing
        profile.update({
            "tsr": None,
            "ter": None,
            "pressure_sr_pct": None,
            "baseline_sr_pct": None,
            "sample_balls": None,
            "reliability_score": None,
            "steal_index": None,
            "acpi": None,
            "tactical_fit_score": None,
            "rr_slot_priority": None,
        })

    # Auction valuation (optional, but useful for the "steal" narrative)
    val_row = session.execute(
        text(
            "SELECT market_value, steal_index FROM auction_valuations WHERE player_id = :pid"
        ),
        {"pid": player_id},
    ).fetchone()
    if val_row:
        profile.update(dict(val_row))

    # CV snapshot – we keep the image in the artifact folder.
    # The image naming convention in this repo is:
    #   cv_snapshots/<player_id>.png (or .jpg)
    artifact_root = os.getenv(
        "ARTIFACT_ROOT",
        os.path.join(
            os.path.expanduser("~"),
            ".gemini",
            "antigravity",
            "brain",
            "961b7d5f-a555-4c40-b15c-d828d01d298e",
        ),
    )
    possible_ext = [".png", ".jpg", ".jpeg"]
    cv_path = None
    for ext in possible_ext:
        candidate = os.path.join(artifact_root, f"cv_snapshots/{player_id}{ext}")
        if os.path.isfile(candidate):
            cv_path = candidate
            break
    # WeasyPrint can embed a local file via an absolute file:// URL.
    cv_image_path = f"file://{cv_path}" if cv_path else None
    profile["cv_image_path"] = cv_image_path

    # Tactical‑fit bullets – keep it simple; you can enrich later.
    bullets = []
    if profile.get("rr_slot_priority"):
        bullets.append(
            f"Ideal for the {profile['rr_slot_priority']} slot in RR’s 2027 squad."
        )
    if profile.get("steal_index"):
        bullets.append(
            f"Steal index {profile['steal_index']:.2f} indicates high upside at auction price."
        )
    if profile.get("reliability_score"):
        bullets.append(
            f"Reliability score {profile['reliability_score']:.2f} places the player in the top‑10 of the cohort."
        )
    profile["tactical_bullets"] = bullets

    # Miscellaneous for the template
    profile["generation_date"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return profile

def render_pdf(template, context: dict, out_path: str) -> None:
    """Renders the Jinja2 template to HTML and then to PDF via WeasyPrint."""
    html_content = template.render(**context)
    HTML(string=html_content, base_url="file://").write_pdf(out_path)

def main():
    parser = argparse.ArgumentParser(description="Generate PDF dossiers for a list of players")
    parser.add_argument(
        "--players",
        required=True,
        help="Path to a JSON file containing an array of player IDs (strings).",
    )
    args = parser.parse_args()

    # Load player IDs
    try:
        with open(args.players, "r", encoding="utf-8") as f:
            player_ids = json.load(f)
    except Exception as exc:
        sys.exit(f"Failed to read player list: {exc}")

    if not isinstance(player_ids, list) or not all(isinstance(p, str) for p in player_ids):
        sys.exit("players.json must be a JSON array of string player IDs")

    # Initialise DB session and Jinja template
    session = Session()
    template = load_template()

    for pid in player_ids:
        try:
            context = {
                "player": fetch_player_data(session, pid),
                "cv_image_path": fetch_player_data(session, pid)["cv_image_path"],
                "tactical_bullets": fetch_player_data(session, pid)["tactical_bullets"],
                "generation_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            }
            out_file = os.path.join(OUTPUT_DIR, f"{pid}.pdf")
            render_pdf(template, context, out_file)
            print(f"✅ Created dossier for player {pid} → {out_file}")
        except Exception as e:
            print(f"⚠️  Failed for player {pid}: {e}")

    session.close()

if __name__ == "__main__":
    main()
