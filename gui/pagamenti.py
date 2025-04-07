import tkinter as tk
from gui.layout import crea_header
from core.db import aggiorna_registro_cassa
from platform import system
from datetime import datetime
from tkinter import messagebox, simpledialog, Toplevel, Text, Scrollbar, RIGHT, Y, BOTH, END
from core.stampa import stampa_termica, stampa_windows, stampa_tagliandino

def menu_pagamento(app):
    from core.logica import aggiorna_orologio
    from gui.cassa import menu_cassa
    for widget in app.root.winfo_children():
        widget.destroy()

    crea_header(app, app.logo_img, lambda lbl: setattr(app, 'orologio_label', lbl))
    aggiorna_orologio(app)
    
    tk.Label(app.root, text="💳 Modalità di Pagamento", font=app.get_font("Symbola", 22, "bold")).pack(pady=int(10 * app.scala))

    app.label_totale = tk.Label(app.root, text=f"Totale: €{app.totale:.2f}", font=app.get_font("Liberation Sans", 18, "bold"))
    app.label_totale.pack(pady=int(10 * app.scala))

    tk.Button(app.root, text="💵 Contanti", command=lambda: menu_contanti(app),
              width=int(25 * app.scala), height=int(3 * app.scala), bg="yellow", font=app.get_font("Symbola", 16, "bold")).pack(pady=int(5 * app.scala))

    tk.Button(app.root, text="📱 Satispay", command=lambda: conferma_pagamento(app, "Satispay"),
              width=int(25 * app.scala), height=int(3 * app.scala), bg="red", fg="white", font=app.get_font("Symbola", 16, "bold")).pack(pady=int(5 * app.scala))

    tk.Button(app.root, text="🏧 POS", command=lambda: conferma_pagamento(app, "POS"),
              width=int(25 * app.scala), height=int(3 * app.scala), bg="green", fg="white", font=app.get_font("Symbola", 16, "bold")).pack(pady=int(5 * app.scala))

    tk.Button(app.root, text="⬅️ Indietro", command=lambda: menu_cassa(app),
              width=int(25 * app.scala), height=int(3 * app.scala), bg="gray", font=app.get_font("Symbola", 16, "bold")).pack(pady=int(10 * app.scala))
              
def menu_contanti(app):
    from core.logica import aggiorna_orologio
    for widget in app.root.winfo_children():
        widget.destroy()

    crea_header(app, app.logo_img, lambda lbl: setattr(app, 'orologio_label', lbl))
    aggiorna_orologio(app)
    
    app.importo_var.set("")
    app.resto_var.set("Resto: €0.00")
    tk.Label(app.root, text="💵 Pagamento in Contanti", font=app.get_font("Symbola", 20, "bold"), fg="darkgreen").pack(pady=int(10 * app.scala))

    # Totale
    frame_totale = tk.Frame(app.root)
    frame_totale.pack(pady=int(2 * app.scala))
    tk.Label(frame_totale, text="Totale da pagare:", font=app.get_font("Liberation Sans", 14)).pack()
    app.label_totale = tk.Label(frame_totale, text=f"€ {app.totale:.2f}", font=app.get_font("Liberation Sans", 20, "bold"), fg="blue")
    app.label_totale.pack()

    # Inserimento importo
    entry_frame = tk.Frame(app.root)
    entry_frame.pack(pady=int(5 * app.scala))
    tk.Label(entry_frame, text="Importo ricevuto:", font=app.get_font("Liberation Sans", 14)).pack()
    entry = tk.Entry(entry_frame, textvariable=app.importo_var, font=app.get_font("Liberation Sans", 18), width=int(10 * app.scala), justify='center')
    entry.pack()
    app.importo_var.trace_add("write", lambda *args: calcola_resto(app))
    tk.Label(entry_frame, textvariable=app.resto_var, font=app.get_font("Liberation Sans", 14, "bold"), fg="darkred").pack(pady=int(3 * app.scala))

    # Tastierino
    tastierino_frame = tk.LabelFrame(app.root, text="Tastierino", font=app.get_font("Liberation Sans", 12, "bold"))
    tastierino_frame.pack(pady=int(5 * app.scala))

    buttons = [
        ('1', 1, 0), ('2', 1, 1), ('3', 1, 2),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
        ('7', 3, 0), ('8', 3, 1), ('9', 3, 2),
        (',', 4, 0), ('0', 4, 1), ('C', 4, 2)
    ]

    for (text, row, col) in buttons:
        tk.Button(tastierino_frame, text=text, command=lambda t=text: aggiungi_importo(app, t),
                  width=int(5 * app.scala), height=int(2 * app.scala), font=app.get_font("Liberation Sans", 14), bg="lightblue").grid(row=row, column=col, padx=int(3 * app.scala), pady=int(3 * app.scala))

    # Pulsanti azione
    tk.Button(app.root, text="✅ Conferma Pagamento", command=lambda: conferma_pagamento_contanti(app, "Contanti"),
              width=int(25 * app.scala), height=int(2 * app.scala), bg="green", fg="white", font=app.get_font("Symbola", 14, "bold")).pack(pady=int(5 * app.scala))

    tk.Button(app.root, text="⬅️ Indietro", command=lambda: menu_pagamento(app),
              width=int(25 * app.scala), height=int(2 * app.scala), bg="gray", fg="white", font=app.get_font("Symbola", 14)).pack(pady=int(5 * app.scala))
              
