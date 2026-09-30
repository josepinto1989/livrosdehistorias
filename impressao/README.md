# Livros para impressão

Esta pasta contém a edição visual atual de cada história em PDF e a coletânea completa **As Histórias do Cão Joaquim**.

Os PDFs da primeira edição visual estão preservados em `v1/impressao`.

## Como imprimir os livretos individuais

Usa estas opções na janela de impressão:

- papel: **A4**;
- orientação: **horizontal**;
- escala: **tamanho real** ou **100%**;
- impressão: **frente e verso**;
- virar: **margem curta**;
- não escolher novamente a opção `Livreto` ou `Booklet`, porque as páginas já estão impostas na ordem correta.

Depois de imprimir, dobra cada conjunto de folhas ao meio e agrafa na dobra. Cada folha A4 transforma-se em quatro páginas A5.

Para uma gráfica, entrega o PDF tal como está e indica que é um livreto A5 imposto em A4, com impressão frente e verso pela margem curta.

## Como imprimir a coletânea completa

O ficheiro `as-historias-do-cao-joaquim.pdf` contém capa, ficha de autoria, índice e todas as histórias em páginas A5 na ordem normal de leitura.

É adequado para impressão frente e verso e encadernação. Numa gráfica, pede:

- formato final: **A5**;
- impressão: **frente e verso**;
- escala: **tamanho real** ou **100%**;
- encadernação: lombada quadrada, espiral ou outra indicada para o número de páginas.

Não peças para o imprimir como um único livreto dobrado: o volume completo é demasiado espesso para esse tipo de acabamento.

## Ficheiros

- `as-historias-do-cao-joaquim.pdf` — coletânea completa, com índice;
- `o-cao-joaquim-e-o-submarino-arco-iris-livreto-a5.pdf`
- `o-cao-joaquim-e-o-escorpiao-do-deserto-livreto-a5.pdf`
- `o-cao-joaquim-no-centro-da-terra-livreto-a5.pdf`
- `o-cao-joaquim-e-o-salto-de-paraquedas-livreto-a5.pdf`
- `o-cao-joaquim-e-as-formigas-livreto-a5.pdf`
- `o-cao-joaquim-e-os-patins-livreto-a5.pdf`

## Gerar novamente

Na primeira utilização, instala as ferramentas necessárias:

```powershell
python -m pip install -r requirements-print.txt
```

Depois de adicionar ou alterar uma história, executa na pasta principal do projeto:

```powershell
python tools/gerar_livros_impressao.py
```

Este comando gera novamente os livretos individuais e a coletânea completa. Todas as histórias marcadas como `available` em `books/books.json` entram automaticamente no índice e no volume.

Para gerar apenas uma história:

```powershell
python tools/gerar_livros_impressao.py --book cao-joaquim-formigas
```

Mesmo com `--book`, a coletânea é atualizada. Para gerar apenas o volume completo:

```powershell
python tools/gerar_livros_impressao.py --collection-only
```

O gerador lê o catálogo e cada `book.json`, por isso as versões impressas mantêm automaticamente a mesma ordem, texto e imagens do site.
