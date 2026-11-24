## Why

Uma chave Gemini nova recebe 404 em `gemini-2.5-flash-lite`: o Google restringe os modelos 2.5 a quem já os usou e aponta o chat para a família 3.x. Com `gemini-3.5-flash-lite`, o `POST /chat` técnico responde 200, mas o campo `answer` chega como a representação de um bloco de conteúdo, com o texto e uma assinatura interna, em vez da frase do manual.

## What Changes

- O padrão de chat Gemini deixa de ser `gemini-2.5-flash-lite` e passa a ser `gemini-3.1-flash-lite`, o modelo de texto mais barato da tabela atual que não está restrito a usuários legados (US$ 0,25 / US$ 1,50 por milhão de tokens). O embedding permanece `gemini-embedding-001`.
- A configuração de ambiente continua podendo trocar os dois identificadores.
- O campo `answer` de um chat técnico com RAG passa a ser só o texto plano da resposta. Estrutura de partes, metadados e assinatura do modelo não entram nesse campo.
- O 400 de Guardrail (palavra proibida e jailbreak) permanece como está.

## Capabilities

### New Capabilities

### Modified Capabilities

- `rag-copilot`: o padrão de chat Gemini e o formato do campo `answer` quando o RAG gera a resposta.

## Impact

- `src/config.py`, `.env.example` e os testes que fixam `gemini-2.5-flash-lite`.
- `src/rag/pipeline.py`, na leitura do conteúdo devolvido pelo chat.
- `POST /chat` técnico: o contrato HTTP não muda de status; muda o texto de `answer` e o modelo chamado quando o ambiente não informa outro id.
- Contas que ainda conseguem chamar `gemini-2.5-flash-lite` continuam podendo apontá-lo por `GEMINI_CHAT_MODEL`.
