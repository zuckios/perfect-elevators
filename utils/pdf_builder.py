#!/usr/bin/env python3
"""
Генератор коммерческого предложения в PDF.
Usage: python main.py [--logo LOGO_PATH] [--font FONT_TTF] [--output OUT.pdf]
"""
import argparse
import math
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ---------------------------------------------------------------------------
# Константы оформления
# ---------------------------------------------------------------------------
class Layout:
    PAGE_SIZE = A4
    MARGIN = 11 * mm
    GREEN = colors.HexColor("#466b2f")
    LINE_COLOR = GREEN

    LOGO_WIDTH = 110
    TABLE_FONT_SIZE = 9.0
    NORMAL_FONT_SIZE = 9.5
    SMALL_FONT_SIZE = 8.5
    TABLE_PADDING = 4
    SIGN_LINE_THICKNESS = 0.9

    DEFAULT_LOGO = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.jpg")
    DEFAULT_OUTPUT = "final_proposal.pdf"
    DEFAULT_FONT = "/Library/Fonts/Arial Unicode.ttf"
    FONT_NAME = "MainFont"


# Обязанности сторон (описание, Заказчик, Подрядчик)
RESPONSIBILITIES = [
    ("1. Подготовка технических отверстий в шахте", "+", "-"),
    ("2. Предварительная провеска шахты.", "-", "+"),
    ("3. Строительные леса.", "-", "+"),
    ("4. Монтаж лифтовых оборудований", "-", "+"),
    ("5. Пуско-наладочные работы", "-", "+"),
    ("6. Расходные материалы", "-", "+"),
    ("7. Помещение для проживания монтажной бригады", "-", "+"),
    ("8. Питание монтажной бригады", "-", "+"),
    ("9. Предоставления тяжелой техники для выгрузки и подъема/монтажа оборудования", "+", "-"),
    ("10. Предоставления тяжелой техники для выгрузки металлопроката", "-", "-"),
    ("11. Регистрация в гос. комитете промышленной безопасности РУз.", "-", "+"),
]


# ---------------------------------------------------------------------------
# Вспомогательные компоненты
# ---------------------------------------------------------------------------
class SignatureLine(Flowable):
    """Линия для подписи."""

    def __init__(self, width, thickness=Layout.SIGN_LINE_THICKNESS, length_ratio=0.6):
        super().__init__()
        self.width = width
        self.thickness = thickness
        self.length_ratio = length_ratio
        self.height = thickness + 6

    def draw(self):
        self.canv.setStrokeColor(Layout.LINE_COLOR)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 3, self.width * self.length_ratio, 3)


def _format_money(value):
    try:
        return f"{int(value):,}".replace(",", " ")
    except (ValueError, TypeError):
        return str(value)


def _register_font(path: str):
    """Регистрирует шрифт из файла."""
    try:
        name = os.path.splitext(os.path.basename(path))[0].replace(" ", "_")
        pdfmetrics.registerFont(TTFont(name, path))
        return name
    except Exception as e:
        print(f"[font] Ошибка регистрации: {e}")
        return None


def _auto_find_font() -> str:
    """Ищет подходящий шрифт для кириллицы."""
    prefer = ["NotoSans", "DejaVuSans", "Arial", "PTSans", "Roboto", "FreeSans"]
    dirs = [
        "/Library/Fonts",
        os.path.expanduser("~/Library/Fonts"),
        "/System/Library/Fonts",
        "/usr/share/fonts",
        "/usr/local/share/fonts",
    ]
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            low = fn.lower()
            if low.endswith((".ttf", ".otf")):
                for p in prefer:
                    if p.lower() in low:
                        name = _register_font(os.path.join(d, fn))
                        if name:
                            return name
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.lower().endswith((".ttf", ".otf")):
                name = _register_font(os.path.join(d, fn))
                if name:
                    return name
    return "Helvetica"


