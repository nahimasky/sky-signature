from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from PIL import Image, ImageDraw
import io

# Каждая иконка — отдельная картинка -> оборачивается СВОИМ [url=...][img][/img][/url]
# в BBCode. Так каждая соцсеть реально кликабельна, а не просто нарисована.

COLOR_BG = (13, 14, 18)
COLOR_BORDER = (36, 38, 49)
COLOR_RASPBERRY = (188, 38, 73)
COLOR_WHITE = (245, 245, 247)

SIZE = 40


def draw_github(draw, cx, cy, s):
    # Стилизованный силуэт "cat-mark": голова + острые уши + лапы снизу
    r = int(s * 0.34)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=COLOR_WHITE)
    ear = int(s * 0.14)
    draw.polygon([(cx - r + 2, cy - r + 4), (cx - r - ear + 4, cy - r - ear),
                  (cx - r + ear + 2, cy - r + 2)], fill=COLOR_WHITE)
    draw.polygon([(cx + r - 2, cy - r + 4), (cx + r + ear - 4, cy - r - ear),
                  (cx + r - ear - 2, cy - r + 2)], fill=COLOR_WHITE)
    for dx in (-r + 6, r - 6):
        draw.ellipse([cx + dx - 3, cy + r - 4, cx + dx + 3, cy + r + 2], fill=COLOR_BG)


def draw_vk(draw, cx, cy, s, font=None):
    r = int(s * 0.30)
    draw.rounded_rectangle(
        [cx - r - 4, cy - r + 4, cx + r + 4, cy + r - 4], radius=4, fill=COLOR_WHITE
    )
    from PIL import ImageFont
    f = ImageFont.load_default()
    draw.text((cx, cy), "VK", fill=COLOR_BG, font=f, anchor="mm")


def draw_telegram(draw, cx, cy, s):
    r = int(s * 0.34)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=COLOR_WHITE, width=1)
    # Бумажный самолётик
    p1 = (cx - r + 6, cy + 2)
    p2 = (cx + r - 4, cy - r + 6)
    p3 = (cx + 2, cy + 4)
    p4 = (cx - r + 12, cy + r - 8)
    draw.line([p1, p2], fill=COLOR_WHITE, width=2)
    draw.line([p2, p4], fill=COLOR_WHITE, width=2)
    draw.line([p1, p3], fill=COLOR_WHITE, width=2)
    draw.line([p3, p2], fill=COLOR_WHITE, width=2)


ICONS = {
    "gh": draw_github,
    "vk": draw_vk,
    "tg": draw_telegram,
}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        icon_type = query_params.get("type", ["gh"])[0]

        img = Image.new("RGB", (SIZE, SIZE), COLOR_BG)
        draw = ImageDraw.Draw(img)

        try:
            draw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=8, outline=COLOR_BORDER, width=1)
        except AttributeError:
            draw.rectangle([0, 0, SIZE - 1, SIZE - 1], outline=COLOR_BORDER, width=1)

        cx, cy = SIZE // 2, SIZE // 2
        fn = ICONS.get(icon_type, draw_github)
        fn(draw, cx, cy, SIZE)

        byte_io = io.BytesIO()
        img.save(byte_io, "PNG")
        byte_io.seek(0)

        self.send_response(200)
        self.send_header("Content-type", "image/png")
        self.send_header("Cache-Control", "public, max-age=86400")  # иконки статичны — можно кэшировать
        self.end_headers()
        self.wfile.write(byte_io.getvalue())
        return
