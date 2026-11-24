# rag-copilot Specification

## Purpose

Responde dúvidas técnicas de suporte apenas com o conteúdo de um manual em PDF, bloqueia prompts inseguros e remove dados pessoais antes de chamar o LLM.

## Requirements

### Requirement: Chat RAG restrito a chamado técnico
A API SHALL expor `POST /chat` com o texto da pergunta. O sistema MUST classificar o texto com o modelo de triagem e, somente se a categoria for técnica, recuperar trechos do manual PDF e gerar a resposta com um LLM. Se a categoria não for técnica, o sistema MUST NÃO chamar o LLM e MUST devolver um roteamento explícito.

#### Scenario: Pergunta técnica usa o manual
- **WHEN** o cliente envia `POST /chat` com uma dúvida coberta pelo manual (por exemplo configuração de um roteador)
- **THEN** a resposta é 200, indica que veio do RAG e contém solução fundamentada nos trechos recuperados do PDF

#### Scenario: Pergunta não técnica não aciona o LLM
- **WHEN** o cliente envia `POST /chat` com um chamado de cobrança ou conta
- **THEN** a API responde 200 com a categoria prevista, informa que o Copilot RAG não se aplica e não envia o texto a nenhum provedor de LLM

#### Scenario: Resposta limitada ao PDF
- **WHEN** a pergunta técnica pede informação que não está no manual
- **THEN** a resposta declara que a informação não foi encontrada no manual em vez de inventar procedimento externo

### Requirement: Guardrails de prompt inseguro
O sistema SHALL recusar, antes de qualquer chamada ao LLM, perguntas que contenham palavras proibidas ou que tentem fazer a IA ignorar o manual / as instruções (jailbreak). A recusa MUST ser explícita e MUST NÃO devolver conteúdo gerado pelo modelo.

#### Scenario: Palavra proibida bloqueia a resposta
- **WHEN** o texto de `POST /chat` contém um termo da lista de palavras proibidas
- **THEN** a API responde 400 com motivo de bloqueio por Guardrail e não consulta o índice nem o LLM

#### Scenario: Tentativa de ignorar o PDF é bloqueada
- **WHEN** o texto tenta instruir o modelo a ignorar o manual, ignorar instruções anteriores ou revelar o prompt de sistema
- **THEN** a API responde 400 com motivo de bloqueio por jailbreak e não consulta o LLM

### Requirement: Proteção de PII antes do LLM
O sistema SHALL detectar e substituir no texto, antes de enviar qualquer conteúdo ao provedor de LLM, identificadores pessoais previsíveis: CPF, endereço de e-mail e número de telefone. O texto original com PII MUST NÃO ser persistido em log de aplicação.

#### Scenario: CPF e e-mail são redigidos
- **WHEN** um chamado técnico contém um CPF e um e-mail válidos em formato brasileiro
- **THEN** o payload enviado ao LLM substitui esses valores por marcadores e a resposta ao cliente não ecoa o CPF nem o e-mail originais nos logs

#### Scenario: Sem chave de LLM
- **WHEN** `POST /chat` é técnico e válido mas a chave do provedor de LLM não está configurada
- **THEN** a API responde 503 explicando a ausência da chave e não vaza segredo
