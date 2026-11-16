---
name: progresso
description: Cria ou atualiza .claude/progresso.json, que alimenta a barra de progresso da status line. Use ao planejar um pedido com mais de uma etapa, ao concluir uma etapa grande, quando o pedido mudar de rumo, ou ao retomar uma sessão para conferir onde parou.
---

# Barra de progresso (progresso.json)

Arquivo: `.claude/progresso.json` na raiz do projeto. A regra completa está no CLAUDE.md.

## Modelo para o último pedido
```json
{
  "pedido": {
    "pedido": "atualizar tabela HTML de preços",
    "etapas": [
      {"nome": "ler tabela atual", "feita": false},
      {"nome": "inserir novas linhas", "feita": false},
      {"nome": "ajustar CSS", "feita": false},
      {"nome": "testar no navegador", "feita": false}
    ],
    "atual": "ler tabela atual"
  }
}
```

## Modelo com objetivo geral + último pedido
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

## Passos
1. **Planejar**: escreva o arquivo com todas as etapas em `feita: false` e `atual` = primeira.
   Se houver objetivo maior em andamento, preencha ou mantenha `geral`.
2. **Concluir etapa**: marque `feita: true`, mova `atual`. Só nas etapas grandes.
3. **Mudou de rumo**: reescreva a lista.
4. **Retomar sessão**: leia o arquivo e continue da etapa `atual`.
5. **Terminou o pedido**: todas `feita: true`; se era etapa do `geral`, marque lá também.

Ver a linha que a status line vai mostrar:
```bash
echo '{}' | python .claude/statusline.py
```

Invocado com argumento (`/progresso <texto>`): trate o texto como o resumo do pedido,
quebre em 3 a 8 etapas grandes e escreva o arquivo.
