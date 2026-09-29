from enum import Enum

from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    REJECTED = "rejected"
    REVIEW = "review"


class VerificationResult(BaseModel):
    status: VerificationStatus
    score: float = Field(ge=0.0, le=1.0)
    organization_number_match: bool
    company_name_match: bool
    website_match: bool
    address_match: bool
    reasons: list[str]