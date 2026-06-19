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
BAIL_R, BAIL_r = 5.0, 2.0            # arceau D : rayon axe 5, tube R2 (Ø4) -> ouverture Ø6, hors-tout Ø14
NECK_R = 2.5                         # col de liaison flamme<->arceau

def build_corps():
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
    return corps.part

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
    flame=fp.part.moved(Location((0,0,SKIRT_H-OVERLAP)))
    tip_z=tip_z0+(SKIRT_H-OVERLAP)
    # ----- arceau porte-cles robuste (demi-cercle en D), construit hors du builder -----
    z_bar=tip_z+3.0
    arch=Torus(BAIL_R, BAIL_r).rotate(Axis.X, 90)
    arch=arch & Box(60,60,60).moved(Location((0,0,30)))          # moitie haute (z>=0)
    arch=arch.moved(Location((tip_x,0,z_bar)))
    bar =Cylinder(BAIL_r, 2*BAIL_R).rotate(Axis.Y, 90).moved(Location((tip_x,0,z_bar)))
    neck=Cylinder(NECK_R, 6.0).moved(Location((tip_x,0,tip_z-1.0)))
    bail=arch + bar + neck
    with BuildPart() as lid:
        with BuildSketch(Plane.XY): Circle(SKIRT_OR)
        extrude(amount=SKIRT_H)
        try:
            chamfer(lid.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], 1.6)
        except Exception: pass
        with BuildSketch(Plane.XY): Circle(FEM_MAJOR/2)
        extrude(amount=SKIRT_H-CEIL, mode=Mode.SUBTRACT)
        add(fem.moved(Location((0,0,1.0))))
        add(flame)
        add(bail)
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
