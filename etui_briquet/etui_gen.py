#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L'Atelier Pixelise — Etui briquet flamme (modele Clipper).
Reproduit la recette validee : build123d + bd_warehouse IsoThread (M27x3),
end_finishes=("fade","fade"), solide plein puis cavite -> pieces watertight.
Genere : corps_b123.stl, couv_b123.stl, etui_clipper_FINAL.stl (2 pieces sur 1 plateau).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build123d import *
from bd_warehouse.thread import IsoThread
from flame_profile import flame_outline
import numpy as np, trimesh

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------- parametres Clipper (recap section 10) -----------------
WALL=2.5; CLR=1.0
BX,BP=22.0,18.0                      # section briquet L x P
IN_X,IN_Y=(BX+CLR)/2,(BP+CLR)/2      # demi-axes cavite
OUT_X,OUT_Y=IN_X+WALL,IN_Y+WALL      # demi-axes exterieur tube
CORPS_H=52.0; TRANS_H=6.0
PITCH=3.0; THREAD_LEN=9.0; JEU=0.4
COL_MAJOR=27.0; FEM_MAJOR=COL_MAJOR+JEU
SKIRT_WALL=2.5; SKIRT_OR=FEM_MAJOR/2+SKIRT_WALL
SKIRT_H=13.0; CEIL=2.0
FLAME_H=32.0; FLAME_T=16.0; OVERLAP=2.5
HOLE_DROP = 6.0                      # trou perce a 6 mm sous la pointe de la flamme
HOLE_R = 2.0                         # rayon du trou porte-cles (Ø4 max, reduit auto si peu de matiere)
FLAME_FILLET = 0.3                   # arrondi du contour de la flamme (finition polie)
FONT = os.path.join(HERE, "DejaVuSans-Bold.ttf")
FONT_PIXEL = os.path.join(HERE, "PressStart2P.ttf")
FONTS = {"pixel": FONT_PIXEL, "standard": FONT}
TEXT_ZC = 29.0                       # hauteur du bloc texte sur le tube
TEXT_W, ROW_H = 26.0, 14.0           # largeur/hauteur max d'une ligne (mm)
MOTIF_SIZE = 13.0                    # taille du motif (mm)
EMBOSS_H = 1.2                       # hauteur du relief (mm)

def _fit_font_size(s, max_w, max_h, font_path):
    from PIL import ImageFont
    probe=100; f=ImageFont.truetype(font_path, probe)
    b=f.getbbox(s); w=(b[2]-b[0])/probe; h=(b[3]-b[1])/probe
    if w<=0 or h<=0: return max_h
    return max(2.0, min(max_w/w, max_h/h))

def _motif_pts(name, size):
    """Renvoie une LISTE de contours (x,z) centres, hauteur ~ size, ou None."""
    import math
    name=(name or "").lower()
    if name in ("coeur","cœur","heart"):
        P=[]
        for k in range(0,360,6):
            t=math.radians(k)
            x=16*math.sin(t)**3
            y=13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
            P.append((x,y))
        sc=size/(max(p[1] for p in P)-min(p[1] for p in P))
        cy=(max(p[1] for p in P)+min(p[1] for p in P))/2
        return [[(x*sc,(y-cy)*sc) for x,y in P]]
    if name in ("etoile","étoile","star"):
        R=size/2; r=R*0.42; P=[]
        for i in range(10):
            a=math.pi/2 + i*math.pi/5; rad=R if i%2==0 else r
            P.append((rad*math.cos(a), rad*math.sin(a)))
        return [P]
    if name=="couronne":
        # reprise de la couronne des medailles (bandeau + 3 pointes + billes)
        h=size; w=h*0.94
        crown=[(-w/2,-0.42*h),(-w/2,0.33*h),(-w/4,-0.13*h),(0,0.45*h),
               (w/4,-0.13*h),(w/2,0.33*h),(w/2,-0.42*h)]
        rr=0.085*h
        def ball(cx,cz):
            return [(cx+rr*math.cos(2*math.pi*k/16), cz+rr*math.sin(2*math.pi*k/16)) for k in range(16)]
        return [crown, ball(0,0.45*h), ball(-w/2,0.33*h), ball(w/2,0.33*h)]
    if name=="moustache":
        A=size*0.92; H=size*0.78
        wing=[(0.10,-0.02),(0.05,0.18),(0.42,0.25),(0.78,0.21),(1.00,0.36),
              (0.90,0.05),(0.55,-0.07),(0.30,-0.22),(0.16,-0.16)]
        right=[(x*A,y*H) for x,y in wing]
        left=[(-x*A,y*H) for x,y in wing]
        return [right,left]
    return None

