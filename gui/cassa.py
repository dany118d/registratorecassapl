import tkinter as tk
import re
from gui.layout import crea_header

def menu_cassa(app):
    from gui.menu import menu_principale
    from gui.pagamenti import menu_pagamento
    from gui.finestre import finestra_sconto
    from core.logica import aggiorna_orologio
    from core.logica import aggiungi_al_carrello
    from core.logica import cancella_ultimo
    from core.logica import aggiorna_scontrino
    from gui.finestre import finestra_nota
    root = app.root
    for widget in root.winfo_children():
        widget.destroy()
    app.sconti = 0.0
    app.totale = sum(voce["prezzo"] for voce in app.carrello)
    if not hasattr(app, 'pagina_corrente'):
        app.pagina_corrente = 0

    crea_header(app, app.logo_img, lambda lbl: setattr(app, 'orologio_label', lbl))
    aggiorna_orologio(app)    
    
    if not app.stampa_abilitata.get():
        tk.Label(root, text="⚠️ Attenzione! Stampa non abilitata!", fg="red", font=app.get_font("Symbola", 12, "bold")).pack()
    tk.Label(root, text="🛒 Cassa", font=app.get_font("Symbola", 20, "bold")).pack(pady=int(5 * app.scala))

    main_frame = tk.Frame(root)
    main_frame.pack(expand=True, fill="both", padx=int(10 * app.scala), pady=int(10 * app.scala))

    frame_prodotti = tk.Frame(main_frame)
    frame_prodotti.pack(side="left", expand=True, fill="both")

    prodotti = list(app.prodotti.items())
    #print("Prodotti Caricati: ", prodotti)
    if app.menu_impaginato.get():  # modalità a pagine
        per_pagina = 10
        pag = app.pagina_corrente
        totale_pagine = (len(prodotti) + per_pagina - 1) // per_pagina
        prodotti_visibili = prodotti[pag * per_pagina : (pag + 1) * per_pagina]

        # Imposta 5 righe per prodotti + 1 fissa per i bottoni di navigazione
        for i in range(6):
            frame_prodotti.grid_rowconfigure(i, weight=1)
        for j in range(2):
            frame_prodotti.grid_columnconfigure(j, weight=1, uniform="nav")

        for idx in range(10):
            riga = idx % 5
            colonna = idx // 5
            if idx < len(prodotti_visibili):
                nome, prezzo = prodotti_visibili[idx]
                display_nome = re.sub(r'^[^\w\s]', '', nome).strip()
                btn = tk.Button(
                    frame_prodotti, text=nome,
                    command=lambda n=display_nome, p=prezzo: aggiungi_al_carrello(app, n, p),
                    font=app.get_font("Symbola", 12),
                    wraplength=int(180 * app.scala),
                    width=int(16 * app.scala), height=int(2 * app.scala), bg="white"
                )
                btn.grid(row=riga, column=colonna, padx=int(5 * app.scala), pady=int(5 * app.scala), sticky="nsew")
            else:
                # Placeholder invisibile per mantenere la griglia
                tk.Label(frame_prodotti).grid(row=riga, column=colonna, padx=int(5 * app.scala), pady=int(5 * app.scala), sticky="nsew")

        def cambia_pagina(delta):
            app.pagina_corrente += delta
            menu_cassa(app)

        btn_indietro = tk.Button(
            frame_prodotti, text="⏪ Indietro", command=lambda: cambia_pagina(-1),
            state="normal" if app.pagina_corrente > 0 else "disabled",
            font=app.get_font("Symbola", 12), width=int(16 * app.scala), height=int(2 * app.scala)
        )
        btn_indietro.grid(row=5, column=0, sticky="nsew", padx=int(5 * app.scala), pady=int(5 * app.scala))

        btn_avanti = tk.Button(
            frame_prodotti, text="Avanti ⏩", command=lambda: cambia_pagina(1),
            state="normal" if app.pagina_corrente < totale_pagine - 1 else "disabled",
            font=app.get_font("Symbola", 12), width=int(16 * app.scala), height=int(2 * app.scala)
        )
        btn_avanti.grid(row=5, column=1, sticky="nsew", padx=int(5 * app.scala), pady=int(5 * app.scala))

    else:
        # Calcolo righe massime (divido in due colonne più equilibrate possibili)
        totale_prodotti = len(prodotti)
        righe = (totale_prodotti + 1) // 2  # prima colonna avrà un elemento in più se dispari

        for i in range(righe):
            frame_prodotti.grid_rowconfigure(i, weight=1)
        for j in range(2):
            frame_prodotti.grid_columnconfigure(j, weight=1)

        for idx, (nome, prezzo) in enumerate(prodotti):
            riga = idx % righe
            colonna = idx // righe  # 0 o 1

            display_nome = re.sub(r'^[^\w\s]', '', nome).strip()

            btn = tk.Button(
                frame_prodotti,
                text=nome,
                command=lambda n=display_nome, p=prezzo: aggiungi_al_carrello(app, n, p),
                font=app.get_font("Symbola", 12),
                wraplength=int(180 * app.scala),
                width=int(16 * app.scala), height=int(2 * app.scala), bg="white"
            )
            btn.grid(row=riga, column=colonna, padx=int(5 * app.scala), pady=int(5 * app.scala), sticky="nsew")

    # Colonna destra: anteprima scontrino
    frame_scontrino = tk.Frame(main_frame, bg="white", relief="solid", bd=1)
    frame_scontrino.pack(side="right", fill="y", padx=(int(5 * app.scala), int (0 * app.scala)))

    tk.Label(frame_scontrino, text="Scontrino", font=app.get_font("Liberation Sans", 14, "bold"), bg="white").pack(pady=(int(10 * app.scala), int(0) * app.scala))

    app.scontrino_box = tk.Text(frame_scontrino, height=20, width=30, bg="white", font=app.get_font("Liberation Mono", 10))
    app.scontrino_box.pack(padx=int(10 * app.scala), pady=int(10 * app.scala))
    app.scontrino_box.config(state="disabled")

    if app.carrello:
        aggiorna_scontrino(app)

    btn_frame = tk.Frame(frame_scontrino, bg="white")
    btn_frame.pack(pady=(int(0 * app.scala), int(10 * app.scala)))

    tk.Button(btn_frame, text="🗑️ Cancella ultimo", command=lambda: cancella_ultimo(app),
              width=int(15 * app.scala), bg="lightgrey", font=app.get_font("Symbola", 10)).pack(side="left", padx=int(3 * app.scala))

    tk.Button(btn_frame, text="🎁 Inserisci sconto", command=lambda: finestra_sconto(app, lambda: aggiorna_scontrino(app)),
              width=int(15 * app.scala), bg="lightyellow", font=app.get_font("Symbola", 10)).pack(side="left", padx=int(3 * app.scala))
    tk.Button(frame_scontrino, text="✍️ Inserisci nota", command=lambda: finestra_nota(app),
          width=32, bg="lightcyan", font=("Symbola", 10)).pack(pady=(0, 10))

    if not hasattr(app, 'totale'):
        app.totale = 0
    if not hasattr(app, 'carrello'):
        app.carrello = []

    app.label_totale = tk.Label(root, text=f"Totale: €{app.totale:.2f}", font=app.get_font("Liberation Sans", 18, "bold"), fg="red")
    app.label_totale.pack(pady=int(5 * app.scala))

    def pulisci_app():
        app.carrello.clear()
        app.totale = 0.0
        app.sconti = 0.0
        app.importo_var.set("") if hasattr(app, 'importo_var') else None
        app.resto_var.set("") if hasattr(app, 'resto_var') else None
        for voce in app.carrello:
            voce["nota"] = None
        if hasattr(app, "scontrino_box") and app.scontrino_box.winfo_exists():
            app.scontrino_box.config(state="normal")
            app.scontrino_box.delete("1.0", "end")
            app.scontrino_box.config(state="disabled")
            
    # Frame contenitore per i due bottoni
    frame_bottoni_finali = tk.Frame(root)
    frame_bottoni_finali.pack(fill="x", pady=int(10 * app.scala))

    tk.Button(frame_bottoni_finali, text="🧾 Conto", command=lambda: menu_pagamento(app),
                width=int(25 * app.scala), height=2, bg="orange",
                font=app.get_font("Symbola", 16, "bold")).pack(side="left", expand=True, fill="x", padx=int(5 * app.scala))

    tk.Button(frame_bottoni_finali, text="⬅️ Esci", command=lambda: [pulisci_app(), menu_principale(app)],
          width=int(25 * app.scala), height=2, bg="gray",
          font=app.get_font("Symbola", 16, "bold")).pack(side="right", expand=True, fill="x", padx=int(5 * app.scala))
