## 1. Texto plano do chat

- [ ] 1.1 Extrair só o texto das partes do modelo em `src/rag/pipeline.py` e verificar com um teste que string continua string e que uma lista com texto e assinatura devolve só a frase, sem a assinatura nem a estrutura da parte
- [ ] 1.2 Cobrir o cenário de bloco no teste do `/chat` com um cliente falso que devolve partes e verificar que `answer` é a frase plana

## 2. Padrão de chat

- [ ] 2.1 Chamar `generateContent` com `gemini-3.1-flash-lite` usando a chave do ambiente, sem imprimir a chave. Se a resposta for 200, manter esse id. Se for 404, usar `gemini-3.5-flash-lite` e atualizar o delta e a spec vigente de `rag-copilot` para esse id antes de seguir
- [ ] 2.2 Trocar o default em `src/config.py` e `GEMINI_CHAT_MODEL` no `.env.example` para o id confirmado em 2.1, sem editar o `.env` e sem colocar chave no exemplo. Verificar que o teste de default lê esse id e que a variável de ambiente ainda substitui chat e embedding
- [ ] 2.3 Atualizar o teste que instancia o cliente Gemini para esperar o id confirmado e o embedding `gemini-embedding-001`, e rodar `uv run pytest tests/test_api.py tests/test_rag_prompt.py -q`
