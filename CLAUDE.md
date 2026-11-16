<!-- claude-code-progress-bar:inicio -->
# Barra de progresso na status line

A status line deste projeto mostra uma barra de progresso lida de `.claude/progresso.json`.
Você (Claude) é quem mantém esse arquivo. Regras:

## Quando usar
- Pedido com **mais de uma etapa**: no começo (ou ao fechar o planejamento, antes de executar),
  escreva a lista de etapas no arquivo.
- Pedido de **uma etapa só**: não mexe no arquivo.
- Atualize **só nas etapas grandes**, não a cada passo miúdo (não gaste token com isso).

## Formato (dois níveis, ambos opcionais)
```json
{
  "geral":  {"pedido": "objetivo maior da sessão/projeto", "etapas": [{"nome": "...", "feita": false}], "atual": "..."},
  "pedido": {"pedido": "resumo do ÚLTIMO pedido em uma linha", "etapas": [{"nome": "...", "feita": true}], "atual": "nome da etapa em andamento"}
}
```
- `pedido` = o último pedido do usuário (ex.: "atualizar tabela HTML"). É o nível que mais muda.
- `geral` = o objetivo maior quando o usuário está numa sequência de pedidos ligados
  (ex.: "reformar a página de relatórios"). Só preencha quando esse contexto existir;
  o pedido atual costuma ser uma etapa do geral: marque-a feita no `geral` ao terminar o pedido.
- O formato plano `{"pedido": "texto", "etapas": [...], "atual": "..."}` também é aceito
  e equivale a só o bloco `pedido`.

## Ciclo
1. **Planejamento**: defina as etapas e escreva o arquivo já com todas em `feita: false`
   e `atual` = primeira etapa.
2. **Ao concluir uma etapa**: marque `feita: true` e troque `atual` para a próxima.
3. **Se o pedido mudar de rumo**: reescreva a lista inteira.
4. **Novo pedido**: substitua o bloco `pedido`; mantenha o `geral` se ainda valer.
5. **Ao retomar sessão (contexto resumido)**: leia o arquivo antes de continuar e siga dele.
6. **Tudo pronto**: deixe todas as etapas `feita: true` (a barra fica cheia). Não precisa apagar.

Edite o arquivo com uma escrita direta (Write/heredoc), sem ler antes se já souber o conteúdo.
A skill `/progresso` tem exemplos prontos.
<!-- claude-code-progress-bar:fim -->
