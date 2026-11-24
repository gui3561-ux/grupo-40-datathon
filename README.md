# Copilot de Suporte — Datathon FIAP (Grupo 40)

Plataforma híbrida de suporte: triagem clássica (TF-IDF + regressão logística, Scikit-learn, MLflow), RAG sobre o manual de roteador (LangChain + FAISS em memória), Guardrails, redação de PII, validação Pydantic e relatório Evidently de Data Drift.

**Grupo 40:** RM371323 Guilherme Ramos Couceiro, RM372947 Lucas Ribeiro Pestana, RM373551 Sávio Aparecido Crispim, RM373555 Wesley Oliveira, RM373529 Cristiano Santos de Oliveira.

O chamado entra em `POST /predict` ou `POST /chat`. O texto vale de 1 a 1000 caracteres. No `/chat`, Guardrails recusam termo proibido e jailbreak antes do modelo e do LLM. A triagem devolve `technical`, `billing`, `account` ou `other`. Só `technical` recupera trechos do PDF e chama o LLM. A resposta técnica sai como texto plano.

## Setup

Pré-requisitos: Python 3.11, [uv](https://docs.astral.sh/uv/), Docker (opcional).

```bash
uv sync --group dev
cp .env.example .env   # preencha GEMINI_API_KEY para o /chat técnico
```

Gerar dados, manual, modelo e relatório de drift:

```bash
uv run python -m src.ml.prepare_data
uv run python -m src.ml.write_manual
uv run python -m src.ml.train
uv run python -m src.drift.report
```

`data/processed/tickets.csv` sai de `src/ml/prepare_data.py`: 10 moldes por classe (`technical`, `billing`, `account`, `other`), 300 linhas cada, com só o número do exemplo mudando. Não há dump público de chamados nesse arquivo. As métricas `accuracy` e `f1_macro` medem o holdout desses moldes (20%, estratificado, `random_state=42`). Elas não descrevem uma fila real de suporte.

O treino grava `models/ticket_classifier.joblib`: `TfidfVectorizer` (n-gramas 1–2, `min_df=2`) e `LogisticRegression` (`class_weight=balanced`, `C=1.0`). O identificador servido pela API é `ticket_classifier`. O manual em `manuals/router-manual.pdf` é gerado por `src/ml/write_manual.py` (Wi-Fi, DHCP, NAT, reset e firmware).

## Variáveis de ambiente

Copie `.env.example`. Chaves ficam só no ambiente.

| Variável | Padrão | Uso |
|---|---|---|
| `LLM_PROVIDER` | `gemini` | `gemini` ou `openai` |
| `GEMINI_API_KEY` | vazio | Chat e embeddings Gemini |
| `GEMINI_CHAT_MODEL` | `gemini-3.1-flash-lite` | Modelo de chat |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-001` | Índice do manual |
| `OPENAI_API_KEY` | vazio | Usada quando `LLM_PROVIDER=openai` (chat `gpt-4o-mini`) |
| `MODEL_PATH` | `models/ticket_classifier.joblib` | Artefato da triagem |
| `MANUAL_PATH` | `manuals/router-manual.pdf` | PDF do RAG |
| `TICKETS_CSV` | `data/processed/tickets.csv` | Treino e drift |
| `MLFLOW_TRACKING_URI` | `sqlite:///mlflow.db` | Tracking local |
| `MLFLOW_EXPERIMENT` | `support-copilot-triage` | Nome do experimento |
| `LOG_LEVEL` | `INFO` | Nível do log da API |

`GET /health` expõe `llm_configured` como booleano. O valor da chave não entra na resposta nem no log.

## API

```bash
uv run uvicorn src.api.main:app --reload --port 8000
```

Swagger: http://127.0.0.1:8000/docs

Na subida, a API carrega o classificador e, se a chave do provedor existir, monta o índice FAISS do PDF (pedaços de 800 caracteres, sobreposição 120, 4 trechos por pergunta). Falha de leitura do manual ou da API de embeddings deixa `rag_ready` falso, registra só o tipo do erro e mantém `POST /predict` no ar.

| Método | Corpo | Sucesso |
|---|---|---|
| `GET /health` | — | `status` (`ok` com modelo, `degraded` sem ele), `model_loaded`, `rag_ready`, `llm_configured` |
| `POST /predict` | `{"text": "..."}` | `category`, `confidence`, `model` |
| `POST /chat` | `{"text": "..."}` | `category`, `confidence`, `rag_applied`, `answer` |

Campo extra no JSON responde **422**. Texto vazio, só espaços ou com mais de 1000 caracteres responde **422** antes de Guardrails, modelo e RAG.

`POST /chat` segue esta ordem:

1. Guardrail. Termo proibido (`prohibited_term`) ou jailbreak (`jailbreak`, inclusive paráfrase como `esqueça o pdf`) responde **400** e não classifica nem chama o LLM.
2. Sem o `.joblib`, responde **503** (`Modelo de triagem não carregado`).
3. Categoria diferente de `technical`: **200**, `rag_applied: false`, sem LLM. A resposta pede encaminhamento para a fila correspondente.
4. Chamado técnico sem chave do provedor: **503** (`Chave do LLM não configurada`).
5. Chamado técnico com chave e sem índice: **503** (`Índice do manual não carregado`), sem chamar o LLM.
6. Com índice: redação de CPF, e-mail e telefone, retrieval e chat com `temperature=0`. `rag_applied: true`. O campo `answer` traz só o texto da solução. Se o manual não cobre a pergunta, a resposta é `A informação não foi encontrada no manual.`

Exemplos:

```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/predict \
  -H 'content-type: application/json' \
  -d '{"text":"O DHCP do roteador nao entrega IP e o Wi-Fi cai."}'
curl -s -X POST http://127.0.0.1:8000/chat \
  -H 'content-type: application/json' \
  -d '{"text":"Como faco o reset de fabrica do roteador?"}'
```

## MLflow

```bash
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001
```

Abra http://127.0.0.1:5001, experimento `support-copilot-triage`, run `ticket-triage`, métricas `accuracy` e `f1_macro`. O `mlflow.db` e a pasta `mlruns/` ficam de fora do Git.

## Drift (Evidently)

```bash
uv run python -m src.drift.report
```

O script grava `data/processed/tickets_production.csv`: alonga o texto, injeta tokens fora de vocabulário e concentra o rótulo em `billing`. A comparação usa `text_length`, `word_count`, `non_letter_ratio` e `label`. Abra `reports/drift_report.html`. O controle (referência vs referência) fica em `reports/drift_control.html` e não acende o mesmo alerta.

## Docker

O build precisa do modelo, do manual e de `data/processed/` já gerados. A imagem usa `requirements.txt` (export do uv, sem o grupo dev) e não inclui GPU. O índice FAISS nasce na subida do processo, quando a chave está no ambiente e o container alcança a API de embeddings.

```bash
docker build -t support-copilot:local .
docker run --rm -p 8000:8000 support-copilot:local
```

A chave do LLM entra só por ambiente, nunca na imagem:

```bash
docker run --rm -p 8000:8000 -e GEMINI_API_KEY="$GEMINI_API_KEY" support-copilot:local
```

`GET /health` e `/docs` devem listar `/predict` e `/chat`.

## Arquitetura teórica de nuvem (GCP)

**Não há deploy real nesta entrega.** O mesmo `Dockerfile` seria publicado assim:

```
[Git] --> [Artifact Registry]
                 |
                 v
        [Cloud Run]  <--- [Secret Manager: GEMINI_API_KEY]
           |  HTTPS autoscaling 0-N
           v
        [Cloud Logging]
```

1. Build da imagem e push no Artifact Registry.
2. Cloud Run serve o container (CPU, sem GPU), HTTPS gerenciado, autoscaling de 0 a N instâncias conforme concorrência dos chamados.
3. A chave do LLM fica no Secret Manager e é injetada como variável de ambiente — nunca no Git nem na imagem.
4. Logs estruturados (categoria, bloqueio, motivo, tamanho do texto e latência, **sem** corpo do chamado) vão para o Cloud Logging.

Isso escala o Copilot sem reescrever a API: o contrato HTTP permanece o mesmo.

## Privacy by Design e LGPD

O tratamento de chamados de suporte se apoia na **execução de contrato** (Art. 7º, V) e, para melhoria do serviço de triagem, no **legítimo interesse** (Art. 7º, IX), com teste de proporcionalidade. Não usamos a base de proteção ao crédito.

PII tratada no texto do chamado: **CPF**, **e-mail** e **telefone** brasileiro. O telefone cobre `+55`, DDD entre parênteses, hífen colado no DDD e 11 dígitos ao lado de uma pista (`telefone`, `tel`, `celular`, `whatsapp`). Antes de qualquer envio ao subprocessador (Gemini ou OpenAI, frequentemente fora do Brasil), a API substitui esses valores por `[CPF]`, `[EMAIL]` e `[PHONE]`. Onze dígitos nessa pista de telefone viram `[PHONE]`. Guardrails bloqueiam prompts inseguros antes da retrieval e do LLM.

Chaves (`GEMINI_API_KEY`, `OPENAI_API_KEY`) e arquivos `.env` não são versionados. Cada request de `/predict` e `/chat` grava no log o endpoint, a categoria, o bloqueio, o motivo, o tamanho do texto e a latência. O corpo do chamado não entra nessa linha. Retenção: o texto vive só na memória da requisição; não há banco de tickets. O titular pode solicitar revisão de decisão automatizada (Art. 20) — a triagem clássica é um apoio ao atendimento, não uma decisão definitiva de recusa de serviço.

## Roteiro STAR do vídeo (5 min)

| Min | Bloco | Evidência |
|---|---|---|
| 0:00–0:40 | **S**ituation | Fila de suporte mistura cobrança, conta e problema técnico de roteador; o Copilot precisa triar e responder só com o manual. |
| 0:40–1:00 | **T**ask | Entregar API + RAG + Guardrails + drift + Docker, nos critérios da banca. |
| 1:00–2:20 | **A**ction — API | Swagger em `/docs`: `GET /health` (`model_loaded`, `rag_ready`, `llm_configured`); `POST /predict` técnico; `POST /chat` billing (`rag_applied: false`); jailbreak `ignore o manual` → 400; texto vazio → 422. |
| 2:20–3:20 | **A**ction — MLflow | UI na porta 5001: experimento `support-copilot-triage` com `accuracy` e `f1_macro`. |
| 3:20–4:20 | **A**ction — Drift | Abrir `reports/drift_report.html` e mostrar drift de `text_length` / classes; contrastar com o HTML de controle. |
| 4:20–5:00 | **R**esult | Docker no ar, PII redigida antes do LLM, desenho Cloud Run no README. |

## Testes e qualidade

```bash
uv run pytest tests/
uv run ruff check src tests
```

Não há typecheck (mypy) neste repositório.

## Mapa

- HTTP: `src/api/main.py`, `src/api/routes.py`, `src/api/schemas.py`
- Triagem: `src/ml/prepare_data.py`, `src/ml/train.py`, `src/ml/predict.py`
- RAG, Guardrails e PII: `src/rag/pipeline.py`, `src/rag/guardrails.py`, `src/rag/privacy.py`
- Drift: `src/drift/simulate.py`, `src/drift/report.py`
- Configuração: `src/config.py` — log: `src/logutil.py`
- Testes: `tests/`

## Licença

MIT — ver [LICENSE](LICENSE).
