## Why

A entrega cobre o contrato da banca, mas três histórias que o README e o desenho contam não batem com o código: o F1 sai de 40 moldes repetidos, telefone sem máscara vaza ou vira `[CPF]`, e o `/chat` técnico pode responder `rag_applied: true` sem um índice de verdade. Corrigir isso agora deixa a demonstração e a seção de LGPD defensáveis se a banca abrir o CSV, digitar um celular ou cair o PDF.

## What Changes

- Manter o CSV gerado por 10 moldes por classe. Nenhuma fonte pública coube na licença e nas quatro filas ao mesmo tempo, e trocar o corpus quebraria o roteiro em português. O README declara essa origem e que Accuracy e F1 medem o holdout desses moldes.
- Redigir telefone brasileiro de ponta a ponta (com `+55`, com DDD entre parênteses, hífen sem espaço e 11 dígitos ao lado de pista de telefone) como `[PHONE]`, sem engolir esse número como CPF. O teste de `/chat` passa a exigir a ausência dos dígitos originais.
- Alargar os Guardrails determinísticos para paráfrases de "ignorar o manual / o PDF / as instruções" em português e inglês, ainda antes da retrieval e do LLM.
- **BREAKING:** sem chave do provedor, o índice deixa de subir com embeddings falsos; `rag_ready` fica false. `/chat` técnico com modelo carregado e índice ausente responde 503 e não devolve `rag_applied: true`.
- `GET /health` ganha um indicador booleano de chave de LLM configurada, sem ecoar o segredo. Falha ao carregar PDF ou índice entra no log. Cada request de `/predict` e `/chat` registra latência além de categoria, bloqueio, motivo e tamanho — nunca o corpo.
- O README descreve os campos de log que a API emite e deixa explícito que `tickets.csv` sai de moldes do repositório, não de um dump público.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `ticket-triage`: o treino continua no CSV de moldes, com essa limitação escrita no README, e o health informa se a chave do LLM está configurada.
- `rag-copilot`: redação de telefone, bloqueio de paráfrase de jailbreak, RAG só quando o índice real existe, e log estruturado com latência e sem corpo.
- `delivery-governance`: o README explica os moldes do dataset e descreve os campos de log emitidos pela API.

## Impact

- `data/processed/tickets.csv`, `models/ticket_classifier.joblib` e os HTML de drift permanecem os artefatos atuais.
- `src/rag/privacy.py`, `src/rag/guardrails.py`, `src/rag/pipeline.py`, `src/api/routes.py`, `src/api/schemas.py`, `src/api/main.py`, `src/logutil.py`.
- `README.md` (origem dos dados, LGPD e logs). Sem novo serviço, sem frontend, sem deploy real.
- A suíte deixa de depender de `FakeEmbeddings` para marcar o índice como pronto. O drift em `data-observability` não muda de requisito: segue comparando a referência versionada com o lote degradado.
- Decisão: sem corpus público que preserve o roteiro e a licença, o CSV de moldes fica e o README deixa de apresentá-lo como fila real.
