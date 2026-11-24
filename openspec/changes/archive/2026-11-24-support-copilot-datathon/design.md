## Context

O repositório é um framework de regras sem aplicação. As Fases 1–4 do grupo já validaram FastAPI, MLflow local, classificador TF-IDF, Evidently e README de LGPD/nuvem — em **outros domínios**. Este desenho reaproveita esses padrões e adiciona RAG + Guardrails. Requisitos observáveis: ver `proposal.md` e as specs em `specs/`.

Restrições que moldam a abordagem:

- Edital manda FastAPI/Flask, Scikit-learn/XGBoost, MLflow local, LangChain ou LlamaIndex, FAISS ou Chroma em memória, OpenAI ou Gemini, Evidently HTML, Pydantic ou Pandera, Dockerfile, `requirements.txt`.
- Texto do chamado: 1–1000 caracteres.
- Sem GPU, sem deploy real, sem versionar chaves.
- Imagem Docker precisa caber em máquina de aluno: embeddings via API, não via sentence-transformers/PyTorch.

## Goals / Non-Goals

**Goals:**

- Um processo FastAPI que cobre triagem, `/chat` RAG, Guardrails e redação de PII.
- Treino reproduzível com MLflow (Accuracy + F1 macro) e artefato `joblib` carregado no startup.
- Script de drift que **força** o Evidently a marcar degradação visual em texto.
- Entrega acadêmica completa: Docker, `requirements.txt`, README (Cloud Run + LGPD + roteiro STAR) e testes dos contratos da banca.

**Non-Goals:**

- Deploy real em GCP/Azure/AWS, CI/CD para nuvem, frontend, Prometheus, Airflow, ONNX, DVC, Model Registry completo.
- Fine-tune de LLM, banco vetorial persistente, autenticação de usuários.
- Copiar datasets/modelos de churn, MovieLens, laudo médico ou crédito.

## Decisions

### D1 — Stack e layout

Python 3.11, FastAPI, Pydantic v2, `uv` + `pyproject.toml` para lock, e `requirements.txt` gerado/exportado porque o edital pede o arquivo. Testes com pytest + httpx. Lint Ruff.

```
src/
  api/          app, rotas, schemas, dependencias
  ml/           treino, inferencia, tracking MLflow
  rag/          carga PDF, split, FAISS, LLM, guardrails, privacy
  drift/        simulacao + relatorio Evidently
data/processed/ tickets.csv (subset publico, colunas text,label)
manuals/        router-manual.pdf (manual original do grupo)
models/         ticket_classifier.joblib
reports/        drift_report.html
```

**Alternativa:** Flask — aceito pelo edital, mas o grupo já opera FastAPI nas Fases 1–4 e o Swagger nativo conta no vídeo.

### D2 — Dataset de tickets

Usar o dataset público de tickets de suporte IT (fila `Technical Support`, `Billing and Payments`, etc.; origem documentada no README, típico Kaggle/HuggingFace *multilingual customer support tickets*). Processar para `data/processed/tickets.csv`:

- `text` = assunto + corpo, truncado em 1000 caracteres (alinha treino ao contrato da API).
- `label` ∈ {`technical`, `billing`, `account`, `other`}, com `technical` agrupando filas técnicas/IT.
- Subset estratificado (ordem de 3–8 mil linhas) versionado no Git para treino e Docker sem credencial Kaggle.

**Alternativa:** TriageIQ 2k sintético — mais leve, mas fraco para a banca. XGBoost sobre TF-IDF — permitido, porém LogisticRegression da Fase 3 já venceu RF em texto e gera vídeo mais simples.

### D3 — Modelo clássico e MLflow

`Pipeline(TfidfVectorizer(ngram_range=(1,2), min_df=2), LogisticRegression(max_iter=1000, class_weight="balanced"))`. Split 80/20 estratificado, `random_state=42`. Persistir `models/ticket_classifier.joblib`.

MLflow tracking em SQLite (`sqlite:///mlflow.db`; o file store `./mlruns` é bloqueado no MLflow 3.18), experimento `support-copilot-triage`. Logar `ngram_range`/`min_df`/`C`, `accuracy`, `f1_macro` e o artefato. UI: `mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001` (porta 5000 conflita com AirPlay no macOS, lição da Fase 4).

### D4 — Contrato HTTP

Pydantic: `text` com `min_length=1`, `max_length=1000`, strip, rejeitar branco → 422 **antes** de Guardrails e modelo.

| Método | Rota | Papel |
|---|---|---|
| GET | `/health` | modelo carregado, índice RAG pronto |
| GET | `/docs` | Swagger (vídeo) |
| POST | `/predict` | só triagem |
| POST | `/chat` | triagem → Guardrails → (se técnico) PII → RAG |

`POST /chat` não técnico: 200 com `rag_applied: false` e mensagem de roteamento. Técnico sem chave LLM: 503. Guardrail: 400. Modelo ausente: 503.

