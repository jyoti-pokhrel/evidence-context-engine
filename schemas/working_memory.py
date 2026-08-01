from pydantic import BaseModel, Field
from datetime import datetime


class Fact(BaseModel):
    key: str
    value: str
    source: str
    discovered_at: datetime = Field(default_factory=datetime.now)


class WorkingMemory(BaseModel):
    facts: list[Fact] = Field(default_factory=list)

    def add_fact(self, key: str, value: str, source: str) -> None:
        fact = Fact(key=key, value=value, source=source)
        self.facts.append(fact)

    def get_fact(self, key: str) -> Fact | None:
        for fact in self.facts:
            if fact.key == key:
                return fact
        return None

    def clear(self) -> None:
        self.facts = []
