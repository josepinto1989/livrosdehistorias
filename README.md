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


## Direitos de autor

Copyright © 2026 Miguel Pinto. Todos os direitos reservados.

Este projeto **não é open source**. A disponibilização do código e do website
serve apenas para consulta. Não é concedida autorização para copiar,
redistribuir, republicar, adaptar, vender, licenciar ou explorar o conteúdo.

Consultar o ficheiro [`LICENSE`](LICENSE) para os termos completos.


### Recomendação de publicação

Para preservar melhor estes direitos, recomenda-se manter o **repositório
GitHub privado** e publicar apenas o site resultante. Um repositório público
no GitHub pode ser visualizado e bifurcado ("fork") por outros utilizadores
nos termos da própria plataforma.

Mesmo com um repositório privado, tudo o que é apresentado num website
público pode ser tecnicamente descarregado ou capturado. A licença estabelece
que a mera possibilidade técnica de acesso não constitui autorização para
reutilização.
