from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
import ssl
from PIL import Image, ImageDraw, ImageFont
import io

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Разбираем никнейм
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        nick = query_params.get('nick', ['sky'])[0]
        
        base_text = "Nah, I’m a "
        nick_text = f"{nick}."
        
        # Фиксированный размер возвращен назад (как ты и просил)
        width = 460
        height = 48
        
        # 2. Создаем холст с мягким темным бэкграундом
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Дорогой едва заметный градиент для основы
        color_bg_start = (13, 14, 18)  # Глубокий графит #0d0e12
        color_bg_end = (18, 19, 24)    # Чуть светлее к правому краю
        for x in range(width):
            r = int(color_bg_start[0] + (color_bg_end[0] - color_bg_start[0]) * (x / width))
            g = int(color_bg_start[1] + (color_bg_end[1] - color_bg_start[1]) * (x / width))
            b = int(color_bg_start[2] + (color_bg_end[2] - color_bg_start[2]) * (x / width))
            draw.line([(x, 0), (x, height)], fill=(r, g, b))

        # Палитра цветов
        color_raspberry = (188, 38, 73)    # Твой малиновый бордо #bc2649
        color_text_white = (245, 245, 247)   # Чистый белый
        color_border = (36, 38, 49)         # Аккуратная темная рамка
        color_tech_grey = (55, 58, 72)       # Невзрачный серый для элементов UI
        color_faint_burgundy = (70, 20, 35)  # Очень тусклый бордовый для фона элементов
        
        # 3. ЖЕЛЕЗНАЯ ЗАГРУЗКА ШРИФТА (Через стабильный CDN jsDelivr + маскировка под Chrome)
        font_url = "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/inter/static/Inter-SemiBold.ttf"
        try:
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(
                font_url, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            )
            font_data = urllib.request.urlopen(req, context=ctx).read()
            font_main = ImageFont.truetype(io.BytesIO(font_data), 15)   # Основной текст
            font_small = ImageFont.truetype(io.BytesIO(font_data), 10)  # Мелкий декоративный шрифт
        except Exception:
            # Сверхнадежный резерв, если сеть упадет
            font_main = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # 4. РИСУЕМ СТИЛЬНУЮ ОБТЕКАЕМУЮ КАПСУЛУ
        try:
            draw.rounded_rectangle([0, 0, width - 1, height - 1], radius=8, outline=color_border, width=1)
        except AttributeError:
            draw.rectangle([0, 0, width - 1, height - 1], outline=color_border, width=1)
        
        # Аккуратный малиновый индикатор слева
        draw.ellipse([14, 21, 20, 27], fill=color_raspberry)

        # 5. ВЫРАВНИВАНИЕ ОСНОВНОГО ТЕКСТА
        x_pos = 32
        y_pos = height / 2
        
        # Наносим "Nah, I'm a "
        draw.text((x_pos, y_pos), base_text, fill=color_text_white, font=font_main, anchor="lm")
        
        # Сдвигаем и наносим малиновый ник с точкой
        first_part_len = font_main.getlength(base_text)
        draw.text((x_pos + first_part_len, y_pos), nick_text, fill=color_raspberry, font=font_main, anchor="lm")
        
        # 6. ЗАПОЛНЕНИЕ ПУСТОТЫ (Эстетичные невзрачные элементы справа)
        
        # Элемент 1: Тонкий вертикальный разделитель (дизайнерская ось)
        draw.line([320, 14, 320, 34], fill=color_border, width=1)
        
        # Элемент 2: Декоративный микро-код/индекс в стиле интерфейсов
        draw.text((335, height / 2), "// SYS_OP", fill=color_faint_burgundy, font=font_small, anchor="lm")
        
        # Элемент 3: Серия из трех тонких минималистичных наклонных линий (штрихкод)
        for i in range(3):
            line_x = 405 + (i * 5)
            draw.line([line_x, 18, line_x - 4, 30], fill=color_tech_grey, width=1)
            
        # Элемент 4: Едва заметный технологический крестик визира (+) в углу пустоты
        cross_x, cross_y = 290, 24
        draw.line([cross_x - 3, cross_y, cross_x + 3, cross_y], fill=color_border, width=1)
        draw.line([cross_x, cross_y - 3, cross_x, cross_y + 3], fill=color_border, width=1)

        # 7. Отдаем результат на форум
        byte_io = io.BytesIO()
        img.save(byte_io, 'PNG')
        byte_io.seek(0)
        
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(byte_io.getvalue())
        return
