## Why

O Datathon (Fase 5) exige um Copilot de suporte ponta a ponta: triagem clássica com tracking, RAG com Guardrails, validação de entrada, relatório de Data Drift, Docker e documentação de nuvem/LGPD. O repositório hoje só contém o framework de regras — sem API, modelo, pipeline ou entregáveis da banca — e a nota máxima depende de cobrir os cinco critérios do edital no mesmo produto, sem copiar os domínios das Fases 1–4.

## What Changes

- Treinar um classificador clássico (TF-IDF + LogisticRegression) sobre dataset público de tickets de suporte, com categorias que incluam fila técnica, e registrar Accuracy e F1 (macro) no MLflow local.
- Expor a inferência em FastAPI (`POST /predict`, `GET /health`) com contrato Pydantic: texto do chamado não vazio e no máximo 1000 caracteres.
- Adicionar `POST /chat`: se a triagem for técnica, carregar manual PDF (roteador), fazer chunking, buscar em FAISS em memória (LangChain) e responder via LLM (Gemini por padrão, OpenAI opcional); caso contrário, recusar RAG e devolver roteamento.
- Implementar Guardrails em código (palavras proibidas e tentativas de ignorar o PDF/jailbreak) e redação de PII (CPF, e-mail, telefone) **antes** de enviar texto ao LLM.
- Script offline que simula degradação dos tickets e gera `reports/drift_report.html` com Evidently, de forma que o drift apareça visualmente.
- Empacotar a API em `Dockerfile` + `requirements.txt` e documentar no `README.md` arquitetura teórica de nuvem (GCP Cloud Run) e Privacy by Design (LGPD), mais roteiro STAR do vídeo de 5 min.

## Capabilities

### New Capabilities

- `ticket-triage`: treino do classificador clássico, registro MLflow (Accuracy, F1) e API de inferência da categoria do chamado.
- `rag-copilot`: endpoint `/chat`, pipeline RAG (PDF → chunk → FAISS → LLM), Guardrails de entrada/saída e redação de PII antes do LLM.
- `data-observability`: validação estrutural do payload na API e geração do relatório Evidently de Data Drift em texto.
- `delivery-governance`: Docker da API, `requirements.txt`, README com nuvem teórica, LGPD e roteiro do vídeo STAR.

### Modified Capabilities

- (nenhuma — repositório sem specs vigentes)

## Impact

- Repositório passa de framework vazio para aplicação Python 3.11 (FastAPI, scikit-learn, MLflow, LangChain, FAISS, Evidently).
- Novos endpoints HTTP, artefato de modelo, PDF de manual, HTML de drift e imagem Docker.
- Segredo `GEMINI_API_KEY` / `OPENAI_API_KEY` só via ambiente; nunca versionado.
- Sem frontend, sem deploy real de nuvem, sem Prometheus/Airflow/ONNX — fora do edital e da nota.
