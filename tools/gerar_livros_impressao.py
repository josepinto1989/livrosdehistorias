#!/usr/bin/env python3
"""Gera livretos A5 impostos em folhas A4 a partir dos book.json."""

from __future__ import annotations

import argparse
import html
import json
import math
import tempfile
import unicodedata
from pathlib import Path

from PIL import Image
from pypdf import PageObject, PdfReader, PdfWriter, Transformation
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, A5, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader


ROOT = Path(__file__).resolve().parents[1]
BOOKS_DIR = ROOT / "books"
OUTPUT_DIR = ROOT / "impressao"
COLLECTION_TITLE = "As Histórias do Cão Joaquim"
COLLECTION_FILENAME = "as-historias-do-cao-joaquim.pdf"
CONTENTS_PER_PAGE = 7

PAGE_WIDTH, PAGE_HEIGHT = A5
SHEET_WIDTH, SHEET_HEIGHT = landscape(A4)

PAPER = colors.HexColor("#f3eadb")
INK = colors.HexColor("#1d1b19")
MUTED = colors.HexColor("#59605b")
LINE = colors.HexColor("#aaa294")
BRICK = colors.HexColor("#b54733")
PETROL = colors.HexColor("#315f63")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_filename(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return "-".join(ascii_value.lower().replace("&", " e ").split())


def draw_page_background(pdf: canvas.Canvas) -> None:
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)


def draw_page_number(pdf: canvas.Canvas, number: int, sequence_page: int) -> None:
    pdf.setFont("Helvetica", 7)
    pdf.setFillColor(MUTED)
    x = 9 * mm if sequence_page % 2 == 0 else PAGE_WIDTH - 9 * mm
    align_right = sequence_page % 2 == 1
    if align_right:
        pdf.drawRightString(x, 7 * mm, str(number))
    else:
        pdf.drawString(x, 7 * mm, str(number))


def fit_image(pdf: canvas.Canvas, path: Path, box: tuple[float, float, float, float]) -> None:
    x, y, width, height = box
    image = ImageReader(str(path))
    image_width, image_height = image.getSize()
    scale = min(width / image_width, height / image_height)
    draw_width = image_width * scale
    draw_height = image_height * scale
    draw_x = x + (width - draw_width) / 2
    draw_y = y + (height - draw_height) / 2

    pdf.setFillColor(PAPER)
    pdf.setStrokeColor(LINE)
    pdf.setLineWidth(0.6)
    pdf.rect(draw_x - 1.5 * mm, draw_y - 1.5 * mm,
             draw_width + 3 * mm, draw_height + 3 * mm, fill=1, stroke=1)
    pdf.drawImage(image, draw_x, draw_y, draw_width, draw_height,
                  preserveAspectRatio=True, mask="auto")


def prepare_print_image(source: Path, cache_dir: Path) -> Path:
    """Converte WebP para JPEG, que o PDF consegue incorporar sem descomprimir."""
    book_id = source.parent.parent.name
    target = cache_dir / f"{book_id}-{source.stem}.jpg"
    if target.exists():
        return target
    with Image.open(source) as image:
        image.convert("RGB").save(
            target,
            "JPEG",
            quality=90,
            subsampling=0,
            optimize=True,
            progressive=True,
            dpi=(300, 300),
        )
    return target


def paragraph_style(name: str, font_size: float, *, italic: bool = False,
                    bold: bool = False, color=INK, leading_factor: float = 1.45) -> ParagraphStyle:
    font = "Times-Roman"
    if italic:
        font = "Times-Italic"
    elif bold:
        font = "Times-Bold"
    return ParagraphStyle(
        name,
        fontName=font,
        fontSize=font_size,
        leading=font_size * leading_factor,
        textColor=color,
        alignment=TA_CENTER,
        spaceAfter=font_size * 0.72,
        splitLongWords=True,
    )


def build_text_blocks(page: dict, font_size: float, accent) -> list[Paragraph]:
    blocks: list[Paragraph] = []
    body_style = paragraph_style("body", font_size)
    for line in page.get("text", []):
        blocks.append(Paragraph(html.escape(line), body_style))

    if page["type"] == "ending" and page.get("end"):
        end_style = paragraph_style("ending", font_size * 1.35, italic=True, color=accent)
        blocks.append(Paragraph(html.escape(page["end"]), end_style))
    return blocks