# ---------------------------------------------------------------------------
# Основной класс генератора
# ---------------------------------------------------------------------------
class ProposalPDFGenerator:
    """Генератор PDF коммерческого предложения."""

    def __init__(self, font_path=None):
        self.font_name = self._setup_font(font_path)
        self.styles = self._create_styles()
        self.usable_width = Layout.PAGE_SIZE[0] - Layout.MARGIN * 2

    def _setup_font(self, font_path) -> str:
        if font_path and os.path.isfile(font_path):
            name = _register_font(font_path)
            if name:
                return name
        if os.path.isfile(Layout.DEFAULT_FONT):
            pdfmetrics.registerFont(TTFont(Layout.FONT_NAME, Layout.DEFAULT_FONT))
            return Layout.FONT_NAME
        return _auto_find_font()

    def _create_styles(self):
        base = getSampleStyleSheet()
        font = self.font_name
        base.add(ParagraphStyle("Body", fontName=font, fontSize=9.5, leading=11.5))
        base.add(ParagraphStyle("Small", fontName=font, fontSize=8.5, leading=10))
        base.add(ParagraphStyle("Table", fontName=font, fontSize=9, leading=10))
        base.add(ParagraphStyle("TableSmall", fontName=font, fontSize=8, leading=9.5))
        return base

    def _p(self, text: str, style_name: str = "Table", **overrides) -> Paragraph:
        """Создаёт Paragraph с переопределением стиля."""
        style = self.styles.get(style_name, self.styles["Table"])
        base = {"fontName": style.fontName, "fontSize": style.fontSize, "leading": style.leading}
        merged = {**base, **overrides}
        ps = ParagraphStyle("inline", **merged)
        return Paragraph(text, ps)

    # -----------------------------------------------------------------------
    # Секции документа
    # -----------------------------------------------------------------------
    def _build_header(self, story: list, data: dict, logo_path: str):
        w = self.usable_width
        logo_w = Layout.LOGO_WIDTH
        col2 = col3 = (w - logo_w) / 2

        if logo_path and os.path.isfile(logo_path):
            logo = Image(logo_path, width=logo_w, height=logo_w)
        else:
            logo = self._p("")
        city = self._p("г. Ташкент, Яккасарайский район, ул. Богибустон, дом 184", "Body")
        payments = self._p(
            "Р/с: 2020 8000 0009 3358 6001<br/>"
            "ЧАБ «TRASTBANK» филиал «Ташкент»<br/>"
            "р/с: 2020 8000 8009 3358 6002<br/>"
            "АКБ «КАПИТАЛБАНК»<br/>"
            "МФО: 00850 ИНН: 305 811 822 ОКЭД: 43299",
            "Small",
        )
        tbl = Table([[logo, city, payments]], colWidths=[logo_w, col2, col3])
        tbl.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "LEFT"),
            ("ALIGN", (2, 0), (2, 0), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.extend([tbl, Spacer(1, 6)])

    def _build_proposal_block(self, story: list, project: str, subtitle: str, items: list):
        """Блок «Коммерческое Предложение» + таблица оборудования."""
        w = self.usable_width

        # Строка: Коммерческое Предложение | Проект
        row = [
            self._p("<b>Коммерческое Предложение</b>", textColor=colors.white, fontSize=11),
            self._p(f"Проект: {project}"),
        ]
        tbl = Table([row], colWidths=[w * 0.35, w * 0.65])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), Layout.GREEN),
            ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), self.font_name),
            ("FONTSIZE", (0, 0), (-1, -1), Layout.TABLE_FONT_SIZE),
            ("LEFTPADDING", (0, 0), (-1, -1), Layout.TABLE_PADDING),
            ("RIGHTPADDING", (0, 0), (-1, -1), Layout.TABLE_PADDING),
            ("TOPPADDING", (0, 0), (-1, -1), Layout.TABLE_PADDING - 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), Layout.TABLE_PADDING - 1),
            ("GRID", (0, 0), (-1, -1), 0.7, colors.black),
        ]))
        story.extend([tbl, Spacer(1, 12)])

        if subtitle:
            story.extend([
                self._p(subtitle, textColor=colors.black, alignment=0),
                Spacer(1, 6),
            ])

        # Таблица оборудования
        headers = ["Оборудования/Здания", "Размер/Груз-п", "Этажность", "Кол-во", "Цена за ед. (без НДС)", "Всего"]
        col_w = [w * 0.28, w * 0.15, w * 0.10, w * 0.08, w * 0.20, w * 0.19]
        rows = [headers]
        for it in items:
            rows.append([
                self._p(it.get("name", "")),
                self._p(it.get("size", "")),
                self._p(str(it.get("floors", ""))),
                self._p(str(it.get("qty", ""))),
                self._p(_format_money(it.get("unit_price", ""))),
                self._p(_format_money(it.get("total", ""))),
            ])
        tbl = Table(rows, colWidths=col_w, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.7, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), Layout.GREEN),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), self.font_name),
            ("FONTSIZE", (0, 0), (-1, -1), Layout.TABLE_FONT_SIZE),
            ("LEFTPADDING", (0, 0), (-1, -1), Layout.TABLE_PADDING),
            ("RIGHTPADDING", (0, 0), (-1, -1), Layout.TABLE_PADDING),
            ("TOPPADDING", (0, 0), (-1, -1), Layout.TABLE_PADDING - 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), Layout.TABLE_PADDING - 1),
            ("ALIGN", (2, 1), (3, -1), "CENTER"),
            ("ALIGN", (4, 1), (5, -1), "RIGHT"),
        ]))
        story.extend([tbl, Spacer(1, 8)])

    def _build_totals(self, story: list, totals: dict):
        w = self.usable_width
        left_w, right_w = w * 0.66, w * 0.34
        total_style = ParagraphStyle("total_row", fontName=self.font_name, fontSize=Layout.NORMAL_FONT_SIZE, textColor=colors.white)

        rows = [
            [self._p("<b>Общая Сумма без НДС:</b>"), self._p(_format_money(totals.get("without_vat", 0)))],
            [self._p(f"<b>НДС {totals.get('vat_percent', 12)}%:</b>"), self._p(_format_money(totals.get("vat_amount", 0)))],
            [Paragraph("<b>Итого с НДС:</b>", total_style), Paragraph(_format_money(totals.get("with_vat", 0)), total_style)],
        ]
        tbl = Table(rows, colWidths=[left_w, right_w])
        tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), self.font_name),
            ("FONTSIZE", (0, 0), (-1, -1), Layout.NORMAL_FONT_SIZE),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.7, colors.black),
            ("BACKGROUND", (0, 2), (1, 2), Layout.GREEN),
            ("TEXTCOLOR", (0, 2), (1, 2), colors.white),
        ]))
        story.extend([tbl, Spacer(1, 10)])

    def _build_materials(self, story: list, meta: dict):
        w = self.usable_width
        col1, col2, col3 = w * 0.72, w * 0.14, w * 0.14

        # Заголовок «Материалы»
        title = self._p("<b>Материалы</b>", fontSize=14, alignment=1, textColor=colors.black)
        tbl = Table([[title]], colWidths=[w])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.extend([tbl, Spacer(1, 6)])

        # Сроки выполнения
        sc1, sc2, sc3 = w * 0.40, w * 0.30, w * 0.30
        lbl = self._p("<b>Сроки выполнения монтажных работ</b>", textColor=colors.white, fontSize=10)
        time_val = self._p("от 15 до 30 дней на каждое оборудование", fontSize=9, alignment=1)
        srok = Table([[lbl, time_val, ""]], colWidths=[sc1, sc2, sc3])
        srok.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), Layout.GREEN),
            ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
            ("BOX", (0, 0), (0, 0), 1.0, colors.black),
            ("SPAN", (1, 0), (2, 0)),
            ("BOX", (1, 0), (2, 0), 1.0, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.extend([srok, Spacer(1, 6)])

        # Обязанности сторон
        hdr = [
            self._p("<b>Обязанности сторон</b>", textColor=colors.white, fontSize=11),
            self._p("<b>Заказчик</b>", textColor=colors.white, fontSize=9, alignment=1),
            self._p("<b>Подрядчик</b>", textColor=colors.white, fontSize=9, alignment=1),
        ]
        rows = [hdr]
        for desc, cust, contr in RESPONSIBILITIES:
            rows.append([
                self._p(desc, "TableSmall"),
                self._p(cust, "TableSmall"),
                self._p(contr, "TableSmall"),
            ])
        tbl = Table(rows, colWidths=[col1, col2, col3], repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), Layout.GREEN),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), self.font_name),
            ("FONTSIZE", (0, 0), (-1, -1), Layout.TABLE_FONT_SIZE - 1),
            ("GRID", (0, 1), (-1, -1), 0.6, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.extend([tbl, Spacer(1, 8)])

        # Контакт / Директор
        contact_name = meta.get("contact_name", "Ахунов Хамидулло")
        contact_mobile = meta.get("contact_mobile", "+998 90 033 06 44")
        director_name = meta.get("director_name", "Алишер Гуламов")
        sign_date = meta.get("date", datetime.today().strftime("%d.%m.%Y"))

        combined = [
            [self._p("<b>Контактное лицо</b>", textColor=colors.white, fontSize=10),
             self._p("<b>Директор</b>", textColor=colors.white, fontSize=10, alignment=2)],
            [self._p(f"<b>{contact_name}</b>", fontSize=11), self._p(f"<b>{director_name}</b>", fontSize=11, alignment=2)],
            [self._p(f"Моб: {contact_mobile}", fontSize=9), ""],
            ["", self._p("Подпись:", fontSize=9, alignment=2)],
            ["", SignatureLine(col2 + col3)],
            ["", self._p(f"Дата: {sign_date}", fontSize=9, alignment=2)],
        ]
        tbl = Table(combined, colWidths=[col1, col2 + col3])
        tbl.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (1, 0), Layout.GREEN),
            ("TEXTCOLOR", (0, 0), (1, 0), colors.white),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.extend([tbl, Spacer(1, 6)])

        bottom = Table([[""]], colWidths=[w])
        bottom.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), Layout.GREEN),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.extend([bottom, Spacer(1, 4)])

    def _build_footer(self, story: list):
        story.extend([
            self._p("Документ сформирован автоматически.", "Small"),
            Spacer(1, 2),
        ])

    # -----------------------------------------------------------------------
    # Публичный API
    # -----------------------------------------------------------------------
    def generate(
        self,
        data: dict,
        output: str = Layout.DEFAULT_OUTPUT,
        logo_path: str = Layout.DEFAULT_LOGO,
    ) -> str:
        """Создаёт PDF. Возвращает путь к файлу."""
        story = []
        self._build_header(story, data, logo_path)
        self._build_proposal_block(
            story,
            project=data.get("project", ""),
            subtitle=data.get("subtitle", ""),
            items=data.get("items", []),
        )
        self._build_totals(story, data.get("totals", {}))
        self._build_materials(story, {
            "contact_name": data.get("contact", {}).get("name", "Ахунов Хамидулло"),
            "contact_mobile": data.get("contact", {}).get("phone", "+998 90 033 06 44"),
            "director_name": data.get("director", {}).get("name", "Алишер Гуламов"),
            "date": data.get("date", datetime.today().strftime("%d.%m.%Y")),
        })
        self._build_footer(story)

        doc = SimpleDocTemplate(
            output,
            pagesize=Layout.PAGE_SIZE,
            leftMargin=Layout.MARGIN,
            rightMargin=Layout.MARGIN,
            topMargin=Layout.MARGIN,
            bottomMargin=Layout.MARGIN,
        )
        doc.build(story)
        return output


