# claude-code-progress-bar

Barra de progresso na status line do Claude Code. Mostra em que etapa do seu pedido o Claude está,
sem você precisar perguntar.

```
Geral █████░░░ 2/3 · Pedido ████░░░░ 2/4 · ajustar CSS · atualizar tabela HTML de preços
```

- **Geral**: o objetivo maior da sessão (ex.: "reformar a página de relatórios").
- **Pedido**: o último pedido que você fez (ex.: "atualizar tabela HTML de preços").
- Depois: a etapa em andamento e o resumo do pedido.

Os dois níveis são opcionais. Só com o pedido, a linha fica assim:

```
███░░░░░ 1/3 · inserir novas linhas · atualizar tabela HTML de preços
```

Sem nada em andamento, a status line mostra só o modelo e a pasta: `Opus · meu-projeto`.

## Como funciona

1. Quando você faz um pedido com mais de uma etapa, o Claude quebra o pedido em etapas no
   planejamento e grava em `.claude/progresso.json`.
2. Ao concluir cada etapa grande, ele marca como feita e avança o ponteiro.
3. Um script Python lê esse arquivo e desenha a barra na status line.
4. Se o pedido mudar de rumo, a lista é reescrita. Ao retomar uma sessão com contexto resumido,
   o Claude confere o arquivo antes de continuar.

O Claude segue essas regras porque elas entram no `CLAUDE.md` do projeto. Ele só atualiza o
arquivo nas etapas grandes, para não gastar token.

## Instalar em um projeto

O instalador **só acrescenta**. Ele não sobrescreve o `CLAUDE.md`, o `.claude/settings.json`
nem o `.gitignore` que já existem no projeto: cola o trecho dele no fim do `CLAUDE.md` entre
marcadores, adiciona a chave `statusLine` ao `settings.json` preservando permissões e hooks, e
copia o script e a skill só se ainda não existirem. Rodar duas vezes não duplica nada.

Requisitos: Python 3 no PATH e git.

### Jeito mais fácil: pedir para o Claude Code

Abra o Claude Code na raiz do projeto e cole:

```
Instale a barra de progresso deste repositório no projeto atual, sem sobrescrever nada:
https://github.com/SEU-USUARIO/claude-code-progress-bar

Clone o repositório numa pasta temporária (fora do projeto), rode
python <pasta-temporária>/claude-code-progress-bar/instalar.py apontando para a raiz deste
projeto, confira a saída do instalador, apague o clone temporário e me mostre a linha que a
status line vai exibir (echo '{}' | python .claude/statusline.py).
```

Depois reinicie a sessão do Claude Code. A barra aparece a partir da próxima sessão.

### No terminal (um comando)

Na raiz do projeto, no Git Bash, Linux ou macOS:

```bash
git clone --depth 1 https://github.com/SEU-USUARIO/claude-code-progress-bar /tmp/ccpb \
  && python /tmp/ccpb/claude-code-progress-bar/instalar.py . \
  && rm -rf /tmp/ccpb
```

No PowerShell:

```powershell
git clone --depth 1 https://github.com/SEU-USUARIO/claude-code-progress-bar $env:TEMP\ccpb
python $env:TEMP\ccpb\claude-code-progress-bar\instalar.py .
Remove-Item -Recurse -Force $env:TEMP\ccpb
```

### Copiando a pasta

Copie a pasta `claude-code-progress-bar/` para dentro do projeto e rode, na raiz:

```bash
python claude-code-progress-bar/instalar.py
```

Depois pode apagar a pasta copiada. Para instalar à mão, arquivo por arquivo, veja
[claude-code-progress-bar/INSTRUCOES.md](claude-code-progress-bar/INSTRUCOES.md).

## O que o instalador cria no projeto

| Caminho | O que é |
|---|---|
| `.claude/statusline.py` | script que desenha a barra (Python 3, sem dependências) |
| `.claude/settings.json` → chave `statusLine` | aponta a status line para o script |
| `CLAUDE.md` → trecho entre marcadores | as regras que o Claude segue para manter o progresso |
| `.claude/skills/progresso/SKILL.md` | skill `/progresso` com os modelos de JSON |
| `.gitignore` → `.claude/progresso.json` | o arquivo de progresso é estado de sessão, não vai pro git |

## Usar

Não precisa fazer nada. Faça um pedido com várias etapas e a barra aparece:

> **Você:** atualiza a tabela HTML de preços com os valores da planilha nova
>
> **Status line:** `███░░░░░ 1/3 · inserir novas linhas · atualizar tabela HTML de preços`

Para uma sequência de pedidos ligados, diga o objetivo maior uma vez e o Claude mantém o nível
**Geral** enquanto os pedidos avançam:

> **Você:** vamos reformar a página de relatórios: tabela nova, filtro por data e exportar PDF.
> Começa pela tabela.
>
> **Status line:** `Geral ░░░░░░░░ 0/3 · Pedido ██░░░░░░ 1/4 · inserir novas linhas · atualizar tabela HTML`

Comandos úteis:

- `/progresso` mostra os modelos de JSON e as regras.
- `/progresso <texto do pedido>` quebra o pedido em etapas e já grava o arquivo.
- `echo '{}' | python .claude/statusline.py` mostra a linha atual sem abrir o Claude Code.

## Formato do `.claude/progresso.json`

```json
{
  "geral": {
    "pedido": "reformar página de relatórios",
    "etapas": [
      {"nome": "atualizar tabela HTML", "feita": false},
      {"nome": "novo filtro por data", "feita": false},
      {"nome": "exportar PDF", "feita": false}
    ],
    "atual": "atualizar tabela HTML"
  },
  "pedido": {
    "pedido": "atualizar tabela HTML de preços",
    "etapas": [
      {"nome": "ler tabela atual", "feita": true},
      {"nome": "inserir novas linhas", "feita": false},
      {"nome": "ajustar CSS", "feita": false}
    ],
    "atual": "inserir novas linhas"
  }
}
```

O formato plano `{"pedido": "texto", "etapas": [...], "atual": "..."}` também é aceito e
equivale a só o bloco `pedido`. A linha é cortada em 100 caracteres.

## Desligar

```bash
python claude-code-progress-bar/instalar.py --desinstalar
```

Remove só o que o instalador colocou: o script, a skill, a chave `statusLine` e o trecho entre
marcadores do `CLAUDE.md`. O resto do projeto fica como estava.

Para desligar só a barra e manter o resto, apague a chave `statusLine` de `.claude/settings.json`.

## Detalhes

- A status line só carrega quando a sessão inicia. Depois de instalar, reinicie o Claude Code.
- O Claude Code pede confirmação de confiança da pasta na primeira vez, porque a status line roda
  um comando. Sem aceitar, a linha fica em branco.
- No Windows o comando usa caminho absoluto com barras normais (`C:/...`), porque o Claude Code
  não garante em que pasta o comando roda. Se mover o projeto, rode o instalador de novo ou
  ajuste o caminho no `settings.json`.
- O script localiza o `progresso.json` pelo `project_dir` que o Claude Code envia no stdin.
