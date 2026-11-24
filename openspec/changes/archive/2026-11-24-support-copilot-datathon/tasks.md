## 1. Scaffold

- [x] 1.1 Criar `pyproject.toml` (Python 3.11, FastAPI, scikit-learn, pandas, joblib, mlflow, langchain, faiss-cpu, pypdf, evidently, pydantic-settings, uvicorn, pytest, httpx, ruff) e `uv lock`, e verificar com `uv sync --group dev` que o ambiente instala sem erro
- [x] 1.2 Criar o layout `src/{api,ml,rag,drift}`, `tests/`, `data/processed/`, `manuals/`, `models/`, `reports/`, `.env.example` (sem segredos) e `.gitignore` (`mlruns/`, `.venv/`, `.env`) e verificar que os diretórios existem
- [x] 1.3 Preencher `AGENTS.md` com stack, comandos (`uv sync`, `uvicorn`, `pytest`, `ruff`) e mapa de pastas, e verificar que nenhuma linha de comando permanece `a definir`

## 2. Dados e manual

- [x] 2.1 Preparar `data/processed/tickets.csv` (colunas `text`,`label` ∈ technical/billing/account/other, textos ≤ 1000 chars, origem pública documentada) e verificar com pandas que há ≥ 200 linhas por classe e zero nulos
- [x] 2.2 Escrever `manuals/router-manual.pdf` original em PT-BR (Wi-Fi, DHCP, NAT, reset, firmware) e verificar que o PDF abre e contém as seções nomeadas

## 3. Triagem clássica e MLflow

- [x] 3.1 Implementar o pipeline TF-IDF + LogisticRegression e o CLI de treino que grava `models/ticket_classifier.joblib`, e verificar que o arquivo existe após `uv run python -m src.ml.train`
- [x] 3.2 Registrar no MLflow local (`sqlite:///mlflow.db`, experimento `support-copilot-triage`) parâmetros, `accuracy` e `f1_macro`, e verificar na UI (`mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001`) que a run lista as duas métricas
- [x] 3.3 Implementar o carregador de inferência (categoria + confiança) e verificar um teste unitário com texto técnico previsto como `technical`

## 4. API de triagem e validação

- [x] 4.1 Criar a app FastAPI com lifespan, `GET /health` e schemas Pydantic (`text` 1–1000, strip, rejeitar branco) e verificar que `GET /health` responde JSON com `model_loaded`
- [x] 4.2 Implementar `POST /predict` (200 com categoria/confiança/modelo; 503 sem artefato) e verificar os testes de 200 e 503
- [x] 4.3 Garantir 422 para texto vazio, só espaços e ≥ 1001 caracteres, e êxito no limite de 1000, em `/predict` e `/chat`, e verificar os testes de schema

## 5. Guardrails e PII

- [x] 5.1 Implementar Guardrails determinísticos (palavras proibidas PT/EN + padrões de jailbreak/ignorar manual) e verificar testes em que o match devolve 400 com `blocked` e `reason` sem chamar LLM
- [x] 5.2 Implementar redação de CPF, e-mail e telefone BR para `[CPF]`/`[EMAIL]`/`[PHONE]` e verificar testes unitários com exemplos válidos
- [x] 5.3 Instrumentar logs para não gravar o corpo bruto do chamado e verificar no teste que o logger não recebe CPF/e-mail originais

## 6. RAG e `/chat`

- [x] 6.1 Carregar o PDF, fazer chunking (800/120) e montar FAISS em memória no lifespan (LangChain, embeddings via `LLM_PROVIDER`) e verificar que `/health` reporta índice RAG pronto quando o PDF existe
- [x] 6.2 Implementar `POST /chat`: não técnico → 200 `rag_applied: false` sem LLM; técnico → PII + retrieval + Gemini/OpenAI só com contexto do PDF; sem chave → 503; e verificar testes com LLM mockado (billing não chama o cliente; técnico chama com texto redigido)
- [x] 6.3 Fixar o prompt para recusar informação fora do manual e verificar um teste de prompt/fixture em que contexto vazio produz a recusa documentada

## 7. Drift Evidently

- [x] 7.1 Implementar a simulação de produção (inflar comprimento, typos/OOV, mix de classes enviesado) e verificar que o CSV degradado difere da referência em comprimento médio e distribuição de labels
- [x] 7.2 Gerar `reports/drift_report.html` com Evidently (descritores de texto) e verificar que o arquivo existe, é HTML e a simulação padrão marca drift detectado
- [x] 7.3 Adicionar o caso controle referência vs referência e verificar que o alerta não replica o da simulação degradada

## 8. Empacotamento

- [x] 8.1 Exportar `requirements.txt` a partir do lock (runtime da API, modelo, RAG, Evidently) e verificar que o arquivo lista fastapi, scikit-learn, langchain, faiss, evidently e mlflow
- [x] 8.2 Escrever `Dockerfile` (python:3.11-slim, sem GPU, COPY modelo+manual, uvicorn :8000, chave só via env) e verificar `docker build` + `GET /health` e `/docs` com `/predict` e `/chat`

## 9. README de entrega

- [x] 9.1 Escrever o README com setup, treino, API, MLflow, drift e Docker, e verificar que um avaliador reproduz os comandos sem ler o código
- [x] 9.2 Incluir arquitetura teórica GCP (Artifact Registry → Cloud Run → Secret Manager → Logging), explícito que não há deploy real, e verificar a seção no README
- [x] 9.3 Incluir Privacy by Design/LGPD (base legal, PII, redação antes do LLM, sem segredos no Git, retenção) alinhada à API, e verificar a seção no README
- [x] 9.4 Incluir roteiro STAR ≤ 5 min (Swagger, MLflow Acc/F1, HTML de drift) com tempos, e verificar que as três evidências do edital estão listadas

## 10. Qualidade

- [x] 10.1 Rodar `uv run pytest tests/` e verificar que a suíte (validação, Guardrails, roteamento `/chat`, health, drift HTML) passa
- [x] 10.2 Rodar `uv run ruff check src tests` e verificar saída limpa
