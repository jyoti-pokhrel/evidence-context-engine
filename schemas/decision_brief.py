from pydantic import BaseModel, Field
from typing import Literal, Optional
from .evidence import Evidence, Conflict
from .working_memory import WorkingMemory


class DecisionBrief(BaseModel):
    decision: Literal["PROCEED", "ESCALATE"]
    reason: Optional[str] = None
    evidence: list[Evidence] = Field(default_factory=list)
    working_memory: WorkingMemory
    missing: list[str] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    stale: list[Evidence] = Field(default_factory=list)
    permission_violations: list[Evidence] = Field(default_factory=list)
    rules_fired: list[str] = Field(default_factory=list)
    context_reduction: float = Field(ge=0.0, le=1.0)
