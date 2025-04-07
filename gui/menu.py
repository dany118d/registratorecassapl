import tkinter as tk
from gui.layout import crea_header
from gui.cassa import menu_cassa
from gui.gestione import menu_gestione
import os
import shutil
import pygame
from core import rtc_sync

def menu_principale(app):
    
    def esci():
        note_path = os.path.join(os.getcwd(), "note")
        if os.path.exists(note_path):
            try:
                shutil.rmtree(note_path)
            except Exception as e:
                print(f"Errore nella cancellazione della cartella note: {e}")
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        root.destroy()
        
    from core.logica import aggiorna_orologio
    root = app.root
    for widget in root.winfo_children():
        widget.destroy()

    # Header comune con logo e orologio
    crea_header(app, app.logo_img, lambda lbl: setattr(app, 'orologio_label', lbl))
    aggiorna_orologio(app)

    # Titolo
    tk.Label(root, text="Menu Principale", font=app.get_font("Symbola", 24, "bold")).pack(pady=int(30 * app.scala))

    # Pulsanti
    tk.Button(root, text="🛒 Cassa", command=lambda: menu_cassa(app),
              width=int(25 * app.scala), height=int(3 * app.scala),
              bg="lightblue", font=app.get_font("Symbola", 16, "bold")).pack(pady=int(10 * app.scala))

    tk.Button(root, text="⚙️ Gestione", command=lambda: menu_gestione(app),
              width=int(25 * app.scala), height=int(3 * app.scala),
              bg="lightgreen", font=app.get_font("Symbola", 16, "bold")).pack(pady=int(10 * app.scala))

    tk.Button(root, text="❌ Esci", command=esci,
              width=int(25 * app.scala), height=int(3 * app.scala),
              bg="red", fg="white", font=app.get_font("Symbola", 16, "bold")).pack(pady=int(10 * app.scala))

    # Sezione opzioni con due colonne
    frame_opzioni = tk.Frame(root)
    frame_opzioni.pack(pady=int(10 * app.scala))

    opzioni = [
        ("🖨️ Abilita stampa", app.stampa_abilitata),
        ("🧾 Stampa tagliandini", app.stampa_tagliandini),
        ("🔐 Cassetto elettronico", app.abilita_cassetto_rele),
        ("📖 Menu cassa a pagine", app.menu_impaginato),        
        ("🎵 Musica di sottofondo", app.musica_attiva)   
    ]

    checkboxes = {}
    for idx, (testo, variabile) in enumerate(opzioni):
        riga = idx // 2
        colonna = idx % 2
        cb = tk.Checkbutton(frame_opzioni, text=testo, variable=variabile,
                            font=app.get_font("Symbola", 12))
        cb.grid(row=riga, column=colonna, sticky="w", padx=10, pady=5)
        checkboxes[testo] = cb  # Salva riferimenti
    
    def aggiorna_stato_tagliandini(*args):
        checkbox = checkboxes.get("🧾 Stampa tagliandini")
        if checkbox and checkbox.winfo_exists():
            if app.stampa_abilitata.get():
                checkbox.config(state="normal")
            else:
                checkbox.config(state="disabled")
                app.stampa_tagliandini.set(False)

    app.stampa_abilitata.trace_add("write", aggiorna_stato_tagliandini)
    aggiorna_stato_tagliandini()  # imposta stato iniziale
    stato_rtc = "⛔ Orologio non trovato o errore di sincronizzazione"
    if rtc_sync.esito_sync is True:
        stato_rtc = "✅ Orologio sincronizzato correttamente"

    lbl_rtc = tk.Label(root, text=stato_rtc, font=app.get_font("Symbola", 11))
    lbl_rtc.pack(pady=(5, 20))