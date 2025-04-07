import tkinter as tk
import sqlite3
import os
from PIL import Image, ImageTk
import sys
from core.prodotti import carica_prodotti
from core.db import crea_tabella
from gui.menu import menu_principale
import pygame
from core import rtc_sync

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
    
DB_FILE = "cassa.db"

class RegistratoreCassa:
    def get_font(self, name="Symbola", base_size=14, style="normal"):
        size = max(8, int(base_size * self.scala))
        return (name, size, style)

    def __init__(self, root):
        self.root = root
        self.root.title("Registratore di Cassa")
        # Dimensione base (sviluppo su desktop remoto)
        base_width = 1024
        base_height = 760
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        larghezza = min(screen_width, base_width)
        altezza = min(screen_height, base_height)
        # Posizione centrata orizzontalmente, allineata in alto
        x = (screen_width // 2) - (larghezza // 2)
        y = 0
        self.root.geometry(f"{larghezza}x{altezza}+{x}+{y}")
        # Calcolo fattore scala dinamico
        self.scala_x = screen_width / base_width
        self.scala_y = screen_height / base_height
        self.scala = min(self.scala_x, self.scala_y)

        self.logo_path = resource_path(os.path.join("assets", "LogoUfficiale.png"))
        self.nota_immagine_path = None
        self.logo_img = None
        if os.path.exists(self.logo_path):
            img = Image.open(self.logo_path).resize((85, 60))
            self.logo_img = ImageTk.PhotoImage(img)
        
        self.totale = 0
        self.stampa_abilitata = tk.BooleanVar(value=True)
        self.abilita_cassetto_rele = tk.BooleanVar(value=True)
        self.menu_impaginato = tk.BooleanVar(value=False)
        self.stampa_tagliandini = tk.BooleanVar(value=True)
        self.musica_attiva = tk.BooleanVar(value=False)  # Musica attiva di default
        self.importo_var = tk.StringVar()
        self.resto_var = tk.StringVar(value="Resto: €0.00")
        self.carrello = []  # Lista temporanea per le comande
        self.sconti = 0.0
        self.sconti_giornalieri = 0.0
        self.prodotti = carica_prodotti()
        self.conn = sqlite3.connect(DB_FILE)
        crea_tabella(self.conn)        
        menu_principale(self)

        def avvia_musica(percorso):
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(percorso)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Errore audio: {e}")

        def ferma_musica():
            try:
                pygame.mixer.music.stop()
            except:
                pass

        musica_path = resource_path(os.path.join("assets", "background.mp3"))
        self.musica_path = musica_path  # salva il path per uso futuro

        # Avvia se abilitata
        if self.musica_attiva.get() and os.path.exists(musica_path):
            avvia_musica(musica_path)

        # Traccia cambiamenti
        def toggle_musica(*args):
            if self.musica_attiva.get():
                if os.path.exists(self.musica_path):
                    avvia_musica(self.musica_path)
            else:
                ferma_musica()

        self.musica_attiva.trace_add("write", toggle_musica)

if __name__ == "__main__":
    rtc_sync.sync()
    root = tk.Tk()
    app = RegistratoreCassa(root)
    root.mainloop()
