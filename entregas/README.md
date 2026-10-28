# Pacote completo

O ficheiro `as-historias-do-cao-joaquim-site-e-pdfs.zip` é criado automaticamente pelo gerador de impressão.

Inclui:

- a cópia completa do site, incluindo a V1 preservada;
- todos os PDFs de impressão;
- os documentos de revisão e instruções.

Para recriar apenas o ZIP:

```powershell
python tools/gerar_livros_impressao.py --package-only
```

O ZIP é ignorado pelo Git por ser demasiado grande para o GitHub.

## Pacote A4 para gráfica

O ficheiro `as-historias-do-cao-joaquim-pacote-grafica-a4.zip` contém:

- páginas completas em A4, 300 dpi e sRGB;
- ilustrações e páginas de texto separadas;
- textos completos em Word;
- capa, contracapa e várias opções de lombada;
- todos os PDFs e uma cópia completa do site.

Para o recriar:

```powershell
python tools/gerar_pacote_grafica_a4.py
```
