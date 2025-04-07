import tkinter as tk
from tkinter import messagebox, Toplevel
from PIL import Image, ImageDraw
import os
from datetime import datetime

def finestra_sconto(app, aggiorna_scontrino):
    finestra = Toplevel(app.root)
    finestra.title("Inserisci importo dello sconto")
    # Centra la finestra sopra alla finestra principale
    base_larghezza = 400
    base_altezza = 500

    larghezza = int(base_larghezza * app.scala)
    altezza = int(base_altezza * app.scala)

    var_sconto = tk.StringVar()

    entry = tk.Entry(finestra, textvariable=var_sconto, font=app.get_font("Liberation Sans", 24), justify="center")
    entry.pack(pady=int(10 * app.scala))

    def aggiungi_cifra(cifra):
        if cifra == 'C':
            var_sconto.set("")
        else:
            var_sconto.set(var_sconto.get() + cifra)

    def conferma():
        try:
            val = float(var_sconto.get().replace(",", "."))
            if val <= 0:
                raise ValueError
        except:
            messagebox.showerror("Errore", "Importo non valido")
            return

        try:
            app.sconti += val
            app.totale -= val
            if hasattr(app, 'label_totale') and app.label_totale.winfo_exists():
                app.label_totale.config(text=f"Totale: €{app.totale:.2f}")
            if callable(aggiorna_scontrino):
                aggiorna_scontrino()
            finestra.destroy()
        except Exception as e:
            messagebox.showerror("Errore durante aggiornamento", str(e))

    # Tastierino
    tastierino = tk.Frame(finestra)
    tastierino.pack()

    tasti = [
        ('1', 1, 0), ('2', 1, 1), ('3', 1, 2),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
        ('7', 3, 0), ('8', 3, 1), ('9', 3, 2),
        (',', 4, 0), ('0', 4, 1), ('C', 4, 2)
    ]

    for txt, r, c in tasti:
        tk.Button(tastierino, text=txt, command=lambda t=txt: aggiungi_cifra(t),
                  width=int(5 * app.scala), height=int(2 * app.scala), font=app.get_font("Liberation Sans", 14)).grid(row=r, column=c, padx=int(2 * app.scala), pady=int(2 * app.scala))

    tk.Button(finestra, text="✅ Conferma", command=conferma,
              bg="green", fg="white", font=app.get_font("Symbola", 14)).pack(pady=int(10 * app.scala))
    tk.Button(finestra, text="❌ Annulla", command=finestra.destroy,
              bg="red", fg="black", font=app.get_font("Symbola",14)).pack(pady=int(10 * app.scala))
    
    finestra.withdraw()
    finestra.update_idletasks()
    schermo_x = finestra.winfo_screenwidth()
    schermo_y = finestra.winfo_screenheight()
    x = (schermo_x // 2) - (larghezza // 2)
    y = (schermo_y // 2) - (altezza // 2)
    finestra.geometry(f"{larghezza}x{altezza}+{x}+{y}")
    finestra.transient(app.root)
    finestra.deiconify()
    finestra.resizable(False,False)
    finestra.grab_set()
    finestra.focus_force()
    finestra.wait_window()

def finestra_nota(app):
    finestra = Toplevel(app.root)
    finestra.title("✍️ Inserisci Nota a Mano Libera")

    larghezza, altezza = 800, 600
    finestra.resizable(False, False)

    canvas = tk.Canvas(finestra, bg="white", width=larghezza, height=altezza)
    canvas.pack()

    image = Image.new("RGB", (larghezza, altezza), "white")
    draw = ImageDraw.Draw(image)

    last = {"x": None, "y": None}

    def set_start(event):
        last["x"], last["y"] = event.x, event.y

    def draw_line(event):
        x, y = event.x, event.y
        if last["x"] is not None and last["y"] is not None:
            canvas.create_line(last["x"], last["y"], x, y, fill="black", width=3)
            draw.line([last["x"], last["y"], x, y], fill="black", width=3)
        last["x"], last["y"] = x, y

    def cancella():
        canvas.delete("all")
        draw.rectangle([0, 0, larghezza, altezza], fill="white")

    def salva():
        os.makedirs("note", exist_ok=True)
        nome_file = f"nota_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join("note", nome_file)
        image.save(path)
        if app.carrello:
            app.carrello[-1]["nota"] = path
        from core.logica import aggiorna_scontrino
        aggiorna_scontrino(app)
        #messagebox.showinfo("Nota salvata", "Nota salvata", parent=finestra)
        finestra.destroy()

    def annulla():
        finestra.destroy()

    canvas.bind("<ButtonPress-1>", set_start)
    canvas.bind("<B1-Motion>", draw_line)

    # Pulsanti
    btn_frame = tk.Frame(finestra)
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="🧽 Cancella", command=cancella, width=10).pack(side="left", padx=5)
    tk.Button(btn_frame, text="💾 Salva", command=salva, width=10, bg="lightgreen").pack(side="left", padx=5)
    tk.Button(btn_frame, text="❌ Annulla", command=annulla, width=10).pack(side="left", padx=5)

    finestra.update_idletasks()
    schermo_x = finestra.winfo_screenwidth()
    schermo_y = finestra.winfo_screenheight()
    x = (schermo_x // 2) - (larghezza // 2)
    y = (schermo_y // 2) - (altezza // 2)
    finestra.geometry(f"{larghezza}x{altezza+50}+{x}+{y-50}")
    finestra.transient(app.root)
    finestra.grab_set_global()
    finestra.resizable(False, False)
    finestra.focus_set()
    finestra.wait_window()
