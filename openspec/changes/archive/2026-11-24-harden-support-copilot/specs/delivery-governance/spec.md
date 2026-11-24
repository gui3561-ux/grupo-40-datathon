## MODIFIED Requirements

### Requirement: Privacy by Design e LGPD
O `README.md` SHALL documentar Privacy by Design: base legal aplicável a chamados de suporte, quais PII o sistema trata, a redação obrigatória antes do LLM, a proibição de versionar chaves e textos com PII, e a política de retenção. A proteção MUST estar alinhada ao comportamento da API (redação antes do provedor externo). O README MUST descrever os campos que o log da API emite — categoria, bloqueio, motivo, tamanho do texto e latência — e MUST afirmar que o corpo do chamado não é registrado.

#### Scenario: Banca encontra a governança LGPD
- **WHEN** o avaliador lê a seção de governança do `README.md`
- **THEN** encontra a redação de CPF/e-mail/telefone antes do LLM, a ausência de segredos no repositório e a base legal do tratamento

#### Scenario: README descreve o log que a API emite
- **WHEN** o avaliador lê a seção de governança ou de nuvem do `README.md`
- **THEN** encontra categoria, bloqueio, latência e tamanho do texto, e a afirmação de que o corpo do chamado não entra no log

## ADDED Requirements

### Requirement: Origem do dataset no README
O `README.md` SHALL explicar que `tickets.csv` é gerado no repositório a partir de 10 moldes por classe (`technical`, `billing`, `account`, `other`), que não há texto de terceiros versionado nesse arquivo, e que `accuracy` e `f1_macro` descrevem o holdout desses moldes.

#### Scenario: Banca encontra a origem dos tickets
- **WHEN** o avaliador abre o `README.md` na parte de dados ou de setup
- **THEN** identifica os 10 moldes por classe, a ausência de dump público e o alcance das métricas de holdout
