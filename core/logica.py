from datetime import datetime

def aggiorna_orologio(app):
    adesso = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if hasattr(app, "orologio_label") and app.orologio_label.winfo_exists():
        app.orologio_label.config(text=adesso)
    app.root.after(1000, aggiorna_orologio, app)

def aggiungi_al_carrello(app, nome, prezzo):
    if not hasattr(app, 'carrello'):
        app.carrello = []
        app.totale = 0

    app.carrello.append({"nome": nome, "prezzo": prezzo, "nota": None})
    app.totale += prezzo
    aggiorna_scontrino(app)
    
def cancella_ultimo(app):
    if app.carrello:
        ultimo = app.carrello.pop()
        app.totale -= ultimo["prezzo"]
        if app.sconti > 0:
            app.totale += app.sconti
            app.sconti = 0.0
        aggiorna_scontrino(app)
        
def aggiorna_scontrino(app):
    app.scontrino_box.config(state="normal")
    app.scontrino_box.delete("1.0", "end")
    
    for voce in app.carrello:
        riga = f"{voce['nome']} - €{voce['prezzo']:.2f}"
        app.scontrino_box.insert("end", riga + "\n")
        if voce.get("nota"):
            app.scontrino_box.insert("end", "📝 Nota inserita\n")
    if app.sconti > 0:
        app.scontrino_box.insert("end", f"\nSconto -€{app.sconti:.2f}\n")
    app.scontrino_box.config(state="disabled")
    app.scontrino_box.see("end")
    if app.totale == 0 and app.carrello:
        app.scontrino_box.config(state="normal")
        app.scontrino_box.insert("end", "\n*** OMAGGIO ***\n")
        app.scontrino_box.config(state="disabled")
    if hasattr(app, "label_totale") and app.label_totale.winfo_exists():
        app.label_totale.config(text=f"Totale: €{app.totale:.2f}")