def draw_text_page(pdf: canvas.Canvas, page: dict, accent, number: int,
                   sequence_page: int) -> None:
    draw_page_background(pdf)
    margin_x = 14 * mm
    margin_y = 18 * mm
    content_width = PAGE_WIDTH - 2 * margin_x
    content_height = PAGE_HEIGHT - 2 * margin_y

    pdf.setStrokeColor(LINE)
    pdf.setLineWidth(0.55)
    pdf.rect(8 * mm, 9 * mm, PAGE_WIDTH - 16 * mm, PAGE_HEIGHT - 18 * mm,
             fill=0, stroke=1)

    font_size = 12.2
    while True:
        blocks = build_text_blocks(page, font_size, accent)
        sizes = [block.wrap(content_width, content_height) for block in blocks]
        total_height = sum(height for _, height in sizes)
        if total_height <= content_height or font_size <= 9.8:
            break
        font_size -= 0.4

    y = margin_y + (content_height + total_height) / 2
    for block, (_, height) in zip(blocks, sizes):
        y -= height
        block.drawOn(pdf, margin_x, y)

    draw_page_number(pdf, number, sequence_page)


def draw_image_page(pdf: canvas.Canvas, image_path: Path, number: int,
                    sequence_page: int) -> None:
    draw_page_background(pdf)
    fit_image(pdf, image_path, (10 * mm, 24 * mm, PAGE_WIDTH - 20 * mm,
                                PAGE_HEIGHT - 48 * mm))
    draw_page_number(pdf, number, sequence_page)


def draw_cover(pdf: canvas.Canvas, cover_path: Path, book: dict) -> None:
    pdf.setFillColor(PETROL)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    fit_image(pdf, cover_path, (7 * mm, 7 * mm, PAGE_WIDTH - 14 * mm,
                               PAGE_HEIGHT - 14 * mm))

    accent = BRICK
    panel_x = 14 * mm
    panel_y = PAGE_HEIGHT - 59 * mm
    panel_width = PAGE_WIDTH - 28 * mm
    panel_height = 39 * mm
    pdf.saveState()
    pdf.setFillAlpha(0.9)
    pdf.setFillColor(PAPER)
    pdf.rect(panel_x, panel_y, panel_width, panel_height, fill=1, stroke=0)
    pdf.restoreState()

    title = Paragraph(
        html.escape(book.get("coverTitle", book["title"])),
        paragraph_style("cover-title", 18, bold=True, leading_factor=1.05),
    )
    subtitle = Paragraph(
        html.escape(book.get("coverSubtitle", book.get("subtitle", ""))),
        paragraph_style("cover-subtitle", 15.5, bold=True, color=accent,
                        leading_factor=1.05),
    )
    _, title_height = title.wrap(panel_width - 8 * mm, 19 * mm)
    _, subtitle_height = subtitle.wrap(panel_width - 8 * mm, 14 * mm)
    content_height = title_height + subtitle_height + 1.5 * mm
    y = panel_y + (panel_height + content_height) / 2
    y -= title_height
    title.drawOn(pdf, panel_x + 4 * mm, y)
    y -= subtitle_height + 1.5 * mm
    subtitle.drawOn(pdf, panel_x + 4 * mm, y)

    credit = book.get("credit")
    if credit:
        credit_style = paragraph_style("cover-credit", 7.3, bold=True,
                                       color=colors.white, leading_factor=1.05)
        credit_block = Paragraph(html.escape(credit), credit_style)
        credit_width = PAGE_WIDTH - 34 * mm
        _, credit_height = credit_block.wrap(credit_width, 12 * mm)
        band_y = 12 * mm
        pdf.saveState()
        pdf.setFillAlpha(0.72)
        pdf.setFillColor(INK)
        pdf.rect(17 * mm, band_y, credit_width, credit_height + 4 * mm,
                 fill=1, stroke=0)
        pdf.restoreState()
        credit_block.drawOn(pdf, 17 * mm, band_y + 2 * mm)


