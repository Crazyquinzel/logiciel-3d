#!/usr/bin/env python3
"""Apercu (mockup) de la medaille Fete des Peres - ecusson / blason.
Rendu raster via Pillow uniquement (aucune dependance externe).
Sert d'apercu visuel AVANT modelisation Fusion 360.
"""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------- parametres geometriques (en pixels de la toile finale) ----------
SS = 3                      # supersampling
W_OUT, H_OUT = 1100, 1500   # toile finale
W, H = W_OUT * SS, H_OUT * SS

CX = W // 2                 # centre horizontal
# boite de l'ecusson (moins allonge : plus compact, ratio H/W ~1.25)
SHIELD_W = int(0.66 * W)
SHIELD_TOP = int(0.205 * H)
SHIELD_H = int(0.605 * H)

import os
THEME = os.environ.get("THEME", "gold")

if THEME == "noir":
    # rendu "PLA noir" (mat/satine)
    GOLD_DARK   = (8, 8, 10)
    GOLD_BASE   = (30, 30, 33)
    GOLD_FACE   = (46, 46, 50)
    GOLD_LIGHT  = (104, 104, 110)
    GOLD_HI     = (150, 150, 158)
    RELIEF_SHAD = (4, 4, 5)
    HALO_RGB    = (210, 215, 230)
    OUT_NAME    = "preview_medaille_noir.png"
    CAP_THEME   = "noir"
else:
    # couleurs "or medaille"
    GOLD_DARK   = (150, 112, 30)
    GOLD_BASE   = (198, 156, 52)
    GOLD_FACE   = (224, 190, 96)
    GOLD_LIGHT  = (244, 222, 150)
    GOLD_HI     = (252, 240, 200)
    RELIEF_SHAD = (132, 98, 24)
    HALO_RGB    = (255, 244, 210)
    OUT_NAME    = "preview_medaille.png"
    CAP_THEME   = "dore"

BG_TOP = (238, 240, 244)
BG_BOT = (205, 210, 218)

