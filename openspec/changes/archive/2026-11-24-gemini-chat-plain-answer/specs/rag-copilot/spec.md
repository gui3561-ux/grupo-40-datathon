## MODIFIED Requirements

### Requirement: Chat RAG restrito a chamado técnico
A API SHALL expor `POST /chat` com o texto da pergunta. O sistema MUST classificar o texto com o modelo de triagem e, somente se a categoria for técnica e o índice do manual estiver carregado, recuperar trechos do manual PDF e gerar a resposta com um LLM. Se a categoria não for técnica, o sistema MUST NÃO chamar o LLM e MUST devolver um roteamento explícito. Se a categoria for técnica, a chave do LLM estiver configurada e o índice do manual não estiver carregado, a API MUST responder 503 e MUST NÃO devolver sucesso com RAG aplicado. Quando o RAG gera a resposta, o campo `answer` MUST ser somente o texto plano dessa resposta. Partes estruturadas, metadados e assinatura devolvidos pelo modelo MUST NÃO aparecer nesse campo.

#### Scenario: Pergunta técnica usa o manual
- **WHEN** o cliente envia `POST /chat` com uma dúvida coberta pelo manual (por exemplo configuração de um roteador) e o índice do manual está carregado
- **THEN** a resposta é 200, indica que veio do RAG e o campo `answer` é texto plano com a solução fundamentada nos trechos recuperados do PDF

#### Scenario: Pergunta não técnica não aciona o LLM
- **WHEN** o cliente envia `POST /chat` com um chamado de cobrança ou conta
- **THEN** a API responde 200 com a categoria prevista, informa que o Copilot RAG não se aplica e não envia o texto a nenhum provedor de LLM

#### Scenario: Resposta limitada ao PDF
- **WHEN** a pergunta técnica pede informação que não está no manual e o índice está carregado
- **THEN** a resposta declara que a informação não foi encontrada no manual em vez de inventar procedimento externo

#### Scenario: Índice ausente não finge RAG
- **WHEN** `POST /chat` é técnico e válido, a chave do LLM está configurada e o índice do manual não está carregado
- **THEN** a API responde 503, não chama o LLM e não responde sucesso com RAG aplicado

#### Scenario: Bloco do modelo não vaza no answer
- **WHEN** o modelo de chat devolve a solução como uma parte de texto acompanhada de metadados ou assinatura
- **THEN** o campo `answer` contém só a frase da solução e não contém a assinatura nem a estrutura da parte

### Requirement: Modelos Gemini configuráveis
Quando o provedor de LLM configurado é Gemini, o sistema MUST usar o modelo de chat `gemini-3.1-flash-lite` e o modelo de embedding `gemini-embedding-001`, salvo quando a configuração de ambiente informar outros identificadores. O padrão de chat MUST NÃO ser `gemini-2.5-flash-lite`, porque uma chave nova recebe 404 nesse identificador. A chave do provedor MUST permanecer só no ambiente e MUST NÃO entrar em log.

#### Scenario: Padrão usa o chat mais barato ainda chamável
- **WHEN** o provedor é Gemini e a configuração não informa identificadores de modelo
- **THEN** a chamada de chat usa `gemini-3.1-flash-lite` e a construção do índice usa `gemini-embedding-001`

#### Scenario: Ambiente troca o identificador
- **WHEN** a configuração informa outro identificador de chat ou de embedding
- **THEN** o sistema usa esses identificadores no lugar dos padrões
