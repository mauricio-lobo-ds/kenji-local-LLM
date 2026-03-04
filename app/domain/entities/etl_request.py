from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.domain.value_objects.business_rule import BusinessRuleSet
from app.domain.value_objects.table_schema import TableSchema


class ETLRequest(BaseModel, frozen=True):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_tables: list[TableSchema]
    target_table: TableSchema
    data_sample: str = ""
    business_rules: BusinessRuleSet = Field(default_factory=BusinessRuleSet)
    target_dialect: str = "SQL"
    additional_context: str = ""
