from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import io

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Разбираем параметры из ссылки. Теперь можно передавать и ?nick=, и ?role=
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        nick = query_params.get('nick', ['sky'])[0]
        role = query_params.get('role', ['Head of Civil'])[0] # Текст для правого бэджа
        
        base_text = "Nah, I’m a "
        nick_text = f"{nick}."
        
        # Оптимальные размеры для форумного баннера
        width = 460
        height = 48
        
        # 2. Создаем холст с благородным темным градиентом
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Плавный переход фона для эффекта глубины
        color_bg_start = (20, 21, 26)  # Ультра-темный графит
        color_bg_end = (28, 30, 38)    # Чуть светлее к правому краю
        for x in range(width):
            r = int(color_bg_start[0] + (color_bg_end[0] - color_bg_start[0]) * (x / width))
            g = int(color_bg_start[1] + (color_bg_end[1] - color_bg_start[1]) * (x / width))
            b = int(color_bg_start[2] + (color_bg_end[2] - color_bg_start[2]) * (x / width))
            draw.line([(x, 0), (x, height)], fill=(r, g, b))

        # Палитра
        color_raspberry = (188, 38, 73)    # Тот самый малиновый бордо #bc2649
        color_text_white = (245, 245, 247)   # Чистый студийный белый
        color_border = (45, 48, 62)         # Стильная темная рамка
        
        # 3. Геометрия и структура плашки
        # Внешняя аккуратная рамка скругленного бэджа
        draw.rounded_rectangle([0, 0, width - 1, height - 1], radius=6, outline=color_border, width=1)
        
        # Левый аккуратный неоновый маркер безопасности
        draw.rounded_rectangle([4, 6, 7, height - 7], radius=2, fill=color_raspberry)

        # 4. Загрузка шрифтов из сети (Inter-SemiBold для веса и четкости)
        font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/static/Inter-SemiBold.ttf"
        try:
            req = urllib.request.Request(font_url, headers={'User-Agent': 'Mozilla/5.0'})
            font_data = urllib.request.urlopen(req).read()
            font_main = ImageFont.truetype(io.BytesIO(font_data), 15)  # Основной текст крупнее
            font_badge = ImageFont.truetype(io.BytesIO(font_data), 12) # Текст в бэдже чуть меньше
        except Exception:
            font_main = ImageFont.load_default()
            font_badge = ImageFont.load_default()
            
        # 5. Рендеринг левой текстовой части
        x_pos = 20
        y_pos = height / 2
        
        # Печатаем "Nah, I'm a "
        draw.text((x_pos, y_pos), base_text, fill=color_text_white, font=font_main, anchor="lm")
        
        # Считаем сдвиг и печатаем малиновый ник с точкой
        first_part_len = font_main.getlength(base_text)
        draw.text((x_pos + first_part_len, y_pos), nick_text, fill=color_raspberry, font=font_main, anchor="lm")
        
        # 6. Рендеринг правого бэджа (Заполняем пустоту в стиле твоего скрина)
        role_text_width = font_badge.getlength(role)
        
        # Расчет динамических координат под размер текста роли
        badge_padding = 12
        badge_h_padding = 8
        badge_width = role_text_width + (badge_padding * 2)
        
        badge_x1 = width - 16 - badge_width
        badge_y1 = (height / 2) - (11 + badge_h_padding / 2)
        badge_x2 = width - 16
        badge_y2 = (height / 2) + (11 + badge_h_padding / 2)
        
        # Рисуем подложку бэджа (как "Head of Civil")
        draw.rounded_rectangle([badge_x1, badge_y1, badge_x2, badge_y2], radius=6, fill=color_raspberry)
        
        # Центрируем текст внутри бэджа
        badge_text_x = badge_x1 + badge_padding
        draw.text((badge_text_x, y_pos), role, fill=color_text_white, font=font_badge, anchor="lm")
        
        # 7. Отдаем готовый результат
        byte_io = io.BytesIO()
        img.save(byte_io, 'PNG')
        byte_io.seek(0)
        
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(byte_io.getvalue())
        return