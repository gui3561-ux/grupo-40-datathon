## Why

A chave do Gemini já está no ambiente, mas o chat e o índice ainda apontam para `gemini-2.0-flash` e `models/text-embedding-004`, ids que saíram da tabela de preços de novembro de 2026. Com a chave real, a montagem do índice chama a API no startup; um erro desse provedor hoje escapa do `except` e pode derrubar o processo inteiro, inclusive o `/predict`.

## What Changes

- O chat Gemini passa a usar `gemini-2.5-flash-lite` por padrão, o modelo de geração mais barato ainda listado (US$ 0,10 / US$ 0,40 por milhão de tokens, com free tier).
- O embedding Gemini passa a usar `gemini-embedding-001` por padrão, o embedding de texto mais barato ainda listado (US$ 0,15 por milhão).
- Os dois ids ficam em configuração (`Settings` e `.env.example`), para a próxima troca não exigir patch no código. O arquivo `.env` com a chave não é editado.
- Falha da API do provedor ao montar o índice deixa `rag_ready` falso, registra o log sem segredo e mantém `/predict` no ar.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `rag-copilot`: o provedor Gemini usa os ids de chat e embedding configuráveis, com esses padrões, e uma falha da API na carga do índice não derruba a triagem.

## Impact

- `src/rag/pipeline.py`, `src/config.py`, `src/api/main.py`, `.env.example`, `tests/test_api.py`.
- Contrato HTTP de `/chat`, `/predict` e `/health` permanece o mesmo. Sem dependência nova, sem persistir o índice, sem mexer em Guardrails ou redação de PII.