def draw_copyright_page(pdf: canvas.Canvas, book: dict) -> None:
    draw_page_background(pdf)
    accent = BRICK
    pdf.setFillColor(accent)
    pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 43 * mm, 10 * mm, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Times-Bold", 12)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 46 * mm, "CJ")

    title = Paragraph(html.escape(book["title"]), paragraph_style("inside-title", 19, bold=True))
    _, title_height = title.wrap(PAGE_WIDTH - 32 * mm, 45 * mm)
    title.drawOn(pdf, 16 * mm, PAGE_HEIGHT - 70 * mm - title_height)

    details = [
        book.get("subtitle", ""),
        book.get("credit", ""),
        "Edição para impressão em formato A5.",
        "Texto, personagens e edição © 2026 Miguel Pinto.",
        "Todos os direitos reservados.",
    ]
    style = paragraph_style("copyright", 9.5, color=MUTED, leading_factor=1.35)
    y = 72 * mm
    for detail in reversed([item for item in details if item]):
        block = Paragraph(html.escape(detail), style)
        _, height = block.wrap(PAGE_WIDTH - 34 * mm, 25 * mm)
        block.drawOn(pdf, 17 * mm, y)
        y += height + 1.5 * mm


def draw_blank_page(pdf: canvas.Canvas) -> None:
    draw_page_background(pdf)


def draw_back_cover(pdf: canvas.Canvas, book: dict) -> None:
    accent = BRICK
    pdf.setFillColor(PETROL)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    pdf.setFillColor(accent)
    pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 14 * mm, 18 * mm, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Times-Bold", 20)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 9.5 * mm, "CJ")
    pdf.setFillColor(INK)
    pdf.setFont("Times-Bold", 14)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 17 * mm,
                          "Cão Joaquim & amigos")
    pdf.setFont("Times-Italic", 10)
    pdf.setFillColor(MUTED)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 25 * mm,
                          "Histórias para ler em família")


def draw_light_page_number(pdf: canvas.Canvas, number: int) -> None:
    pdf.setFont("Helvetica", 7)
    pdf.setFillColor(PAPER)
    x = 9 * mm if number % 2 == 0 else PAGE_WIDTH - 9 * mm
    if number % 2:
        pdf.drawRightString(x, 7 * mm, str(number))
    else:
        pdf.drawString(x, 7 * mm, str(number))


def draw_collection_cover(pdf: canvas.Canvas, books: list[tuple[Path, dict]],
                          image_cache: Path) -> None:
    pdf.setFillColor(PETROL)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

    panel_x = 10 * mm
    panel_y = PAGE_HEIGHT - 57 * mm
    panel_width = PAGE_WIDTH - 20 * mm
    panel_height = 47 * mm
    pdf.setFillColor(PAPER)
    pdf.rect(panel_x, panel_y, panel_width, panel_height, fill=1, stroke=0)

    title = Paragraph(
        "As Histórias do<br/><font size=27>Cão Joaquim</font>",
        paragraph_style("collection-cover-title", 18, bold=True, leading_factor=1.08),
    )
    _, title_height = title.wrap(panel_width - 12 * mm, 32 * mm)
    title.drawOn(pdf, panel_x + 6 * mm, panel_y + 11 * mm)

    pdf.setFont("Times-Italic", 8.5)
    pdf.setFillColor(BRICK)
    pdf.drawCentredString(PAGE_WIDTH / 2, panel_y + 6 * mm,
                          "Uma coleção de aventuras para ler em família")

    columns = 3
    rows = max(1, math.ceil(len(books) / columns))
    gap = 3.5 * mm
    grid_x = 10 * mm
    grid_y = 12 * mm
    grid_width = PAGE_WIDTH - 20 * mm
    grid_height = panel_y - grid_y - 6 * mm
    cell_width = (grid_width - gap * (columns - 1)) / columns
    cell_height = (grid_height - gap * (rows - 1)) / rows

    for index, (book_dir, book) in enumerate(books):
        row = index // columns
        column = index % columns
        x = grid_x + column * (cell_width + gap)
        y = grid_y + (rows - 1 - row) * (cell_height + gap)
        cover = prepare_print_image(book_dir / book["pages"][0]["image"], image_cache)
        fit_image(pdf, cover, (x, y, cell_width, cell_height))

    pdf.setFont("Times-Bold", 7.5)
    pdf.setFillColor(PAPER)
    pdf.drawCentredString(PAGE_WIDTH / 2, 6 * mm, "Histórias de Miguel Pinto")


