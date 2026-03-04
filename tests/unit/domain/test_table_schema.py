import pytest
from pydantic import ValidationError

from app.domain.value_objects.table_schema import ColumnDefinition, TableSchema


def test_table_schema_frozen():
    schema = TableSchema(table_name="orders")
    with pytest.raises((TypeError, ValidationError)):
        schema.table_name = "other"  # type: ignore[misc]


def test_duplicate_column_names_raises():
    with pytest.raises(ValidationError):
        TableSchema(
            table_name="orders",
            columns=[
                ColumnDefinition(name="id", data_type="INT"),
                ColumnDefinition(name="id", data_type="VARCHAR"),
            ],
        )


def test_to_ddl_string_with_raw():
    raw = "CREATE TABLE foo (id INT);"
    schema = TableSchema(table_name="foo", ddl_raw=raw)
    assert schema.to_ddl_string() == raw


def test_to_ddl_string_no_columns_no_raw():
    schema = TableSchema(table_name="empty_table")
    ddl = schema.to_ddl_string()
    assert "empty_table" in ddl
    assert "no schema provided" in ddl


def test_to_ddl_string_renders_columns():
    schema = TableSchema(
        table_name="products",
        columns=[
            ColumnDefinition(name="id", data_type="INT", nullable=False, primary_key=True),
            ColumnDefinition(name="name", data_type="VARCHAR(255)", nullable=False),
        ],
    )
    ddl = schema.to_ddl_string()
    assert "CREATE TABLE products" in ddl
    assert "id INT NOT NULL PRIMARY KEY" in ddl
    assert "name VARCHAR(255) NOT NULL" in ddl


def test_column_names():
    schema = TableSchema(
        table_name="t",
        columns=[
            ColumnDefinition(name="a", data_type="INT"),
            ColumnDefinition(name="b", data_type="TEXT"),
        ],
    )
    assert schema.column_names() == ["a", "b"]