def conferma_pagamento(app, metodo):
        from gui.cassa import menu_cassa
        """Registra la transazione nel database e svuota il carrello."""
        if not app.carrello:
            messagebox.showinfo("Errore", "Nessun prodotto selezionato!")
            return

        cursor = app.conn.cursor()
        
        """Registra la transazione"""
        aggiorna_registro_cassa(app.conn, metodo, app.totale)

        """Registra le comande"""
        for voce in app.carrello:
            cursor.execute("""
            INSERT INTO vendite (prodotto, quantita)
            VALUES (?, 1)
            ON CONFLICT(prodotto) DO UPDATE SET quantita = quantita + 1
            """, (voce["nome"],))
        
        app.conn.commit()
        testo = ""
        testo += "-" * 45 + "\n"
        testo += f"{'DESCRIZIONE':<35}{'TOT':>10}\n"
        testo += "-" * 45 + "\n"
        totale_teorico = 0

        scritti = set()
        for voce in app.carrello:
            nome = voce["nome"]
            prezzo = voce["prezzo"]
            if nome not in scritti:
                count = sum(1 for v in app.carrello if v["nome"] == nome)
                riga = f"{nome} x{count}"
                tot = f"€{prezzo * count:.2f}"
                testo += f"{riga:<35}{tot:>10}\n"
                scritti.add(nome)
        testo += "-" * 45 + "\n"
        # 💸 Calcolo e stampa eventuale sconto
        totale_teorico = 0
        scritti = set()
        for voce in app.carrello:
            nome = voce["nome"]
            prezzo = voce["prezzo"]
            if nome not in scritti:
                count = sum(1 for v in app.carrello if v["nome"] == nome)
                totale_teorico += prezzo * count
                scritti.add(nome)

        sconto = round(totale_teorico - app.totale, 2)
        if sconto > 0:
            testo += f"{'SCONTO':<35}{f'-€{sconto:.2f}':>10}\n"

        # ✅ Totale finale
        if app.totale == 0 and app.carrello:
            testo += "*** OMAGGIO ***\n"
        else:
            testo += "-" * 45 + "\n"
            testo += f"{'TOTALE':<35}{f'€{app.totale:.2f}':>10}\n"
            testo += f"{'PAGAMENTO':<35}{metodo:>10}\n"

        testo += "-" * 45 + "\n"
        from core.db import prossimo_numero_scontrino
        numero_scontrino = prossimo_numero_scontrino(app.conn)
        adesso = datetime.now()
        testo += f"Scontrino n. {numero_scontrino} del {adesso.strftime('%d/%m/%Y')} - ore {adesso.strftime('%H:%M:%S')}\n"
        testo += "NON FISCALE\n"
        testo += "Grazie per averci scelto! Seguici sui social:\n"
        testo += "prolococaravino.masino\n"
        if not app.stampa_abilitata.get():
            skippa = 1
        else:
            popup = tk.Toplevel(app.root)
            popup.title("Stampa in corso")
            popup.geometry("300x100")
            popup_label = tk.Label(popup, text="🖨️ Attendere stampa...", font=app.get_font("Symbola", 14))
            popup_label.pack(expand=True, fill="both", pady=20)
            popup.transient(app.root)
            popup.grab_set()
            popup.update()
            try:
                if system() == "Windows":
                    stampa_windows(testo)
                else:
                    from escpos.printer import File
                    p = None
                    try:
                        p = File("/dev/usb/lp0")
                        if app.stampa_tagliandini.get():
                            for voce in app.carrello:
                                stampa_tagliandino(voce, p)
                        stampa_termica(testo, printer=p)
                    except Exception as e:
                        messagebox.showerror("Errore Stampa", str(e), parent=popup)
                    finally:
                        try:
                            if p:
                                p.close()
                        except:
                            pass
            finally:
                popup.destroy()
                app.totale = 0
        from core.db import aggiorna_sconti
        aggiorna_sconti(app.conn, app.sconti)
        app.sconti = 0.0
        app.carrello.clear()
        for voce in app.carrello:
            voce["nota"] = None
        if hasattr(app, "scontrino_box") and app.scontrino_box.winfo_exists():
            app.scontrino_box.config(state="normal")
            app.scontrino_box.delete("1.0", "end")
            app.scontrino_box.config(state="disabled")
        menu_cassa(app)