# ---------- helpers ----------
def cubic(p0, p1, p2, p3, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3*p0[0] + 3*mt*mt*t*p1[0] + 3*mt*t*t*p2[0] + t**3*p3[0]
        y = mt**3*p0[1] + 3*mt*mt*t*p1[1] + 3*mt*t*t*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts

def shield_polygon(cx, top, w, h, scale=1.0):
    """ecu francais : haut plat, epaules droites, pointe basse arrondie."""
    hw = w * 0.5 * scale
    bot = top + h * scale
    shoulder = top + 0.50 * h * scale
    # decalage pour centrer le scale autour du centre visuel
    pts = []
    pts.append((cx - hw, top))                 # haut gauche
    pts.append((cx + hw, top))                 # haut droit
    pts.append((cx + hw, shoulder))            # epaule droite
    # courbe bas droite -> pointe
    pts += cubic((cx + hw, shoulder),
                 (cx + hw, top + 0.82*h*scale),
                 (cx + 0.34*w*scale, top + 0.965*h*scale),
                 (cx, bot), 36)
    # courbe bas gauche (miroir, en remontant)
    pts += cubic((cx, bot),
                 (cx - 0.34*w*scale, top + 0.965*h*scale),
                 (cx - hw, top + 0.82*h*scale),
                 (cx - hw, shoulder), 36)
    return pts

def rotate(px, py, ox, oy, ang):
    s, c = math.sin(ang), math.cos(ang)
    dx, dy = px - ox, py - oy
    return (ox + dx*c - dy*s, oy + dx*s + dy*c)

def _leaf_pts(cx, cy, length, width, ang):
    n = 26
    pts = []
    for i in range(n + 1):
        t = i / n * 2 * math.pi
        ex = math.cos(t) * length * 0.5
        ey = math.sin(t) * width * 0.5 * (abs(math.sin(t))**0.35)
        pts.append(rotate(cx + ex, cy + ey, cx, cy, ang))
    return pts

def leaf(draw, cx, cy, length, width, ang, fill, outline, ow):
    """feuille de laurier = amande orientee, avec ombre de relief + nervure."""
    # ombre portee (relief) - legere pour rester discret
    draw.polygon(_leaf_pts(cx+3*SS, cy+4*SS, length, width, ang),
                 fill=(70, 52, 14, 70))
    pts = _leaf_pts(cx, cy, length, width, ang)
    draw.polygon(pts, fill=fill, outline=outline, width=ow)
    # nervure centrale
    a = rotate(cx - length*0.42, cy, cx, cy, ang)
    b = rotate(cx + length*0.42, cy, cx, cy, ang)
    draw.line([a, b], fill=outline, width=max(1, ow))

# ---------- toile + fond degrade ----------
img = Image.new("RGB", (W, H), BG_TOP)
dd = ImageDraw.Draw(img)
for y in range(H):
    t = y / H
    r = int(BG_TOP[0]*(1-t) + BG_BOT[0]*t)
    g = int(BG_TOP[1]*(1-t) + BG_BOT[1]*t)
    b = int(BG_TOP[2]*(1-t) + BG_BOT[2]*t)
    dd.line([(0, y), (W, y)], fill=(r, g, b))

draw = ImageDraw.Draw(img, "RGBA")

# ---------- RUBAN TRICOLORE (derriere la medaille, dans la fente) ----------
slot_y = SHIELD_TOP + int(0.055 * SHIELD_H)
ribbon_w = int(0.30 * SHIELD_W)
# deux pans qui montent en V depuis la fente
top_y = int(0.02 * H)
spread = int(0.10 * W)
def tricolore(quad):
    # quad = (xL_top,xR_top,xR_bot,xL_bot) ; remplit 3 bandes verticales
    (xlt, xrt, xrb, xlb, yt, yb) = quad
    cols = [(0, 45, 122), (245, 245, 245), (206, 17, 38)]  # bleu/blanc/rouge
    for k in range(3):
        a = k/3; b = (k+1)/3
        p = [(xlt+(xrt-xlt)*a, yt), (xlt+(xrt-xlt)*b, yt),
             (xlb+(xrb-xlb)*b, yb), (xlb+(xrb-xlb)*a, yb)]
        draw.polygon(p, fill=cols[k])
# pan gauche
tricolore((CX - spread - ribbon_w//2, CX - spread + ribbon_w//2,
           CX - ribbon_w//2, CX - ribbon_w - ribbon_w//4, top_y, slot_y + int(0.02*H)))
# pan droit
tricolore((CX + spread - ribbon_w//2, CX + spread + ribbon_w//2,
           CX + ribbon_w + ribbon_w//4, CX + ribbon_w//2, top_y, slot_y + int(0.02*H)))

# ---------- OMBRE PORTEE de la medaille ----------
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.polygon([(x+10*SS, y+14*SS) for (x, y) in shield_polygon(CX, SHIELD_TOP, SHIELD_W, SHIELD_H)],
           fill=(0, 0, 0, 110))
shadow = shadow.filter(ImageFilter.GaussianBlur(12*SS))
img.paste(shadow, (0, 0), shadow)
draw = ImageDraw.Draw(img, "RGBA")

# ---------- CORPS DE L'ECUSSON (chanfrein) ----------
outer = shield_polygon(CX, SHIELD_TOP, SHIELD_W, SHIELD_H, 1.0)
# tranche / chanfrein : ecusson exterieur fonce
draw.polygon(outer, fill=GOLD_DARK)
# bevel : couronne degradee (plusieurs ecus retreci)
steps = 16
for i in range(steps, -1, -1):
    s = 1.0 - 0.055 * (i/steps)
    t = i/steps
    col = (int(GOLD_BASE[0]*(1-t)+GOLD_DARK[0]*t),
           int(GOLD_BASE[1]*(1-t)+GOLD_DARK[1]*t),
           int(GOLD_BASE[2]*(1-t)+GOLD_DARK[2]*t))
    poly = shield_polygon(CX, SHIELD_TOP + int(0.028*SHIELD_H*(1-s)/0.055),
                          SHIELD_W, SHIELD_H, s)
    draw.polygon(poly, fill=col)
# face plate principale
face = shield_polygon(CX, SHIELD_TOP + int(0.028*SHIELD_H), SHIELD_W, SHIELD_H, 0.945)
draw.polygon(face, fill=GOLD_FACE)

# eclat lumineux haut-gauche
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.polygon(shield_polygon(CX - int(0.08*W), SHIELD_TOP - int(0.02*H),
                          SHIELD_W, SHIELD_H, 0.70), fill=(255, 255, 255, 55))
glow = glow.filter(ImageFilter.GaussianBlur(40*SS))
img.paste(glow, (0, 0), glow)
draw = ImageDraw.Draw(img, "RGBA")

# ---------- LISERE (bordure en relief) ----------
border = shield_polygon(CX, SHIELD_TOP + int(0.028*SHIELD_H), SHIELD_W, SHIELD_H, 0.90)
draw.line(border + [border[0]], fill=GOLD_LIGHT, width=int(0.011*W), joint="curve")
draw.line(border + [border[0]], fill=RELIEF_SHAD, width=int(0.004*W), joint="curve")

# ---------- FENTE PLATE pour le ruban (25 mm) ----------
fente_w = int(0.34 * SHIELD_W)
fente_h = int(0.030 * SHIELD_H)
fy = SHIELD_TOP + int(0.075 * SHIELD_H)
draw.rounded_rectangle([CX-fente_w//2, fy, CX+fente_w//2, fy+fente_h],
                       radius=fente_h//2, fill=(70, 55, 18, 255))
draw.rounded_rectangle([CX-fente_w//2, fy, CX+fente_w//2, fy+fente_h],
                       radius=fente_h//2, outline=GOLD_LIGHT, width=int(0.004*W))

# ---------- COURONNE DE LAURIERS (elliptique, symetrique, centree) ----------
def leaf_lanceole(cx, cy, L, Wl, ang, bend, fill, outline, ow):
    """feuille lanceolee (laurier) : pointue aux deux bouts, legerement courbee."""
    n = 18
    top, bot = [], []
    for i in range(n+1):
        u = i/n
        x = (u-0.5)*L
        prof = (math.sin(math.pi*u))**0.62        # largeur -> 0 aux pointes
        half = Wl*0.5*prof
        sy = bend*Wl*math.sin(math.pi*u)          # courbure de la nervure
        top.append((x, sy-half))
        bot.append((x, sy+half))
    local = top + bot[::-1]
    P = [rotate(cx+px, cy+py, cx, cy, ang) for (px, py) in local]
    draw.polygon([(p[0]+3*SS, p[1]+4*SS) for p in P], fill=(70, 52, 14, 70))  # relief
    draw.polygon(P, fill=fill, outline=outline, width=ow)

def draw_wreath():
    cx = CX
    cy = SHIELD_TOP + int(0.575*SHIELD_H)     # centre de la couronne
    rx = int(0.330*SHIELD_W)
    ry = int(0.275*SHIELD_H)
    L  = int(0.090*SHIELD_W)
    Wl = int(0.034*SHIELD_W)
    ow = max(1, int(0.0013*W))
    N  = 13                                   # feuilles par cote
    a0, a1 = 92.0, -66.0                      # du bas (92) au sommet droit (-66)
    # arc dense (cote droit) pour la tige + repere de tangente
    arc = [(cx+rx*math.cos(math.radians(a0+(a1-a0)*i/120)),
            cy+ry*math.sin(math.radians(a0+(a1-a0)*i/120))) for i in range(121)]
    for side in (+1, -1):
        # tige
        stem = [(2*cx-x, y) if side < 0 else (x, y) for (x, y) in arc]
        draw.line(stem, fill=GOLD_LIGHT, width=max(1, int(0.0018*W)), joint="curve")
        # feuilles regulierement reparties en angle
        for k in range(N):
            t = (k+0.5)/N
            a = math.radians(a0 + (a1-a0)*t)
            x = cx + rx*math.cos(a)
            y = cy + ry*math.sin(a)
            # tangente (sens de parcours) via derivee parametrique
            tx, ty = -rx*math.sin(a), ry*math.cos(a)
            tang = math.atan2(ty, tx) + math.pi          # sens bas->haut
            # feuille inclinee vers l'exterieur, posee sur la tige
            radial = math.atan2(y-cy, x-cx)
            ox = x + math.cos(radial)*Wl*0.30
            oy = y + math.sin(radial)*Wl*0.30
            ang = tang - math.radians(34)
            bend = -0.6
            if side < 0:                                  # miroir parfait
                ox = 2*cx - ox
                ang = math.pi - ang
                bend = 0.6
            # leger amenuisement vers les pointes
            sc = 0.82 + 0.18*math.sin(math.pi*t)
            leaf_lanceole(ox, oy, L*sc, Wl*sc, ang, bend, GOLD_LIGHT, RELIEF_SHAD, ow)

DRAW_WREATH = False     # lauriers retires -> medaille epuree
if DRAW_WREATH:
    draw_wreath()

# ---------- OUTILS DE BRICOLAGE (de chaque cote de SUPER PAPA) ----------
def circle_poly(cx, cy, r, n=30):
    return [(cx+r*math.cos(2*math.pi*i/n), cy+r*math.sin(2*math.pi*i/n)) for i in range(n)]

def _emit(tool, cx, cy, ang, fill=GOLD_LIGHT, outline=RELIEF_SHAD):
    """tool = (polys, cuts). Dessine relief + corps + creux (couleur face)."""
    polys, cuts = tool
    ow = max(1, int(0.0016*W))
    P = lambda poly: [rotate(cx+px, cy+py, cx, cy, ang) for (px, py) in poly]
    for poly in polys:                       # ombre de relief
        draw.polygon([(p[0]+4*SS, p[1]+5*SS) for p in P(poly)], fill=(70, 52, 14, 95))
    for poly in polys:                       # corps
        draw.polygon(P(poly), fill=fill, outline=outline, width=ow)
    for poly in cuts:                        # creux (trou d'anneau, gorge de fourche)
        draw.polygon(P(poly), fill=GOLD_FACE, outline=outline, width=ow)

def wrench_tool(L):
    """cle mixte : anneau (box) d'un cote, fourche ouverte de l'autre, manche fin."""
    polys, cuts = [], []
    # manche fin et legerement fusele
    polys.append([(-0.34*L, -0.052*L), (0.34*L, -0.045*L),
                  (0.34*L, 0.045*L), (-0.34*L, 0.052*L)])
    # --- anneau (cote gauche) ---
    polys.append(circle_poly(-0.42*L, 0, 0.155*L))
    cuts.append(circle_poly(-0.42*L, 0, 0.082*L))           # trou
    # --- fourche ouverte (cote droit) ---
    polys.append(circle_poly(0.42*L, 0, 0.150*L))
    # gorge en V ouverte vers l'exterieur (+x)
    cuts.append([(0.40*L, -0.058*L), (0.66*L, -0.10*L),
                 (0.66*L, 0.10*L), (0.40*L, 0.058*L)])
    return polys, cuts

def hammer_tool(L):
    """marteau a griffe : manche fusele + tete + panne plate + griffe fendue."""
    polys, cuts = [], []
    # manche (legerement fusele, pommeau)
    polys.append([(-0.56*L, -0.050*L), (0.14*L, -0.044*L),
                  (0.14*L, 0.044*L), (-0.56*L, 0.050*L)])
    polys.append(circle_poly(-0.56*L, 0, 0.060*L, 18))      # pommeau
    # oeil / collet (jonction tete-manche)
    polys.append([(0.06*L, -0.085*L), (0.26*L, -0.085*L),
                  (0.26*L, 0.085*L), (0.06*L, 0.085*L)])
    # tete perpendiculaire au manche (barre verticale)
    polys.append([(0.12*L, -0.30*L), (0.30*L, -0.30*L),
                  (0.30*L, 0.30*L), (0.12*L, 0.30*L)])
    # panne plate (cote +y) legerement evasee
    polys.append([(0.10*L, 0.28*L), (0.32*L, 0.28*L),
                  (0.36*L, 0.42*L), (0.06*L, 0.42*L)])
    # griffe recourbee (cote -y) : deux dents bien separees
    polys.append([(0.30*L, -0.28*L), (0.345*L, -0.42*L), (0.305*L, -0.56*L),
                  (0.255*L, -0.52*L), (0.275*L, -0.40*L), (0.25*L, -0.30*L)])   # dent ext
    polys.append([(0.12*L, -0.28*L), (0.075*L, -0.42*L), (0.115*L, -0.56*L),
                  (0.165*L, -0.52*L), (0.145*L, -0.40*L), (0.17*L, -0.30*L)])   # dent int
    return polys, cuts

def draw_tools():
    yC = SHIELD_TOP + int(0.520*SHIELD_H)
    dx = int(0.345*SHIELD_W)
    L = int(0.240*SHIELD_W)
    _emit(wrench_tool(L), CX-dx, yC, math.radians(-90-10))   # cle a gauche
    _emit(hammer_tool(L), CX+dx, yC, math.radians(-90+10))   # marteau a droite

DRAW_TOOLS = False     # outils retires -> medaille 100% epuree
if DRAW_TOOLS:
    draw_tools()

# ---------- TEXTE ----------
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(sz): return ImageFont.truetype(FONT, sz)

def halo(cx, cy, rx, ry):
    """halo lumineux doux pour mettre le texte en valeur."""
    h = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(h)
    hd.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=HALO_RGB + (70,))
    h = h.filter(ImageFilter.GaussianBlur(28*SS))
    img.paste(h, (0, 0), h)

def ctext(s, y, sz, fill=GOLD_HI, shadow=RELIEF_SHAD, round_amt=0.085):
    f = font(sz)
    sw = max(1, int(sz*round_amt))   # contour -> lettres plus rondes et 'pleines'
    bbox = draw.textbbox((0, 0), s, font=f, stroke_width=sw)
    tw = bbox[2]-bbox[0]
    x = CX - tw//2 - bbox[0]
    # ombre relief
    draw.text((x+int(0.006*W), y+int(0.006*W)), s, font=f, fill=shadow,
              stroke_width=sw, stroke_fill=shadow)
    # liseré sombre fin (arete du relief) puis remplissage clair
    draw.text((x, y), s, font=f, fill=fill, stroke_width=sw, stroke_fill=GOLD_DARK)

# halo de mise en valeur derriere le bloc principal (recentre)
halo(CX, SHIELD_TOP + int(0.49*SHIELD_H), int(0.36*SHIELD_W), int(0.26*SHIELD_H))
draw = ImageDraw.Draw(img, "RGBA")

# ---- CARTOUCHE PRENOM (zone personnalisable, au-dessus de SUPER PAPA) ----
cy_name = SHIELD_TOP + int(0.350*SHIELD_H)
cw, ch = int(0.52*SHIELD_W), int(0.090*SHIELD_H)
x0, y0, x1, y1 = CX-cw//2, cy_name-ch//2, CX+cw//2, cy_name+ch//2
rad = ch//2
# cadre grave (leger creux) : ombre haute + reflet bas
draw.rounded_rectangle([x0, y0, x1, y1], radius=rad, fill=GOLD_BASE)
draw.rounded_rectangle([x0, y0, x1, y1], radius=rad, outline=RELIEF_SHAD, width=int(0.004*W))
draw.line([(x0+rad, y1-int(0.002*W)), (x1-rad, y1-int(0.002*W))],
          fill=GOLD_LIGHT, width=int(0.0025*W))
# petits losanges decoratifs aux extremites
for sx in (x0+rad, x1-rad):
    draw.regular_polygon((sx, cy_name, int(0.012*W)), 4, rotation=45,
                         fill=GOLD_LIGHT, outline=RELIEF_SHAD)
# texte d'exemple (placeholder) du prenom
nf = font(int(0.055*SHIELD_W))
ph = "‹ Prénom ›"
bb = draw.textbbox((0,0), ph, font=nf)
draw.text((CX-(bb[2]-bb[0])//2 - bb[0], cy_name-(bb[3]+bb[1])//2),
          ph, font=nf, fill=GOLD_HI)

ctext("SUPER", SHIELD_TOP + int(0.460*SHIELD_H), int(0.130*SHIELD_W))
ctext("PAPA",  SHIELD_TOP + int(0.600*SHIELD_H), int(0.195*SHIELD_W))

# ---------- legende ----------
lf = font(int(0.022*W))
cap = "Apercu (%s) — medaille ecusson 'SUPER PAPA' (modele Fusion 360)" % CAP_THEME
bbox = draw.textbbox((0,0), cap, font=lf)
draw.text((CX-(bbox[2]-bbox[0])//2, H-int(0.045*H)), cap, font=lf, fill=(90,95,105))

# ---------- export ----------
img = img.resize((W_OUT, H_OUT), Image.LANCZOS)
out = "/home/user/logiciel-3d/" + OUT_NAME
img.save(out, quality=95)
print("OK ->", out, img.size)
