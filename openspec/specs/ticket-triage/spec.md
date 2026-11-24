# ticket-triage Specification

## Purpose

Classifica o assunto de um chamado de suporte com modelo clássico, registra Accuracy e F1 no MLflow local e serve a inferência por HTTP para a triagem do Copilot.

## Requirements

### Requirement: Treino de classificador clássico de tickets
O sistema SHALL treinar um modelo clássico de classificação de texto sobre um dataset público de chamados de suporte que inclua ao menos a categoria técnica, persistir o artefato treinado e avaliar Accuracy e F1 macro em holdout estratificado.

#### Scenario: Treino produz artefato e métricas
- **WHEN** o script de treino é executado sobre o dataset de tickets versionado no repositório
- **THEN** o sistema grava um artefato de modelo carregável e reporta Accuracy e F1 macro do conjunto de teste

#### Scenario: Categorias incluem fila técnica
- **WHEN** o modelo treinado recebe um chamado cujo assunto é um problema técnico de equipamento de rede
- **THEN** a categoria prevista é a fila técnica usada para acionar o Copilot RAG

### Requirement: Registro de experimentos no MLflow
O treino SHALL registrar em um servidor MLflow local o nome do experimento, os parâmetros relevantes, a Accuracy e o F1 macro, de modo que as runs sejam visíveis na UI do MLflow.

#### Scenario: Métricas aparecem na UI local
- **WHEN** o treino conclui com MLflow apontando para o tracking URI local
- **THEN** existe ao menos uma run no experimento do Copilot contendo as métricas `accuracy` e `f1_macro`

### Requirement: Inferência HTTP da categoria
A API SHALL expor `POST /predict` recebendo o texto do chamado e devolvendo a categoria prevista, a confiança e o identificador do modelo. A API SHALL expor `GET /health` indicando se o artefato de modelo está carregado.

#### Scenario: Predição bem-sucedida
- **WHEN** um cliente envia `POST /predict` com um texto de chamado válido
- **THEN** a resposta é 200 com categoria, confiança numérica e identificador do modelo

#### Scenario: Serviço degradado sem modelo
- **WHEN** a API inicia sem o artefato de modelo
- **THEN** `GET /health` reporta que o modelo não está carregado e `POST /predict` responde 503
