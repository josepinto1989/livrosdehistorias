# As Aventuras do Cão Joaquim e amigos

Biblioteca digital de histórias infantis ilustradas, criada por Miguel Pinto para o Guilherme e Xavier.

## O site

- `index.html` apresenta a coleção e os livros disponíveis.
- `reader.html` abre qualquer história num leitor responsivo.
- `books/books.json` contém o catálogo.
- `books/<id>/book.json` contém o texto e a ordem das páginas.
- `books/<id>/images/` contém as ilustrações otimizadas em WebP.

O leitor mostra páginas duplas em ecrãs largos e uma página de cada vez em telemóvel. Aceita botões, teclado, clique nas metades do livro e gesto horizontal.

## Ver localmente

Como o catálogo é carregado por JavaScript, o site deve ser servido por HTTP:

```powershell
python -m http.server 8000
```

Depois, abrir `http://localhost:8000`.

## Adicionar uma aventura

1. Criar `books/nome-do-livro/`.
2. Colocar as ilustrações em `books/nome-do-livro/images/`.
3. Copiar e adaptar a estrutura de `book.json`.
4. Adicionar o livro a `books/books.json`.

Para manter a coleção coerente, as ilustrações devem conservar a identidade visual das personagens, o formato de capa vertical e as cenas interiores horizontais.

## Publicação

O projeto está preparado para GitHub Pages a partir da branch `main` e da pasta raiz. Em **Settings → Pages**, selecionar **Deploy from a branch**, `main` e `/ (root)`.

## Direitos de autor

Copyright © 2026 Miguel Pinto. Todos os direitos reservados.

Este projeto não é open source. A disponibilização do código e do website serve apenas para consulta. Consultar [LICENSE](LICENSE) para os termos completos.
