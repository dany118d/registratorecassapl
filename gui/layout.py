import tkinter as tk

def crea_header(app, logo_img, orologio_label_callback):
    top_frame = tk.Frame(app.root)
    top_frame.pack(fill='x', pady=(int(10 * app.scala), int(0 * app.scala)))
    
    if logo_img:
        tk.Label(top_frame, image=logo_img).pack(side='left', padx=int(10 * app.scala))

    orologio_label = tk.Label(top_frame, font=app.get_font("Liberation Sans", 16, "bold"))
    orologio_label.pack(side='right', padx=int(10 * app.scala))

    # La callback serve per dire all'esterno: "ecco il label che ho appena creato"
    orologio_label_callback(orologio_label)
