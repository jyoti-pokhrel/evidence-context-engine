from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class Claim(BaseModel):
    claim_id: str
    text: str
    source: str = Field(description="Document source, e.g., 'architecture.md'")
    source_type: Literal["code", "security_policy", "architecture_docs", "readme", "meeting_notes"]
    topic: str = Field(description="Topic category, e.g., 'authentication_method'")
    timestamp: datetime
    authority: int = Field(description="Authority level 1-5, where 1=highest authority (code) and 5=lowest authority (meeting notes)")
    confidence: float = Field(ge=0.0, le=1.0)
    is_fact: bool = Field(default=False)
    fact_key: Optional[str] = None
    fact_value: Optional[str] = None


class Evidence(BaseModel):
    claim: Claim
    validated_at: datetime = Field(default_factory=datetime.now)
    is_valid: bool = True
    validation_reason: Optional[str] = None


class Conflict(BaseModel):
    claim_a: Evidence
    claim_b: Evidence
    topic: str
    resolved: bool = False
    winner: Optional[Evidence] = None
    resolution_reason: Optional[str] = None
