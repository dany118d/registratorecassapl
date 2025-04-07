import os
import csv
import re
from datetime import datetime
from tkinter import messagebox, Toplevel, Text, Scrollbar, RIGHT, Y, BOTH, END, Button
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from core.stampa import stampa_windows, stampa_termica
from core.prodotti import carica_prodotti
import sys
from platform import system

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

def genera_report(app, conn, stampa_abilitata, logo_path, _):
    prodotti = carica_prodotti()
    cursor = conn.cursor()

    # Dati base
    oggi = datetime.now().strftime("%Y-%m-%d")
    report_dir = "report"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"report_{oggi}.csv")

    # Recupero dati
    cursor.execute("SELECT metodo, importo FROM incassi")
    incassi = cursor.fetchall()

    cursor.execute("SELECT importo FROM fondo_cassa ORDER BY id DESC LIMIT 1")
    fondo_row = cursor.fetchone()
    fondo = fondo_row[0] if fondo_row else 0.00

    cursor.execute("SELECT prodotto, quantita FROM vendite")
    vendite = cursor.fetchall()

    cursor.execute("SELECT SUM (totale) FROM sconti")
    ris = cursor.fetchone()
    sconti_giornalieri = ris[0] if ris[0] is not None else 0.0

    # Preparazione contenuto
    testo = f"\n\nReport Giornaliero - {oggi}\n\n"
    testo += "---------------- INCASSI --------------------\n"
    totale_incassi = 0.0
    for metodo, importo in incassi:
        testo += f"{metodo:<13}: € {importo:.2f}\n"
        totale_incassi += importo
    testo += f"FONDO CASSA  : € {fondo:.2f}\n"
    testo += f"\nTotale Incassato: Euro {totale_incassi:.2f}\n"
    testo += "---------------------------------------------\n"
    testo += "\n--------------- VENDITE ---------------------\n"
    testo += f"{'Prodotto':<22}{'Prezzo':>6}{'Qtà':>4}{'Tot':>8}\n"
    testo += "-" * 45 + "\n"
    totale_vendite = 0.0
    totale_pezzi = 0
    prodotti_puliti = {re.sub(r'^[^\w\s]', '', k).strip(): v for k, v in prodotti.items()}
    for prodotto, quantita in vendite:
        prodotto_clean = re.sub(r'^[^\w\s]', '', prodotto).strip()
        #print(f"Prodotto: {prodotto_clean}, Prezzo: {prodotti.get(prodotto_clean, 'Non trovato')}")
        prezzo_unitario = prodotti_puliti.get(prodotto_clean, 0.0)
        #print(f"Prodotto: {prodotto_clean}, Prezzo unitario: {prezzo_unitario}")
        totale_prodotto = prezzo_unitario * quantita
        totale_vendite += totale_prodotto
        totale_pezzi += quantita
        testo += f"{prodotto:<22}€ {prezzo_unitario:>6.2f}{quantita:>4}{totale_prodotto:>8.2f}\n"
    testo += "-" * 45 + "\n"
    #testo += f"{'Totale pezzi':<27}{totale_pezzi:>4}{'':5}{totale_vendite:>8.2f}\n"
    testo += f"{'Totale pezzi':<22}{totale_pezzi:>4}{'  Euro':>10}{totale_vendite:>12.2f}\n"
    #testo += "\nTotale Vendite (lordo):{:>5} pezzi   € {:>.2f}".format(totale_pezzi, totale_vendite)
    if sconti_giornalieri > 0:
        testo += "-" * 45 + "\n"
        testo += f"{'Sconti Totali Applicati':<36}{sconti_giornalieri:>8.2f}\n"

    # Salvataggio CSV 
    #with open(report_path, "w", newline="", encoding="utf-8") as f:
    #    writer = csv.writer(f)
    #    writer.writerow(["Report Giornaliero", oggi])
    #    writer.writerow([])
    #    writer.writerow(["Metodo", "Importo"])
    #    for metodo, importo in incassi:
    #        writer.writerow([metodo, f"{importo:.2f}"])
    #    writer.writerow(["Fondo Cassa", f"{fondo:.2f}"])
    #    writer.writerow(["Totale Incassato", f"{totale_incassi:.2f}"])
    #    writer.writerow([])
    #    writer.writerow(["Prodotto", "Prezzo Unitario", "Quantità", "Totale Prodotto"])
    #    for prodotto, quantita in vendite:
    #        prezzo_unitario = prodotti.get(prodotto, 0.0)
    #        totale_prodotto = prezzo_unitario * quantita
    #        writer.writerow([prodotto, f"{prezzo_unitario:.2f}", quantita, f"{totale_prodotto:.2f}"])
    #    writer.writerow(["Totale Vendite", "", totale_pezzi, f"{totale_vendite:.2f}"])
    #    if sconti_giornalieri > 0:
    #        writer.writerow(["Sconti Totali", "", "", f"{sconti_giornalieri:.2f}"])

    # Visualizzazione in finestra con opzioni
    finestra = Toplevel(app.root)
    finestra.transient(app.root)    # Si comporta come finestra figlia
    finestra.grab_set()              # Rende modale (blocca interazione con il resto)
    finestra.focus_force()           # Forza il focus su di lei
    finestra.title("Report Giornaliero")
    base_width, base_height = 600, 700
    larghezza = int(base_width * app.scala)
    altezza = int(base_height * app.scala)

    x = (finestra.winfo_screenwidth() - larghezza) // 2
    y = (finestra.winfo_screenheight() - altezza) // 2
    finestra.geometry(f"{larghezza}x{altezza}+{x}+{y}")

    scrollbar = Scrollbar(finestra)
    scrollbar.pack(side=RIGHT, fill=Y)

    text_widget = Text(finestra, wrap="word", yscrollcommand=scrollbar.set,
                  font=app.get_font("Liberation Mono", 11))
    text_widget.insert(END, testo)
    text_widget.pack(expand=True, fill=BOTH)

    scrollbar.config(command=text_widget.yview)

    def azzera():
        conferma = messagebox.askyesno("Conferma", "Vuoi azzerare il registro cassa e le vendite?")
        if conferma:
            cursor.execute("UPDATE incassi SET importo = 0")
            cursor.execute("DELETE FROM vendite")
            cursor.execute("DELETE FROM sconti")
            conn.commit()
            sconti_giornalieri = 0.0  # ✅ Azzera anche gli sconti
            messagebox.showinfo("Completato", "Dati azzerati con successo.")
            finestra.destroy()

    def stampa():
        if not stampa_abilitata.get():
            messagebox.showinfo("Stampa", "Stampa non abilitata")
        else:
            if system() == "Windows":
                try:
                    messagebox.showinfo("Stampa","Stampa in corso...")
                    stampa_windows(testo)
                except Exception as e:
                    messagebox.showerror("Errore Stampa", str(e))
            else:
                try:
                    from escpos.printer import File
                    p = File("/dev/usb/lp0")
                    try:
                        stampa_termica(testo, printer=p)
                    finally:
                        p.close()
                except Exception as e:
                    messagebox.showerror("Errore Stampa", str(e))

    def esci():
        finestra.destroy()

    def esporta_pdf():
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader

        pdf_path = os.path.join(report_dir, f"report_{oggi}.pdf")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        # Inserisce il logo se esiste
        logo_path = resource_path(os.path.join("assets", "LogoUfficiale.jpg"))
        if logo_path:
            try:
                logo = ImageReader(logo_path)
                c.drawImage(logo, 40, height - 80, width=80, height=60)  # Posizione e dimensione
            except Exception as e:
                print(f"Errore nel caricare il logo per il PDF: {e}")

        # Titolo (a destra del logo)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(130, height - 50, f"Report Giornaliero - {oggi}")

        # Contenuto
        c.setFont("Helvetica", 10)
        lines = testo.split("\n")
        y = height - 100
        for line in lines:
            c.drawString(40, y, line)
            y -= 14
            if y < 40:
                c.showPage()
                y = height - 50

        c.save()
        messagebox.showinfo("PDF Creato", f"Il report è stato salvato come:\n{pdf_path}")

    from tkinter import Button
    Button(finestra, text="Stampa", command=stampa, width=int(20 * app.scala),
       font=app.get_font("Symbola", 12), bg="lightblue").pack(pady=int(5 * app.scala))

    Button(finestra, text="📄 Esporta in PDF", command=esporta_pdf, width=int(20 * app.scala),
           font=app.get_font("Symbola", 12)).pack(pady=int(5 * app.scala))

    Button(finestra, text="Azzera Dati", command=azzera, width=int(20 * app.scala),
           font=app.get_font("Symbola", 12), bg="tomato").pack(pady=int(5 * app.scala))

    Button(finestra, text="Esci", command=esci, width=int(20 * app.scala),
           font=app.get_font("Symbola", 12), bg="gray").pack(pady=int(5 * app.scala))
