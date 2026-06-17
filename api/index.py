from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import io

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Разбираем никнейм из ссылки (?nick=...)
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        nick = query_params.get('nick', ['sky'])[0]
        
        # Новый кастомный текст
        text = f"Nah, I’m a {nick}."
        
        # Немного увеличим высоту, чтобы плашка дышала и выглядела как премиальный бэдж
        width = 450
        height = 42
        
        # 2. Создаем холст с глубоким матовым премиум-цветом (Тёмно-графитовый #0d0e12)
        img = Image.new('RGB', (width, height), color=(13, 14, 18))
        draw = ImageDraw.Draw(img)
        
        # 3. МИНИМАЛИСТИЧНЫЙ ДИЗАЙН
        # Делаем очень тонкую, едва заметную стильную рамку (#1f212a)
        draw.rectangle([0, 0, width - 1, height - 1], outline=(31, 33, 42))
        
        # Свежий акцент: ультра-тонкая вертикальная линия неоново-фиолетового цвета слева
        # Она заменяет громоздкие иконки и придаёт статусности
        draw.rectangle([0, 0, 2, height - 1], fill=(124, 58, 237)) 
        
        # 4. СОВРЕМЕННЫЙ ШРИФТ ИЗ СЕТИ
        # Скачиваем чистый, минималистичный шрифт Inter-Medium
        font_url = "https://github.com/google/fonts/raw/main/ofl/inter/static/Inter-Medium.ttf"
        try:
            font_data = urllib.request.urlopen(font_url).read()
            font = ImageFont.truetype(io.BytesIO(font_data), 14) # Размер 14 — аккуратный и читаемый
        except Exception:
            font = ImageFont.load_default()
            
        # 5. ИДЕАЛЬНОЕ ЦЕНТРИРОВАНИЕ ТЕКСТА
        # anchor="lm" автоматически выравнивает текст строго по центру вертикали. 
        # Отступ слева делаем 24 пикселя, чтобы текст красиво отступал от фиолетовой линии.
        draw.text((24, height / 2), text, fill=(243, 244, 246), font=font, anchor="lm")
        
        # 6. ОТПРАВЛЯЕМ КАРТИНКУ НА ФОРУМ
        byte_io = io.BytesIO()
        img.save(byte_io, 'PNG')
        byte_io.seek(0)
        
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(byte_io.getvalue())
        return