"""
Royals ScoutIQ - Phase 1 Scouting Intelligence Models
Pydantic schemas for candidate registry, evidence management, age calculations,
and eligibility routing under Protocol v1.1.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class IdentityStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    PENDING_DISAMBIGUATION = "PENDING_DISAMBIGUATION"
    REJECTED = "REJECTED"


class DOBPrecision(str, Enum):
    FULL_DATE = "FULL_DATE"
    YEAR_MONTH_ONLY = "YEAR_MONTH_ONLY"
    YEAR_ONLY = "YEAR_ONLY"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
    PENDING = "PENDING"
    UNSUPPORTED = "UNSUPPORTED"
    CONFLICTING = "CONFLICTING"


class EligibilityStatus(str, Enum):
    ELIGIBLE_UNCAPPED = "ELIGIBLE_UNCAPPED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    EXCLUDED_CAPPED = "EXCLUDED_CAPPED"
    EXCLUDED_OVERSEAS = "EXCLUDED_OVERSEAS"


class ProvenanceStatus(str, Enum):
    VERIFIED = "VERIFIED"
    CALCULATED = "CALCULATED"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
    UNSUPPORTED = "UNSUPPORTED"


class EvidenceItem(BaseModel):
    claim: str
    value_supported: Any
    source_title: str
    publisher: str
    source_url: str
    source_type: str = "OFFICIAL_PROFILE"  # OFFICIAL_RECORD, COMPETITION_PACK, OFFICIAL_PROFILE, TOURNAMENT_SITE, NEWS_LEAD
    retrieved_on: str
    checked_by: str
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    notes: Optional[str] = ""


class CandidateIdentity(BaseModel):
    unstop_name: str
    verified_name: Optional[str] = None
    name_status: IdentityStatus = IdentityStatus.PENDING
    original_entry_indices: List[int] = Field(default_factory=list)


class CandidateDOB(BaseModel):
    value: Optional[str] = None  # YYYY-MM-DD
    precision: Optional[DOBPrecision] = None
    status: VerificationStatus = VerificationStatus.PENDING
    evidence: List[EvidenceItem] = Field(default_factory=list)


class NationalityAndStatus(BaseModel):
    country: Optional[str] = None
    is_indian_domestic_player: Optional[bool] = None
    is_overseas: Optional[bool] = None
    status: VerificationStatus = VerificationStatus.PENDING
    evidence: List[EvidenceItem] = Field(default_factory=list)


class InternationalAndContractRecord(BaseModel):
    senior_india_international_appearances: Optional[int] = None
    india_test_appearances: Optional[int] = None
    india_odi_appearances: Optional[int] = None
    india_t20i_appearances: Optional[int] = None
    other_full_member_senior_appearances: Optional[int] = None
    bcci_senior_central_contract_status: VerificationStatus = VerificationStatus.PENDING
    bcci_central_contract: Optional[str] = "NONE"
    senior_capped_status: str = "PENDING"  # NONE_CONFIRMED, CAPPED, PENDING
    u19_appearances: Optional[str] = None
    india_a_appearances: Optional[str] = None
    u19_india_a_representation: Optional[str] = None  # Notes developmental squads without capping
    audit_methodology: str = "Senior International Appearance Audit"
    source_coverage_and_limitations: Optional[str] = None
    status: VerificationStatus = VerificationStatus.PENDING
    evidence: List[EvidenceItem] = Field(default_factory=list)


class PlayingProfile(BaseModel):
    role: Optional[str] = None
    batting_hand: Optional[str] = None
    bowling_style: Optional[str] = None
    state_team: Optional[str] = None
    status: VerificationStatus = VerificationStatus.PENDING
    evidence: List[EvidenceItem] = Field(default_factory=list)


class PerformanceData(BaseModel):
    source_status: str = "NOT_RESEARCHED"
    provenance: ProvenanceStatus = ProvenanceStatus.UNSUPPORTED
    statistics: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[EvidenceItem] = Field(default_factory=list)


class AgeCalculationRecord(BaseModel):
    years: Optional[int] = None
    months: Optional[int] = None
    days: Optional[int] = None
    total_days: Optional[int] = None
    status: str = "NOT_CALCULATED"  # CALCULATED, NOT_CALCULATED


class CandidateAgeCalculations(BaseModel):
    as_of_2026_11_08: AgeCalculationRecord = Field(default_factory=AgeCalculationRecord)
    as_of_2027_04_01: AgeCalculationRecord = Field(default_factory=AgeCalculationRecord)


class CandidateEligibility(BaseModel):
    competition_rule_reference: str = "Annexure A, Clause 5 (Round 1: Youngest Uncapped Player)"
    status: EligibilityStatus = EligibilityStatus.PENDING_VERIFICATION
    reason: Optional[str] = None
    evidence: List[EvidenceItem] = Field(default_factory=list)


class CandidateVerificationAudit(BaseModel):
    overall_status: str = "PENDING_VERIFICATION"
    checked_by: Optional[str] = None
    checked_on: Optional[str] = None
    review_notes: List[str] = Field(default_factory=list)


class CandidateRecord(BaseModel):
    candidate_id: str
    identity: CandidateIdentity
    dob: CandidateDOB
    nationality_and_status: NationalityAndStatus
    international_and_contract_record: InternationalAndContractRecord
    playing_profile: PlayingProfile
    performance_data: PerformanceData = Field(default_factory=PerformanceData)
    age_calculations: CandidateAgeCalculations = Field(default_factory=CandidateAgeCalculations)
    eligibility: CandidateEligibility
    verification: CandidateVerificationAudit


class VerificationUpdateRequest(BaseModel):
    candidate_id: str
    verified_name: Optional[str] = None
    dob: Optional[str] = None
    dob_precision: Optional[DOBPrecision] = DOBPrecision.FULL_DATE
    country: Optional[str] = "India"
    is_indian_domestic: Optional[bool] = True
    is_overseas: Optional[bool] = False
    senior_capped_status: Optional[str] = "NONE_CONFIRMED"
    india_test_appearances: Optional[int] = 0
    india_odi_appearances: Optional[int] = 0
    india_t20i_appearances: Optional[int] = 0
    other_senior_international_appearances: Optional[int] = 0
    u19_appearances: Optional[str] = None
    india_a_appearances: Optional[str] = None
    bcci_central_contract: Optional[str] = "NONE"
    source_coverage_and_limitations: Optional[str] = None
    role: Optional[str] = None
    batting_hand: Optional[str] = None
    bowling_style: Optional[str] = None
    state_team: Optional[str] = None
    eligibility_status: Optional[EligibilityStatus] = None
    reviewer: str = "Royals Scout Analyst"
    reviewer_notes: Optional[str] = ""
    evidence: Optional[EvidenceItem] = None


class DisambiguationRequest(BaseModel):
    candidate_id: str
    resolution_status: IdentityStatus  # VERIFIED or REJECTED
    disambiguated_name: str
    distinguishing_notes: str
    reviewer: str = "Royals Lead Scout"


class CandidateComparisonRequest(BaseModel):
    candidate_ids: List[str]


class DOBCampaignItem(BaseModel):
    candidate_id: str
    unstop_name: str
    verified_name: Optional[str] = None
    dob: Optional[str] = None
    dob_precision: Optional[str] = None
    dob_source_title: Optional[str] = None
    dob_source_url: Optional[str] = None
    checked_date: Optional[str] = None
    verification_status: str
    priority_tier: str  # TIER_1_ACTIVE_DOMESTIC, TIER_2_DOMESTIC_ROSTER, TIER_3_PENDING_REGISTRATION, EXCLUDED_RULE
    reviewer_notes: Optional[str] = None


class ResearchCompletenessGate(BaseModel):
    total_unique_candidates: int
    verified_candidates: int
    year_only_dob_count: int
    missing_dob_count: int
    unresolved_identity_count: int
    excluded_rules_count: int
    remaining_domestic_pending_research: int
    absolute_ranking_unlocked: bool
    gate_status: str  # "LOCKED_PROVISIONAL_MODE" | "UNLOCKED_ABSOLUTE_MODE"
    provisional_title: str
    blocking_reasons: List[str]
    methodology_limitation: str

