import tkinter as tk
from gui.layout import crea_header
from core.db import (
    imposta_fondo,
    visualizza_registro_cassa,
    visualizza_vendite,
    azzera_fondo,
    azzera_incassi,
    azzera_vendite
)
from core.report import genera_report

def menu_gestione(app):
    from gui.menu import menu_principale
    from core.logica import aggiorna_orologio
    for widget in app.root.winfo_children():
        widget.destroy()

    crea_header(app, app.logo_img, lambda lbl: setattr(app, 'orologio_label', lbl))
    aggiorna_orologio(app)  

    tk.Label(app.root, text="⚙️ Gestione", font=app.get_font("Symbola", 22, "bold")).pack(pady=int(10 * app.scala))

    frame = tk.Frame(app.root)
    frame.pack(pady=int(10 * app.scala))

    # Sezione: Gestione Cassa
    tk.Label(frame, text="💰 Gestione Cassa", font=app.get_font("Symbola", 16, "bold"),fg="darkgreen").grid(row=0, column=0, columnspan=2, pady=(int(0 * app.scala), int(10 * app.scala)))

    tk.Button(frame, text="📥 Imposta Fondo Cassa", command=lambda: imposta_fondo(app.root, app.conn),
    width=int(25 * app.scala), height=int(2 * app.scala), font=app.get_font("Symbola", 14), bg="khaki1").grid(row=1, column=0, padx=int(5 * app.scala), pady=int(5 * app.scala))
    tk.Button(frame, text="📊 Visualizza Registro Cassa", command=lambda: visualizza_registro_cassa(app.root, app.conn),
    width=int(25 * app.scala), height=int(2 * app.scala), font=app.get_font("Symbola", 14), bg="lightgreen").grid(row=1, column=1, padx=int(5 * app.scala), pady=int(5 * app.scala))

    # Sezione: Vendite e Azzeramenti
    tk.Label(frame, text="🧾 Vendite e Azzeramenti", font=app.get_font("Symbola", 16, "bold"), fg="darkred").grid(row=2, column=0, columnspan=2, pady=(int(20 * app.scala), int(10 * app.scala)))

    tk.Button(frame, text="📈 Visualizza Registro Vendite", command=lambda: visualizza_vendite(app.root, app.conn),
    width=int(25 * app.scala), height=int(2 * app.scala), font=app.get_font("Symbola", 14), bg="lightgreen").grid(row=3, column=0, padx=int(5 * app.scala), pady=int(5 * app.scala))
    tk.Button(frame, text="🗑️ Azzera Fondo Cassa", command=lambda: azzera_fondo(app.root, app.conn),
    width=int(25 * app.scala), height=int(2 * app.scala), font=app.get_font("Symbola", 14), bg="tomato").grid(row=3, column=1, padx=int(5 * app.scala), pady=int(5 * app.scala))

    tk.Button(frame, text="🗑️ Azzera Registro Cassa", command=lambda: azzera_incassi(app.root, app.conn),
    width=int(25 * app.scala), height=int(2 * app.scala), font=app.get_font("Symbola", 14), bg="tomato").grid(row=4, column=0, padx=int(5 * app.scala), pady=int(5 * app.scala))
    tk.Button(frame, text="🗑️ Azzera Registro Vendite", command=lambda: azzera_vendite(app.root, app.conn),
    width=int(25 * app.scala), height=int(2 * app.scala), font=app.get_font("Symbola", 14), bg="tomato").grid(row=4, column=1, padx=int(5 * app.scala), pady=int(5 * app.scala))

    # Sezione: Report
    tk.Label(frame, text="📊 Report", font=app.get_font("Symbola", 16, "bold"), fg="navy").grid(row=5, column=0, columnspan=2, pady=(int(20 * app.scala), int(10 * app.scala)))

    tk.Button(frame, text="📄 Report Giornaliero", command=lambda: genera_report(app, app.conn, app.stampa_abilitata, app.logo_path, app.sconti_giornalieri),
    width=int(25 * app.scala), height=int(2 * app.scala), font=app.get_font("Symbola", 14), bg="lightblue").grid(row=6, column=0, columnspan=2, pady=int(5 * app.scala))

    # Bottone Esci centrato
    tk.Button(app.root, text="⬅️ Esci", command=lambda: menu_principale(app),
    width=int(50 * app.scala), height=int(3 * app.scala), bg="gray", font=("Symbola", 14)).pack(pady=int(20 * app.scala))