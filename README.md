# Copilot de Suporte — Datathon FIAP (Grupo 40)

Plataforma híbrida de suporte: triagem clássica (Scikit-learn + MLflow), RAG sobre manual de roteador (LangChain + FAISS), Guardrails, redação de PII, validação Pydantic e relatório Evidently de Data Drift.

**Grupo 40:** Guilherme Ramos Couceiro, Lucas Ribeiro Pestana, Sávio Aparecido Crispim, Wesley Oliveira, Cristiano Santos de Oliveira.

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

`data/processed/tickets.csv` sai de `src/ml/prepare_data.py`: 10 moldes por classe (`technical`, `billing`, `account`, `other`), 300 linhas cada, com só o número do exemplo mudando. Não há dump público de chamados nesse arquivo. As métricas `accuracy` e `f1_macro` medem o holdout desses moldes. Elas não descrevem uma fila real de suporte.

## API

```bash
uv run uvicorn src.api.main:app --reload --port 8000
```

- Swagger: http://127.0.0.1:8000/docs
- `GET /health` — modelo e índice RAG
- `POST /predict` — `{"text": "..."}` (1–1000 caracteres) → categoria
- `POST /chat` — triagem + Guardrails; RAG só se a categoria for `technical`

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

Texto vazio ou com mais de 1000 caracteres responde **422**. Palavras proibidas ou jailbreak (`ignore o manual`) respondem **400** sem chamar o LLM. Chamado de cobrança devolve `rag_applied: false`. Chamado técnico sem `GEMINI_API_KEY` responde **503**.

## MLflow

```bash
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001
```

Abra http://127.0.0.1:5001, experimento `support-copilot-triage`, métricas `accuracy` e `f1_macro`.

## Drift (Evidently)

```bash
uv run python -m src.drift.report
```

O script infla o comprimento dos tickets, injeta tokens fora de vocabulário e enviesa o mix de classes. Abra `reports/drift_report.html` — o preset marca Data Drift nos descritores de texto. O controle (referência vs referência) fica em `reports/drift_control.html` e **não** acende o mesmo alerta.

## Docker

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

PII tratada no texto do chamado: **CPF**, **e-mail**, **telefone**. Antes de qualquer envio ao subprocessador (Gemini/OpenAI, frequentemente fora do Brasil), a API substitui esses valores por `[CPF]`, `[EMAIL]` e `[PHONE]`. Guardrails bloqueiam prompts inseguros **antes** da retrieval e do LLM.

Chaves (`GEMINI_API_KEY`, `OPENAI_API_KEY`) e arquivos `.env` não são versionados. Cada request de `/predict` e `/chat` grava no log a categoria, o bloqueio, o motivo, o tamanho do texto e a latência. O corpo do chamado não entra nessa linha. Retenção: o texto vive só na memória da requisição; não há banco de tickets. O titular pode solicitar revisão de decisão automatizada (Art. 20) — a triagem clássica é um apoio ao atendimento, não uma decisão definitiva de recusa de serviço.

## Roteiro STAR do vídeo (5 min)

| Min | Bloco | Evidência |
|---|---|---|
| 0:00–0:40 | **S**ituation | Fila de suporte mistura cobrança, conta e problema técnico de roteador; o Copilot precisa triar e responder só com o manual. |
| 0:40–1:00 | **T**ask | Entregar API + RAG + Guardrails + drift + Docker, nos critérios da banca. |
| 1:00–2:20 | **A**ction — API | Swagger em `/docs`: `POST /predict` técnico; `POST /chat` billing (`rag_applied: false`); jailbreak `ignore o manual` → 400; texto vazio → 422. |
| 2:20–3:20 | **A**ction — MLflow | UI na porta 5001: experimento `support-copilot-triage` com `accuracy` e `f1_macro`. |
| 3:20–4:20 | **A**ction — Drift | Abrir `reports/drift_report.html` e mostrar drift de `text_length` / classes; contrastar com o HTML de controle. |
| 4:20–5:00 | **R**esult | Docker no ar, PII redigida antes do LLM, desenho Cloud Run no README. |

## Testes e qualidade

```bash
uv run pytest tests/
uv run ruff check src tests
```

## Licença

MIT — ver [LICENSE](LICENSE).
