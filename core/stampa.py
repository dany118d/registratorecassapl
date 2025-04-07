from platform import system
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def normalizza_accenti(testo):
    sostituzioni = {
        "à": "a", "è": "e", "é": "e", "ì": "i", "ò": "o", "ù": "u",
        "À": "A", "È": "E", "É": "E", "Ì": "I", "Ò": "O", "Ù": "U"
    }
    for originale, sostituto in sostituzioni.items():
        testo = testo.replace(originale, sostituto)
    return testo

def stampa_windows(testo, path_immagine=None):
    if platform.system() == "Windows":
        import win32print
        import win32ui
        import os
        import win32con
        from PIL import Image
        printer_name = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(printer_name)
        printer_info = win32print.GetPrinter(hprinter, 2)
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(printer_name)
        hdc.StartDoc("Scontrino")
        hdc.StartPage()

        font = win32ui.CreateFont({
            "name": "Courier New",
            "height": 100,
            "weight": 400,
        })
        hdc.SelectObject(font)

        x, y = 100, 100
        for line in testo.splitlines():
            hdc.TextOut(x, y, line)
            y += 120  # Vai alla riga successiva
         # Se presente un'immagine, la stampa
        if path_immagine and os.path.exists(path_immagine):
            try:
                img = Image.open(path_immagine).convert("RGB")
                img = img.resize((400, 200))  # Adatta la dimensione
                dib = win32ui.CreateBitmap()
                dib.CreateCompatibleBitmap(hdc, img.width, img.height)

                # Inserisce i pixel dell'immagine
                hdc_mem = hdc.CreateCompatibleDC()
                hdc_mem.SelectObject(dib)

                bmpinfo = img.tobytes("raw", "BGRX")
                dib.SetBitmapBits(bmpinfo)

                hdc.StretchBlt(x, y + 50, img.width, img.height, hdc_mem, 0, 0, img.width, img.height, win32con.SRCCOPY)
                hdc_mem.DeleteDC()
            except Exception as e:
                print("Errore nella stampa dell'immagine:", e)
        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()
    else:
        print("Simulazione stampa su Raspberry:")
        print(testo)

def stampa_termica(testo, printer=None):
    from escpos.printer import File
    try:
        p = printer if printer else File("/dev/usb/lp0")
        #p = File("/dev/usb/lp0")
        p.charcode = 'PC437'
        # Stampa del logo residente (memorizzato in NVM slot 1)
        p._raw(b"\x1b\x61\x01")      # ESC a 1: align center
        p._raw(b"\x1c\x70\x01\x00")  # ESC/POS: FS p m n
        # Riga vuota dopo il logo
        p.text("\n")
        p.set(align='center', width=2, height=5, bold=True)
        p.text("Via G. Mazzini 35\n")
        p.text("10010 Caravino (TO)\n")
        p.text("P.IVA 13166420011\n")
        p.text("C.F. 93054120014\n")
        # Stampa del contenuto testuale formattato
        p.set(align='left', width=1, height=1, bold=False)
        for riga in testo.splitlines():
            p.text(normalizza_accenti(riga) + "\n")
        # Apertura cassetto
        p.cashdraw(2)
        # Taglio
        p.cut()
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Errore stampa", f"Stampa termica fallita:\n{e}")

def stampa_tagliandino(voce, p):
    from escpos.printer import File
    from PIL import Image
    import os
    import time
    import re
    try:
        #p = File("/dev/usb/lp0")
        p.charcode = 'PC437'
        nome_pulito = re.sub(r"[^\w\s]", "", voce["nome"]).strip().lower().replace(" ", "_")
        percorso_img = os.path.join(BASE_DIR, "assets", "tagliandini", f"{nome_pulito}.png")
        if os.path.isfile(percorso_img):
            print(percorso_img)
            img = Image.open(percorso_img)
            larghezzamax = 576
            if img.width > larghezzamax:
                rapporto = larghezzamax / img.width
                nuovaaltezza = int(img.height * rapporto)
                img = img.resize((larghezzamax, nuovaaltezza), Image.LANCZOS)
            p.image(img)
        else:
            print(percorso_img)
            # Fallback: stampa solo il nome come testo grande
            p.set(align='center', width=2, height=6, bold=True)
            p.text("COMANDA\n")
            p.text(voce["nome"].upper() + "\n")
        # Se c'è una nota immagine, stampala
        if voce.get("nota") and os.path.isfile(voce["nota"]):
            try:
                img = Image.open(voce["nota"]).convert("RGB")
                img = img.resize((576, 240), Image.LANCZOS)
                img = img.convert("1")  # converte in bianco e nero per compatibilità escpos
                p.image(img)
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Errore stampa", f"Errore nella stampa dell'immagine:\n{e}")

        # Taglio alla fine del tagliandino
        p.cut()
        time.sleep(0.5)
        #p.close()
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Errore stampa", f"Stampa tagliandino fallita:\n{e}")
