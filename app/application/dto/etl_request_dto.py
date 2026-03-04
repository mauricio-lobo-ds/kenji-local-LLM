from __future__ import annotations

from pydantic import BaseModel, Field


class TableSchemaDTO(BaseModel):
    table_name: str
    ddl_or_description: str = Field(min_length=10)


class ETLRequestDTO(BaseModel):
    source_tables_raw: list[TableSchemaDTO]
    target_table_raw: TableSchemaDTO
    data_sample: str = ""
    business_rules_text: str = ""
    target_dialect: str = "SQL"
    additional_context: str = ""