### D5 — RAG (LangChain + FAISS em memória)

No lifespan: carregar `manuals/router-manual.pdf` (manual **original** em PT-BR sobre roteador doméstico: Wi-Fi, DHCP, NAT, reset, firmware — evita PDF proprietário). `RecursiveCharacterTextSplitter` (chunk 800, overlap 120). Embeddings e chat pelo mesmo provedor (`LLM_PROVIDER=gemini` padrão, `openai` opcional). Índice FAISS fica em memória do processo.

Prompt de sistema: responder **somente** com o contexto recuperado; se não houver trecho suficiente, dizer que o manual não cobre o assunto. `k=4`.

**Alternativa:** LlamaIndex + Chroma — equivalente no edital. LangChain+FAISS é o exemplo literal da banca. Embeddings locais — imagem Docker pesada demais.

### D6 — Guardrails em código (não LLM-as-judge)

Camada determinística **antes** da retrieval:

1. Lista de palavras proibidas (PT/EN): insultos graves, pedido de crime, exploração.
2. Padrões de jailbreak: `ignore (the )?(pdf|manual|previous instructions)`, `ignore o manual`, `desconsidere (as instruções|o pdf)`, `reveal (the )?system prompt`, `jailbreak`.

Match → 400 `{ "blocked": true, "reason": "prohibited_term"|"jailbreak" }` sem chamar FAISS/LLM. Testável sem chave.

**Alternativa:** NeMo Guardrails / LLM classificador — custo, latência e flakiness no vídeo. O edital pede “lógica de Guardrails no código”.

### D7 — PII antes do LLM

Regex no texto já validado:

- CPF: `000.000.000-00` ou 11 dígitos.
- E-mail RFC simplificado.
- Telefone BR: com/sem `+55`.

Substituir por `[CPF]`, `[EMAIL]`, `[PHONE]`. Logs estruturados gravam só categoria, `blocked`, latência — nunca o corpo bruto. Chaves só em env (`GEMINI_API_KEY`, `OPENAI_API_KEY`).

### D8 — Drift de **texto** (não PSI tabular da Fase 4)

Referência = `tickets.csv`. Produção simulada:

1. Inflar comprimento (repetir sentenças) — drift de `text_length`.
2. Injetar ruído/typos e tokens fora de vocabulário.
3. Enviesar o mix de classes (ex.: 80% `billing`).

Evidently: coluna de texto + descritores (length, OOV, non-letter) e/ou `DataDriftPreset` com mapping de texto. Saída: `reports/drift_report.html`. Controle: referência vs referência não deve acender o mesmo alerta.

### D9 — Docker e nuvem teórica

`Dockerfile` `python:3.11-slim`: `pip install -r requirements.txt`, COPY `src/`, `models/`, `manuals/`. CMD `uvicorn` na 8000. Sem GPU. Compose opcional só para MLflow no vídeo; o entregável obrigatório é o Dockerfile da API.

README: Artifact Registry → Cloud Run (HTTPS, CPU, autoscaling 0–N) → Secret Manager (chave LLM) → Cloud Logging. Sem deploy real. LGPD: base legal de execução de contrato/legítimo interesse para atendimento; PII mapeada; redação obrigatória antes de subprocessador no exterior (Gemini/OpenAI); retenção do chamado só o tempo do request.

### D10 — Testes que a banca “vê” no código

- 422 vazio / >1000 / 200 no limite 1000.
- Guardrail palavra proibida e jailbreak → 400, LLM mock não chamado.
- `/chat` billing → `rag_applied: false`.
- Health sem modelo → degradado.
- Script de drift cria HTML com tamanho > 0.

RAG com LLM real fica fora da suíte default (marca `integration`, skip sem chave).

## Risks / Trade-offs

- [Dataset sintético/fraco] → Mitigation: subset real de tickets IT com fila técnica documentada; truncar em 1000 chars para não mentir no contrato.
- [Imagem Docker pesada] → Mitigation: embeddings via API; `faiss-cpu`; não instalar torch/jupyter.
- [Gemini/OpenAI fora no dia do vídeo] → Mitigation: Guardrails e triagem funcionam offline; README com `.env.example`; 503 claro se faltar chave; gravar `/chat` técnico com chave válida **antes**.
- [Evidently 0.4+ mudou API] → Mitigation: pin da versão no lock; consultar docs da versão instalada no apply (Context7).
- [Copyright de manual de fabricante] → Mitigation: PDF original do grupo, não dump de TP-Link.
- [F1 baixo demais na banca] → Mitigation: `class_weight="balanced"`, n-grams, subset com classes mínimas; logar classification_report no MLflow.

## Migration Plan

Greenfield: a change **cria** a aplicação. Não há schema de produção nem consumidores. Rollback = não mesclar a change. Artefatos gerados (`models/`, `reports/`, `mlruns/`) ficam no `.gitignore` exceto o joblib e o HTML que a banca precisa ver versionados após o primeiro treino/drift.
