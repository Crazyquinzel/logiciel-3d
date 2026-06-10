#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Médaille « SUPER PAPA » — Outil de personnalisation (double-clic).
Tape un prénom, clique, et le fichier STL imprimable est créé dans le sous-dossier "STL".

Dépendance unique : Pillow  (s'installe avec :  pip install pillow)
Police fournie à côté de ce fichier : DejaVuSans-Bold.ttf
"""
import os, re, struct, sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import tkinter.messagebox as mb
    import tkinter as tk
    r = tk.Tk(); r.withdraw()
    mb.showerror("Pillow manquant",
                 "Le module 'Pillow' n'est pas installé.\n\n"
                 "Ouvre une invite de commande et tape :\n\n    pip install pillow\n\n"
                 "puis relance l'outil.")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))

# ===================== PARAMÈTRES DE LA MÉDAILLE (mm) =====================
H_MM, W_MM = 75.0, 60.0
CS = 0.22
BASE = 5.0
H_RELIEF = BASE + 0.9
H_LISERE = BASE + 0.8

def load_font(size_px):
    size_px = max(6, int(size_px))
    for p in (os.path.join(HERE, "DejaVuSans-Bold.ttf"),
              r"C:\Windows\Fonts\arialbd.ttf",
              "/Library/Fonts/Arial Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size_px)
    return ImageFont.load_default()

# ----------------- contour du blason -----------------
CX = W_MM / 2.0
def _cubic(p0, p1, p2, p3, n=48):
    out = []
    for i in range(1, n + 1):
        t = i / n; mt = 1 - t
        out.append((mt**3*p0[0]+3*mt*mt*t*p1[0]+3*mt*t*t*p2[0]+t**3*p3[0],
                    mt**3*p0[1]+3*mt*mt*t*p1[1]+3*mt*t*t*p2[1]+t**3*p3[1]))
    return out
SHIELD = [(0.0,0.0),(W_MM,0.0),(W_MM,0.5*H_MM)]
SHIELD += _cubic((W_MM,0.5*H_MM),(W_MM,0.82*H_MM),(CX+0.34*W_MM,0.965*H_MM),(CX,H_MM))
SHIELD += _cubic((CX,H_MM),(CX-0.34*W_MM,0.965*H_MM),(0.0,0.82*H_MM),(0.0,0.5*H_MM))
_cxc = sum(p[0] for p in SHIELD)/len(SHIELD)
_cyc = sum(p[1] for p in SHIELD)/len(SHIELD)
def _scale(pts, s): return [(_cxc+(x-_cxc)*s, _cyc+(y-_cyc)*s) for (x,y) in pts]


def generate_stl(prenom, outdir):
    """Génère le STL pour 'prenom'. Retourne le chemin du fichier créé."""
    prenom = (prenom or "").strip().upper()
    slug = re.sub(r"[^A-Za-z0-9]+", "", prenom) or "PRENOM"

    NX = int(round(W_MM/CS)) + 1
    NY = int(round(H_MM/CS)) + 1
    def px(v): return v / CS
    H = [0.0]*(NX*NY)

    def newmask():
        m = Image.new("L", (NX, NY), 0)
        return m, ImageDraw.Draw(m)
    def stamp(mask, value):
        for idx, v in enumerate(mask.getdata()):
            if v > 127:
                H[idx] = value
    def to_px(pts): return [(px(x), px(y)) for (x, y) in pts]
    def text_mask(s, y_mm, h_mm, max_w_mm=None):
        h = h_mm
        if max_w_mm:
            tmp = ImageDraw.Draw(Image.new("L", (10, 10)))
            w = tmp.textlength(s, font=load_font(px(h)))
            if w > px(max_w_mm):
                h = h * px(max_w_mm) / w
        m, d = newmask()
        d.text((px(CX), px(y_mm)), s, font=load_font(px(h)), fill=255, anchor="mm")
        return m

    # 1) corps
    m, d = newmask(); d.polygon(to_px(SHIELD), fill=255); stamp(m, BASE)
    # 2) liseré
    m, d = newmask(); d.polygon(to_px(_scale(SHIELD, 0.905)), fill=255); stamp(m, H_LISERE)
    m, d = newmask(); d.polygon(to_px(_scale(SHIELD, 0.840)), fill=255); stamp(m, BASE)
    # 3) cartouche
    cy = 26.0
    def rrect(cx, cyc, w, h, r, val):
        m, d = newmask()
        d.rounded_rectangle([px(cx-w/2), px(cyc-h/2), px(cx+w/2), px(cyc+h/2)],
                            radius=px(r), fill=255)
        stamp(m, val)
    rrect(CX, cy, 40, 9, 4.5, H_LISERE)
    rrect(CX, cy, 40-2.4, 9-2.4, 3.3, BASE)
    # 4) textes
    stamp(text_mask(prenom, cy, 5.0, max_w_mm=34.0), H_RELIEF)
    stamp(text_mask("SUPER", 35.0, 9.0), H_RELIEF)
    stamp(text_mask("PAPA", 46.0, 13.0), H_RELIEF)
    # 5) fente ruban (trou traversant)
    m, d = newmask()
    d.rounded_rectangle([px(CX-13), px(8-1.5), px(CX+13), px(8+1.5)], radius=px(1.5), fill=255)
    stamp(m, 0.0)

    # ---- maillage étanche ----
    def node(i, j): return H[j*NX+i]
    def filled(i, j):
        if i < 0 or j < 0 or i >= NX-1 or j >= NY-1: return False
        return (node(i,j) > 0 and node(i+1,j) > 0 and node(i,j+1) > 0 and node(i+1,j+1) > 0)
    def wy(j): return (NY-1-j)*CS
    tris = []
    def quad(a, b, c, dd):
        tris.append(a+b+c); tris.append(a+c+dd)
    for j in range(NY-1):
        for i in range(NX-1):
            if not filled(i, j): continue
            x0, x1 = i*CS, (i+1)*CS
            y0, y1 = wy(j), wy(j+1)
            v00=(x0,y0,node(i,j)); v10=(x1,y0,node(i+1,j))
            v11=(x1,y1,node(i+1,j+1)); v01=(x0,y1,node(i,j+1))
            quad(v00, v01, v11, v10)
            quad((x0,y0,0.),(x1,y0,0.),(x1,y1,0.),(x0,y1,0.))
            if not filled(i-1, j): quad((x0,y0,0.),(x0,y1,0.),v01,v00)
            if not filled(i+1, j): quad((x1,y0,0.),v10,v11,(x1,y1,0.))
            if not filled(i, j-1): quad((x0,y0,0.),v00,v10,(x1,y0,0.))
            if not filled(i, j+1): quad((x0,y1,0.),(x1,y1,0.),v11,v01)

    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"medaille_super_papa_{slug}.stl")
    with open(path, "wb") as f:
        f.write(b"medaille super papa".ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        z = struct.pack("<fff", 0., 0., 0.)
        for t in tris:
            f.write(z); f.write(struct.pack("<9f", *t)); f.write(struct.pack("<H", 0))
    return path, len(tris)


# ============================ INTERFACE ============================
def run_gui():
    import tkinter as tk
    from tkinter import messagebox

    OUTDIR = os.path.join(HERE, "STL")

    root = tk.Tk()
    root.title("Médaille SUPER PAPA")
    root.geometry("420x250")
    root.configure(bg="#1f2937")
    root.resizable(False, False)

    tk.Label(root, text="🏅  Médaille SUPER PAPA", bg="#1f2937", fg="#f3f4f6",
             font=("Segoe UI", 15, "bold")).pack(pady=(18, 4))
    tk.Label(root, text="Prénom à graver :", bg="#1f2937", fg="#cbd5e1",
             font=("Segoe UI", 11)).pack(pady=(8, 2))

    var = tk.StringVar()
    entry = tk.Entry(root, textvariable=var, font=("Segoe UI", 14), justify="center", width=20)
    entry.pack(pady=4); entry.focus()

    status = tk.Label(root, text="", bg="#1f2937", fg="#93c5fd",
                      font=("Segoe UI", 9), wraplength=380, justify="center")
    status.pack(pady=(8, 0))

    def go(event=None):
        name = var.get().strip()
        if not name:
            messagebox.showwarning("Prénom vide", "Tape d'abord un prénom.")
            return
        status.config(text="Génération en cours…", fg="#93c5fd"); root.update()
        try:
            path, ntri = generate_stl(name, OUTDIR)
        except Exception as e:
            status.config(text="Erreur : %s" % e, fg="#fca5a5"); return
        status.config(text="✅ Créé : %s\n(%d triangles)" % (os.path.basename(path), ntri),
                      fg="#86efac")
        # ouvrir le dossier
        try:
            if sys.platform.startswith("win"): os.startfile(OUTDIR)            # noqa
            elif sys.platform == "darwin": os.system('open "%s"' % OUTDIR)
            else: os.system('xdg-open "%s"' % OUTDIR)
        except Exception:
            pass

    tk.Button(root, text="Créer le fichier STL", command=go,
              font=("Segoe UI", 12, "bold"), bg="#2563eb", fg="white",
              activebackground="#1d4ed8", relief="flat", padx=10, pady=6).pack(pady=14)
    entry.bind("<Return>", go)
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:                     # mode ligne de commande : python medaille_app.py LUCAS
        p, n = generate_stl(sys.argv[1], os.path.join(HERE, "STL"))
        print("OK ->", p, "(%d triangles)" % n)
    else:
        run_gui()
