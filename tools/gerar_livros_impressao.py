#!/usr/bin/env python3
"""Gera livretos A5 impostos em folhas A4 a partir dos book.json."""

from __future__ import annotations

import argparse
import html
import json
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

PAGE_WIDTH, PAGE_HEIGHT = A5
SHEET_WIDTH, SHEET_HEIGHT = landscape(A4)

PAPER = colors.HexColor("#fbfaf5")
INK = colors.HexColor("#17354b")
MUTED = colors.HexColor("#66727a")
LINE = colors.HexColor("#d9d6cc")
LIBRARY_BLUE = colors.HexColor("#dceff5")


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

    pdf.setFillColor(colors.white)
    pdf.setStrokeColor(LINE)
    pdf.setLineWidth(0.6)
    pdf.rect(draw_x - 1.5 * mm, draw_y - 1.5 * mm,
             draw_width + 3 * mm, draw_height + 3 * mm, fill=1, stroke=1)
    pdf.drawImage(image, draw_x, draw_y, draw_width, draw_height,
                  preserveAspectRatio=True, mask="auto")


def prepare_print_image(source: Path, cache_dir: Path) -> Path:
    """Converte WebP para JPEG, que o PDF consegue incorporar sem descomprimir."""
    target = cache_dir / f"{source.stem}.jpg"
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
    if page["type"] == "sound":
        sound_style = paragraph_style("sound", font_size * 1.65, bold=True, color=accent,
                                      leading_factor=1.05)
        blocks.append(Paragraph(html.escape(page.get("sound", "")), sound_style))

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
    pdf.setFillColor(LIBRARY_BLUE)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    fit_image(pdf, cover_path, (7 * mm, 7 * mm, PAGE_WIDTH - 14 * mm,
                               PAGE_HEIGHT - 14 * mm))

    accent = colors.HexColor(book.get("themeColor", "#bd563e"))
    panel_x = 14 * mm
    panel_y = PAGE_HEIGHT - 59 * mm
    panel_width = PAGE_WIDTH - 28 * mm
    panel_height = 39 * mm
    pdf.saveState()
    pdf.setFillAlpha(0.9)
    pdf.setFillColor(PAPER)
    pdf.roundRect(panel_x, panel_y, panel_width, panel_height, 2.5 * mm,
                  fill=1, stroke=0)
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
        pdf.roundRect(17 * mm, band_y, credit_width, credit_height + 4 * mm,
                      1.5 * mm, fill=1, stroke=0)
        pdf.restoreState()
        credit_block.drawOn(pdf, 17 * mm, band_y + 2 * mm)


def draw_copyright_page(pdf: canvas.Canvas, book: dict) -> None:
    draw_page_background(pdf)
    accent = colors.HexColor(book.get("themeColor", "#bd563e"))
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
    accent = colors.HexColor(book.get("themeColor", "#bd563e"))
    pdf.setFillColor(LIBRARY_BLUE)
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
            draw_text_page(pdf, page, colors.HexColor(book.get("themeColor", "#bd563e")),
                           number, sequence_page)
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", help="Gerar apenas o livro com este id")
    args = parser.parse_args()

    catalog = load_json(BOOKS_DIR / "books.json")
    book_ids = [args.book] if args.book else [
        book["id"] for book in catalog["books"] if book.get("status") == "available"
    ]
    for book_id in book_ids:
        output = build_book(book_id)
        print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
