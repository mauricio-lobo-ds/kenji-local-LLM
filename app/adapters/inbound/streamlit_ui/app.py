from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on sys.path when running via streamlit run
_project_root = Path(__file__).resolve().parents[4]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import streamlit as st

from app.adapters.inbound.streamlit_ui.components import (
    render_add_table_button,
    render_llm_status_badge,
    render_sql_result,
    render_table_input_section,
)
from app.application.dto.etl_request_dto import ETLRequestDTO, TableSchemaDTO
from app.main import create_use_case

st.set_page_config(
    page_title="Kenji — ETL SQL Generator",
    page_icon="🗄️",
    layout="wide",
)


@st.cache_resource
def _get_use_case():
    return create_use_case()


# ── Header ──────────────────────────────────────────────────────────────────
header_col, badge_col = st.columns([8, 2])
with header_col:
    st.title("Kenji — ETL SQL Generator")
    st.caption("Generate production-ready ETL SQL from table schemas, data samples, and business rules.")

use_case = _get_use_case()

with badge_col:
    st.write("")  # vertical spacing
    adapter = use_case._llm_port  # type: ignore[attr-defined]
    render_llm_status_badge(adapter.health_check())

st.divider()

# ── Dynamic source table counter ─────────────────────────────────────────────
if "source_table_count" not in st.session_state:
    st.session_state["source_table_count"] = 1

# ── Main form ────────────────────────────────────────────────────────────────
left_col, right_col = st.columns(2)

source_tables_raw: list[TableSchemaDTO] = []

with left_col:
    st.subheader("Source Tables")
    for i in range(st.session_state["source_table_count"]):
        with st.expander(f"Source Table {i + 1}", expanded=True):
            name, ddl = render_table_input_section(
                label=f"Source Table {i + 1}",
                key_prefix=f"src_{i}",
            )
            if name and ddl:
                source_tables_raw.append(
                    TableSchemaDTO(table_name=name, ddl_or_description=ddl)
                )

    if render_add_table_button("main"):
        st.session_state["source_table_count"] += 1
        st.rerun()

    st.subheader("Data Sample")
    data_sample = st.text_area(
        "Representative rows from source tables (CSV, JSON, or plain text)",
        key="data_sample",
        placeholder="id,name,amount\n1,Alice,100.00\n2,Bob,200.50",
        height=150,
    )

with right_col:
    st.subheader("Target Table")
    target_name, target_ddl = render_table_input_section(
        label="Target Table",
        key_prefix="tgt",
    )

    st.subheader("Business Rules")
    business_rules_text = st.text_area(
        "One rule per line",
        key="business_rules",
        placeholder="Only include orders with status = 'completed'\nConvert amounts from cents to dollars\nExclude test accounts (email LIKE '%@test.%')",
        height=150,
    )

    st.subheader("SQL Dialect")
    target_dialect = st.selectbox(
        "Target dialect",
        options=["SQL", "PostgreSQL", "MySQL", "SQL Server", "BigQuery", "Snowflake", "DuckDB"],
        key="dialect",
    )

# ── Additional context (full width) ──────────────────────────────────────────
st.subheader("Additional Context (optional)")
additional_context = st.text_area(
    "Any extra information the LLM should know",
    key="additional_context",
    placeholder="The orders table is partitioned by month. Use date_trunc for grouping.",
    height=80,
)

st.divider()

# ── Generate button ───────────────────────────────────────────────────────────
generate_clicked = st.button("Generate ETL SQL", type="primary", use_container_width=True)

if generate_clicked:
    # Validate minimum required fields
    errors: list[str] = []
    if not source_tables_raw:
        errors.append("Provide at least one source table name and DDL/description.")
    if not target_name or not target_ddl:
        errors.append("Provide the target table name and DDL/description.")

    if errors:
        for err in errors:
            st.warning(err)
    else:
        dto = ETLRequestDTO(
            source_tables_raw=source_tables_raw,
            target_table_raw=TableSchemaDTO(
                table_name=target_name, ddl_or_description=target_ddl
            ),
            data_sample=data_sample,
            business_rules_text=business_rules_text,
            target_dialect=target_dialect or "SQL",
            additional_context=additional_context,
        )

        with st.spinner("Generating ETL SQL…"):
            result = use_case.execute(dto)

        render_sql_result(result)
