from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import io

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        nick = query_params.get('nick', ['sky'])[0]
        
        text = f"Nah, I’m a {nick}."
        
        width = 450
        height = 42
        
        img = Image.new('RGB', (width, height), color=(13, 14, 18))
        draw = ImageDraw.Draw(img)
        
        # Минималистичный дизайн
        draw.rectangle([0, 0, width - 1, height - 1], outline=(31, 33, 42))
        draw.rectangle([0, 0, 2, height - 1], fill=(124, 58, 237)) 
        
        # ИСПРАВЛЕННЫЙ URL ШРИФТА (Прямой линк без HTML-оболочки)
        font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/static/Inter-Medium.ttf"
        try:
            req = urllib.request.Request(
                font_url, 
                headers={'User-Agent': 'Mozilla/5.0'} # Маскируемся под браузер, чтобы GitHub не блокировал
            )
            font_data = urllib.request.urlopen(req).read()
            font = ImageFont.truetype(io.BytesIO(font_data), 14)
        except Exception as e:
            # Если что-то пойдет не так, мы хотя бы крупно увидим стандартный шрифт, но новый URL стабилен
            font = ImageFont.load_default()
            
        draw.text((24, height / 2), text, fill=(243, 244, 246), font=font, anchor="lm")
        
        byte_io = io.BytesIO()
        img.save(byte_io, 'PNG')
        byte_io.seek(0)
        
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(byte_io.getvalue())
        return