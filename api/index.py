from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from PIL import Image, ImageDraw, ImageFont
import io
import os

# ============================================================
# ШРИФТ ГРУЗИТСЯ ЛОКАЛЬНО ИЗ РЕПО, БЕЗ СЕТИ.
# Раньше тянули TTF с jsDelivr на каждый холодный старт - если
# исходящая сеть с serverless-функции недоступна/режется (частая
# ситуация на Vercel), это валило функцию в 500. Теперь шрифт -
# обычный статический файл рядом со скриптом, читается с диска.
#
# НУЖНО: положить Inter-SemiBold.ttf в ту же папку, что и этот
# файл (например api/fonts/Inter-SemiBold.ttf), и поправить
# FONT_PATH ниже под реальный путь в твоём репо.
# ============================================================

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "Inter-SemiBold.ttf")

_FONT_CACHE = {}


def get_fonts():
    if "fonts" in _FONT_CACHE:
        return _FONT_CACHE["fonts"]
    try:
        fonts = (
            ImageFont.truetype(FONT_PATH, 15),  # основной текст
            ImageFont.truetype(FONT_PATH, 10),  # подпись/декор
            ImageFont.truetype(FONT_PATH, 9),   # мини-бейджи
        )
    except Exception:
        # Если шрифта нет на диске - не роняем функцию,
        # используем дефолтный битмап-шрифт PIL.
        d = ImageFont.load_default()
        fonts = (d, d, d)
    _FONT_CACHE["fonts"] = fonts
    return fonts


def safe_text(draw, xy, text, fill, font, anchor="lm"):
    """draw.text с anchor может кидать TypeError на очень старых
    версиях Pillow / дефолтном битмап-шрифте. Подстраховка, чтобы
    в худшем случае просто немного съехал текст, а не 500-ка."""
    try:
        draw.text(xy, text, fill=fill, font=font, anchor=anchor)
    except TypeError:
        draw.text(xy, text, fill=fill, font=font)


def safe_length(font, text):
    try:
        return font.getlength(text)
    except AttributeError:
        return font.getsize(text)[0]  # старый Pillow API


# Палитра — в твоей фирменной тёмно-бордовой стилистике
COLOR_BG_START = (13, 14, 18)
COLOR_BG_END = (18, 19, 24)
COLOR_RASPBERRY = (188, 38, 73)
COLOR_TEXT_WHITE = (245, 245, 247)
COLOR_TEXT_MUTED = (140, 142, 152)
COLOR_BORDER = (36, 38, 49)
COLOR_TECH_GREY = (55, 58, 72)
COLOR_FAINT_BURGUNDY = (70, 20, 35)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        nick = query_params.get("nick", ["sky"])[0]

        base_text = "Nah, I'm a "
        nick_text = f"{nick}."
        subtitle_text = "code by day, samp by night"

        font_main, font_small, _unused = get_fonts()

        # Ширина считается динамически под контент ника
        left_text_width = int(
            safe_length(font_main, base_text) + safe_length(font_main, nick_text)
        )
        width = max(360, 80 + left_text_width + 120)
        height = 60

        img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(img)

        # Градиентный фон
        for x in range(width):
            r = int(COLOR_BG_START[0] + (COLOR_BG_END[0] - COLOR_BG_START[0]) * (x / width))
            g = int(COLOR_BG_START[1] + (COLOR_BG_END[1] - COLOR_BG_START[1]) * (x / width))
            b = int(COLOR_BG_START[2] + (COLOR_BG_END[2] - COLOR_BG_START[2]) * (x / width))
            draw.line([(x, 0), (x, height)], fill=(r, g, b))

        # Внешняя рамка-капсула
        try:
            draw.rounded_rectangle([0, 0, width - 1, height - 1], radius=8, outline=COLOR_BORDER, width=1)
        except AttributeError:
            draw.rectangle([0, 0, width - 1, height - 1], outline=COLOR_BORDER, width=1)

        # Малиновый индикатор слева
        draw.ellipse([14, 26, 20, 32], fill=COLOR_RASPBERRY)

        # Основной текст (верхняя строка)
        x_pos = 32
        y_main = 22
        safe_text(draw, (x_pos, y_main), base_text, COLOR_TEXT_WHITE, font_main)
        first_part_len = safe_length(font_main, base_text)
        safe_text(draw, (x_pos + first_part_len, y_main), nick_text, COLOR_RASPBERRY, font_main)

        # Подпись (нижняя строка) — приглушённая
        safe_text(draw, (x_pos, y_main + 20), subtitle_text, COLOR_TEXT_MUTED, font_small)

        # Декоративный тех-индекс справа
        divider_x = 80 + left_text_width + 20
        draw.line([divider_x, 12, divider_x, height - 12], fill=COLOR_BORDER, width=1)
        safe_text(draw, (divider_x + 14, 15), "// SYS_OP", COLOR_FAINT_BURGUNDY, font_small)

        # Три диагональные штрихкод-линии под индексом
        for i in range(3):
            line_x = divider_x + 14 + (i * 5)
            draw.line([line_x, 30, line_x - 4, 42], fill=COLOR_TECH_GREY, width=1)

        # Едва заметный крестик-визир в пустоте справа
        cross_x, cross_y = divider_x + 60, height // 2
        draw.line([cross_x - 3, cross_y, cross_x + 3, cross_y], fill=COLOR_BORDER, width=1)
        draw.line([cross_x, cross_y - 3, cross_x, cross_y + 3], fill=COLOR_BORDER, width=1)

        byte_io = io.BytesIO()
        img.save(byte_io, "PNG")
        byte_io.seek(0)

        self.send_response(200)
        self.send_header("Content-type", "image/png")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(byte_io.getvalue())
        return