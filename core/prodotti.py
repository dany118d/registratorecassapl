import json
import os
import sys

def resource_path(rel_path):
    # Prima cerca asset accanto all'eseguibile (uso preferito)
    exe_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
    external_path = os.path.join(exe_dir, rel_path)
    if os.path.exists(external_path):
        return external_path

    # Altrimenti fallback a cartella temporanea interna di PyInstaller
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, rel_path)

    # Fallback finale (in sviluppo)
    return os.path.join(os.path.abspath("."), rel_path)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_FILE = resource_path(os.path.join(BASE_DIR, "assets", "prodotti.json"))

def carica_prodotti():
    try:
        from PIL import Image, ImageDraw, ImageFont
        import re

        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        for nome in data:
            # Pulisce il nome per usarlo come nome file
            nome_pulito = ''.join(c for c in nome if c.isalnum() or c.isspace()).strip().lower().replace(" ", "_")
            path_img = os.path.join(BASE_DIR, "assets", "tagliandini", f"{nome_pulito}.png")

            if not os.path.isfile(path_img):
                os.makedirs(os.path.dirname(path_img), exist_ok=True)
                img = Image.new("RGB", (576, 120), color="white")
                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 60)
                except:
                    font = ImageFont.load_default()

                text = re.sub(r"[^\w\s]", "", nome.upper())
                font_size = 60
                while font_size >= 20:
                    font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
                    text_width, text_height = draw.textsize(text, font=font)
                    if text_width <= 576:
                        break
                    font_size -= 2  # prova con font leggermente più piccolo
                pos = ((576 - text_width) // 2, (120 - text_height) // 2)
                draw.text(pos, text, fill="black", font=font)
                img.save(path_img)

        return data

    except FileNotFoundError:
        return {}

def carica_prodotti_old():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def carica_prodotti_debug():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            contenuto = f.read()
            with open("/tmp/debug_prodotti_check.txt", "w") as log:
                log.write(f"PATH: {CONFIG_FILE}\n")
                log.write(f"CONTENUTO:\n{contenuto}\n")
            f.seek(0)
            return json.loads(contenuto)
    except Exception as e:
        with open("/tmp/debug_prodotti_check.txt", "w") as log:
            log.write(f"ERRORE: {e}\nPATH: {CONFIG_FILE}\n")
        return {}
