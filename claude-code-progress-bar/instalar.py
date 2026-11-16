#!/usr/bin/env python3
"""Instala a barra de progresso num projeto SEM sobrescrever nada que já exista.

Uso (de dentro da raiz do projeto de destino, ou passando o caminho):
    python claude-code-progress-bar/instalar.py            # instala em .
    python claude-code-progress-bar/instalar.py C:/meu/projeto
    python claude-code-progress-bar/instalar.py --desinstalar

O que faz:
- copia statusline.py para .claude/statusline.py (só se não existir)
- copia a skill para .claude/skills/progresso/SKILL.md (só se não existir)
- acrescenta a chave "statusLine" em .claude/settings.json, preservando o resto
  (não mexe se já houver uma statusLine configurada)
- acrescenta o trecho de regras no fim do CLAUDE.md (não repete se já estiver lá)
- adiciona .claude/progresso.json ao .gitignore

--desinstalar remove só o que este instalador colocou (reconhece pelos marcadores).
"""
import json
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
MARCA_INI = "<!-- claude-code-progress-bar:inicio -->"
MARCA_FIM = "<!-- claude-code-progress-bar:fim -->"
IGNORE = ".claude/progresso.json"


def log(msg):
    print("  " + msg)


def copiar(origem, destino):
    if os.path.exists(destino):
        log(f"já existe, mantido: {destino}")
        return
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.copyfile(origem, destino)
    log(f"criado: {destino}")


def instalar_settings(raiz):
    caminho = os.path.join(raiz, ".claude", "settings.json")
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    dados = {}
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            bruto = f.read().strip()
        if bruto:
            try:
                dados = json.loads(bruto)
            except json.JSONDecodeError:
                log(f"ERRO: {caminho} não é JSON válido; statusLine NÃO foi configurada. Edite à mão.")
                return
    if "statusLine" in dados:
        if "statusline.py" in str((dados["statusLine"] or {}).get("command", "")):
            log(f"statusLine da barra já configurada em {caminho}, mantida")
        else:
            log(f"já existe OUTRA statusLine em {caminho}, mantida. Troque à mão se quiser a barra:")
            log('  "statusLine": {"type": "command", "command": "python <raiz>/.claude/statusline.py"}')
        return
    with open(os.path.join(AQUI, "settings-trecho.json"), encoding="utf-8") as f:
        trecho = json.load(f)
    comando = trecho["statusLine"]["command"]
    # Caminho absoluto com barras normais: a documentação não garante o diretório
    # em que o comando da status line roda.
    script_abs = os.path.join(raiz, ".claude", "statusline.py").replace("\\", "/")
    trecho["statusLine"]["command"] = comando.replace(".claude/statusline.py", script_abs)
    dados["statusLine"] = trecho["statusLine"]
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
        f.write("\n")
    log(f"statusLine adicionada em {caminho}")


def instalar_claude_md(raiz):
    caminho = os.path.join(raiz, "CLAUDE.md")
    with open(os.path.join(AQUI, "CLAUDE-trecho.md"), encoding="utf-8") as f:
        trecho = f.read().strip()
    bloco = f"\n\n{MARCA_INI}\n{trecho}\n{MARCA_FIM}\n"
    existente = ""
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            existente = f.read()
        if MARCA_INI in existente:
            log(f"trecho já presente em {caminho}, mantido")
            return
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(existente.rstrip("\n") + bloco if existente.strip() else bloco.lstrip("\n"))
    log(f"trecho acrescentado em {caminho}" if existente else f"criado: {caminho}")


def instalar_gitignore(raiz):
    caminho = os.path.join(raiz, ".gitignore")
    texto = ""
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            texto = f.read()
    if IGNORE in [l.strip() for l in texto.splitlines()]:
        return
    with open(caminho, "a", encoding="utf-8", newline="") as f:
        if texto and not texto.endswith("\n"):
            f.write("\n")
        f.write(IGNORE + "\n")
    log(f"{IGNORE} adicionado ao .gitignore")


def instalar(raiz):
    print(f"Instalando em {raiz}")
    copiar(os.path.join(AQUI, "statusline.py"), os.path.join(raiz, ".claude", "statusline.py"))
    copiar(os.path.join(AQUI, "skills", "progresso", "SKILL.md"),
           os.path.join(raiz, ".claude", "skills", "progresso", "SKILL.md"))
    instalar_settings(raiz)
    instalar_claude_md(raiz)
    instalar_gitignore(raiz)
    print("Pronto. Reinicie a sessão do Claude Code para a status line aparecer.")


def desinstalar(raiz):
    print(f"Desinstalando de {raiz}")
    for rel in (".claude/statusline.py", ".claude/skills/progresso/SKILL.md", ".claude/progresso.json"):
        caminho = os.path.join(raiz, rel)
        if os.path.exists(caminho):
            os.remove(caminho)
            log(f"removido: {rel}")
    pasta_skill = os.path.join(raiz, ".claude", "skills", "progresso")
    if os.path.isdir(pasta_skill) and not os.listdir(pasta_skill):
        os.rmdir(pasta_skill)
    caminho = os.path.join(raiz, ".claude", "settings.json")
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
        cmd = (dados.get("statusLine") or {}).get("command", "")
        if "statusline.py" in cmd:
            del dados["statusLine"]
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
                f.write("\n")
            log("statusLine removida de .claude/settings.json")
    caminho = os.path.join(raiz, "CLAUDE.md")
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            texto = f.read()
        if MARCA_INI in texto and MARCA_FIM in texto:
            ini = texto.index(MARCA_INI)
            fim = texto.index(MARCA_FIM) + len(MARCA_FIM)
            resto = (texto[:ini].rstrip("\n") + "\n" + texto[fim:].lstrip("\n")).strip("\n")
            if resto:
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(resto + "\n")
                log("trecho removido do CLAUDE.md")
            else:
                os.remove(caminho)
                log("CLAUDE.md removido (só tinha o trecho da barra)")
    print("Pronto.")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = list(sys.argv[1:])
    modo_remover = "--desinstalar" in args
    args = [a for a in args if a != "--desinstalar"]
    raiz = os.path.abspath(args[0] if args else os.getcwd())
    if not os.path.isdir(raiz):
        sys.exit(f"Pasta não encontrada: {raiz}")
    (desinstalar if modo_remover else instalar)(raiz)


if __name__ == "__main__":
    main()
