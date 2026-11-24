# AGENTS.md

Contrato deste repositório. O código vence este arquivo quando divergirem.

`a definir` significa: descubra na hora, no repositório, e siga em frente. Grave o valor aqui só quando o pedido for documentar o projeto.

Se o repositório não contiver aplicação (apenas este framework de regras), altere só as regras, o README, os instaladores e este arquivo.

## Projeto
Framework de regras para os agentes do Cursor (Grok 4.7) e do Antigravity (Gemini). Em uma aplicação, esta seção descreve o que o sistema faz.

## Stack
Fatos tirados de lockfile e manifesto. Versão ausente daqui continua desconhecida.

- Linguagem: a definir
- Framework: a definir
- Banco: a definir
- Testes: a definir

## Comandos
O agente executa os comandos preenchidos antes de declarar uma mudança pronta. Linha `a definir` não é comando.

- Instalar: a definir
- Dev: a definir
- Teste: a definir
- Teste focado: a definir
- Lint: a definir
- Typecheck: a definir
- Build: a definir

## Mapa
Caminhos reais da árvore. `a definir` não é diretório.

- Entrada HTTP: a definir
- Regras de negócio: a definir
- Persistência: a definir
- UI: a definir
- Testes: a definir

## Convenções
Só o que foge do habitual neste código. Exemplo preenchido: "erro de domínio usa Result; handler traduz para HTTP".

- Consulta prévia ao MCP Context7: antes de implementar ou alterar código que utilize bibliotecas, frameworks, SDKs ou APIs da stack, consulte sempre o MCP do Context7 (`resolve-library-id` e `query-docs`) para obter a documentação da versão instalada e aplicar as melhores práticas recomendadas.
- a definir

## OpenSpec
Mudança de comportamento passa pelo OpenSpec. O procedimento é o que `openspec init` instalou neste repositório (skills e commands). As regras deste framework não substituem esse procedimento.

- Config: `openspec/config.yaml`
- Comportamento vigente: `openspec/specs/`
- Change em andamento: `openspec/changes/<id>/`
- Instruções da fase, se o CLI existir: `openspec instructions <artifact|apply|archive> --change <id>`

Pasta ou skill ausente: diga que o OpenSpec não está inicializado. Não invente subcomando, artefato ou template.
