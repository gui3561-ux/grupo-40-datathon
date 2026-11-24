## Purpose

Empacota a API de forma reproduzível e documenta, no README, a escala em nuvem, a proteção LGPD antes do LLM e o roteiro do vídeo STAR da banca.

## ADDED Requirements

### Requirement: Container da API
O repositório SHALL conter um `Dockerfile` e um `requirements.txt` suficientes para construir a imagem e subir a API com o modelo e o manual embutidos. A imagem MUST NÃO exigir GPU. Segredos de LLM MUST entrar só por variável de ambiente.

#### Scenario: Build e run local
- **WHEN** um avaliador executa o build do `Dockerfile` e sobe o container mapeando a porta da API
- **THEN** `GET /health` responde com sucesso e `/docs` exibe os endpoints `/predict` e `/chat`

#### Scenario: Dependências declaradas
- **WHEN** o avaliador inspeciona `requirements.txt`
- **THEN** o arquivo lista as dependências de runtime da API, do modelo, do RAG e do Evidently usadas no projeto

### Requirement: Arquitetura teórica de nuvem no README
O `README.md` SHALL descrever como o mesmo container seria publicado em GCP Cloud Run (serviço HTTPS, autoscaling, Secret Manager para a chave do LLM), com diagrama ou texto equivalente claro para a banca. O README MUST deixar explícito que o deploy real não faz parte da entrega.

#### Scenario: Banca encontra o desenho de nuvem
- **WHEN** o avaliador abre o `README.md` na seção de arquitetura de nuvem
- **THEN** identifica o fluxo Container Registry → Cloud Run → Secret Manager e a justificativa de escala do Copilot

### Requirement: Privacy by Design e LGPD
O `README.md` SHALL documentar Privacy by Design: base legal aplicável a chamados de suporte, quais PII o sistema trata, a redação obrigatória antes do LLM, a proibição de versionar chaves e textos com PII, e a política de retenção. A proteção MUST estar alinhada ao comportamento da API (redação antes do provedor externo).

#### Scenario: Banca encontra a governança LGPD
- **WHEN** o avaliador lê a seção de governança do `README.md`
- **THEN** encontra a redação de CPF/e-mail/telefone antes do LLM, a ausência de segredos no repositório e a base legal do tratamento

### Requirement: Roteiro STAR do vídeo
O `README.md` SHALL incluir um roteiro de até 5 minutos no formato STAR cobrindo: API no Swagger ou equivalente, painel MLflow com Accuracy e F1, e explicação do relatório Evidently de drift.

#### Scenario: Roteiro cobre as três evidências da banca
- **WHEN** o grupo grava o vídeo seguindo o roteiro do README
- **THEN** as três demonstrações pedidas no edital (API rodando, MLflow, drift HTML) estão listadas em ordem com tempo sugerido
