## Context

Ver `proposal.md` (Why). O comportamento novo está nos deltas em `specs/`. Hoje o treino lê `data/processed/tickets.csv` gerado por moldes em `src/ml/prepare_data.py` (1200 linhas, 40 esqueletos). `redact_pii` trata 11 dígitos como CPF antes do telefone. `load_rag_index` cai em embeddings aleatórios sem chave, o `lifespan` engole falha de carga, e `POST /chat` marca `rag_applied: true` com índice ausente. `log_request` não recebe latência. A rota de chat reconstrói o cliente de LLM a partir do ambiente quando `app.state.llm` é nulo.

Restrições que permanecem: Python 3.11, FastAPI, o mesmo `Pipeline` TF-IDF + LogisticRegression, FAISS em memória, Guardrails determinísticos, sem GPU, sem deploy real, chave só em ambiente.

## Goals / Non-Goals

**Goals:**

- Um CSV versionado que cumpre os limiares do delta de `ticket-triage`, com fonte e licença apontadas no README.
- Redação de telefone que não colide com CPF, Guardrails que pegam as paráfrases nomeadas no delta, e um `/chat` que só aplica RAG com índice real.
- Health, log e README alinhados ao que a API emite.

**Non-Goals:**

- Trocar o algoritmo, o manual PDF, o preset de drift ou o provedor de LLM.
- Persistir o índice FAISS em disco, adicionar classificador de jailbreak por LLM, ou autenticação.
- Separar `requirements.txt` de treino e de runtime. O edital continua exigindo Evidently nesse arquivo.
- Inventar frases se a licença do corpus público não permitir versionar o texto.

## Decisions

### D1 — Corpus público versionado, com teto

`prepare_data` deixa de expandir moldes. O fluxo passa a ser: arquivo-fonte em `data/raw/`, mapeamento para `text` + `label`, truncamento em 1000 caracteres, amostra estratificada se a fonte for maior, gravação de `data/processed/tickets.csv`.

Mapeamento de filas (ajustado ao vocabulário real da fonte, documentado no README):

- suporte técnico, rede, produto, IT → `technical`
- cobrança, pagamento, fatura → `billing`
- conta, login, acesso → `account`
- o restante usado na amostra → `other`

Teto de 4000 linhas estratificadas, piso do spec (800 linhas, 50 por classe, 200 textos distintos depois de normalizar dígitos). Assim o Git e a imagem Docker continuam leves.

Primeira fonte a verificar na implementação, nesta ordem, parando na primeira cuja licença permita redistribuir o texto no Git (CC0, CC-BY, MIT ou equivalente explícito):

1. O conjunto público de tickets de suporte ao cliente multilíngue citado no desenho arquivado (origem típica Hugging Face ou Kaggle), só se o download não exigir segredo e a licença autorizar o CSV processado.
2. Um segundo conjunto público de tickets de suporte com colunas de assunto e fila, sob a mesma regra de licença.

Se nenhuma passar, a tarefa para e relata o bloqueio. Não há fallback sintético.

**Alternativa:** gerar mais moldes com um LLM local. Rejeitada: continua sendo corpus artificial e não recupera a decisão de dataset público.

**Decisão na implementação:** nenhuma fonte passou na licença e nas quatro filas juntas. O CSV de `prepare_data` (10 moldes por classe) permanece, para o roteiro em português continuar reproduzível. O README declara essa origem e o alcance do F1. D1 não é executado.

### D2 — Ordem da redação e janela da pista

Em `redact_pii`, a ordem fica:

1. Telefone já formatado (`+55`, DDD entre parênteses com ou sem espaço, hífen `1198765-4321`).
2. Sequência de 11 dígitos somente se estiver a até 24 caracteres de uma pista (`telefone`, `tel`, `celular`, `whatsapp`, `fone`) → `[PHONE]`.
3. CPF pontuado, e-mail, e o 11 dígitos restante → `[CPF]`.

A janela evita que a palavra "telefone" no início do chamado pinte um CPF nú de `[PHONE]` no fim. O DDD do padrão com parênteses entra no trecho substituído, para `(11)98765-4321` não deixar `11` para trás.

**Alternativa:** validar dígito verificador de CPF. Fora do delta; onze dígitos sem pista continuam `[CPF]`, como o spec vigente já pedia.

### D3 — Guardrails continuam lista e regex

