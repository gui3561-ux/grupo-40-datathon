## 1. Configuração

- [x] 1.1 Acrescentar `gemini_chat_model` e `gemini_embedding_model` em `Settings`, com os padrões da spec, e documentar `GEMINI_CHAT_MODEL` e `GEMINI_EMBEDDING_MODEL` no `.env.example` sem editar o `.env` — verificar que um teste lê o padrão `gemini-2.5-flash-lite` / `gemini-embedding-001` e que uma variável de ambiente substitui cada um

## 2. Clientes Gemini

- [x] 2.1 Fazer `GeminiClient` e `_embeddings` usarem os ids de `Settings` (`model=` com `api_key` no chat e `google_api_key` no embedding), sem o prefixo `models/` e sem alterar o caminho OpenAI — verificar o cenário "Padrão usa os identificadores mais baratos" e o cenário "Ambiente troca o identificador" com os construtores do LangChain substituídos, sem chamada de rede

## 3. Carga do índice

- [x] 3.1 Capturar `Exception` em `load_rag_index` no lifespan e manter o log só com o tipo da exceção e o caminho do manual — verificar o cenário "Falha da API de embeddings não derruba a triagem": `rag_ready` falso, `POST /predict` responde e o log não contém o segredo colocado na mensagem da exceção

## 4. Verificação

- [x] 4.1 Rodar a suíte da área e o lint — verificar `uv run pytest tests/test_api.py -q` e `uv run ruff check src tests` sem falha
