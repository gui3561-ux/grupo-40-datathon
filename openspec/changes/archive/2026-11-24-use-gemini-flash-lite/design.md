## Context

Ver `proposal.md` para o motivo. Hoje `GeminiClient` e `_embeddings` ignoram `Settings` e passam ids fixos para `ChatGoogleGenerativeAI` e `GoogleGenerativeAIEmbeddings`. O lifespan em `src/api/main.py` só trata `FileNotFoundError`, `OSError`, `ValueError` e `RagUnavailable`. O log dessa falha grava o tipo da exceção e o caminho do PDF, nunca a mensagem.

## Goals / Non-Goals

**Goals:**

- Defaults de chat e embedding Gemini nos ids da spec, lidos da configuração.
- Carga do índice que falha na API do provedor degrada para `rag_ready` falso sem derrubar o processo.
- O log dessa falha continua sem segredo.

**Non-Goals:**

- Persistir o FAISS, desligar thinking, trocar o modelo OpenAI, editar o `.env` que guarda a chave, ou alterar Guardrails, PII e o contrato HTTP.

## Decisions

### Ids em Settings, não no construtor

`Settings` ganha `gemini_chat_model` (padrão `gemini-2.5-flash-lite`) e `gemini_embedding_model` (padrão `gemini-embedding-001`). O pydantic-settings já lê o `.env`; os nomes de ambiente são `GEMINI_CHAT_MODEL` e `GEMINI_EMBEDDING_MODEL`. `.env.example` documenta os dois com esses valores. O `.env` real não é alterado: quem não definir a variável fica no padrão do código.

Alternativa: deixar o id só no construtor. Foi rejeitada porque a próxima troca de preço voltaria a exigir patch.

O embedding usa o id puro `gemini-embedding-001`, sem o prefixo `models/` do id antigo. É o identificador da tabela atual do Gemini Developer API. O caminho OpenAI (`gpt-4o-mini` e `OpenAIEmbeddings`) permanece como está.

`GeminiClient` e `_embeddings` recebem o `Settings` e repassam `model=` junto com a chave que já usam (`api_key` no chat, `google_api_key` no embedding).

### Except largo só na carga do índice

O `try` de `load_rag_index` passa a capturar `Exception`. O log segue o formato atual: `rag_index_unavailable`, `type(exc).__name__` e o caminho do manual. A mensagem da exceção não entra no log, porque clientes HTTP às vezes ecoam a chave nela.

Alternativa: capturar só `google.genai.errors.APIError`. Foi rejeitada porque o erro real pode vir embrulhado pelo LangChain ou pelo transporte, e um tipo estreito deixa o processo cair — o problema que esta change fecha.

Um bug de programação na carga também cai nesse ramo e aparece como índice indisponível. O tipo no log distingue isso de um PDF ausente. O processo continuar no ar vale mais do que derrubar o `/predict`.

## Risks / Trade-offs

- [Flash-Lite 2.5 responde pior em português que um Flash maior] → o id é configuração; troca sem patch.
- [O id some da API no futuro] → mesma saída, via ambiente.
- [Except largo esconde TypeError na carga] → o log traz o nome da classe; o sintoma visível é `rag_ready` falso, não um processo morto.
- [Trocar o embedding invalida um índice antigo] → o índice é só memória e nasce de novo a cada boot. Não há arquivo para migrar.

## Migration Plan

Reiniciar o processo. Rollback é voltar os dois padrões em `Settings` e os ids passados ao cliente. Não há schema nem dado persistido.
