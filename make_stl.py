#!/usr/bin/env python3
"""Genere un VRAI fichier STL imprimable de la medaille 'SUPER PAPA' (ecusson).
Methode : carte de hauteurs (heightmap) -> solide maille etanche (watertight).
Pur Python + Pillow (deja installe). Aucune dependance lourde.

Sortie : medaille_super_papa.stl  (+ heightmap_preview.png pour controle)
"""
import math, struct, sys, re
from PIL import Image, ImageDraw, ImageFont

# ----------------- parametres (mm) -----------------
H_MM, W_MM = 75.0, 60.0          # blason
CS = 0.22                        # taille de cellule (resolution) en mm
BASE = 5.0                       # epaisseur du corps
H_RELIEF = BASE + 0.9            # sommet du texte
H_LISERE = BASE + 0.8            # sommet du lisere / cartouche

# >>> PRENOM : 1er argument en ligne de commande, sinon "THOMAS" par defaut <<<
#     ex :  python3 make_stl.py LUCAS
PRENOM = (sys.argv[1] if len(sys.argv) > 1 else "THOMAS").upper()
SLUG = re.sub(r"[^A-Za-z0-9]+", "", PRENOM) or "PRENOM"

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NX = int(round(W_MM / CS)) + 1   # noeuds en X
NY = int(round(H_MM / CS)) + 1   # noeuds en Y
def px(v): return v / CS         # mm -> pixels(noeuds)

# ----------------- contour du blason (mm) -----------------
CX = W_MM / 2.0
def cubic(p0, p1, p2, p3, n=48):
    out = []
    for i in range(1, n+1):
        t = i/n; mt = 1-t
        out.append((mt**3*p0[0]+3*mt*mt*t*p1[0]+3*mt*t*t*p2[0]+t**3*p3[0],
                    mt**3*p0[1]+3*mt*mt*t*p1[1]+3*mt*t*t*p2[1]+t**3*p3[1]))
    return out
SHIELD = [(0.0,0.0),(W_MM,0.0),(W_MM,0.5*H_MM)]
SHIELD += cubic((W_MM,0.5*H_MM),(W_MM,0.82*H_MM),(CX+0.34*W_MM,0.965*H_MM),(CX,H_MM))
SHIELD += cubic((CX,H_MM),(CX-0.34*W_MM,0.965*H_MM),(0.0,0.82*H_MM),(0.0,0.5*H_MM))

# centroide pour les decalages (lisere) par homothetie
cxc = sum(p[0] for p in SHIELD)/len(SHIELD)
cyc = sum(p[1] for p in SHIELD)/len(SHIELD)
def scale_pts(pts, s):
    return [(cxc+(x-cxc)*s, cyc+(y-cyc)*s) for (x,y) in pts]
def to_px(pts):
    return [(px(x), px(y)) for (x,y) in pts]

# ----------------- composition de la carte de hauteurs -----------------
H = [0.0]*(NX*NY)
def newmask():
    m = Image.new("L", (NX, NY), 0)
    return m, ImageDraw.Draw(m)
def stamp(mask, value):
    d = mask.getdata()
    for idx, v in enumerate(d):
        if v > 127:
            H[idx] = value

def font(sz): return ImageFont.truetype(FONT, max(6, int(sz)))
def text_mask(s, y_mm, h_mm, max_w_mm=None):
    """texte centre ; si max_w_mm est donne, reduit la taille pour tenir (prenom long)."""
    h = h_mm
    if max_w_mm:
        tmp = Image.new("L", (10, 10)); td = ImageDraw.Draw(tmp)
        w = td.textlength(s, font=font(px(h)))
        if w > px(max_w_mm):
            h = h * px(max_w_mm) / w        # mise a l'echelle pour tenir dans la largeur
    m, d = newmask()
    d.text((px(CX), px(y_mm)), s, font=font(px(h)), fill=255, anchor="mm")
    return m

# 1) corps du blason -> BASE
m, d = newmask(); d.polygon(to_px(SHIELD), fill=255); stamp(m, BASE)
# 2) lisere (anneau a ~3 mm du bord) -> H_LISERE
m, d = newmask(); d.polygon(to_px(scale_pts(SHIELD, 0.905)), fill=255); stamp(m, H_LISERE)
m, d = newmask(); d.polygon(to_px(scale_pts(SHIELD, 0.840)), fill=255); stamp(m, BASE)
# 3) cartouche prenom (cadre) -> H_LISERE
cy_cart = 26.0
def rrect(cx, cy, w, h, r, val):
    m, d = newmask()
    d.rounded_rectangle([px(cx-w/2), px(cy-h/2), px(cx+w/2), px(cy+h/2)],
                        radius=px(r), fill=255)
    stamp(m, val)
