# rag-copilot Specification

## Purpose

Responde dúvidas técnicas de suporte apenas com o conteúdo de um manual em PDF, bloqueia prompts inseguros e remove dados pessoais antes de chamar o LLM.

## Requirements

### Requirement: Chat RAG restrito a chamado técnico
A API SHALL expor `POST /chat` com o texto da pergunta. O sistema MUST classificar o texto com o modelo de triagem e, somente se a categoria for técnica e o índice do manual estiver carregado, recuperar trechos do manual PDF e gerar a resposta com um LLM. Se a categoria não for técnica, o sistema MUST NÃO chamar o LLM e MUST devolver um roteamento explícito. Se a categoria for técnica, a chave do LLM estiver configurada e o índice do manual não estiver carregado, a API MUST responder 503 e MUST NÃO devolver sucesso com RAG aplicado.

#### Scenario: Pergunta técnica usa o manual
- **WHEN** o cliente envia `POST /chat` com uma dúvida coberta pelo manual (por exemplo configuração de um roteador) e o índice do manual está carregado
- **THEN** a resposta é 200, indica que veio do RAG e contém solução fundamentada nos trechos recuperados do PDF

#### Scenario: Pergunta não técnica não aciona o LLM
- **WHEN** o cliente envia `POST /chat` com um chamado de cobrança ou conta
- **THEN** a API responde 200 com a categoria prevista, informa que o Copilot RAG não se aplica e não envia o texto a nenhum provedor de LLM

#### Scenario: Resposta limitada ao PDF
- **WHEN** a pergunta técnica pede informação que não está no manual e o índice está carregado
- **THEN** a resposta declara que a informação não foi encontrada no manual em vez de inventar procedimento externo

#### Scenario: Índice ausente não finge RAG
- **WHEN** `POST /chat` é técnico e válido, a chave do LLM está configurada e o índice do manual não está carregado
- **THEN** a API responde 503, não chama o LLM e não responde sucesso com RAG aplicado

### Requirement: Guardrails de prompt inseguro
O sistema SHALL recusar, antes de qualquer chamada ao LLM, perguntas que contenham palavras proibidas ou que tentem fazer a IA ignorar o manual, o PDF ou as instruções (jailbreak), inclusive paráfrases em português ou inglês que não usem a frase exata já coberta. A recusa MUST ser explícita e MUST NÃO devolver conteúdo gerado pelo modelo.

#### Scenario: Palavra proibida bloqueia a resposta
- **WHEN** o texto de `POST /chat` contém um termo da lista de palavras proibidas
- **THEN** a API responde 400 com motivo de bloqueio por Guardrail e não consulta o índice nem o LLM

#### Scenario: Tentativa de ignorar o PDF é bloqueada
- **WHEN** o texto tenta instruir o modelo a ignorar o manual, ignorar instruções anteriores ou revelar o prompt de sistema
- **THEN** a API responde 400 com motivo de bloqueio por jailbreak e não consulta o LLM

#### Scenario: Paráfrase de ignorar o manual é bloqueada
- **WHEN** o texto pede para esquecer, desconsiderar ou não seguir o manual ou o PDF sem usar a frase exata "ignore o manual" (por exemplo "esqueça o pdf", "ignora o manual" ou "disregard the manual")
- **THEN** a API responde 400 com motivo de bloqueio por jailbreak e não consulta o índice nem o LLM

### Requirement: Proteção de PII antes do LLM
O sistema SHALL detectar e substituir no texto, antes de enviar qualquer conteúdo ao provedor de LLM, identificadores pessoais previsíveis: CPF, endereço de e-mail e número de telefone brasileiro. Telefone com `+55`, com DDD entre parênteses, com hífen sem espaço depois do DDD e com 11 dígitos adjacentes a uma pista de telefone (telefone, tel, celular ou whatsapp) MUST ser substituído por `[PHONE]`, inclusive o DDD. Onze dígitos nessa pista MUST NÃO ser marcados como `[CPF]`. O texto original com PII MUST NÃO ser persistido em log de aplicação.

#### Scenario: CPF e e-mail são redigidos
- **WHEN** um chamado técnico contém um CPF e um e-mail válidos em formato brasileiro
- **THEN** o payload enviado ao LLM substitui esses valores por marcadores e a resposta ao cliente não ecoa o CPF nem o e-mail originais nos logs

#### Scenario: Sem chave de LLM
- **WHEN** `POST /chat` é técnico e válido mas a chave do provedor de LLM não está configurada
- **THEN** a API responde 503 explicando a ausência da chave e não vaza segredo

#### Scenario: Celular de 11 dígitos não vira CPF
- **WHEN** um chamado técnico contém um CPF pontuado e o trecho "telefone 11987654321"
- **THEN** o payload enviado ao LLM traz `[CPF]` no documento pontuado, traz `[PHONE]` no celular e não contém os dígitos `11987654321`

#### Scenario: Celular com hífen sem espaço é redigido
- **WHEN** um chamado técnico contém o número `1198765-4321`
- **THEN** o payload enviado ao LLM não contém esses dígitos e marca o número como `[PHONE]`

#### Scenario: DDD entre parênteses sai inteiro
- **WHEN** um chamado técnico contém `(11)98765-4321`
- **THEN** o payload enviado ao LLM não contém o DDD `11` nem o assinante `98765-4321` desse telefone

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

### Requirement: Log estruturado sem corpo do chamado
Cada request atendida em `POST /predict` e `POST /chat` SHALL gerar uma linha de log com endpoint, categoria quando já conhecida, indicador de bloqueio, motivo, tamanho do texto e latência. A linha MUST NÃO incluir o texto do chamado.

#### Scenario: Log de chat traz latência e omite o texto
- **WHEN** o cliente envia `POST /chat` com um texto que contém um e-mail
- **THEN** o log dessa request inclui um valor de latência e não contém o e-mail nem o restante do texto do chamado

### Requirement: Modelos Gemini configuráveis
Quando o provedor de LLM configurado é Gemini, o sistema MUST usar o modelo de chat `gemini-2.5-flash-lite` e o modelo de embedding `gemini-embedding-001`, salvo quando a configuração de ambiente informar outros identificadores. A chave do provedor MUST permanecer só no ambiente e MUST NÃO entrar em log.

#### Scenario: Padrão usa os identificadores mais baratos
- **WHEN** o provedor é Gemini e a configuração não informa identificadores de modelo
- **THEN** a chamada de chat usa `gemini-2.5-flash-lite` e a construção do índice usa `gemini-embedding-001`

#### Scenario: Ambiente troca o identificador
- **WHEN** a configuração informa outro identificador de chat ou de embedding
- **THEN** o sistema usa esses identificadores no lugar dos padrões