def conferma_pagamento_contanti(app, metodo):
    from gui.cassa import menu_cassa
    try:
        importo_ricevuto = float(app.importo_var.get().replace(',', '.'))
        resto = importo_ricevuto - app.totale
        if resto < 0:
            messagebox.showinfo("Pagamento", "Importo insufficiente!")
            return
        """Registra la transazione nel database e svuota il carrello"""
        if not app.carrello:
            messagebox.showinfo("Errore", "Nessun prodotto selezionato!")
            return

        cursor = app.conn.cursor()
    
        """Registra la transazione"""
        aggiorna_registro_cassa(app.conn, metodo, app.totale)

        """Registra le comande"""
        for voce in app.carrello:
            cursor.execute("""
                INSERT INTO vendite (prodotto, quantita)
                VALUES (?, 1)
                ON CONFLICT(prodotto) DO UPDATE SET quantita = quantita + 1
            """, (voce["nome"],))
    
        app.conn.commit()
        testo = ""
        testo += "-" * 45 + "\n"

        scritti = set()
        for voce in app.carrello:
            nome = voce["nome"]
            prezzo = voce["prezzo"]
            if nome not in scritti:
                count = sum(1 for v in app.carrello if v["nome"] == nome)
                riga = f"{nome} x{count}"
                tot = f"€{prezzo * count:.2f}"
                testo += f"{riga:<35}{tot:>10}\n"
                scritti.add(nome)

        testo += "-" * 45 + "\n"

        # 💸 Calcolo e stampa eventuale sconto
        totale_teorico = 0
        scritti = set()
        for voce in app.carrello:
            nome = voce["nome"]
            prezzo = voce["prezzo"]
            if nome not in scritti:
                count = sum(1 for v in app.carrello if v["nome"] == nome)
                totale_teorico += prezzo * count
                scritti.add(nome)

        sconto = round(totale_teorico - app.totale, 2)
        if sconto > 0:
            testo += f"{'SCONTO':<35}{f'-€{sconto:.2f}':>10}\n"

        # ✅ Totale finale
        if app.totale == 0 and app.carrello:
            testo += "*** OMAGGIO ***\n"
        else:
            testo += f"{'TOTALE':<35}{f'€{app.totale:.2f}':>10}\n"
            testo += f"{'CONTANTI':<35}{f'€{importo_ricevuto:.2f}':>10}\n"
            testo += f"{'RESTO':<35}{f'€{resto:.2f}':>10}\n"
        testo += "-" * 45 + "\n"
        from core.db import prossimo_numero_scontrino
        numero_scontrino = prossimo_numero_scontrino(app.conn)
        numero_scontrino = prossimo_numero_scontrino(app.conn)
        adesso = datetime.now()
        testo += f"Scontrino n. {numero_scontrino} del {adesso.strftime('%d/%m/%Y')} - ore {adesso.strftime('%H:%M:%S')}\n"
        testo += "NON FISCALE\n"
        testo += "Grazie per averci scelto! Seguici sui social:\n"
        testo += "prolococaravino.masino\n"
        if not app.stampa_abilitata.get():
            skippa = 1
        else:
            popup = tk.Toplevel(app.root)
            popup.title("Stampa in corso")
            popup.geometry("300x100")
            popup_label = tk.Label(popup, text="🖨️ Attendere stampa...", font=app.get_font("Symbola", 14))
            popup_label.pack(expand=True, fill="both", pady=20)
            popup.transient(app.root)
            popup.grab_set()
            popup.update()
            try:
                if system() == "Windows":
                    stampa_windows(testo, getattr(app, 'nota_immagine_path', None))
                else:
                    from escpos.printer import File
                    p = File("/dev/usb/lp0")
                    try:
                        if app.stampa_tagliandini.get():
                            for voce in app.carrello:
                                stampa_tagliandino(voce, p)
                        stampa_termica(testo, printer=p)
                    except Exception as e:
                        messagebox.showerror("Errore Stampa", str(e), parent=popup)
                    finally:
                        try:
                            p.close()
                        except:
                            pass
            finally:
                popup.destroy()
                app.totale = 0
        if app.abilita_cassetto_rele.get():
            from core.cassetto import setup_rele, apri_cassetto, pulisci
            setup_rele()
            apri_cassetto()
            pulisci()
        from core.db import aggiorna_sconti
        aggiorna_sconti(app.conn, app.sconti)
        app.sconti = 0.0
        for voce in app.carrello:
            voce["nota"] = None
        app.carrello.clear()
        app.importo_var.set("")
        app.resto_var.set("Resto: €0.00")
        if hasattr(app, "scontrino_box") and app.scontrino_box.winfo_exists():
            app.scontrino_box.config(state="normal")
            app.scontrino_box.delete("1.0", "end")
            app.scontrino_box.config(state="disabled")
        menu_cassa(app)
    except ValueError:
        messagebox.showinfo("Errore", "Importo non valido!")

def aggiungi_importo(app, cifra):
    if cifra == 'C':
        app.importo_var.set("")
    else:
        app.importo_var.set(app.importo_var.get() + cifra)
   
def calcola_resto(app, *args):
    try:
        importo_ricevuto = float(app.importo_var.get().replace(',', '.'))
        resto = importo_ricevuto - app.totale
        if resto < 0:
            app.resto_var.set("Importo insufficiente!")
        else:
            app.resto_var.set(f"Resto: €{resto:.2f}")
    except ValueError:
        app.resto_var.set("Errore nell'importo!")