rrect(CX, cy_cart, 40, 9, 4.5, H_LISERE)     # cadre exterieur
rrect(CX, cy_cart, 40-2.4, 9-2.4, 3.3, BASE) # evidement -> cadre 1.2 mm
# 4) textes en relief -> H_RELIEF  (le prenom s'adapte a la largeur du cartouche)
stamp(text_mask(PRENOM, cy_cart, 5.0, max_w_mm=34.0), H_RELIEF)
stamp(text_mask("SUPER", 35.0, 9.0), H_RELIEF)
stamp(text_mask("PAPA", 46.0, 13.0), H_RELIEF)
# 5) fente du ruban (trou traversant) -> 0
m, d = newmask()
d.rounded_rectangle([px(CX-13), px(8-1.5), px(CX+13), px(8+1.5)], radius=px(1.5), fill=255)
stamp(m, 0.0)

# apercu de controle (vue de dessus de la heightmap)
hmax = max(H) or 1.0
prev = Image.new("L", (NX, NY))
prev.putdata([int(255*h/hmax) for h in H])
prev.save(f"/home/user/logiciel-3d/apercu_{SLUG}.png")

# ----------------- maillage heightmap -> solide etanche -----------------
def node(i, j): return H[j*NX+i]
def cell_filled(i, j):
    if i < 0 or j < 0 or i >= NX-1 or j >= NY-1: return False
    return (node(i,j) > 0 and node(i+1,j) > 0 and
            node(i,j+1) > 0 and node(i+1,j+1) > 0)
def wy(j): return (NY-1-j)*CS        # flip -> modele a l'endroit (Z = hauteur)

tris = []   # chaque element : (ax,ay,az, bx,by,bz, cx,cy,cz)
def quad(a, b, c, d):                # deux triangles
    tris.append(a+b+c); tris.append(a+c+d)

for j in range(NY-1):
    for i in range(NX-1):
        if not cell_filled(i, j):
            continue
        x0, x1 = i*CS, (i+1)*CS
        y0, y1 = wy(j), wy(j+1)
        h00, h10 = node(i,j), node(i+1,j)
        h01, h11 = node(i,j+1), node(i+1,j+1)
        # dessus (CCW -> normale +Z)
        v00=(x0,y0,h00); v10=(x1,y0,h10); v11=(x1,y1,h11); v01=(x0,y1,h01)
        quad(v00, v01, v11, v10)
        # dessous (z=0, sens inverse)
        b00=(x0,y0,0.0); b10=(x1,y0,0.0); b11=(x1,y1,0.0); b01=(x0,y1,0.0)
        quad(b00, b10, b11, b01)
        # murs lateraux uniquement sur la silhouette / le trou
        if not cell_filled(i-1, j):   # bord gauche (noeuds v00,v01)
            quad((x0,y0,0.0),(x0,y1,0.0),v01,v00)
        if not cell_filled(i+1, j):   # bord droit (v10,v11)
            quad((x1,y0,0.0),v10,v11,(x1,y1,0.0))
        if not cell_filled(i, j-1):   # bord haut (v00,v10)
            quad((x0,y0,0.0),v00,v10,(x1,y0,0.0))
        if not cell_filled(i, j+1):   # bord bas (v01,v11)
            quad((x0,y1,0.0),(x1,y1,0.0),v11,v01)

# ----------------- ecriture STL binaire -----------------
path = f"/home/user/logiciel-3d/medaille_super_papa_{SLUG}.stl"
with open(path, "wb") as f:
    f.write(b"medaille super papa - heightmap solid".ljust(80, b" "))
    f.write(struct.pack("<I", len(tris)))
    z = struct.pack("<fff", 0.0, 0.0, 0.0)   # normale nulle (le slicer recalcule)
    for t in tris:
        f.write(z)
        f.write(struct.pack("<9f", *t))
        f.write(struct.pack("<H", 0))

print(f"OK : prenom = {PRENOM}")
print(f"  -> {path}")
print(f"  -> apercu_{SLUG}.png")
print(f"  triangles : {len(tris):,} | dimensions : {W_MM:.0f} x {H_MM:.0f} x {max(H):.1f} mm")