def build_corps(lines=None, motif="", font="pixel", engrave_depth=None, split_relief=False):
    """split_relief=True -> renvoie (base, relief) separes (relief=None si pas de texte/motif),
    pour pouvoir imprimer le texte/motif dans une AUTRE couleur (AMS) que le corps."""
    ext=IsoThread(major_diameter=COL_MAJOR, pitch=PITCH, length=THREAD_LEN,
                  external=True, end_finishes=("fade","fade"), hand="right")
    root_r=ext.min_radius
    z_col=CORPS_H+TRANS_H
    # paroi du col >= ~1.1 mm pour rester imprimable (evite la "couche vide" a la base du col)
    bore_r=min(IN_X, root_r-1.1)
    with BuildPart() as corps:
        with BuildSketch(Plane.XY): Ellipse(OUT_X, OUT_Y)
        extrude(amount=CORPS_H)
        with BuildSketch(Plane.XY.offset(CORPS_H)): Ellipse(OUT_X, OUT_Y)
        with BuildSketch(Plane.XY.offset(z_col)): Circle(root_r)
        loft()
        with BuildSketch(Plane.XY.offset(z_col)): Circle(root_r)
        extrude(amount=THREAD_LEN)
        add(ext.moved(Location((0,0,z_col))))
        with BuildSketch(Plane.XY.offset(WALL)): Ellipse(IN_X, IN_Y)
        extrude(amount=CORPS_H-WALL, mode=Mode.SUBTRACT)
        with BuildSketch(Plane.XY.offset(CORPS_H)): Circle(bore_r)
        extrude(amount=TRANS_H+THREAD_LEN, mode=Mode.SUBTRACT)
    # ----- texte + motif en RELIEF (projetes sur la face bombee, puis extrudes) -----
    base=corps.part
    rows=[r for r in (lines or []) if r.strip()]
    mouts=_motif_pts(motif, MOTIF_SIZE)
    if not rows and not mouts:
        return (base, None) if split_relief else base
    gap=2.2; n=len(rows); rh=ROW_H if n<=1 else ROW_H-1.5
    text_h=(n*rh+(n-1)*gap) if rows else 0.0
    total=text_h + (MOTIF_SIZE+gap if mouts else 0.0)
    ztop=TEXT_ZC + total/2
    feats=[]                                   # (sketch, z_centre)
    if mouts:
        zc=ztop-MOTIF_SIZE/2
        for outline in mouts:
            with BuildSketch(Plane.XY) as msk:
                with BuildLine(): Polyline([(float(a),float(b)) for a,b in outline], close=True)
                make_face()
            feats.append((msk.sketch, zc))
        ztop-=MOTIF_SIZE+gap
    fontpath=FONTS.get(font, FONT_PIXEL)
    z0=ztop-rh/2
    for i,row in enumerate(rows):
        fs=_fit_font_size(row, TEXT_W, rh, fontpath)
        with BuildSketch(Plane.XY) as tsk:
            Text(row, font_size=fs, font_path=fontpath)
        feats.append((tsk.sketch, z0-i*(rh+gap)))
    solids=[]
    for sketch,zc in feats:
        plane=Plane(origin=(0,OUT_Y+6,zc), x_dir=(-1,0,0), z_dir=(0,1,0))
        for f in plane.from_local_coords(sketch).faces():
            for pf in f.project_to_shape(base, direction=(0,-1,0)):
                ctr=pf.center()
                try: ny=pf.normal_at(ctr).Y
                except Exception:
                    try: ny=pf.normal_at().Y
                    except Exception: ny=1.0
                if ctr.Y<=0 or ny<=0.2:        # garder UNIQUEMENT la face avant exterieure
                    continue
                try:
                    s=extrude(pf, amount=EMBOSS_H, dir=(0,1,0))
                except Exception:
                    continue
                if s is None or getattr(s,"wrapped",None) is None: continue
                try:
                    if s.volume < 1e-6: continue
                except Exception:
                    continue
                solids.append(s)
    if split_relief:
        relief=None
        for s in solids:
            try: relief=s if relief is None else relief+s
            except Exception: pass
        return base, relief
    res=base
    for s in solids:
        try: res=res+s
        except Exception: pass
    return res

