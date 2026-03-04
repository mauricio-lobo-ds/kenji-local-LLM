from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities.etl_request import ETLRequest


@dataclass(frozen=True)
class PromptPair:
    system_prompt: str
    user_prompt: str


class PromptBuilderService:
    _SYSTEM_TEMPLATE = (
        "You are an expert ETL SQL engineer. Your ONLY output must be valid, production-ready SQL code.\n"
        "\n"
        "Rules you MUST follow:\n"
        "- Output ONLY raw SQL. No markdown code fences. No explanations. No comments outside SQL.\n"
        "- The SQL must be a single, complete, executable statement or a well-structured script.\n"
        "- Respect every business rule listed in the request.\n"
        "- Use appropriate JOIN types based on the data relationships described.\n"
        "- Apply data type conversions explicitly where needed.\n"
        "- Handle NULL values defensively using COALESCE or CASE WHEN as appropriate.\n"
        "- Use aliases for readability.\n"
        "- Dialect: {dialect}"
    )

    _USER_TEMPLATE = (
        "## Source Tables\n"
        "{source_tables_ddl}\n"
        "\n"
        "## Target Table\n"
        "{target_table_ddl}\n"
        "\n"
        "## Data Sample (representative rows from source tables)\n"
        "{data_sample}\n"
        "\n"
        "## Business Rules\n"
        "{business_rules}\n"
        "\n"
        "{additional_context_section}"
        "Generate the ETL SQL that reads from the source tables and populates the target table\n"
        "according to the business rules above. Output only SQL."
    )

    def build(self, request: ETLRequest) -> PromptPair:
        system_prompt = self._SYSTEM_TEMPLATE.format(dialect=request.target_dialect)

        source_tables_ddl = "\n\n".join(
            t.to_ddl_string() for t in request.source_tables
        )
        target_table_ddl = request.target_table.to_ddl_string()
        data_sample = request.data_sample or "(no sample data provided)"
        business_rules = request.business_rules.to_numbered_list()

        if request.additional_context:
            additional_context_section = (
                f"## Additional Context\n{request.additional_context}\n\n"
            )
        else:
            additional_context_section = ""

        user_prompt = self._USER_TEMPLATE.format(
            source_tables_ddl=source_tables_ddl,
            target_table_ddl=target_table_ddl,
            data_sample=data_sample,
            business_rules=business_rules,
            additional_context_section=additional_context_section,
        )

        return PromptPair(system_prompt=system_prompt, user_prompt=user_prompt)
