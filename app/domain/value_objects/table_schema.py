from __future__ import annotations

from pydantic import BaseModel, model_validator


class ColumnDefinition(BaseModel, frozen=True):
    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    description: str = ""


class TableSchema(BaseModel, frozen=True):
    table_name: str
    columns: list[ColumnDefinition] = []
    ddl_raw: str | None = None
    description: str = ""

    @model_validator(mode="after")
    def _unique_column_names(self) -> TableSchema:
        names = [col.name for col in self.columns]
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate column names in table '{self.table_name}'")
        return self

    def to_ddl_string(self) -> str:
        if self.ddl_raw:
            return self.ddl_raw
        if not self.columns:
            return f"-- Table: {self.table_name} (no schema provided)"
        col_lines = []
        for col in self.columns:
            null_str = "NULL" if col.nullable else "NOT NULL"
            pk_str = " PRIMARY KEY" if col.primary_key else ""
            comment = f"  -- {col.description}" if col.description else ""
            col_lines.append(f"    {col.name} {col.data_type} {null_str}{pk_str}{comment}")
        cols_sql = ",\n".join(col_lines)
        return f"CREATE TABLE {self.table_name} (\n{cols_sql}\n);"

    def column_names(self) -> list[str]:
        return [col.name for col in self.columns]
