## ADDED Requirements

### Requirement: Modelos Gemini configuráveis
Quando o provedor de LLM configurado é Gemini, o sistema MUST usar o modelo de chat `gemini-2.5-flash-lite` e o modelo de embedding `gemini-embedding-001`, salvo quando a configuração de ambiente informar outros identificadores. A chave do provedor MUST permanecer só no ambiente e MUST NÃO entrar em log.

#### Scenario: Padrão usa os identificadores mais baratos
- **WHEN** o provedor é Gemini e a configuração não informa identificadores de modelo
- **THEN** a chamada de chat usa `gemini-2.5-flash-lite` e a construção do índice usa `gemini-embedding-001`

#### Scenario: Ambiente troca o identificador
- **WHEN** a configuração informa outro identificador de chat ou de embedding
- **THEN** o sistema usa esses identificadores no lugar dos padrões

## MODIFIED Requirements

### Requirement: Prontidão do índice do manual
`GET /health` SHALL indicar `rag_ready` verdadeiro somente quando o índice em memória do manual foi construído com os embeddings do provedor configurado. Sem credencial desse provedor, quando a carga do manual falha, ou quando a API do provedor de embeddings falha durante a construção do índice, `rag_ready` MUST ser falso. A falha de carga MUST ser registrada no log de aplicação, sem corpo de chamado e sem segredo. Uma falha da API do provedor na construção do índice MUST NÃO impedir o processo de atender `GET /health` e `POST /predict`.

#### Scenario: Sem credencial o índice não fica pronto
- **WHEN** a API inicia sem a chave do provedor de embeddings
- **THEN** `GET /health` reporta `rag_ready` falso

#### Scenario: Falha ao ler o manual fica no log
- **WHEN** a API inicia com a chave configurada e o arquivo do manual ausente ou ilegível
- **THEN** `GET /health` reporta `rag_ready` falso e o log registra a falha de carga sem incluir segredo

#### Scenario: Falha da API de embeddings não derruba a triagem
- **WHEN** a API inicia com a chave configurada e a construção do índice falha por erro do provedor de embeddings
- **THEN** `GET /health` reporta `rag_ready` falso, `POST /predict` continua respondendo e o log registra a falha sem incluir segredo
