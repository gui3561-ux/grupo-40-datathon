# Bloqueio do corpus (tarefa 1.1)

Nenhuma fonte passou ao mesmo tempo na licença (CC0, CC-BY, MIT ou equivalente que autorize versionar o texto) e nas quatro categorias do spec. Nenhum CSV sintético novo foi gerado.

Decisão: manter os moldes atuais e declarar isso no README. O roteiro em português (DHCP do roteador e fatura duplicada) continua reproduzível. CSV, joblib e HTML de drift não são trocados.

## Fonte 1 — tickets multilíngues com fila

- URL: https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets
- Licença declarada na API do Hugging Face: `cc-by-nc-4.0`
- Download público, sem chave
- Tem filas como Technical Support e Billing and Payments
- CC-BY-NC restringe uso comercial e não equivale a CC-BY, MIT ou CC0

## Fonte 2 — conjuntos com licença que permite republicar

- https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset
  - Licença: `cdla-sharing-1.0` (permite publicar o texto com atribuição e a mesma licença)
  - Categorias: ACCOUNT, ORDER, REFUND, INVOICE, CONTACT, PAYMENT, FEEDBACK, DELIVERY, SHIPPING, SUBSCRIPTION, CANCEL
  - Não há fila de equipamento de rede, então o cenário de chamado técnico de roteador não tem de onde sair
- https://huggingface.co/datasets/tasksource/it-support-tickets
  - Licença: `cc-by-4.0`
  - Fonte original: Leonardo Santiago Benitez Pereira, DOI https://doi.org/10.5281/zenodo.7648117
  - 2229 tickets reais de TI
  - Rótulos: Active Directory, Computer-Services, EOL, Fileservice, O365, Software, Support general
  - Não há fila de cobrança, então `billing` não chega a 50 linhas sem inventar texto
