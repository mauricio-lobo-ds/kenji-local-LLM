# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands use the local virtualenv at `venv/`. On Windows use `venv/Scripts/`; on Unix use `venv/bin/`.

```bash
# Install dependencies
venv/Scripts/pip install -r requirements.txt

# Run the Streamlit app (must be run from the repo root so .env is found)
venv/Scripts/streamlit run app/adapters/inbound/streamlit_ui/app.py

# Run all unit tests
venv/Scripts/pytest tests/unit/ -v

# Run a single test file
venv/Scripts/pytest tests/unit/domain/test_prompt_builder.py -v

# Run a single test by name
venv/Scripts/pytest tests/unit/ -v -k "test_business_rules_parsed_from_text"

# Run integration tests (requires Ollama running with qwen2.5-coder:7b)
venv/Scripts/pytest tests/integration/ -v
```

## Architecture

Hexagonal Architecture with three concentric rings:

**Domain** (`app/domain/`) — pure Python, zero I/O, zero framework imports.
- `value_objects/` — `TableSchema`, `ColumnDefinition`, `BusinessRule`, `BusinessRuleSet`, `RulePriority`. All frozen Pydantic models.
- `entities/` — `ETLRequest` (aggregate root), `SQLResult` (with `SQLResultStatus`). Both frozen.
- `services/prompt_builder.py` — `PromptBuilderService` transforms an `ETLRequest` into a `PromptPair` (system + user strings). This is the only place prompt templates live.

**Application** (`app/application/`) — orchestration, defines the boundary.
- `ports/llm_port.py` — `LLMPort` ABC with `generate_sql(ETLRequest) → SQLResult` and `health_check() → bool`. Any LLM backend must implement this.
- `dto/etl_request_dto.py` — loose Pydantic DTOs (`ETLRequestDTO`, `TableSchemaDTO`) that accept raw user input from the UI.
- `use_cases/generate_etl_sql.py` — `GenerateETLSQLUseCase.execute(dto)` maps the DTO → domain entity → calls `LLMPort`. **Never raises**; all exceptions are caught and returned as `SQLResult.failure(...)`.

**Adapters** (`app/adapters/`)
- `outbound/llm/ollama_client.py` — raw `httpx.Client` wrapper; `chat()` calls `POST /v1/chat/completions`, `is_reachable()` calls `GET /v1/models`.
- `outbound/llm/ollama_adapter.py` — implements `LLMPort`; calls `PromptBuilderService`, sends to `OllamaClient`, strips accidental markdown fences with `_extract_sql()`.
- `inbound/streamlit_ui/app.py` — Streamlit entry point. Uses `@st.cache_resource` on `create_use_case()` so the `httpx.Client` connection pool is reused across rerenders.

**Infrastructure** (`app/infrastructure/`)
- `config/settings.py` — `pydantic-settings` `BaseSettings` reading from `.env`. Fields: `ollama_base_url`, `ollama_model`, `llm_temperature`, `llm_max_tokens`, `log_level`.
- `logging/logger.py` — `configure_logging(settings)` called once at startup in `create_use_case()`.

**DI wiring** (`app/main.py`) — `create_use_case()` is the single factory that wires `Settings → OllamaClient → OllamaLLMAdapter → GenerateETLSQLUseCase`. The Streamlit app calls this through `@st.cache_resource`.

## Key Constraints

- **`LLMPort` receives `ETLRequest`, not `PromptPair`** — each adapter builds its own prompts, enabling future adapters (function-calling, etc.) without touching the domain.
- **DDL parsing is deferred (v1)** — `TableSchema` always uses `ddl_raw`; `columns` list is populated as empty from DTOs. The raw DDL string is forwarded directly to the LLM.
- **Sync only** — `httpx.Client` (not `AsyncClient`) is intentional; Streamlit is synchronous.
- **`SQLResult` never raises** — the use case catches all exceptions; the UI always receives a renderable result.
- Integration tests auto-skip when Ollama is unreachable (`pytest.mark.skipif` via `is_reachable()`).
