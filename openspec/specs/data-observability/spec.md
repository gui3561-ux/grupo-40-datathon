# data-observability Specification

## Purpose

Garante contrato de entrada dos chamados na API e produz evidência visual de Data Drift no texto do classificador clássico, como exigido pelas Fases 3 e 4 do Datathon.

## Requirements

### Requirement: Validação estrutural do texto do chamado
A API SHALL rejeitar payload cujo campo de texto esteja ausente, seja vazio ou só espaços, ou ultrapasse 1000 caracteres. A rejeição MUST ocorrer antes da inferência, do RAG e dos Guardrails de conteúdo.

#### Scenario: Texto vazio é rejeitado
- **WHEN** o cliente envia `POST /predict` ou `POST /chat` com texto vazio ou apenas espaços
- **THEN** a API responde 422 e não executa o modelo

#### Scenario: Texto acima de 1000 caracteres é rejeitado
- **WHEN** o cliente envia um texto com 1001 caracteres ou mais
- **THEN** a API responde 422 e não executa o modelo nem o RAG

#### Scenario: Texto no limite é aceito
- **WHEN** o cliente envia um texto com exatamente 1000 caracteres não vazios
- **THEN** a validação passa e o fluxo segue para triagem ou Guardrails

### Requirement: Simulação de degradação e relatório Evidently
O repositório SHALL incluir um script que gera um lote de produção degradado a partir dos tickets de referência (deslocamento de comprimento, ruído lexical e mudança de mix de classes) e produz `reports/drift_report.html` com Evidently comparando referência versus produção.

#### Scenario: Relatório HTML é gerado
- **WHEN** o script de drift é executado
- **THEN** o arquivo `reports/drift_report.html` existe e é um relatório Evidently navegável

#### Scenario: Drift aparece visualmente
- **WHEN** um avaliador abre o HTML gerado após a simulação padrão
- **THEN** o relatório indica Data Drift detectado nos descritores de texto ou na distribuição de classes, de forma visível sem inspecionar o código

#### Scenario: Referência estável não é o lote degradado
- **WHEN** o script compara o conjunto de referência consigo mesmo
- **THEN** o relatório não marca o mesmo nível de drift da simulação degradada
