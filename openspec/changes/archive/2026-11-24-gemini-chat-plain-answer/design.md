## Context

Ver proposal.md, Why. `GeminiClient.invoke` faz `str(content)`. No `gemini-3.5-flash-lite` esse conteúdo veio como lista de partes, e o `answer` ficou com o texto mais uma assinatura. O padrão em `Settings` e no exemplo de ambiente ainda é `gemini-2.5-flash-lite`. A tabela oficial de 24 de novembro de 2026 cobra US$ 0,10 / US$ 0,40 nesse id, US$ 0,25 / US$ 1,50 em `gemini-3.1-flash-lite` e US$ 0,30 / US$ 2,50 em `gemini-3.5-flash-lite`. O id 2.5 está restrito a quem já o usou; a chave nova deste projeto recebeu 404 e a API indicou `gemini-3.5-flash-lite`, que respondeu 200.

## Goals / Non-Goals

**Goals:**

- Trocar o padrão de chat para o modelo de texto mais barato que uma chave nova consegue chamar.
- Entregar `answer` como texto plano, seja o conteúdo uma string ou uma lista de partes.
- Manter override por `GEMINI_CHAT_MODEL` e `GEMINI_EMBEDDING_MODEL`.

**Non-Goals:**

- Alterar Guardrails, o 400, a triagem, o embedding padrão ou o contrato de status HTTP.
- Gravar a chave no exemplo de ambiente.
- Desligar o parâmetro de temperatura só porque a família 3.x o ignora.

## Decisions

O padrão de chat passa a ser `gemini-3.1-flash-lite`. É o menor preço de texto da tabela atual fora do id 2.5 bloqueado para chave nova. `gemini-3.5-flash-lite` fica como fallback verificado: o apply chama `generateContent` no 3.1 com a chave do ambiente; se a API responder 404, o padrão e o exemplo passam a `gemini-3.5-flash-lite` e a spec vigente é ajustada no mesmo apply. Não se volta para `gemini-2.5-flash-lite`.

A extração do texto fica em um único ponto, antes de `answer_from_context` devolver a string. String permanece string. Lista ou objeto de partes contribui só com o texto de cada parte, na ordem, unido sem separador extra além do que o próprio texto já traz. Campos de assinatura, extras e tipo da parte são descartados. O cliente de chat continua devolvendo `str` para o restante do fluxo.

O `.env` real não é reescrito pelo apply. Quem já definiu `GEMINI_CHAT_MODEL` continua no id escolhido. O exemplo e o default do código é que mudam.

## Risks / Trade-offs

- [O 3.1 também recusa a chave nova] → O apply confirma um 200 antes de fechar o padrão; o fallback verificado é o 3.5.
- [Outro formato de conteúdo no futuro] → A extração aceita string e lista de partes com texto; um formato desconhecido falha o teste do cenário de bloco, em vez de serializar o objeto.
- [O 3.1 custa mais que o 2.5] → O 2.5 não atende chave nova. O 3.1 é o menor preço ainda listado para esse caso.

## Migration Plan

Atualizar o default, o `.env.example` e os testes que citam `gemini-2.5-flash-lite`. Confirmar o id com uma chamada real de chat. Publicar o texto plano no `answer`. Rollback é voltar o default para o id anterior só se essa conta ainda receber 200 nele; para chave nova, o rollback utilizável é `gemini-3.5-flash-lite`.
