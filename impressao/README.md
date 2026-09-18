# Livros para impressão

Esta pasta contém uma versão em PDF de cada história, preparada como livreto A5 em folhas A4.

## Como imprimir

Usa estas opções na janela de impressão:

- papel: **A4**;
- orientação: **horizontal**;
- escala: **tamanho real** ou **100%**;
- impressão: **frente e verso**;
- virar: **margem curta**;
- não escolher novamente a opção `Livreto` ou `Booklet`, porque as páginas já estão impostas na ordem correta.

Depois de imprimir, dobra cada conjunto de folhas ao meio e agrafa na dobra. Cada folha A4 transforma-se em quatro páginas A5.

Para uma gráfica, entrega o PDF tal como está e indica que é um livreto A5 imposto em A4, com impressão frente e verso pela margem curta.

## Ficheiros

- `o-cao-joaquim-e-o-submarino-arco-iris-livreto-a5.pdf`
- `o-cao-joaquim-e-o-escorpiao-do-deserto-livreto-a5.pdf`
- `o-cao-joaquim-no-centro-da-terra-livreto-a5.pdf`
- `o-cao-joaquim-e-o-salto-de-paraquedas-livreto-a5.pdf`
- `o-cao-joaquim-e-as-formigas-livreto-a5.pdf`

## Gerar novamente

Na primeira utilização, instala as ferramentas necessárias:

```powershell
python -m pip install -r requirements-print.txt
```

Depois de adicionar ou alterar uma história, executa na pasta principal do projeto:

```powershell
python tools/gerar_livros_impressao.py
```

Para gerar apenas uma história:

```powershell
python tools/gerar_livros_impressao.py --book cao-joaquim-formigas
```

O gerador lê o catálogo e cada `book.json`, por isso as versões impressas mantêm automaticamente a mesma ordem, texto e imagens do site.
