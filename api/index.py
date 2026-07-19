from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
import ssl
from PIL import Image, ImageDraw, ImageFont
import io

# ============================================================
# ШРИФТ ГРУЗИТСЯ ОДИН РАЗ НА УРОВНЕ МОДУЛЯ.
# На Vercel/serverless процесс переиспользуется между "тёплыми"
# вызовами -> код вне класса handler выполняется только на
# холодном старте. Раньше шрифт качался с CDN на КАЖДЫЙ запрос -
# это и медленно, и хрупко (сеть/CDN может лечь).
# ============================================================

FONT_URL = "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/inter/static/Inter-SemiBold.ttf"

_FONT_CACHE = {}


def _load_font_bytes():
    if "data" in _FONT_CACHE:
        return _FONT_CACHE["data"]
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(
            FONT_URL,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
        )
        data = urllib.request.urlopen(req, context=ctx, timeout=5).read()
        _FONT_CACHE["data"] = data
        return data
    except Exception:
        _FONT_CACHE["data"] = None
        return None


def get_fonts():
    raw = _load_font_bytes()
    if raw is None:
        d = ImageFont.load_default()
        return d, d, d
    return (
        ImageFont.truetype(io.BytesIO(raw), 15),  # основной текст
        ImageFont.truetype(io.BytesIO(raw), 10),  # подпись/декор
        ImageFont.truetype(io.BytesIO(raw), 9),   # мини-бейджи соцсетей
    )


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
            font_main.getlength(base_text) + font_main.getlength(nick_text)
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
        draw.text((x_pos, y_main), base_text, fill=COLOR_TEXT_WHITE, font=font_main, anchor="lm")
        first_part_len = font_main.getlength(base_text)
        draw.text((x_pos + first_part_len, y_main), nick_text, fill=COLOR_RASPBERRY, font=font_main, anchor="lm")

        # Подпись (нижняя строка) — приглушённая
        draw.text((x_pos, y_main + 20), subtitle_text, fill=COLOR_TEXT_MUTED, font=font_small, anchor="lm")

        # Декоративный тех-индекс
        divider_x = 80 + left_text_width + 20
        draw.line([divider_x, 12, divider_x, height - 12], fill=COLOR_BORDER, width=1)
        draw.text((divider_x + 14, 15), "// SYS_OP", fill=COLOR_FAINT_BURGUNDY, font=font_small, anchor="lm")

        # Три диагональные штрихкод-линии под индексом
        for i in range(3):
            line_x = divider_x + 14 + (i * 5)
            draw.line([line_x, 30, line_x - 4, 42], fill=COLOR_TECH_GREY, width=1)

        # ---- Блок соцсетей: минималистичные круглые бейджи ----
        badges_start_x = width - badge_block_width - 24
        draw.line([badges_start_x - 16, 12, badges_start_x - 16, height - 12], fill=COLOR_BORDER, width=1)

        bx = badges_start_x
        badge_r = 11
        cy = height // 2
        for label, _url in SOCIALS:
            cx = bx + badge_r
            draw.ellipse(
                [cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r],
                outline=COLOR_RASPBERRY,
                width=1,
            )
            draw.text((cx, cy), label, fill=COLOR_TEXT_WHITE, font=font_badge, anchor="mm")
            bx += badge_r * 2 + 12

        # Едва заметный крестик-визир в пустоте между блоками
        cross_x, cross_y = divider_x + 55, height // 2
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