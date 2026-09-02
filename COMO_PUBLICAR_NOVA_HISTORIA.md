# Como publicar uma nova história

Este guia explica como acrescentar uma aventura à biblioteca e publicá-la no site.

## 1. Preparar a história

Antes de mexer nos ficheiros, reúne:

- o título e o subtítulo;
- o texto dividido em pequenas páginas;
- uma capa vertical em formato WebP;
- uma imagem horizontal em formato WebP para cada página de texto.

Cada imagem deve mostrar apenas aquilo que o texto imediatamente anterior já contou. No telemóvel aparece primeiro o texto e depois a imagem; no computador os dois aparecem lado a lado.

## 2. Criar a pasta do livro

Dentro de `books`, copia a pasta de uma história existente e dá-lhe um identificador simples, sem espaços nem acentos. Por exemplo:

```text
books/cao-joaquim-floresta/
├── book.json
└── images/
    ├── cover.webp
    ├── 01-primeira-cena.webp
    ├── 02-segunda-cena.webp
    └── ...
```

Não alteres as pastas das histórias que já estão publicadas.

## 3. Preencher o `book.json`

Abre o `book.json` copiado e altera:

- `id`: deve ser igual ao nome da pasta;
- `title`, `subtitle`, `coverTitle` e `coverSubtitle`;
- `themeColor`, se quiseres outra cor de destaque;
- todas as páginas, textos, nomes de imagens e descrições `alt`.

A ordem recomendada é sempre:

```text
capa → texto → imagem → texto → imagem → ... → final → imagem final
```

Usa páginas do tipo `text` para a narração, `sound` apenas para sons ou gritos que façam parte da história e `ending` para o final. Evita títulos em cada página: a narração deve continuar naturalmente.

Confirma que cada vírgula, aspas e parêntesis do JSON está correto. Um erro no JSON impede o livro de abrir.

## 4. Adicionar o livro à biblioteca

Abre `books/books.json` e acrescenta uma entrada dentro de `books`:

```json
{
  "id": "cao-joaquim-floresta",
  "title": "O Cão Joaquim na Floresta",
  "subtitle": "Uma aventura entre árvores",
  "cover": "books/cao-joaquim-floresta/images/cover.webp",
  "status": "available",
  "href": "reader.html?book=cao-joaquim-floresta"
}
```

Coloca uma vírgula entre esta entrada e a anterior, mas não depois da última entrada.

## 5. Testar antes de publicar

Na pasta principal do projeto, abre o PowerShell e executa:

```powershell
python -m http.server 8000
```

Depois abre `http://localhost:8000` no navegador e confirma:

- a nova capa aparece na página inicial;
- o livro abre sem erros;
- todas as imagens carregam;
- no telemóvel, o texto aparece antes da respetiva imagem;
- no computador, cada texto está ao lado da imagem correta;
- a última abertura tem apenas o final e uma imagem;
- nenhum texto fica cortado.

Para terminar o servidor, volta ao PowerShell e carrega em `Ctrl+C`.

## 6. Evitar versões antigas em cache

Antes de publicar, aumenta o número da versão em dois locais:

1. Em `assets/js/reader.js`, altera `assetVersion`.
2. Em `reader.html`, altera o mesmo número em `reader.js?v=...`.

Se alterares a página inicial ou `library.js`, aumenta também o número de `library.js?v=...` no fim de `index.html`.

Exemplo: muda `20260902-5` para `20260902-6` em todos os locais correspondentes.

## 7. Publicar no GitHub

Depois dos testes, executa na pasta do projeto:

```powershell
git add .
git commit -m "Adicionar nova história do Cão Joaquim"
git push origin main
```

O GitHub Pages atualiza automaticamente o site. A publicação pode demorar alguns minutos. No fim, confirma a biblioteca em:

https://josepinto1989.github.io/livrosdehistorias/

## Lista final

- [ ] A pasta e o `id` têm exatamente o mesmo nome.
- [ ] A capa é vertical e as cenas são horizontais.
- [ ] Os nomes das imagens no JSON correspondem aos ficheiros.
- [ ] Cada texto aparece antes da imagem que o ilustra.
- [ ] `books/books.json` contém a nova história.
- [ ] As versões de cache foram atualizadas.
- [ ] O livro foi testado no computador e no telemóvel.
- [ ] As alterações foram enviadas para a branch `main`.
