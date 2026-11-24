"""Gera o subset acadêmico de tickets alinhado às filas públicas de suporte IT."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import get_settings

LABELS = ("technical", "billing", "account", "other")
PER_CLASS = 300
MAX_CHARS = 1000

TECHNICAL = [
    "O Wi-Fi do roteador {n} cai a cada poucos minutos. Preciso reconfigurar o canal 5 GHz.",
    "O DHCP nao entrega IP para os dispositivos da rede {n}. O LED WAN esta verde.",
    "Nao consigo habilitar o NAT no roteador modelo G40-{n}. A internet fica sem saida.",
    "O firmware do roteador esta desatualizado (build {n}). Como atualizar sem perder o Wi-Fi?",
    "Preciso fazer reset de fabrica no roteador. Qual o procedimento do botao reset?",
    "Sinal Wi-Fi fraco no segundo andar. Canal {n} parece congestionado.",
    "A porta LAN {n} nao negocia 1 Gbps. Cabo esta ok.",
    "O roteador reinicia sozinho depois de atualizar o firmware {n}.",
    "Nao abre a pagina 192.168.1.1. O DHCP pode estar desligado?",
    "Quero configurar QoS para videoconferencia no SSID principal do roteador {n}.",
]

BILLING = [
    "Fui cobrado duas vezes na fatura {n}. Quero estorno do valor extra.",
    "O boleto da mensalidade {n} nao compensou. Preciso da segunda via.",
    "Quero cancelar a cobranca automatica do plano {n}.",
    "O reembolso da fatura {n} ainda nao caiu na conta.",
    "A nota fiscal {n} veio com valor diferente do contrato.",
    "Preciso de comprovante de pagamento da fatura {n}.",
    "Houve reajuste indevido na fatura {n}. Abrir contestacao.",
    "O desconto prometido nao apareceu na fatura {n}.",
    "Quero alterar a forma de pagamento da assinatura {n} para boleto.",
    "A cobranca {n} refere-se a um mes em que o servico estava fora.",
]

ACCOUNT = [
    "Nao consigo redefinir a senha da conta {n}. O e-mail de reset nao chega.",
    "O login da conta {n} esta bloqueado apos tentativas erradas.",
    "Quero ativar 2FA na conta {n}.",
    "Preciso trocar o e-mail cadastrado da conta {n}.",
    "A conta {n} aparece como inativa depois da migracao.",
    "Esqueci o usuario da conta {n}. Como recuperar o acesso?",
    "O perfil da conta {n} mostra nome errado. Quero corrigir.",
    "Nao recebo o codigo SMS para entrar na conta {n}.",
    "Quero encerrar a conta {n} e exportar os dados.",
    "O aplicativo pede senha antiga da conta {n} que eu ja alterei.",
]

OTHER = [
    "Gostaria de elogiar o atendimento do chamado {n}. Foi rapido.",
    "Qual o horario de funcionamento do suporte no feriado {n}?",
    "Sugiro um aplicativo para acompanhar o chamado {n}.",
    "Pergunta geral: voces atendem empresas no endereco regional {n}?",
    "Quero saber se ha programa de indicacao numero {n}.",
    "O site institucional esta fora no banner {n}. Nao e um problema tecnico meu.",
    "Posso agendar uma visita comercial para o plano {n}?",
    "Onde encontro o termo de uso da versao {n}?",
    "Quero participar da pesquisa de satisfacao {n}.",
    "Informativo: mudanca de endereco de correspondencia protocolo {n}.",
]


def _expand(templates: list[str], label: str, count: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    while len(rows) < count:
        idx = len(rows)
        text = templates[idx % len(templates)].format(n=idx + 1)
        rows.append({"text": text[:MAX_CHARS], "label": label})
    return rows


def build_tickets_frame(per_class: int = PER_CLASS) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    rows.extend(_expand(TECHNICAL, "technical", per_class))
    rows.extend(_expand(BILLING, "billing", per_class))
    rows.extend(_expand(ACCOUNT, "account", per_class))
    rows.extend(_expand(OTHER, "other", per_class))
    return pd.DataFrame(rows)


def write_tickets_csv(path: Path | None = None) -> Path:
    settings = get_settings()
    target = path or settings.tickets_csv
    target.parent.mkdir(parents=True, exist_ok=True)
    frame = build_tickets_frame()
    frame.to_csv(target, index=False)
    return target


if __name__ == "__main__":
    output = write_tickets_csv()
    print(f"wrote {output}")
