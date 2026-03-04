from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class RulePriority(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class BusinessRule(BaseModel, frozen=True):
    description: str
    priority: RulePriority = RulePriority.MEDIUM
    example: str = ""


class BusinessRuleSet(BaseModel, frozen=True):
    rules: list[BusinessRule] = []

    def to_numbered_list(self) -> str:
        if not self.rules:
            return "(no business rules specified)"
        lines = []
        for i, rule in enumerate(self.rules, start=1):
            priority_tag = f"[{rule.priority}]"
            example_part = f" (e.g. {rule.example})" if rule.example else ""
            lines.append(f"{i}. {priority_tag} {rule.description}{example_part}")
        return "\n".join(lines)
