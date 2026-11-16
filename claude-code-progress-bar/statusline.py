#!/usr/bin/env python3
"""Status line do Claude Code com barra de progresso.

Le .claude/progresso.json (ao lado deste script) e imprime UMA linha:

    Geral ███░░░░░ 2/5 · Pedido ████░░░░ 4/8 · etapa atual · resumo do pedido

Se so houver o bloco "pedido" (ou o formato antigo, plano):

    ████░░░░ 4/8 · etapa atual · resumo do pedido

Se o arquivo nao existir, estiver vazio ou invalido, imprime so o modelo e o
diretorio que o Claude Code passa pelo stdin. Sem dependencias externas.
"""
import json
import os
import sys

LARGURA_MAX = 100
LARGURA_BARRA = 8
CHEIO = "█"  # █
VAZIO = "░"  # ░

PASTA_SCRIPT = os.path.dirname(os.path.abspath(__file__))


def localizar_arquivo(entrada):
    """Prefere <project_dir>/.claude/progresso.json; senao usa a pasta do script."""
    ws = entrada.get("workspace") or {}
    for base in (ws.get("project_dir"), ws.get("current_dir"), entrada.get("cwd")):
        if base:
            candidato = os.path.join(base, ".claude", "progresso.json")
            if os.path.isfile(candidato):
                return candidato
    return os.path.join(PASTA_SCRIPT, "progresso.json")


def ler_stdin():
    try:
        bruto = sys.stdin.read()
        return json.loads(bruto) if bruto.strip() else {}
    except Exception:
        return {}


def ler_progresso(arquivo):
    try:
        with open(arquivo, encoding="utf-8") as f:
            bruto = f.read()
        if not bruto.strip():
            return None
        dados = json.loads(bruto)
        return dados if isinstance(dados, dict) and dados else None
    except Exception:
        return None


def normalizar(bloco):
    """Devolve (nome, feitas, total, atual) ou None se o bloco nao for util."""
    if not isinstance(bloco, dict):
        return None
    etapas = bloco.get("etapas") or []
    if not isinstance(etapas, list) or not etapas:
        return None
    total = len(etapas)
    feitas = sum(1 for e in etapas if isinstance(e, dict) and e.get("feita"))
    atual = bloco.get("atual") or ""
    if not atual:
        pendentes = [e.get("nome", "") for e in etapas if isinstance(e, dict) and not e.get("feita")]
        atual = pendentes[0] if pendentes else "concluído"
    nome = bloco.get("pedido") or bloco.get("nome") or ""
    return str(nome).strip(), feitas, total, str(atual).strip()


def barra(feitas, total):
    cheios = round(LARGURA_BARRA * feitas / total) if total else 0
    return CHEIO * cheios + VAZIO * (LARGURA_BARRA - cheios)


def truncar(texto, limite):
    if len(texto) <= limite:
        return texto
    return texto[: max(limite - 1, 0)].rstrip() + "…"


def linha_padrao(entrada):
    modelo = (entrada.get("model") or {}).get("display_name") or ""
    pasta = (entrada.get("workspace") or {}).get("current_dir") or entrada.get("cwd") or os.getcwd()
    partes = [p for p in (modelo, os.path.basename(pasta.rstrip("/\\")) or pasta) if p]
    return truncar(" · ".join(partes), LARGURA_MAX)


def linha_progresso(dados):
    # Formato plano ({"pedido": "texto", "etapas": [...], "atual": "..."}) = so o pedido atual.
    if isinstance(dados.get("etapas"), list):
        pedido = normalizar(dados)
    else:
        pedido = normalizar(dados.get("pedido"))
    geral = normalizar(dados.get("geral"))

    if pedido is None and geral is None:
        return None

    blocos = []
    if geral and pedido:
        blocos.append(f"Geral {barra(geral[1], geral[2])} {geral[1]}/{geral[2]}")
        blocos.append(f"Pedido {barra(pedido[1], pedido[2])} {pedido[1]}/{pedido[2]}")
        principal = pedido
    else:
        principal = pedido or geral
        blocos.append(f"{barra(principal[1], principal[2])} {principal[1]}/{principal[2]}")

    prefixo = " · ".join(blocos)
    texto = " · ".join(t for t in (principal[3], principal[0]) if t)
    sobra = LARGURA_MAX - len(prefixo) - 3
    if texto and sobra > 3:
        return prefixo + " · " + truncar(texto, sobra)
    return truncar(prefixo, LARGURA_MAX)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    entrada = ler_stdin()
    dados = ler_progresso(localizar_arquivo(entrada))
    saida = linha_progresso(dados) if dados else None
    print(saida if saida else linha_padrao(entrada))


if __name__ == "__main__":
    main()
