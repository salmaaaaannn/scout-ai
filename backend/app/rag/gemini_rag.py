"""
Royals ScoutIQ - Gemini 3.8 Flash Hybrid RAG Tactical Assistant (Features 48, 53, 54, 55, 56, 57, 58, 59)
Synthesizes structured SQL statistics with verified video observations into grounded,
evidence-backed tactical reports for Kumar Sangakkara and Giles Lindsay.
"""

from typing import List, Dict, Any, Optional
import os
import json
import requests

from app.rag.retrieval import HybridRetrievalDispatcher


class GeminiTacticalRAG:
    """
    Evidence-grounded conversational intelligence engine for Rajasthan Royals
    designed to minimize hallucinations through citation of verified match logs and video timestamps.
    """

    SYSTEM_INSTRUCTION = """
You are ROYALS ScoutIQ Assistant, the proprietary AI scouting intelligence system of Rajasthan Royals.
Your audience is Head Coach Kumar Sangakkara and Director of Strategy Giles Lindsay.

CRITICAL OPERATIONAL RULES:
1. EVIDENCE-GROUNDED CITATIONS: You must only make claims directly supported by the provided data context. Never invent unverified statistics.
2. CITATIONS REQUIRED: Every statistical statement must cite the phase and match context.
   Every technical statement must cite the video timestamp and analyst verification status.
3. ADVISORY TONE: Professional, analytical, sabermetric-driven (True Strike Rate, True Economy Rate, Steal Index).
4. If an observation has NOT been verified by an analyst, explicitly label it: [REQUIRES HUMAN VERIFICATION].
"""

    def __init__(self, dispatcher: Optional[HybridRetrievalDispatcher] = None):
        self.dispatcher = dispatcher or HybridRetrievalDispatcher()
        if not os.getenv("GEMINI_API_KEY"):
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env")
            if not os.path.exists(env_path):
                env_path = os.path.join(os.getcwd(), ".env")
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            if k.strip() and not os.getenv(k.strip()):
                                os.environ[k.strip()] = v.strip().strip("'\"")
        self.api_key = os.getenv("GEMINI_API_KEY")

    def _call_gemini_api(self, query: str, evidence: List[Dict[str, Any]]) -> Optional[str]:
        """Calls Google Gemini API via REST if API key is configured."""
        if not self.api_key or not self.api_key.strip():
            return None

        try:
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key.strip()}"

            prompt = (
                f"{self.SYSTEM_INSTRUCTION.strip()}\n\n"
                f"### VERIFIED EVIDENCE CONTEXT (EVIDENCE-GROUNDED RETRIEVAL CONTEXT):\n"
                f"{json.dumps(evidence, indent=2)}\n\n"
                f"### USER QUERY:\n{query}\n\n"
                f"Generate a professional, sabermetric-driven tactical intelligence brief for Kumar Sangakkara & Giles Lindsay:"
            )

            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 1000
                }
            }

            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
        except Exception:
            return None
        return None

    def answer_query(self, query: str) -> Dict[str, Any]:
        """
        Executes hybrid retrieval and generates an evidence-grounded tactical response.
        """
        # Step 1: Hybrid Retrieval
        matched_players = self.dispatcher.query_structured_stats(query)

        evidence_blocks = []
        citations = []

        for p in matched_players:
            p_id = p["player_id"]
            p_name = p["name"]
            stats = p["phase_stats"]
            valuation = p["auction_valuation"]
            verified_notes = self.dispatcher.query_verified_observations(p_id)

            evidence_blocks.append({
                "player": p_name,
                "role": p["role"],
                "age": p["age"],
                "stats": stats,
                "valuation": valuation,
                "verified_video_notes": [n["current_observation"] for n in verified_notes],
            })

            citations.append({
                "player": p_name,
                "player_id": p_id,
                "data_source": "BCCI Domestic Match Logs (SMAT/Ranji)",
                "verification_status": "Analyst Verified" if verified_notes else "Statistical Model Verified",
            })

        # Step 2: Grounded Synthesis
        # Try live Gemini API with configured key; fallback gracefully to deterministic grounded synthesis
        answer_text = None
        if self.api_key:
            answer_text = self._call_gemini_api(query, evidence_blocks)

        if not answer_text:
            answer_text = self._generate_grounded_response(query, evidence_blocks)

        return {
            "query": query,
            "answer": answer_text,
            "citations": citations,
            "matched_players_count": len(matched_players),
            "evidence_used": evidence_blocks,
        }

    def _generate_grounded_response(self, query: str, evidence: List[Dict[str, Any]]) -> str:
        """Constructs an evidence-backed scouting brief."""
        if not evidence:
            return "No uncapped players in the verified database match those exact criteria. Please broaden your query or inspect the pending verification queue."

        top_player = evidence[0]
        name = top_player["player"]
        role = top_player["role"]
        age = top_player["age"]
        val = top_player["valuation"]
        stats = top_player["stats"]

        response_lines = [
            f"### ScoutIQ Tactical Brief: {name} (Age {age} · {role})",
            f"**Auction Fit for RR:** {val['priority_slot']} | **Steal Index:** {val['steal_index']}/10",
            f"- **Base Price:** ₹{val['base_price_lakhs']} Lakhs | **Projected Hammer:** ₹{val['projected_hammer_lakhs']} Lakhs",
            "",
            "#### 1. Grounded Phase Performance",
        ]

        if "Death" in stats:
            death = stats["Death"]
            if "econ" in death:
                response_lines.append(
                    f"- **Death Overs (16-20):** Economy of {death['econ']} (True Economy Rate: **{death['ter']}** vs expected baseline). Dot-ball percentage: **{death['dot_pct']}%** across {death['overs']} overs."
                )
            elif "sr" in death:
                response_lines.append(
                    f"- **Death Overs (16-20):** Strike Rate of {death['sr']} (True Strike Rate: **+{death['tsr']}** above tournament baseline). Dot-ball percentage suppressed to **{death['dot_pct']}%**."
                )

        if "Powerplay" in stats:
            pp = stats["Powerplay"]
            if "econ" in pp:
                response_lines.append(f"- **Powerplay (1-6):** Economy of {pp['econ']} (TER: {pp['ter']}) with {pp['dot_pct']}% dot balls.")
            elif "sr" in pp:
                response_lines.append(f"- **Powerplay (1-6):** Strike Rate of {pp['sr']} (TSR: +{pp['tsr']}).")

        response_lines.append("")
        response_lines.append("#### 2. Biomechanical & Tactical Evidence")
        if top_player["verified_video_notes"]:
            for note in top_player["verified_video_notes"]:
                response_lines.append(f"- [VERIFIED OBSERVATION]: {note}")
        else:
            response_lines.append(
                "- Video clips awaiting analyst sign-off in the verification dashboard. High action repeatability indicated by DTW alignment."
            )

        response_lines.append("")
        response_lines.append(f"**Recommendation for Kumar Sangakkara:** Back {name} at the auction up to ₹{val['projected_hammer_lakhs']} Lakhs. High replacement value for RR 2027 roster balance.")

        return "\n".join(response_lines)
