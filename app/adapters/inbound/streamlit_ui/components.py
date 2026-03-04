from __future__ import annotations

import streamlit as st

from app.domain.entities.sql_result import SQLResult


def render_table_input_section(label: str, key_prefix: str) -> tuple[str, str]:
    """Render inputs for a single table. Returns (table_name, ddl_or_description)."""
    table_name = st.text_input(
        f"{label} — Table Name",
        key=f"{key_prefix}_name",
        placeholder="e.g. orders",
    )
    ddl_or_description = st.text_area(
        f"{label} — DDL or Description",
        key=f"{key_prefix}_ddl",
        placeholder="CREATE TABLE orders (\n  id INT PRIMARY KEY,\n  ...\n);",
        height=120,
    )
    return table_name, ddl_or_description


def render_sql_result(result: SQLResult) -> None:
    """Render the SQL generation result."""
    if result.is_success():
        st.success("SQL generated successfully.")
        st.code(result.sql, language="sql")
    else:
        st.error(f"Generation failed: {result.error_message}")
        if result.raw_llm_response:
            with st.expander("Raw LLM response"):
                st.text(result.raw_llm_response)

    if result.model_name or result.prompt_tokens or result.completion_tokens:
        with st.expander("Token usage"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Model", result.model_name or "—")
            col2.metric("Prompt tokens", result.prompt_tokens)
            col3.metric("Completion tokens", result.completion_tokens)


def render_llm_status_badge(is_connected: bool) -> None:
    """Render a green/red status indicator for the LLM backend."""
    if is_connected:
        st.markdown(
            '<span style="color: #28a745; font-weight: bold;">● LLM Connected</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span style="color: #dc3545; font-weight: bold;">● LLM Disconnected</span>',
            unsafe_allow_html=True,
        )


def render_add_table_button(session_key: str) -> bool:
    """Render an 'Add source table' button. Returns True if clicked."""
    return st.button("＋ Add source table", key=f"add_table_{session_key}")