def build_couvercle():
    fem=IsoThread(major_diameter=FEM_MAJOR, pitch=PITCH, length=THREAD_LEN,
                  external=False, end_finishes=("fade","fade"), hand="right")
    fo=flame_outline(n_per=14, height=FLAME_H)
    flame_pts=[(float(x),float(z)) for x,z in fo]
    ti=int(np.argmax(fo[:,1])); tip_x, tip_z0=float(fo[ti,0]), float(fo[ti,1])
    with BuildPart() as fp:
        with BuildSketch(Plane.XZ):
            with BuildLine(): Polyline(flame_pts, close=True)
            make_face()
        extrude(amount=FLAME_T/2, both=True)
        # arrondi du contour (silhouette moins "decoupee au cutter", plus poli)
        perim=[e for e in fp.part.edges().filter_by(GeomType.LINE) if abs(e.length-FLAME_T)<0.05]
        try: fillet(perim, FLAME_FILLET)
        except Exception: pass
    flame=fp.part.moved(Location((0,0,SKIRT_H-OVERLAP)))
    tip_z=tip_z0+(SKIRT_H-OVERLAP)
    # ----- trou traversant pour anneau porte-cles, pres du haut de la flamme -----
    zc_local=fo[:,1].max()-HOLE_DROP                       # un peu sous la pointe
    band=fo[(fo[:,1]>zc_local-1.6)&(fo[:,1]<zc_local+1.6)]
    hx=float(band[:,0].mean()) if len(band) else tip_x
    xspan=float(band[:,0].max()-band[:,0].min()) if len(band) else 6.0
    hole_r=min(HOLE_R, max(1.1, xspan/2-1.6))             # garde >=1.6mm de matiere autour
    hz=zc_local+(SKIRT_H-OVERLAP)
    hole=Cylinder(hole_r, FLAME_T+6).rotate(Axis.X, 90).moved(Location((hx,0,hz)))
    with BuildPart() as lid:
        with BuildSketch(Plane.XY): Circle(SKIRT_OR)
        extrude(amount=SKIRT_H)
        zedges=lid.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)
        try: chamfer(zedges[-1], 1.6)              # haut (jonction flamme) - poli
        except Exception: pass
        try: chamfer(zedges[0], 0.8)                # bas (entree de visse) - plus discret
        except Exception: pass
        with BuildSketch(Plane.XY): Circle(FEM_MAJOR/2)
        extrude(amount=SKIRT_H-CEIL, mode=Mode.SUBTRACT)
        add(fem.moved(Location((0,0,1.0))))
        add(flame)
        add(hole, mode=Mode.SUBTRACT)
        # chanfrein du trou porte-cles (confort, pas d'arete vive au toucher)
        try:
            hedges=lid.edges().filter_by(GeomType.CIRCLE).filter_by(lambda e: abs(e.radius-hole_r)<0.05)
            chamfer(hedges, 0.4)
        except Exception: pass
    return lid.part

def check(path):
    m=trimesh.load(path)
    print(f"  {os.path.basename(path):28s} watertight={m.is_watertight} "
          f"vol={m.volume/1000:6.2f}cm3 bbox={[round(x,1) for x in m.extents]}")
    return m

if __name__=="__main__":
    print("Construction du corps...")
    corps=build_corps(); export_stl(corps, f"{HERE}/corps_b123.stl")
    print("Construction du couvercle...")
    couv=build_couvercle(); export_stl(couv, f"{HERE}/couv_b123.stl")
    print("Verification :")
    mc=check(f"{HERE}/corps_b123.stl"); ml=check(f"{HERE}/couv_b123.stl")
    # plateau final : 2 pieces cote a cote
    ml2=ml.copy(); ml2.apply_translation([SKIRT_OR+OUT_X+6, 0, 0])
    plate=trimesh.util.concatenate([mc, ml2]); plate.export(f"{HERE}/etui_clipper_FINAL.stl")
    print(f"  etui_clipper_FINAL.stl : plateau { [round(x,1) for x in plate.extents] }")
