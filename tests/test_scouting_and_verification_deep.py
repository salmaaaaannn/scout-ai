"""
Royals ScoutIQ - Scouting Registry & Human Verification Deep Unit Tests
Covers CandidateRegistryService, CandidateFiltering, AgeVerification,
and AnalystVerificationService end-to-end.
"""

import pytest
import os
from pathlib import Path
from backend.app.scouting.registry_service import CandidateRegistryService
from backend.app.scouting.models import VerificationUpdateRequest, DisambiguationRequest, EvidenceItem
from backend.app.scouting.fixtures import seed_verified_fixtures
from backend.app.verification.verification_service import AnalystVerificationService, VerificationStatus


def test_registry_service_lifecycle_and_filters(tmp_path):
    temp_reg = tmp_path / "test_reg_1.json"
    service = CandidateRegistryService(registry_file=temp_reg)
    summary = service.ingest_from_raw_pool()
    assert "total_entries_ingested" in summary
    assert summary["total_entries_ingested"] >= 335

    seed_verified_fixtures(service)
    routing = service.execute_routing()
    assert routing["eligible_count"] > 0
    assert routing["total_candidates"] >= 335

    # Filter by query
    query_res = service.list_candidates(query="Andre", limit=5)
    assert query_res["total_count"] >= 1
    assert any("Andre" in c["identity"]["unstop_name"] for c in query_res["candidates"])

    # Filter by eligibility
    eligible = service.list_candidates(eligibility="ELIGIBLE_UNCAPPED", limit=10)
    assert len(eligible["candidates"]) > 0

    # Test pagination
    page1 = service.list_candidates(limit=5, offset=0)
    page2 = service.list_candidates(limit=5, offset=5)
    assert len(page1["candidates"]) == 5
    assert len(page2["candidates"]) == 5
    assert page1["candidates"][0]["candidate_id"] != page2["candidates"][0]["candidate_id"]


def test_registry_candidate_lookup_and_verification_update(tmp_path):
    temp_reg = tmp_path / "test_reg_2.json"
    service = CandidateRegistryService(registry_file=temp_reg)
    service.ingest_from_raw_pool()
    seed_verified_fixtures(service)

    candidates = service.list_candidates(limit=1)["candidates"]
    cid = candidates[0]["candidate_id"]
    cand = service.get_candidate(cid)
    assert cand is not None
    assert cand["candidate_id"] == cid

    # Find candidate by name
    name = cand["identity"]["unstop_name"]
    found = service.find_candidate_by_name(name)
    assert found is not None
    assert found["candidate_id"] == cid

    # Unknown lookup
    assert service.get_candidate("NON_EXISTENT_ID_9999") is None

    # Update verification
    ev = EvidenceItem(
        claim="Date of birth verification",
        value_supported="2004-06-15",
        source_title="Official BCCI Player Directory",
        publisher="BCCI",
        source_url="https://bcci.tv/players",
        retrieved_on="2026-11-10",
        checked_by="Giles Lindsay",
        notes="Audit verified",
    )
    update_req = VerificationUpdateRequest(
        candidate_id=cid,
        dob="2004-06-15",
        evidence=ev,
    )
    updated = service.update_verification(update_req)
    assert updated["candidate_id"] == cid
    assert updated["dob"]["value"] == "2004-06-15"


def test_registry_disambiguation_and_comparison(tmp_path):
    temp_reg = tmp_path / "test_reg_3.json"
    service = CandidateRegistryService(registry_file=temp_reg)
    service.ingest_from_raw_pool()
    seed_verified_fixtures(service)

    # Resolve disambiguation
    himanshu_cands = [c for c in service.list_candidates(query="Himanshu Singh")["candidates"]]
    if len(himanshu_cands) >= 2:
        target_id = himanshu_cands[0]["candidate_id"]
        ev = EvidenceItem(
            claim="Disambiguate duplicate entry",
            value_supported="Himanshu Singh (MCA Off-Spinner)",
            source_title="Mumbai Cricket Association Player Record",
            publisher="MCA",
            source_url="https://mumbaicricket.com",
            retrieved_on="2026-11-10",
            checked_by="Royals Scout",
            notes="Tall bounce off-spinner",
        )
        disambig_req = DisambiguationRequest(
            candidate_id=target_id,
            verified_identity_name="Himanshu Singh (MCA Off-Spinner)",
            verified_dob="2003-09-15",
            evidence=ev,
        )
        res = service.resolve_disambiguation(disambig_req)
        assert res["success"] is True

    # Compare candidates
    cands = service.list_candidates(limit=2)["candidates"]
    cid1 = cands[0]["candidate_id"]
    cid2 = cands[1]["candidate_id"]
    comp_res = service.compare_candidates([cid1, cid2])
    assert comp_res["comparison_count"] == 2
    assert len(comp_res["candidates"]) == 2