def draw_collection_copyright_page(pdf: canvas.Canvas) -> None:
    draw_page_background(pdf)
    pdf.setFillColor(BRICK)
    pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 43 * mm, 10 * mm, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Times-Bold", 12)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 46 * mm, "CJ")

    title = Paragraph(
        html.escape(COLLECTION_TITLE),
        paragraph_style("collection-inside-title", 21, bold=True),
    )
    _, title_height = title.wrap(PAGE_WIDTH - 32 * mm, 45 * mm)
    title.drawOn(pdf, 16 * mm, PAGE_HEIGHT - 72 * mm - title_height)

    details = [
        "Uma coleção de aventuras para ler em família.",
        "Histórias, personagens e textos de Miguel Pinto.",
        "Edição para impressão em formato A5.",
        "Texto, personagens e edição © 2026 Miguel Pinto.",
        "Todos os direitos reservados.",
    ]
    style = paragraph_style("collection-copyright", 9.5, color=MUTED,
                            leading_factor=1.35)
    y = 64 * mm
    for detail in reversed(details):
        block = Paragraph(html.escape(detail), style)
        _, height = block.wrap(PAGE_WIDTH - 34 * mm, 25 * mm)
        block.drawOn(pdf, 17 * mm, y)
        y += height + 1.5 * mm


def draw_contents_page(pdf: canvas.Canvas, entries: list[dict], page_number: int,
                       part: int, total_parts: int) -> None:
    draw_page_background(pdf)
    pdf.setStrokeColor(LINE)
    pdf.setLineWidth(0.55)
    pdf.rect(8 * mm, 9 * mm, PAGE_WIDTH - 16 * mm, PAGE_HEIGHT - 18 * mm,
             fill=0, stroke=1)

    pdf.setFillColor(BRICK)
    pdf.setFont("Times-Bold", 11)
    pdf.drawString(16 * mm, PAGE_HEIGHT - 25 * mm, "As Histórias do Cão Joaquim")
    pdf.setFillColor(INK)
    pdf.setFont("Times-Bold", 25)
    pdf.drawString(16 * mm, PAGE_HEIGHT - 40 * mm, "Índice")
    if total_parts > 1:
        pdf.setFont("Times-Italic", 8)
        pdf.setFillColor(MUTED)
        pdf.drawRightString(PAGE_WIDTH - 16 * mm, PAGE_HEIGHT - 39 * mm,
                            f"{part + 1} de {total_parts}")

    y = PAGE_HEIGHT - 59 * mm
    for entry in entries:
        number_x = 17 * mm
        title_x = 29 * mm
        page_x = PAGE_WIDTH - 17 * mm

        pdf.setFillColor(BRICK)
        pdf.setFont("Times-Bold", 10)
        pdf.drawString(number_x, y, f"{entry['number']:02d}")

        title = Paragraph(
            html.escape(entry["title"]),
            ParagraphStyle(
                "contents-title",
                fontName="Times-Bold",
                fontSize=10.5,
                leading=12,
                textColor=INK,
                spaceAfter=0,
            ),
        )
        title_width = PAGE_WIDTH - title_x - 31 * mm
        _, title_height = title.wrap(title_width, 14 * mm)
        title.drawOn(pdf, title_x, y - title_height + 2.5 * mm)

        pdf.setDash(1, 2)
        pdf.setStrokeColor(LINE)
        pdf.line(title_x, y - 4.5 * mm, page_x - 7 * mm, y - 4.5 * mm)
        pdf.setDash()
        pdf.setFillColor(INK)
        pdf.setFont("Times-Bold", 10)
        pdf.drawRightString(page_x, y, str(entry["page"]))

        subtitle = entry.get("subtitle", "")
        if subtitle:
            pdf.setFont("Times-Italic", 8)
            pdf.setFillColor(MUTED)
            pdf.drawString(title_x, y - 7 * mm, subtitle)

        pdf.linkAbsolute(
            entry["title"], entry["bookmark"],
            Rect=(number_x, y - 10 * mm, page_x, y + 4 * mm),
            thickness=0,
        )
        y -= 20 * mm

    draw_page_number(pdf, page_number, page_number)


