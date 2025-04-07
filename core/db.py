import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

def crea_tabella(conn):
    """Crea le tabelle nel database se non esistono."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scontrini (
            data TEXT,
            numero INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incassi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metodo TEXT,
            importo REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendite (
            prodotto TEXT PRIMARY KEY,
            quantita INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fondo_cassa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            importo REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sconti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            totale REAL
        )
    """)

    """Verifica se le voci esistono già nella tabella incassi"""
    cursor.execute("SELECT COUNT(*) FROM incassi WHERE metodo IN ('Contanti', 'Satispay', 'POS')")
    count = cursor.fetchone()[0]

    """Se non ci sono ancora, le aggiunge"""
    if count < 3:
        for metodo in ["Contanti", "Satispay", "POS"]:
            cursor.execute("INSERT OR IGNORE INTO incassi (metodo, importo) VALUES (?, 0)", (metodo,))
    
    conn.commit()

def aggiorna_sconti(conn, importo):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sconti (totale) VALUES (?)", (importo,))
    conn.commit()

def aggiorna_registro_cassa(conn, metodo, importo):
    """Aggiorna il totale dell'importo per il metodo di pagamento specificato."""
    cursor = conn.cursor()
    cursor.execute("UPDATE incassi SET importo = importo + ? WHERE metodo = ?", (importo, metodo))
    conn.commit()
    
def visualizza_registro_cassa(root, conn):
    """Mostra il totale degli incassi suddivisi per metodo di pagamento."""
    cursor = conn.cursor()
    cursor.execute("SELECT metodo, importo FROM incassi")
    incassi = cursor.fetchall()
    """Recupera il fondo cassa (se esiste)"""
    cursor.execute("SELECT importo FROM fondo_cassa ORDER BY id DESC LIMIT 1")
    fondo = cursor.fetchone()
    fondo_importo = fondo[0] if fondo else 0.00

    testo = "\n".join([f"{metodo}: €{importo:.2f}" for metodo, importo in incassi]) if incassi else "Nessuna transazione registrata."
    """Aggiunge il fondo cassa"""
    testo += f"\nFONDO: €{fondo_importo:.2f}"
    messagebox.showinfo("Registro Cassa", testo, parent=root)

def imposta_fondo(root, conn):
    """Imposta il fondo cassa."""
    finestra = tk.Toplevel(root)
    finestra.title("Imposta Fondo Cassa")

    larghezza, altezza = 300, 400
    x = root.winfo_rootx() + (root.winfo_width() // 2) - (larghezza // 2)
    y = root.winfo_rooty() + (root.winfo_height() // 2) - (altezza // 2)
    finestra.geometry(f"{larghezza}x{altezza}+{x}+{y}")
    finestra.transient(root)
    finestra.grab_set()
    finestra.focus_force()

    valore_var = tk.StringVar()

    # Display
    display = tk.Entry(finestra, textvariable=valore_var, font=("Liberation Sans", 24), justify="center", state="readonly")
    display.pack(pady=10, ipadx=5, ipady=5)

    # Tastierino
    tastierino = tk.Frame(finestra)
    tastierino.pack()

    def aggiungi(cifra):
        if cifra == '⌫':
            valore_var.set(valore_var.get()[:-1])
        else:
            valore_var.set(valore_var.get() + cifra)

    tasti = [
        ('1', 1, 0), ('2', 1, 1), ('3', 1, 2),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
        ('7', 3, 0), ('8', 3, 1), ('9', 3, 2),
        (',', 4, 0), ('0', 4, 1), ('⌫', 4, 2)
    ]

    for txt, r, c in tasti:
        tk.Button(
            tastierino, text=txt, command=lambda t=txt: aggiungi(t),
            width=5, height=2, font=("Liberation Sans", 14)
        ).grid(row=r, column=c, padx=2, pady=2)

    # Pulsanti Azione
    def conferma():
        try:
            valore = float(valore_var.get().replace(',', '.'))
            if valore <= 0:
                raise ValueError
            cursor = conn.cursor()
            cursor.execute("INSERT INTO fondo_cassa (importo) VALUES (?)", (valore,))
            conn.commit()
            messagebox.showinfo("Fondo Cassa", f"Fondo cassa impostato a € {valore:.2f}")
            finestra.destroy()
        except ValueError:
            messagebox.showerror("Errore", "Importo non valido")

    def annulla():
        finestra.destroy()

    btn_frame = tk.Frame(finestra)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="✅ Conferma", command=conferma, width=12, bg="green", fg="white", font=("Symbola", 12)).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="❌ Annulla", command=annulla, width=12, bg="gray", font=("Symbola", 12)).grid(row=0, column=1, padx=5)
        
def azzera_fondo(root, conn):
    if messagebox.askyesno("Conferma", "Sei sicuro di voler azzerare il fondo cassa?", parent=root):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fondo_cassa")
        conn.commit()
        messagebox.showinfo("Fondo Cassa", "Fondo cassa azzerato.", parent=root)

def azzera_incassi(root, conn):
    if messagebox.askyesno("Conferma", "Sei sicuro di voler azzerare gli incassi?", parent=root):
        cursor = conn.cursor()
        cursor.execute("UPDATE incassi SET importo = 0")
        cursor.execute("DELETE FROM sconti")
        conn.commit()
        messagebox.showinfo("Incassi", "Registro incassi e sconti azzerato.", parent=root)

def azzera_vendite(root, conn):
    if messagebox.askyesno("Conferma", "Sei sicuro di voler azzerare le vendite?", parent=root):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vendite")
        conn.commit()
        messagebox.showinfo("Vendite", "Storico vendite azzerato.")
        
def visualizza_vendite(root, conn):
    """Visualizza lo storico delle comande."""
    cursor = conn.cursor()
    cursor.execute("SELECT prodotto, SUM(quantita) FROM vendite GROUP BY prodotto")
    comande = cursor.fetchall()
    
    testo = "\n".join([f"{prodotto}: {quantita} pezzi" for prodotto, quantita in comande]) if comande else "Nessuna vendita registrata."
    messagebox.showinfo("Storico Vendite", testo, parent=root)

def prossimo_numero_scontrino(conn):
    oggi = datetime.now().strftime("%Y-%m-%d")
    cursor = conn.cursor()

    cursor.execute("SELECT numero FROM scontrini WHERE data = ?", (oggi,))
    row = cursor.fetchone()

    if row:
        numero = row[0] + 1
        cursor.execute("UPDATE scontrini SET numero = ? WHERE data = ?", (numero, oggi))
    else:
        numero = 1
        cursor.execute("INSERT INTO scontrini (data, numero) VALUES (?, ?)", (oggi, numero))

    conn.commit()
    return numero
