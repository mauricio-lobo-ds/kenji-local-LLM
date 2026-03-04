# Kenji — ETL SQL Generator

Gera SQL ETL pronto para produção a partir de schemas de tabelas, amostras de dados e regras de negócio, usando um LLM local via Ollama.

---

## Pré-requisitos

- Python 3.11+
- [Ollama](https://ollama.com) instalado e rodando localmente

---

## Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd kenji
```

### 2. Crie e ative o ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o ambiente

```bash
cp .env.example .env
```

O `.env` já vem com os valores padrão e funciona sem alteração:

| Variável | Padrão | Descrição |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Endereço da API do Ollama |
| `OLLAMA_MODEL` | `qwen2.5-coder:7b` | Modelo a ser usado |
| `LLM_TEMPERATURE` | `0.1` | Temperatura de geração (mais baixo = mais determinístico) |
| `LLM_MAX_TOKENS` | `2048` | Limite de tokens na resposta |
| `LOG_LEVEL` | `INFO` | Nível de log (`DEBUG`, `INFO`, `WARNING`) |

---

## Rodando o modelo local

Antes de iniciar a aplicação, baixe e suba o modelo no Ollama:

```bash
ollama run qwen2.5-coder:7b
```

Na primeira execução o modelo será baixado (~4 GB). Nas próximas, o comando sobe direto.

> Para usar outro modelo, basta alterar `OLLAMA_MODEL` no `.env` e garantir que ele esteja disponível no Ollama (`ollama list`).

---

## Rodando a aplicação

**Execute sempre a partir da raiz do projeto** (onde fica o `.env`):

```bash
# Windows (venv ativo)
venv\Scripts\streamlit run app/adapters/inbound/streamlit_ui/app.py

# Linux / macOS (venv ativo)
venv/bin/streamlit run app/adapters/inbound/streamlit_ui/app.py
```

A interface abrirá automaticamente em `http://localhost:8501`.

### Como usar

1. **Source Tables** — informe o nome e o DDL (ou descrição) de cada tabela de origem. Use "＋ Add source table" para adicionar mais de uma.
2. **Data Sample** — cole algumas linhas representativas das tabelas de origem (CSV, JSON ou texto livre).
3. **Target Table** — informe o nome e o DDL da tabela de destino.
4. **Business Rules** — escreva uma regra por linha.
5. **SQL Dialect** — selecione o banco de destino (PostgreSQL, Snowflake, BigQuery, etc.).
6. **Additional Context** — campo opcional para informações extras.
7. Clique em **Generate ETL SQL**.

O SQL gerado aparece abaixo do botão. Um badge no canto superior direito indica se o Ollama está conectado.

---

## Testes

### Unitários (sem dependências externas)

```bash
venv\Scripts\pytest tests/unit/ -v
```

### Um único arquivo ou teste

```bash
venv\Scripts\pytest tests/unit/domain/test_prompt_builder.py -v
venv\Scripts\pytest tests/unit/ -v -k "test_business_rules_parsed_from_text"
```

### Integração (requer Ollama rodando)

```bash
venv\Scripts\pytest tests/integration/ -v
```

Os testes de integração são pulados automaticamente se o Ollama não estiver acessível.
