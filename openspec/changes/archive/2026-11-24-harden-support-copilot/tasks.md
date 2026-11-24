## 1. Corpus

- [x] 1.1 Escolher a primeira fonte de D1 cuja licença permita versionar o texto (CC0, CC-BY, MIT ou equivalente explícito), registrar URL e licença, e parar com o bloqueio escrito se nenhuma servir — verificar que a nota de fonte/licença existe ou que a change ficou explicitamente bloqueada, sem CSV sintético novo
- [x] 1.2 Manter `prepare_data` e `data/processed/tickets.csv` como estão — verificar que o README declara 10 moldes por classe e que o CSV não foi substituído por fonte externa
- [x] 1.3 Manter `models/ticket_classifier.joblib` treinado nos moldes atuais — verificar que o artefato continua no repositório e que o treino não foi refeito em outro corpus
- [x] 1.4 Manter `reports/drift_report.html` e `reports/drift_control.html` gerados sobre o CSV atual — verificar que os HTML não foram regenerados a partir de outra referência

## 2. PII e Guardrails

- [x] 2.1 Reordenar `redact_pii` como em D2 (telefone formatado, 11 dígitos a até 24 caracteres da pista, depois CPF e e-mail) — verificar testes dos cenários "Celular de 11 dígitos não vira CPF", "Celular com hífen sem espaço é redigido" e "DDD entre parênteses sai inteiro"
- [x] 2.2 Acrescentar os regex imperativos de D3 sem remover os padrões atuais — verificar teste do cenário "Paráfrase de ignorar o manual é bloqueada" para "esqueça o pdf", "ignora o manual" e "disregard the manual", com o LLM falso sem chamadas
- [x] 2.3 Estender o teste de `/chat` técnico para exigir ausência dos dígitos do celular no prompt — verificar `uv run pytest tests/test_privacy.py tests/test_api.py -q` verde nesses casos

## 3. Índice, health e log

- [x] 3.1 Tirar embeddings aleatórios do caminho de produção; sem chave ou com PDF ilegível, deixar `rag_index` nulo e registrar a falha sem segredo — verificar o cenário "Sem credencial o índice não fica pronto" (`rag_ready` false) e o cenário "Falha ao ler o manual fica no log"
- [x] 3.2 Fazer `/chat` técnico responder 503 quando o índice falta e a chave existe, e ler só `app.state.llm` sem reconstruir cliente no request — verificar o cenário "Índice ausente não finge RAG" e o cenário "Sem chave de LLM" com `.env` preenchido e `state.llm` nulo
- [x] 3.3 Adicionar `llm_configured` em `GET /health` sem ecoar a chave; manter `status` preso ao modelo — verificar os cenários "Health indica chave sem revelá-la" e "Health sem chave de LLM"
- [x] 3.4 Incluir `latency_ms` no log de `/predict` e `/chat`, inclusive em 400 e 503, sem passar o texto — verificar o cenário "Log de chat traz latência e omite o texto"

## 4. README

- [x] 4.1 Documentar no README que o CSV vem de 10 moldes por classe e que `accuracy` e `f1_macro` medem esse holdout — verificar a seção de setup
- [x] 4.2 Alinhar a seção de governança/nuvem aos campos reais do log (categoria, bloqueio, motivo, tamanho, latência, sem corpo) — verificar que o README deixa de prometer campo que a API não emite e cita a latência

## 5. Verificação integrada

- [x] 5.1 Rodar a suíte e o lint — verificar `uv run pytest tests/ -q` e `uv run ruff check src tests` sem falha
