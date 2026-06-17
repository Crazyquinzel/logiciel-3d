#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Médaille personnalisée — Outil double-clic.
Onglet 1 : prénom + mention (PAPA, MAMAN, PARRAIN, PROF, MAÎTRE...).
Onglet 2 : forme (Blason / Cercle / Hexagone) + icône en relief (foot, outils, étoile, cœur...).

Dépendance unique : Pillow  (pip install pillow)
Police fournie à côté : DejaVuSans-Bold.ttf
"""
import os, re, struct, sys, math

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import tkinter as tk, tkinter.messagebox as mb
    r = tk.Tk(); r.withdraw()
    mb.showerror("Pillow manquant",
                 "Le module 'Pillow' n'est pas installé.\n\n"
                 "Ouvre une invite de commande et tape :\n\n    pip install pillow\n\n"
                 "puis relance l'outil.")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))

# ===================== PARAMÈTRES (mm) =====================
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

# ----------------- géométrie des contours -----------------
def _cubic(p0, p1, p2, p3, n=48):
    out = []
    for i in range(1, n + 1):
        t = i / n; mt = 1 - t
        out.append((mt**3*p0[0]+3*mt*mt*t*p1[0]+3*mt*t*t*p2[0]+t**3*p3[0],
                    mt**3*p0[1]+3*mt*mt*t*p1[1]+3*mt*t*t*p2[1]+t**3*p3[1]))
    return out

def shield_pts(W, H):
    cx = W/2.0
    p = [(0.0,0.0),(W,0.0),(W,0.5*H)]
    p += _cubic((W,0.5*H),(W,0.82*H),(cx+0.34*W,0.965*H),(cx,H))
    p += _cubic((cx,H),(cx-0.34*W,0.965*H),(0.0,0.82*H),(0.0,0.5*H))
    return p

def circle_pts(cx, cy, r, n=200):
    return [(cx+r*math.cos(2*math.pi*i/n), cy+r*math.sin(2*math.pi*i/n)) for i in range(n)]

def hexagon_pts(cx, cy, r):
    # sommets à 0,60,...  -> côtés horizontaux en haut et en bas (pratique pour la fente)
    return [(cx+r*math.cos(math.radians(60*i)), cy+r*math.sin(math.radians(60*i))) for i in range(6)]

def scale_about(pts, s):
    cx = sum(p[0] for p in pts)/len(pts); cy = sum(p[1] for p in pts)/len(pts)
    return [(cx+(x-cx)*s, cy+(y-cy)*s) for (x, y) in pts]

# Configuration par forme : dimensions du canevas + positions des textes (mm)
SHAPES = {
    "blason":   dict(W=60, H=75, slot_y=8.0,  cart_y=26.0, super_y=35.0, role_y=46.0, icon_y=60.0, icon_h=13.0),
    "cercle":   dict(W=74, H=74, slot_y=11.0, cart_y=27.0, super_y=37.0, role_y=48.0, icon_y=60.0, icon_h=12.0),
    "hexagone": dict(W=72, H=74, slot_y=9.0,  cart_y=27.0, super_y=37.0, role_y=48.0, icon_y=60.0, icon_h=12.0),
}

def outline_for(shape, W, H):
    if shape == "cercle":
        r = min(W, H)/2.0 - 1.0
        return circle_pts(W/2.0, H/2.0, r)
    if shape == "hexagone":
        r = min(W, H)/2.0 - 1.0
        return hexagon_pts(W/2.0, H/2.0, r)
    return shield_pts(W, H)

# ----------------- icônes (silhouettes en relief) -----------------
def _star(d, px, cx, cy, h, pts=5):
    R = h/2.0; r = R*0.42; poly = []
    for i in range(pts*2):
        a = -math.pi/2 + i*math.pi/pts
        rad = R if i % 2 == 0 else r
        poly.append((px(cx+rad*math.cos(a)), px(cy+rad*math.sin(a))))
    d.polygon(poly, fill=255)

def _heart(d, px, cx, cy, h):
    poly = []
    for k in range(0, 361, 4):
        t = math.radians(k)
        x = 16*math.sin(t)**3
        y = 13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
        poly.append((px(cx + x*h/34.0), px(cy - y*h/34.0)))
    d.polygon(poly, fill=255)

def _pencil(d, px, cx, cy, h):
    ang = math.radians(-35); ca, sa = math.cos(ang), math.sin(ang)
    w = h*0.24; top = -h*0.5; ts = h*0.20; tip = h*0.5
    loc = [(-w/2, top), (w/2, top), (w/2, ts), (0, tip), (-w/2, ts)]
    d.polygon([(px(cx+X*ca-Y*sa), px(cy+X*sa+Y*ca)) for X, Y in loc], fill=255)

def _hammer(d, px, cx, cy, h):
    head_w = h*0.78; head_h = h*0.28
    d.rounded_rectangle([px(cx-head_w/2), px(cy-h/2), px(cx+head_w/2), px(cy-h/2+head_h)],
                        radius=px(h*0.05), fill=255)
    hw = h*0.17
    d.rectangle([px(cx-hw/2), px(cy-h/2+head_h*0.7), px(cx+hw/2), px(cy+h/2)], fill=255)

def _wrench(d, px, cx, cy, h):
    # clé plate à double tête ouverte (horizontale)
    L = h*0.46; w = h*0.22
    d.rounded_rectangle([px(cx-L/2), px(cy-w/2), px(cx+L/2), px(cy+w/2)], radius=px(w/2), fill=255)
    for sgn in (-1, 1):
        hx = cx + sgn*L/2; rr = h*0.30
        d.ellipse([px(hx-rr), px(cy-rr), px(hx+rr), px(cy+rr)], fill=255)
    for sgn in (-1, 1):                       # têtes ouvertes (encoche en C vers l'extérieur)
        hx = cx + sgn*L/2; rr = h*0.30
        d.ellipse([px(hx-rr*0.5), px(cy-rr*0.5), px(hx+rr*0.5), px(cy+rr*0.5)], fill=0)
        d.polygon([(px(hx), px(cy-rr*0.92)), (px(hx+sgn*rr*1.35), px(cy-rr*0.34)),
                   (px(hx+sgn*rr*1.35), px(cy+rr*0.34)), (px(hx), px(cy+rr*0.92))], fill=0)

def _apple(d, px, cx, cy, h):
    bw = h*0.84; bh = h*0.86
    d.ellipse([px(cx-bw/2), px(cy-bh/2+h*0.10), px(cx+bw/2), px(cy+bh/2)], fill=255)
    d.rectangle([px(cx-h*0.04), px(cy-bh/2-h*0.02), px(cx+h*0.04), px(cy-bh/2+h*0.16)], fill=255)
    d.ellipse([px(cx+h*0.03), px(cy-bh/2-h*0.04), px(cx+h*0.24), px(cy-bh/2+h*0.14)], fill=255)

def _crown(d, px, cx, cy, h):
    w = h*0.94; bottom = cy+h*0.42; top = cy-h*0.45; band = bottom-h*0.26
    d.rectangle([px(cx-w/2), px(band), px(cx+w/2), px(bottom)], fill=255)   # bandeau
    pts = [(cx-w/2, band), (cx-w/2, top+h*0.12), (cx-w/4, band-h*0.03), (cx, top),
           (cx+w/4, band-h*0.03), (cx+w/2, top+h*0.12), (cx+w/2, band)]
    d.polygon([(px(x), px(y)) for x, y in pts], fill=255)
    for bx, by in ((cx-w/2, top+h*0.12), (cx, top), (cx+w/2, top+h*0.12)):  # billes
        rr = h*0.075
        d.ellipse([px(bx-rr), px(by-rr), px(bx+rr), px(by+rr)], fill=255)

def _music(d, px, cx, cy, h):
    hw = h*0.36; hh = h*0.27; hcx = cx-h*0.10; hcy = cy+h*0.30
    d.ellipse([px(hcx-hw/2), px(hcy-hh/2), px(hcx+hw/2), px(hcy+hh/2)], fill=255)  # tête
    sx = hcx+hw/2-h*0.05
    d.rectangle([px(sx-h*0.05), px(cy-h*0.44), px(sx+h*0.05), px(hcy)], fill=255)  # hampe
    d.polygon([(px(sx+h*0.05), px(cy-h*0.44)), (px(sx+h*0.30), px(cy-h*0.18)),
               (px(sx+h*0.05), px(cy-h*0.06))], fill=255)                          # crochet

def _flower(d, px, cx, cy, h):
    cyf = cy-h*0.14; pr = h*0.30; petal = h*0.155
    d.rectangle([px(cx-h*0.045), px(cyf), px(cx+h*0.045), px(cy+h*0.5)], fill=255)  # tige
    d.ellipse([px(cx), px(cy+h*0.16), px(cx+h*0.24), px(cy+h*0.34)], fill=255)      # feuille
    for i in range(6):
        a = i*math.pi/3 - math.pi/2
        pxc = cx+pr*math.cos(a); pyc = cyf+pr*math.sin(a)
        d.ellipse([px(pxc-petal), px(pyc-petal), px(pxc+petal), px(pyc+petal)], fill=255)
    d.ellipse([px(cx-h*0.115), px(cyf-h*0.115), px(cx+h*0.115), px(cyf+h*0.115)], fill=0)  # cœur creux

def _car(d, px, cx, cy, h):
    bw = h*0.98; btop = cy-h*0.08; bbot = cy+h*0.20
    d.rounded_rectangle([px(cx-bw/2), px(btop), px(cx+bw/2), px(bbot)], radius=px(h*0.10), fill=255)
    d.polygon([(px(cx-bw*0.26), px(btop)), (px(cx-bw*0.13), px(cy-h*0.34)),
               (px(cx+bw*0.17), px(cy-h*0.34)), (px(cx+bw*0.30), px(btop))], fill=255)  # toit
    wr = h*0.16
    for wx in (cx-bw*0.27, cx+bw*0.27):
        d.ellipse([px(wx-wr), px(bbot-wr*0.5), px(wx+wr), px(bbot+wr*1.5)], fill=255)

def _cross(d, px, cx, cy, h):
    a = h*0.30; L = h*0.50
    d.rectangle([px(cx-a/2), px(cy-L), px(cx+a/2), px(cy+L)], fill=255)
    d.rectangle([px(cx-L), px(cy-a/2), px(cx+L), px(cy+a/2)], fill=255)

ICONS = ["aucun", "etoile", "coeur", "foot", "crayon", "marteau", "cle", "pomme",
         "couronne", "musique", "fleur", "voiture", "sante"]
ICON_LABEL = {"aucun":"Aucune", "etoile":"Étoile", "coeur":"Cœur", "foot":"Ballon de foot",
              "crayon":"Crayon", "marteau":"Marteau", "cle":"Clé (outils)", "pomme":"Pomme",
              "couronne":"Couronne", "musique":"Musique", "fleur":"Fleur (jardinage)",
              "voiture":"Voiture", "sante":"Croix médicale"}

ROLES = ["PAPA","PAPI","MAMAN","MAMIE","TONTON","TATIE","PARRAIN","MARRAINE",
         "PROF","MAÎTRE","MAÎTRESSE","ATSEM"]
SHAPE_LABEL = {"blason":"Blason", "cercle":"Cercle", "hexagone":"Hexagone"}


def generate_stl(prenom, role, shape, icon, outdir, show_super=True):
    prenom = (prenom or "").strip().upper()
    role = (role or "PAPA").strip().upper()
    shape = (shape or "blason").lower()
    icon = (icon or "aucun").lower()
    cfg = SHAPES.get(shape, SHAPES["blason"])
    W_MM, H_MM = cfg["W"], cfg["H"]; CX = W_MM/2.0
    slug = re.sub(r"[^A-Za-z0-9]+", "", prenom) or "PRENOM"
    rslug = re.sub(r"[^A-Za-z0-9]+", "", role).lower() or "papa"

    NX = int(round(W_MM/CS)) + 1
    NY = int(round(H_MM/CS)) + 1
    def px(v): return v/CS
    H = [0.0]*(NX*NY)

    def newmask(): m = Image.new("L", (NX, NY), 0); return m, ImageDraw.Draw(m)
    def stamp(mask, value):
        for idx, v in enumerate(mask.getdata()):
            if v > 127: H[idx] = value
    def to_px(pts): return [(px(x), px(y)) for (x, y) in pts]
    def text_mask(s, y_mm, h_mm, max_w_mm=None):
        h = h_mm
        if max_w_mm:
            t = ImageDraw.Draw(Image.new("L", (10, 10)))
            w = t.textlength(s, font=load_font(px(h)))
            if w > px(max_w_mm): h = h*px(max_w_mm)/w
        m, d = newmask()
        d.text((px(CX), px(y_mm)), s, font=load_font(px(h)), fill=255, anchor="mm")
        return m

    outline = outline_for(shape, W_MM, H_MM)
    # 1) corps  2) liseré  3) champ intérieur
    m, d = newmask(); d.polygon(to_px(outline), fill=255); stamp(m, BASE)
    m, d = newmask(); d.polygon(to_px(scale_about(outline, 0.905)), fill=255); stamp(m, H_LISERE)
    m, d = newmask(); d.polygon(to_px(scale_about(outline, 0.840)), fill=255); stamp(m, BASE)
    # cartouche prénom
    cy = cfg["cart_y"]
    def rrect(w, h, r, val):
        m, d = newmask()
        d.rounded_rectangle([px(CX-w/2), px(cy-h/2), px(CX+w/2), px(cy+h/2)], radius=px(r), fill=255)
        stamp(m, val)
    rrect(40, 9, 4.5, H_LISERE); rrect(40-2.4, 9-2.4, 3.3, BASE)
    # textes
    stamp(text_mask(prenom, cy, 5.0, max_w_mm=34.0), H_RELIEF)
    if show_super:
        stamp(text_mask("SUPER", cfg["super_y"], 9.0), H_RELIEF)
        stamp(text_mask(role, cfg["role_y"], 13.0, max_w_mm=48.0), H_RELIEF)
    else:
        my = (cfg["super_y"] + cfg["role_y"]) / 2.0
        stamp(text_mask(role, my, 14.0, max_w_mm=50.0), H_RELIEF)
    # icône
    if icon and icon != "aucun":
        icx, icy, ich = CX, cfg["icon_y"], cfg["icon_h"]
        if icon == "foot":
            r = ich/2.0
            m, d = newmask()
            d.ellipse([px(icx-r), px(icy-r), px(icx+r), px(icy+r)], fill=255); stamp(m, H_RELIEF)
            # motif en creux : pentagone central + branches vers le bord
            mm, dd = newmask()
            pent = [(icx+r*0.34*math.cos(-math.pi/2+i*2*math.pi/5),
                     icy+r*0.34*math.sin(-math.pi/2+i*2*math.pi/5)) for i in range(5)]
            dd.polygon([(px(x), px(y)) for x, y in pent], fill=255)
            for vx, vy in pent:
                ex = icx + (vx-icx)/(r*0.34)*r*0.92
                ey = icy + (vy-icy)/(r*0.34)*r*0.92
                dd.line([(px(vx), px(vy)), (px(ex), px(ey))], fill=255, width=max(1, int(px(0.7))))
            stamp(mm, BASE)
        else:
            m, d = newmask()
            {"etoile":_star, "coeur":_heart, "crayon":_pencil, "marteau":_hammer,
             "cle":_wrench, "pomme":_apple, "couronne":_crown, "musique":_music,
             "fleur":_flower, "voiture":_car, "sante":_cross}[icon](d, px, icx, icy, ich)
            stamp(m, H_RELIEF)
    # fente ruban (trou traversant)
    m, d = newmask()
    sy = cfg["slot_y"]
    d.rounded_rectangle([px(CX-13), px(sy-1.5), px(CX+13), px(sy+1.5)], radius=px(1.5), fill=255)
    stamp(m, 0.0)

    # ---- maillage étanche ----
    def node(i, j): return H[j*NX+i]
    def filled(i, j):
        if i < 0 or j < 0 or i >= NX-1 or j >= NY-1: return False
        return (node(i,j) > 0 and node(i+1,j) > 0 and node(i,j+1) > 0 and node(i+1,j+1) > 0)
    def wy(j): return (NY-1-j)*CS
    tris = []
    def quad(a, b, c, dd): tris.append(a+b+c); tris.append(a+c+dd)
    for j in range(NY-1):
        for i in range(NX-1):
            if not filled(i, j): continue
            x0, x1 = i*CS, (i+1)*CS; y0, y1 = wy(j), wy(j+1)
            v00=(x0,y0,node(i,j)); v10=(x1,y0,node(i+1,j))
            v11=(x1,y1,node(i+1,j+1)); v01=(x0,y1,node(i,j+1))
            quad(v00, v01, v11, v10)
            quad((x0,y0,0.),(x1,y0,0.),(x1,y1,0.),(x0,y1,0.))
            if not filled(i-1, j): quad((x0,y0,0.),(x0,y1,0.),v01,v00)
            if not filled(i+1, j): quad((x1,y0,0.),v10,v11,(x1,y1,0.))
            if not filled(i, j-1): quad((x0,y0,0.),v00,v10,(x1,y0,0.))
            if not filled(i, j+1): quad((x0,y1,0.),(x1,y1,0.),v11,v01)

    os.makedirs(outdir, exist_ok=True)
    extra = "" if icon in ("", "aucun") else "_" + icon
    pre = "super_" if show_super else ""
    path = os.path.join(outdir, f"medaille_{pre}{rslug}_{slug}_{shape}{extra}.stl")
    with open(path, "wb") as f:
        f.write(b"medaille personnalisee".ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        z = struct.pack("<fff", 0., 0., 0.)
        for t in tris:
            f.write(z); f.write(struct.pack("<9f", *t)); f.write(struct.pack("<H", 0))
    return path, len(tris)


# ============================ INTERFACE ============================
def run_gui():
    import tkinter as tk
    from tkinter import ttk, messagebox

    OUTDIR = os.path.join(HERE, "STL")
    BG = "#1f2937"
    root = tk.Tk()
    root.title("Médaille personnalisée")
    root.geometry("460x520"); root.configure(bg=BG); root.resizable(False, False)

    tk.Label(root, text="🏅  Médaille personnalisée", bg=BG, fg="#f3f4f6",
             font=("Segoe UI", 15, "bold")).pack(pady=(14, 8))

    nb = ttk.Notebook(root); nb.pack(fill="both", expand=False, padx=12)

    # --- onglet 1 : texte ---
    t1 = tk.Frame(nb, bg=BG)
    tk.Label(t1, text="Prénom à graver :", bg=BG, fg="#cbd5e1", font=("Segoe UI", 11)).pack(pady=(14, 2))
    name_var = tk.StringVar()
    e = tk.Entry(t1, textvariable=name_var, font=("Segoe UI", 14), justify="center", width=20)
    e.pack(pady=2); e.focus()
    tk.Label(t1, text="Mention :", bg=BG, fg="#cbd5e1", font=("Segoe UI", 11)).pack(pady=(10, 2))
    role_var = tk.StringVar(value="PAPA")
    om = tk.OptionMenu(t1, role_var, *ROLES)
    om.config(font=("Segoe UI", 11), bg="#374151", fg="white", highlightthickness=0,
              relief="flat", width=14); om["menu"].config(bg="#374151", fg="white")
    om.pack(pady=2)
    tk.Label(t1, text="… ou mention personnalisée (texte libre) :", bg=BG, fg="#94a3b8",
             font=("Segoe UI", 9)).pack(pady=(8, 1))
    custom_var = tk.StringVar()
    tk.Entry(t1, textvariable=custom_var, font=("Segoe UI", 12), justify="center",
             width=22).pack(pady=1)
    super_var = tk.BooleanVar(value=True)
    tk.Checkbutton(t1, text="Garder le mot « SUPER »", variable=super_var, bg=BG, fg="#e5e7eb",
                   selectcolor="#374151", activebackground=BG, font=("Segoe UI", 10)).pack(pady=(6, 0))
    nb.add(t1, text="  Médaille  ")

    # --- onglet 2 : forme & déco ---
    t2 = tk.Frame(nb, bg=BG)
    tk.Label(t2, text="Forme :", bg=BG, fg="#cbd5e1", font=("Segoe UI", 11)).pack(pady=(14, 2))
    shape_var = tk.StringVar(value="blason")
    fr = tk.Frame(t2, bg=BG); fr.pack()
    for key in ("blason", "cercle", "hexagone"):
        tk.Radiobutton(fr, text=SHAPE_LABEL[key], variable=shape_var, value=key, bg=BG,
                       fg="#e5e7eb", selectcolor="#374151", activebackground=BG,
                       font=("Segoe UI", 11)).pack(side="left", padx=6)
    tk.Label(t2, text="Icône en relief :", bg=BG, fg="#cbd5e1", font=("Segoe UI", 11)).pack(pady=(14, 2))
    icon_var = tk.StringVar(value="Aucune")
    iom = tk.OptionMenu(t2, icon_var, *[ICON_LABEL[i] for i in ICONS])
    iom.config(font=("Segoe UI", 11), bg="#374151", fg="white", highlightthickness=0,
               relief="flat", width=16); iom["menu"].config(bg="#374151", fg="white")
    iom.pack(pady=2)
    nb.add(t2, text="  Forme & déco  ")

    status = tk.Label(root, text="", bg=BG, fg="#93c5fd", font=("Segoe UI", 9),
                      wraplength=400, justify="center"); status.pack(pady=(10, 0))

    def go(event=None):
        name = name_var.get().strip()
        if not name:
            messagebox.showwarning("Prénom vide", "Tape d'abord un prénom."); return
        icon_key = next((k for k, v in ICON_LABEL.items() if v == icon_var.get()), "aucun")
        mention = custom_var.get().strip() or role_var.get()
        status.config(text="Génération en cours…", fg="#93c5fd"); root.update()
        try:
            path, ntri = generate_stl(name, mention, shape_var.get(), icon_key, OUTDIR,
                                      show_super=super_var.get())
        except Exception as ex:
            status.config(text="Erreur : %s" % ex, fg="#fca5a5"); return
        status.config(text="✅ Créé : %s" % os.path.basename(path), fg="#86efac")
        try:
            if sys.platform.startswith("win"): os.startfile(OUTDIR)          # noqa
            elif sys.platform == "darwin": os.system('open "%s"' % OUTDIR)
            else: os.system('xdg-open "%s"' % OUTDIR)
        except Exception: pass

    tk.Button(root, text="Créer le fichier STL", command=go, font=("Segoe UI", 12, "bold"),
              bg="#2563eb", fg="white", activebackground="#1d4ed8", relief="flat",
              padx=10, pady=7).pack(pady=14)
    root.bind("<Return>", go)
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:   # CLI : python medaille_app.py PRENOM [ROLE] [SHAPE] [ICON]
        a = sys.argv + ["PAPA", "blason", "aucun"]
        p, n = generate_stl(a[1], a[2], a[3], a[4], os.path.join(HERE, "STL"))
        print("OK ->", p, "(%d triangles)" % n)
    else:
        run_gui()