def test_registry_list_a_list_b_and_exports(tmp_path):
    temp_reg = tmp_path / "test_reg_4.json"
    service = CandidateRegistryService(registry_file=temp_reg)
    service.ingest_from_raw_pool()
    seed_verified_fixtures(service)

    list_a = service.generate_list_a()
    assert "top10_candidates" in list_a
    assert len(list_a["top10_candidates"]) > 0

    list_b = service.generate_list_b()
    assert "shortlist" in list_b
    assert len(list_b["shortlist"]) > 0

    # Campaign and completeness
    completeness = service.get_research_completeness()
    assert "total_unique_candidates" in completeness

    campaign = service.get_dob_verification_campaign()
    assert "total_queue_count" in campaign

    # CSV Export
    csv_text = service.export_csv()
    assert "candidate_id" in csv_text
    assert len(csv_text.splitlines()) > 10


def test_analyst_verification_service_full_workflow(tmp_path):
    store_file = os.path.join(str(tmp_path), "test_verification.json")
    service = AnalystVerificationService(store_path=store_file)

    # 1. Enqueue
    item = service.enqueue_observation(
        obs_id="OBS_TEST_DEEP_01",
        player_id="37052",
        player_name="Naman Dhir",
        video_id="CLIP_01",
        timestamp_seconds=2.4,
        ai_observation="Bat downswing 135 rad/s with high head stability.",
        raw_confidence=0.75,
    )
    assert item["status"] == VerificationStatus.PENDING

    # 2. Confirm
    confirmed = service.confirm_observation("OBS_TEST_DEEP_01", analyst_name="Kumar Sangakkara")
    assert confirmed["status"] == VerificationStatus.CONFIRMED
    assert confirmed["confidence_multiplier"] == 1.0

    # 3. Enqueue second and correct
    service.enqueue_observation(
        obs_id="OBS_TEST_DEEP_02",
        player_id="8661",
        player_name="Matheesha Pathirana",
        video_id="CLIP_02",
        timestamp_seconds=1.1,
        ai_observation="High-Arm release detected at 82 degrees.",
        raw_confidence=0.60,
    )
    corrected = service.correct_observation(
        obs_id="OBS_TEST_DEEP_02",
        analyst_name="Shane Bond",
        corrected_text="Sling action release at 38 degrees with lateral trunk flexion.",
        notes="Corrected erroneous high-arm classification to authentic sling trajectory.",
    )
    assert corrected["status"] == VerificationStatus.CORRECTED
    assert corrected["current_observation"] == "Sling action release at 38 degrees with lateral trunk flexion."

    # 4. Enqueue third and reject
    service.enqueue_observation(
        obs_id="OBS_TEST_DEEP_03",
        player_id="999",
        player_name="Ghost Candidate",
        video_id="CLIP_03",
        timestamp_seconds=0.5,
        ai_observation="Irrelevant background movement detected.",
        raw_confidence=0.30,
    )
    rejected = service.reject_observation(
        obs_id="OBS_TEST_DEEP_03",
        analyst_name="Giles Lindsay",
        reason="False positive detection of umpire silhouette.",
    )
    assert rejected["status"] == VerificationStatus.REJECTED
    assert rejected["confidence_multiplier"] == 0.0

    # 5. Pending queue check
    pending = service.get_pending_queue()
    assert len(pending) == 0  # all 3 resolved

    # 6. Verified knowledge for RAG
    rag_knowledge_naman = service.get_verified_knowledge_for_rag("37052")
    assert len(rag_knowledge_naman) == 1
    assert rag_knowledge_naman[0]["status"] == VerificationStatus.CONFIRMED

    rag_knowledge_ghost = service.get_verified_knowledge_for_rag("999")
    assert len(rag_knowledge_ghost) == 0  # rejected item not included in RAG