def draw_collection_back_cover(pdf: canvas.Canvas, story_count: int) -> None:
    pdf.setFillColor(PETROL)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    pdf.setFillColor(BRICK)
    pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 19 * mm, 20 * mm, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Times-Bold", 22)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 13.5 * mm, "CJ")
    pdf.setFillColor(PAPER)
    pdf.setFont("Times-Bold", 15)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 15 * mm,
                          "As Histórias do Cão Joaquim")
    pdf.setFont("Times-Italic", 10)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 25 * mm,
                          f"{story_count} aventuras para ler em família")


def create_sequential_pdf(book_dir: Path, book: dict, output_path: Path,
                          image_cache: Path) -> None:
    pdf = canvas.Canvas(str(output_path), pagesize=A5, pageCompression=1)
    pdf.setTitle(book["title"])
    pdf.setAuthor("Miguel Pinto")
    pdf.setSubject("Edição A5 para impressão em livreto")

    cover = book["pages"][0]
    draw_cover(pdf, prepare_print_image(book_dir / cover["image"], image_cache), book)
    pdf.showPage()

    draw_copyright_page(pdf, book)
    pdf.showPage()

    story_pages = book["pages"][1:]
    for number, page in enumerate(story_pages, start=1):
        sequence_page = number + 2
        if page["type"] == "image":
            image_path = prepare_print_image(book_dir / page["image"], image_cache)
            draw_image_page(pdf, image_path, number, sequence_page)
        else:
            draw_text_page(pdf, page, BRICK, number, sequence_page)
        pdf.showPage()

    current_count = 2 + len(story_pages)
    blank_count = (-(current_count + 1)) % 4
    for _ in range(blank_count):
        draw_blank_page(pdf)
        pdf.showPage()

    draw_back_cover(pdf, book)
    pdf.showPage()
    pdf.save()


