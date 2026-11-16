# Barra de progresso na status line do Claude Code

Mostra na status line em que etapa o Claude está no seu pedido:

```
Geral ███░░░░░ 1/3 · Pedido ████░░░░ 2/4 · ajustar CSS · atualizar tabela HTML de preços
```

Dois níveis, os dois opcionais: **Geral** é o objetivo maior da sessão (ex.: reformar a página
de relatórios) e **Pedido** é o último pedido que você fez (ex.: atualizar a tabela HTML).
O Claude cria as etapas no planejamento e marca cada uma ao concluir.

## O que tem nesta pasta

| Arquivo | Para quê |
|---|---|
| `instalar.py` | instala no projeto sem sobrescrever nada que já exista |
| `statusline.py` | o script da status line (Python 3, sem dependências) |
| `skills/progresso/SKILL.md` | skill `/progresso` com os modelos de JSON |
| `CLAUDE-trecho.md` | as regras que o Claude segue; vai para o fim do CLAUDE.md |
| `settings-trecho.json` | a chave `statusLine` que vai para `.claude/settings.json` |

## Instalar (jeito fácil)

Copie esta pasta para dentro do projeto e rode, na raiz do projeto:

```bash
python claude-code-progress-bar/instalar.py
```

Ou aponte para outra pasta: `python claude-code-progress-bar/instalar.py C:/meu/projeto`.

O instalador:
- copia `statusline.py` e a skill para `.claude/` **só se ainda não existirem**;
- acrescenta `statusLine` ao `.claude/settings.json` preservando o que já tem
  (se já houver uma status line configurada, não mexe e avisa);
- acrescenta o trecho de regras ao **fim** do `CLAUDE.md` entre marcadores,
  sem tocar no que já estava escrito;
- adiciona `.claude/progresso.json` ao `.gitignore`.

Depois reinicie a sessão do Claude Code. A barra só aparece depois de aceitar a
confiança da pasta, porque a status line roda um comando.

Depois de instalar pode apagar a pasta `claude-code-progress-bar/` do projeto se quiser.

## Instalar à mão

1. Copie `statusline.py` para `.claude/statusline.py`.
2. Copie `skills/progresso/` para `.claude/skills/progresso/`.
3. Cole o conteúdo de `CLAUDE-trecho.md` no fim do seu `CLAUDE.md`.
4. Em `.claude/settings.json`, adicione a chave de `settings-trecho.json`.
   Use caminho absoluto com barras normais no `command`, por exemplo
   `python C:/meu/projeto/.claude/statusline.py`, porque o Claude Code não garante
   em que pasta o comando roda.

## Formato do `.claude/progresso.json`

```json
{
  "geral":  {"pedido": "reformar página de relatórios", "etapas": [{"nome": "atualizar tabela HTML", "feita": false}], "atual": "atualizar tabela HTML"},
  "pedido": {"pedido": "atualizar tabela HTML de preços", "etapas": [{"nome": "ler tabela atual", "feita": true}, {"nome": "inserir novas linhas", "feita": false}], "atual": "inserir novas linhas"}
}
```

Só com `pedido` a linha fica `███░░░░░ 1/3 · etapa atual · resumo do pedido`.
Sem arquivo, a status line mostra só modelo e pasta. A linha é cortada em 100 caracteres.

Para ver a linha sem abrir o Claude Code:

```bash
echo '{}' | python .claude/statusline.py
```

## Desligar

```bash
python claude-code-progress-bar/instalar.py --desinstalar
```

Remove só o que o instalador colocou: o script, a skill, a chave `statusLine`
e o trecho entre marcadores do CLAUDE.md. Ou, à mão, apague a chave `statusLine`
do `.claude/settings.json` (a regra no CLAUDE.md pode ficar, não atrapalha).
