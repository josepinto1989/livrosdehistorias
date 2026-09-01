# As Histórias do Guilherme e do Xavier

Site estático para GitHub Pages com uma pequena biblioteca de livros infantis.

## Estrutura

- `index.html` — biblioteca/entrada
- `reader.html` — leitor comum a todas as histórias
- `books/books.json` — catálogo dos livros
- `books/<id>/book.json` — texto e paginação de cada livro
- `books/<id>/images/` — ilustrações
- `assets/cao-joaquim-referencia.png` — referência visual do peluche do Cão Joaquim para futuras ilustrações

## Publicar no GitHub Pages

1. Criar um repositório novo no GitHub.
2. Carregar todo o conteúdo desta pasta para a raiz do repositório.
3. Em **Settings → Pages**, escolher **Deploy from a branch**.
4. Selecionar a branch `main` e a pasta `/ (root)`.
5. Guardar. O GitHub indicará o endereço do site.

## Adicionar um novo livro

1. Criar `books/nome-do-livro/`.
2. Colocar as imagens em `books/nome-do-livro/images/`.
3. Copiar a estrutura de `book.json` do primeiro livro e trocar conteúdo/imagens.
4. Adicionar uma entrada em `books/books.json`.

O leitor é responsivo:
- desktop/tablet horizontal: capa individual + páginas duplas;
- telemóvel vertical: uma página de cada vez;
- setas, teclado, clique nas metades do ecrã e swipe.
