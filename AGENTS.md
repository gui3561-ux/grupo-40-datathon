# AGENTS.md

Contrato deste repositório. O código vence este arquivo quando divergirem.

## Projeto
Copilot de suporte híbrido (Datathon FIAP, Grupo 40): triagem clássica de tickets, RAG sobre manual de roteador, Guardrails, redação de PII, relatório Evidently de drift e entrega Docker.

## Stack
- Linguagem: Python 3.11
- Framework: FastAPI + Pydantic v2
- Banco: FAISS em memória (RAG); MLflow SQLite (`sqlite:///mlflow.db`)
- Testes: pytest + httpx (TestClient)

## Comandos
- Instalar: `uv sync --group dev`
- Dev: `uv run uvicorn src.api.main:app --reload --port 8000`
- Teste: `uv run pytest tests/`
- Teste focado: `uv run pytest tests/test_api.py -q`
- Lint: `uv run ruff check src tests`
- Typecheck: (não há mypy neste projeto)
- Build: `docker build -t support-copilot:local .`

## Mapa
- Entrada HTTP: `src/api/main.py`
- Regras de negócio: `src/ml/`, `src/rag/`, `src/drift/`
- Persistência: `models/ticket_classifier.joblib`, `data/processed/tickets.csv`, `manuals/router-manual.pdf`
- UI: Swagger em `/docs` (sem frontend)
- Testes: `tests/`

## Convenções
- Consulta prévia ao MCP Context7: antes de implementar ou alterar código que utilize bibliotecas, frameworks, SDKs ou APIs da stack, consulte sempre o MCP do Context7 (`resolve-library-id` e `query-docs`) para obter a documentação da versão instalada e aplicar as melhores práticas recomendadas.
- Texto do chamado: 1 a 1000 caracteres, validado na borda (Pydantic) antes de modelo, Guardrails e RAG.
- Segredos (`GEMINI_API_KEY`, `OPENAI_API_KEY`) só em ambiente; logs não gravam o corpo do chamado.

## OpenSpec
Mudança de comportamento passa pelo OpenSpec. O procedimento é o que `openspec init` instalou neste repositório (skills e commands). As regras deste framework não substituem esse procedimento.

- Config: `openspec/config.yaml`
- Comportamento vigente: `openspec/specs/`
- Change em andamento: `openspec/changes/<id>/`
- Instruções da fase, se o CLI existir: `openspec instructions <artifact|apply|archive> --change <id>`

Pasta ou skill ausente: diga que o OpenSpec não está inicializado. Não invente subcomando, artefato ou template.
