# Como acrescentar capturas reais do Power BI

A prévia `preview_sintetico.png` é uma visualização calculada em Python, e `referencia_visual_opcao_1.png` é um mockup de design. Nenhuma das duas é uma captura de tela do arquivo PBIP.

Para incluir imagens reais do dashboard na documentação:

1. Abra `powerbi/projetogit.pbip` no Power BI Desktop e confirme os dados.
2. Oculte os painéis de edição (Dados, Visualizações e Filtros), quando possível, e use a exibição da página adequada à tela.
3. Na página **Visão Geral**, use `Win + Shift + S` e capture apenas a área do relatório (sem barra do Windows, informações pessoais, popup ou menus de edição). Salve como `docs/visao_geral_powerbi.png`.
4. Repita para a página **Transportadoras** e salve como `docs/transportadoras_powerbi.png`.
5. Adicione ao README, acima da prévia ilustrativa, o seguinte trecho:

```markdown
## Dashboard no Power BI Desktop

![Visão Geral no Power BI](docs/visao_geral_powerbi.png)

![Transportadoras no Power BI](docs/transportadoras_powerbi.png)
```

**Importante:** antes de fotografar, selecione os filtros padrão (todas as transportadoras e todos os CDs), verifique a data de corte e confira os totais dos cartões. Isso evita publicar um print com filtros acidentais ou inconsistência na leitura.