def impose_booklet(source_path: Path, output_path: Path, title: str) -> None:
    reader = PdfReader(str(source_path))
    page_count = len(reader.pages)
    if page_count % 4:
        raise ValueError(f"O número de páginas tem de ser múltiplo de quatro: {page_count}")

    writer = PdfWriter()
    writer.add_metadata({
        "/Title": f"{title} - livreto A5 em folhas A4",
        "/Author": "Miguel Pinto",
        "/Subject": "Imprimir frente e verso, virar pela margem curta e dobrar ao meio",
    })

    for sheet in range(page_count // 4):
        layouts = (
            (page_count - 2 * sheet, 1 + 2 * sheet),
            (2 + 2 * sheet, page_count - 1 - 2 * sheet),
        )
        for left_number, right_number in layouts:
            sheet_page = PageObject.create_blank_page(width=SHEET_WIDTH, height=SHEET_HEIGHT)
            sheet_page.merge_transformed_page(
                reader.pages[left_number - 1], Transformation().translate(tx=0, ty=0)
            )
            sheet_page.merge_transformed_page(
                reader.pages[right_number - 1], Transformation().translate(tx=PAGE_WIDTH, ty=0)
            )
            writer.add_page(sheet_page)

    with output_path.open("wb") as stream:
        writer.write(stream)


def build_book(book_id: str) -> Path:
    book_dir = BOOKS_DIR / book_id
    book = load_json(book_dir / "book.json")
    output_name = f"{safe_filename(book['title'])}-livreto-a5.pdf"
    output_path = OUTPUT_DIR / output_name
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cao-joaquim-impressao-") as temp_dir:
        temp_path = Path(temp_dir)
        sequential_path = temp_path / f"{book_id}-a5.pdf"
        image_cache = temp_path / "images"
        image_cache.mkdir()
        create_sequential_pdf(book_dir, book, sequential_path, image_cache)
        impose_booklet(sequential_path, output_path, book["title"])

    return output_path


def build_collection() -> Path:
    catalog = load_json(BOOKS_DIR / "books.json")
    books: list[tuple[Path, dict]] = []
    for item in catalog["books"]:
        if item.get("status") != "available":
            continue
        book_dir = BOOKS_DIR / item["id"]
        books.append((book_dir, load_json(book_dir / "book.json")))

    if not books:
        raise ValueError("A coletânea precisa de pelo menos uma história disponível.")

    contents_pages = max(1, math.ceil(len(books) / CONTENTS_PER_PAGE))
    physical_page = 2 + contents_pages
    if physical_page % 2:
        physical_page += 1

    entries: list[dict] = []
    for index, (_, book) in enumerate(books, start=1):
        start_page = physical_page + 1
        entries.append({
            "number": index,
            "title": book["title"],
            "subtitle": book.get("subtitle", ""),
            "page": start_page,
            "bookmark": f"historia-{index}",
        })
        physical_page += len(book["pages"])
        if index < len(books) and physical_page % 2:
            physical_page += 1

    output_path = OUTPUT_DIR / COLLECTION_FILENAME
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cao-joaquim-coletanea-") as temp_dir:
        image_cache = Path(temp_dir) / "images"
        image_cache.mkdir()

        pdf = canvas.Canvas(str(output_path), pagesize=A5, pageCompression=1)
        pdf.setTitle(COLLECTION_TITLE)
        pdf.setAuthor("Miguel Pinto")
        pdf.setSubject("Coletânea A5 para impressão frente e verso e encadernação")

        current_page = 1
        draw_collection_cover(pdf, books, image_cache)
        pdf.showPage()

        current_page += 1
        draw_collection_copyright_page(pdf)
        pdf.showPage()

        for part in range(contents_pages):
            current_page += 1
            if part == 0:
                pdf.bookmarkPage("indice")
                pdf.addOutlineEntry("Índice", "indice", level=0, closed=False)
            start = part * CONTENTS_PER_PAGE
            end = start + CONTENTS_PER_PAGE
            draw_contents_page(pdf, entries[start:end], current_page, part, contents_pages)
            pdf.showPage()

        if current_page % 2:
            current_page += 1
            draw_blank_page(pdf)
            pdf.showPage()

        for index, (book_dir, book) in enumerate(books):
            current_page += 1
            entry = entries[index]
            if current_page != entry["page"]:
                raise ValueError("A paginação do índice não corresponde ao conteúdo.")

            pdf.bookmarkPage(entry["bookmark"])
            pdf.addOutlineEntry(book["title"], entry["bookmark"], level=0,
                                closed=False)
            cover = prepare_print_image(book_dir / book["pages"][0]["image"], image_cache)
            draw_cover(pdf, cover, book)
            draw_light_page_number(pdf, current_page)
            pdf.showPage()

            for page in book["pages"][1:]:
                current_page += 1
                if page["type"] == "image":
                    image_path = prepare_print_image(book_dir / page["image"], image_cache)
                    draw_image_page(pdf, image_path, current_page, current_page)
                else:
                    draw_text_page(pdf, page, BRICK, current_page, current_page)
                pdf.showPage()

            if index < len(books) - 1 and current_page % 2:
                current_page += 1
                draw_blank_page(pdf)
                pdf.showPage()

        if current_page % 2 == 0:
            current_page += 1
            draw_blank_page(pdf)
            pdf.showPage()

        current_page += 1
        draw_collection_back_cover(pdf, len(books))
        pdf.showPage()
        pdf.save()

    reader = PdfReader(str(output_path))
    if len(reader.pages) != current_page or current_page % 2:
        raise ValueError("A coletânea não terminou com um número par de páginas.")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", help="Gerar apenas o livro com este id")
    parser.add_argument("--collection-only", action="store_true",
                        help="Gerar apenas a coletânea completa")
    args = parser.parse_args()

    catalog = load_json(BOOKS_DIR / "books.json")
    if not args.collection_only:
        book_ids = [args.book] if args.book else [
            book["id"] for book in catalog["books"] if book.get("status") == "available"
        ]
        for book_id in book_ids:
            output = build_book(book_id)
            print(output.relative_to(ROOT))

    collection_output = build_collection()
    print(collection_output.relative_to(ROOT))


if __name__ == "__main__":
    main()
