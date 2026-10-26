# Publicar o Last-Mile Analytics no GitHub

Nome sugerido para o repositório: `last-mile-analytics`.

## Pelo navegador

1. Acesse GitHub → **New repository**.
2. Informe o nome `last-mile-analytics` e marque **Public** (se for um projeto aberto de portfólio).
3. **Não** selecione “Add a README” nem “Choose a license” no site: esses arquivos já estão neste pacote.
4. Crie o repositório. Em seguida, escolha **uploading an existing file**.
5. Adicione o **conteúdo descompactado desta pasta** (README.md, `powerbi/`, `src/`, `data/`, etc.), preservando as subpastas. Não envie o ZIP como um único arquivo.
6. Faça o commit e confira se `README.md` aparece na página inicial e se o projeto PBIP está em `powerbi/`.

Se o navegador não conseguir carregar toda a estrutura de pastas, prefira o Git pela linha de comando.

## Pelo Git no computador

Abra um terminal **dentro da pasta descompactada**, que contém `README.md` e `powerbi/`. Execute:

```bash
git init
git add .
git commit -m "Publica projeto Last-Mile Analytics"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/last-mile-analytics.git
git push -u origin main
```

Substitua `SEU_USUARIO` pelo seu usuário real e crie o repositório vazio antes do `push`. Se o Git pedir autenticação, utilize o fluxo de autenticação do GitHub; não salve senhas nem tokens em arquivos do projeto.

## Conferência final

- `README.md`, `LICENSE` e `CHANGELOG.md` aparecem na raiz.
- `powerbi/projetogit.pbip` e as duas pastas `.Report` e `.SemanticModel` estão presentes.
- Nenhuma pasta `.pbi/` ou arquivo `cache.abf`, `localSettings.json` ou credencial foi publicado.
- Os testes do GitHub Actions passaram.
- As imagens incluídas estão identificadas como **prévias ilustrativas**, até você inserir capturas reais seguindo `docs/CAPTURAS.md`.
