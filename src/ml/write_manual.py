"""Gera o PDF original do manual de roteador (PT-BR)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.font_manager as font_manager
from fpdf import FPDF

from src.config import get_settings

SECTIONS = {
    "Wi-Fi": (
        "O roteador Grupo 40 opera nas bandas 2,4 GHz e 5 GHz. "
        "Para configurar o Wi-Fi, acesse 192.168.1.1 com o usuario admin. "
        "Em Rede sem fio, defina o SSID, a senha WPA2/WPA3 e o canal. "
        "Se o sinal cair, troque o canal 5 GHz para 36, 40 ou 44 e evite interferencia. "
        "O LED Wi-Fi azul indica associacao; apagado indica radio desligado."
    ),
    "DHCP": (
        "O servidor DHCP do roteador entrega enderecos na faixa 192.168.1.100 a 192.168.1.200. "
        "O gateway padrao e 192.168.1.1 e a mascara e 255.255.255.0. "
        "Para reservar IP, associe o MAC do dispositivo a um endereco fixo em LAN > DHCP. "
        "Se o cliente nao recebe IP, confira se o DHCP esta habilitado e se nao ha outro servidor na rede."
    ),
    "NAT": (
        "O NAT (Network Address Translation) traduz o IP privado para o IP publico da WAN. "
        "O NAT deve permanecer ligado para acesso a internet em IPv4. "
        "Para expor um servico interno, crie redirecionamento de porta em NAT > Virtual Server, "
        "informando porta externa, IP interno e porta de destino. "
        "Desligar o NAT impede a saida para a internet em redes residenciais tipicas."
    ),
    "Reset": (
        "O reset de fabrica restaura SSID, senha e regras de NAT. "
        "Com o roteador ligado, pressione o botao Reset por 10 segundos ate os LEDs piscarem. "
        "Aguarde dois minutos. Usuario e senha voltam a admin/admin. "
        "Nao desligue a energia durante o reset. "
        "Apos o reset, reconecte o cabo WAN e reconfigure o Wi-Fi."
    ),
    "Firmware": (
        "Mantenha o firmware atualizado para correcoes de seguranca. "
        "Baixe a imagem oficial no portal do Grupo 40 e envie em Administracao > Firmware. "
        "Nao interrompa a atualizacao. O equipamento reinicia sozinho ao concluir. "
        "Se o roteador reiniciar em loop apos o firmware, use o reset de fabrica e reinstale a versao anterior."
    ),
}


def _font_path() -> Path:
    return Path(font_manager.findfont("DejaVu Sans"))


def write_manual_pdf(path: Path | None = None) -> Path:
    settings = get_settings()
    target = path or settings.manual_path
    target.parent.mkdir(parents=True, exist_ok=True)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.add_font("Manual", fname=str(_font_path()))
    font = "Manual"

    def write_block(content: str, size: int, height: float) -> None:
        pdf.set_x(pdf.l_margin)
        pdf.set_font(font, size=size)
        pdf.multi_cell(pdf.epw, height, content)

    write_block("Manual do Roteador Residencial — Grupo 40", 16, 10)
    pdf.ln(2)
    write_block(
        "Documento original do Datathon. Use apenas este PDF como fonte do Copilot RAG.",
        11,
        7,
    )
    for title, body in SECTIONS.items():
        pdf.ln(3)
        write_block(title, 13, 8)
        write_block(body, 11, 6)
    pdf.output(str(target))
    return target


if __name__ == "__main__":
    output = write_manual_pdf()
    print(f"wrote {output}")