Acrescentar padrões imperativos, sem LLM:

- `esqueça|esquece|ignora|ignore|desconsidere|não siga|nao siga` + manual, PDF ou instruções
- `disregard|forget|do not follow` + manual, PDF ou instructions

Os padrões atuais (`ignore o manual`, `reveal the system prompt`, termos proibidos) permanecem. Não se tenta cobrir jailbreak codificado ou em outro idioma.

**Alternativa:** NeMo ou classificador. Continua fora: custo e flakiness no vídeo, e o delta pede recusa determinística.

### D4 — Índice real, cliente de LLM só no startup

`load_rag_index` só constrói FAISS com os embeddings do provedor configurado. Sem chave, não cria índice. Exceção de arquivo ausente, PDF ilegível ou falha do provedor sobe ao `lifespan`, que zera `rag_index`, grava a falha (tipo e caminho, sem segredo) e segue o processo no ar para `/predict`.

`build_llm_client` roda no `lifespan`. A rota lê `app.state.llm` e não instancia outro cliente no meio do request. Assim, anular o cliente no teste não ressuscita a chave do `.env`, e o 503 do spec fica estável.

Testes que precisam de retrieval colocam um `RagIndex` já pronto em `app.state` e um LLM falso. O health sem chave espera `rag_ready: false`. Embeddings aleatórios saem do caminho de produção.

```
lifespan
   |-- modelo ausente --> classifier = None  (health degradado, /predict 503)
   |-- sem chave ou PDF ruim --> rag_index = None, log da falha
   |-- chave ok + PDF ok --> FAISS com embeddings do provedor
   '-- llm = cliente ou None

POST /chat
   validacao --> guardrail --> triagem
        | nao tecnico --> 200 rag_applied false
        | sem llm --> 503
        | sem indice --> 503
        '-- redact --> retrieve --> LLM --> 200 rag_applied true
```

**Alternativa:** manter embeddings aleatórios e só mudar o booleano do health. Rejeitada: o booleano verdadeiro voltaria a significar "há um índice", não "há um índice do manual".

### D5 — Health e latência

`HealthResponse` ganha `llm_configured: bool`, verdadeiro quando `llm_api_key` está preenchida. `status` continua `ok` só com o modelo carregado. O valor da chave não entra no schema.

`log_request` ganha `latency_ms`, medido com `time.perf_counter` em `/predict` e `/chat`, inclusive nos retornos 400 e 503 desses handlers. O texto do chamado não é argumento do log.

### D6 — Drift e artefato

O simulador e o preset Evidently não mudam. Depois do CSV novo, o treino regrava `models/ticket_classifier.joblib` e o script de drift regrava `reports/drift_report.html` e o HTML de controle. `mlflow.db` segue fora do Git; quem for gravar o vídeo roda o treino local como o README já descreve.

## Risks / Trade-offs

- [Licença impede versionar o texto] → Parar na tarefa de corpus e avisar. Não substituir por molde.
- [F1 cai diante do corpus real] → Aceitar. Manter `class_weight="balanced"` e registrar `accuracy` e `f1_macro`. O número deixa de ser memorização de molde.
- [Regex de telefone marca pedido ("protocolo 11987654321") quando a pista está perto] → Janela de 24 caracteres. Caso ambíguo longe da pista continua `[CPF]`.
- [Paráfrase imperativa bloqueia uma frase legítima que cita "ignore o manual" no meio de um procedimento] → O mesmo risco já existe para a frase do roteiro. Não alargar para qualquer ocorrência de "manual".
- [Boot com chave chama a API de embeddings toda vez] → Fora desta change. Índice persistido exigiria outro contrato de artefato.
- [Quem dependia de `rag_ready: true` sem chave vê false] → É o breaking descrito na proposal. Testes e README acompanham.

## Migration Plan

1. Confirmar licença, gravar o CSV processado, citar fonte e licença no README.
2. Retreinar o joblib e regenerar os HTML de drift.
3. Subir API, PII, Guardrails, health e log em seguida, para a suíte não misturar corpus novo com asserções do índice falso.
4. Rollback: restaurar `tickets.csv`, `ticket_classifier.joblib` e os HTML anteriores no Git. Não há migração de banco.

## Open Questions

Nenhuma. A fonte exata se resolve na primeira tarefa pela regra de licença de D1; se nenhuma servir, o trabalho para em vez de escolher outro desenho.
