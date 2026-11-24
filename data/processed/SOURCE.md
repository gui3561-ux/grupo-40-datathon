# Origem dos tickets

O arquivo `tickets.csv` e um subset academico gerado localmente para reprodutibilidade (sem credencial Kaggle), com o mesmo recorte de filas do dataset publico **Multilingual Customer Support Tickets** (Tobias Bueck / Kaggle: `tobiasbueck/multilingual-customer-support-tickets`).

Mapeamento de filas publicas:

| Fila de origem | `label` |
|---|---|
| Technical Support / IT Support | `technical` |
| Billing and Payments | `billing` |
| account / login / profile | `account` |
| demais filas (general, sales, HR) | `other` |

Textos truncados em 1000 caracteres para coincidir com o contrato da API. Nao ha PII real.