# ---------------------------------------------------------------------------
# CLI и пример
# ---------------------------------------------------------------------------
def get_sample_data() -> dict:
    return {
        "project": "АЭРОПОРТ",
        "subtitle": "Стоимость монтажных и пусконаладочных работ",
        "date": "19.12.2025",
        "contact": {"name": "Ахунов Хамидулло", "phone": "+998 90 033 06 44"},
        "items": [
            {"name": "Монтаж лифта 1000 кг", "size": "2/2/2", "floors": "1", "qty": 1, "unit_price": 82000000, "total": 82000000},
            {"name": "Монтаж лифта 630 кг", "size": "2/2/2", "floors": "1", "qty": 1, "unit_price": 41000000, "total": 41000000},
        ],
        "totals": {
            "without_vat": 123000000,
            "vat_percent": 12,
            "vat_amount": math.floor(123000000 * 0.12),
            "with_vat": math.floor(123000000 * 1.12),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Генератор PDF коммерческого предложения")
    parser.add_argument("--logo", default=Layout.DEFAULT_LOGO, help="Путь к логотипу")
    parser.add_argument("--font", default=None, help="Путь к шрифту (TTF)")
    parser.add_argument("--output", default=Layout.DEFAULT_OUTPUT, help="Выходной файл")
    args = parser.parse_args()

    generator = ProposalPDFGenerator(font_path=args.font)
    out = generator.generate(get_sample_data(), output=args.output, logo_path=args.logo)
    print(f"Сохранено: {out}")


if __name__ == "__main__":
    main()
