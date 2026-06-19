#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L'Atelier Pixelisé — Personnalisation de l'étui briquet flamme (Clipper).
Tape 1 à 2 lignes de texte + un motif → grave en creux sur le corps et génère le STL.

Le COUVERCLE (flamme + trou porte-clés) ne change pas : il est construit une seule fois et réutilisé.
Seul le CORPS (gravé) est régénéré à chaque commande.

Dépendances : build123d, bd_warehouse, trimesh, numpy, pillow
"""
import os, sys, re, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))

MOTIFS = [("Aucun",""),("Cœur","coeur"),("Étoile","etoile"),
          ("Couronne","couronne"),("Moustache","moustache")]
PRESETS = ["(libre)","DAD","PAPA","#1 DAD","SUPER / PAPA","PAPI","TONTON"]

def _slug(*parts):
    clean=[re.sub(r"[^A-Za-z0-9]+","",p) for p in parts]
    return "_".join(p for p in clean if p) or "etui"

def generate(lines, motif, outdir, status=lambda s: None, font="pixel", color_split=False):
    """Construit le corps grave + assemble avec le couvercle. Retourne le chemin du plateau.
    color_split=True -> exporte aussi le texte/motif en relief a part (corps_relief_*.stl),
    pour pouvoir l'imprimer dans une AUTRE couleur AMS que le corps (objets separes au slicer)."""
    from build123d import export_stl
    import trimesh
    import etui_gen as E
    os.makedirs(outdir, exist_ok=True)
    slug=_slug(*lines, motif)

    # couvercle (construit 1 seule fois, mis en cache a cote de l'appli)
    couv_cache=os.path.join(HERE,"couv_b123.stl")
    if not os.path.exists(couv_cache):
        status("Construction du couvercle (1re fois, ~1 min)…")
        export_stl(E.build_couvercle(), couv_cache)

    status("Construction du corps en relief… (~1 min)")
    try:
        base, relief = E.build_corps(lines=lines, motif=motif, font=font, split_relief=True)
    except Exception:
        if font!="standard":
            status("Police pixel indispo pour ces caractères → police standard")
            base, relief = E.build_corps(lines=lines, motif=motif, font="standard", split_relief=True)
        else:
            raise

    relief_path=None
    if color_split and relief is not None:
        base_path=os.path.join(outdir, f"corps_base_{slug}.stl")
        relief_path=os.path.join(outdir, f"corps_motif_{slug}.stl")
        export_stl(base, base_path)
        export_stl(relief, relief_path)
        corps_path=base_path
    else:
        corps=base+relief if relief is not None else base
        corps_path=os.path.join(outdir, f"corps_{slug}.stl")
        export_stl(corps, corps_path)

    status("Assemblage du plateau…")
    mc=trimesh.load(corps_path); ml=trimesh.load(couv_cache)
    ml.apply_translation([E.SKIRT_OR+E.OUT_X+6, 0, 0])
    parts=[mc, ml]
    if relief_path:
        mr=trimesh.load(relief_path); parts.append(mr)
    plate=trimesh.util.concatenate(parts)
    final=os.path.join(outdir, f"etui_{slug}_FINAL.stl")
    plate.export(final)
    return final, relief_path

# ----------------------------- INTERFACE -----------------------------
def run_gui():
    import tkinter as tk
    from tkinter import messagebox
    OUTDIR=os.path.join(HERE,"STL")
    BG="#1f2937"
    root=tk.Tk(); root.title("Étui briquet — Personnalisation")
    root.geometry("440x520"); root.configure(bg=BG); root.resizable(False,False)

    tk.Label(root,text="🔥  Étui briquet flamme",bg=BG,fg="#f3f4f6",
             font=("Segoe UI",15,"bold")).pack(pady=(14,2))
    tk.Label(root,text="Modèle : Clipper",bg=BG,fg="#9ca3af",
             font=("Segoe UI",9)).pack()

    tk.Label(root,text="Texte à graver (1 à 2 lignes) :",bg=BG,fg="#cbd5e1",
             font=("Segoe UI",11)).pack(pady=(12,2))
    l1=tk.StringVar(); l2=tk.StringVar()
    tk.Entry(root,textvariable=l1,font=("Segoe UI",13),justify="center",width=22).pack(pady=2)
    tk.Entry(root,textvariable=l2,font=("Segoe UI",13),justify="center",width=22).pack(pady=2)

    # presets
    pv=tk.StringVar(value="(libre)")
    def apply_preset(*_):
        v=pv.get()
        if v=="(libre)": return
        if "/" in v: a,b=[x.strip() for x in v.split("/",1)]; l1.set(a); l2.set(b)
        else: l1.set(v); l2.set("")
    fr=tk.Frame(root,bg=BG); fr.pack(pady=(6,0))
    tk.Label(fr,text="Préréglage :",bg=BG,fg="#9ca3af",font=("Segoe UI",10)).pack(side="left")
    om=tk.OptionMenu(fr,pv,*PRESETS,command=apply_preset)
    om.config(font=("Segoe UI",10),bg="#374151",fg="white",relief="flat",highlightthickness=0)
    om["menu"].config(bg="#374151",fg="white"); om.pack(side="left",padx=6)

    fr2=tk.Frame(root,bg=BG); fr2.pack(pady=(12,0))
    tk.Label(fr2,text="Motif :",bg=BG,fg="#cbd5e1",font=("Segoe UI",11)).pack(side="left")
    mv=tk.StringVar(value="Aucun")
    om2=tk.OptionMenu(fr2,mv,*[m[0] for m in MOTIFS])
    om2.config(font=("Segoe UI",11),bg="#374151",fg="white",relief="flat",
               highlightthickness=0,width=11); om2["menu"].config(bg="#374151",fg="white")
    om2.pack(side="left",padx=6)

    fr3=tk.Frame(root,bg=BG); fr3.pack(pady=(8,0))
    tk.Label(fr3,text="Police :",bg=BG,fg="#cbd5e1",font=("Segoe UI",11)).pack(side="left")
    fv=tk.StringVar(value="Pixel")
    om3=tk.OptionMenu(fr3,fv,"Pixel","Standard")
    om3.config(font=("Segoe UI",11),bg="#374151",fg="white",relief="flat",
               highlightthickness=0,width=11); om3["menu"].config(bg="#374151",fg="white")
    om3.pack(side="left",padx=6)

    cv=tk.BooleanVar(value=False)
    cb=tk.Checkbutton(root,text="Texte/motif dans une AUTRE couleur (fichier séparé pour l'AMS)",
                       variable=cv,bg=BG,fg="#cbd5e1",selectcolor="#374151",
                       activebackground=BG,activeforeground="#cbd5e1",
                       font=("Segoe UI",9)); cb.pack(pady=(10,0))

    status=tk.Label(root,text="",bg=BG,fg="#93c5fd",font=("Segoe UI",9),
                    wraplength=400,justify="center"); status.pack(pady=(10,0))
    btn_holder={}

    def set_status(s): status.config(text=s); root.update_idletasks()

    def worker():
        lines=[l1.get().strip(), l2.get().strip()]
        motif=dict(MOTIFS)[mv.get()]
        font="pixel" if fv.get()=="Pixel" else "standard"
        try:
            final, relief_path=generate(lines, motif, OUTDIR, set_status, font=font, color_split=cv.get())
            if relief_path:
                set_status("✅ Créé : "+os.path.basename(final)+" + "+os.path.basename(relief_path)+" (texte/motif a part)")
            else:
                set_status("✅ Créé : "+os.path.basename(final))
            try:
                if sys.platform.startswith("win"): os.startfile(OUTDIR)   # noqa
                elif sys.platform=="darwin": os.system('open "%s"'%OUTDIR)
                else: os.system('xdg-open "%s"'%OUTDIR)
            except Exception: pass
        except Exception as e:
            set_status("Erreur : %s"%e)
        finally:
            btn_holder["b"].config(state="normal", text="Créer le fichier STL")

    def go():
        if not (l1.get().strip() or l2.get().strip() or dict(MOTIFS)[mv.get()]):
            messagebox.showwarning("Vide","Tape au moins une ligne de texte ou choisis un motif.")
            return
        btn_holder["b"].config(state="disabled", text="Génération… (patiente ~1-2 min)")
        threading.Thread(target=worker, daemon=True).start()

    b=tk.Button(root,text="Créer le fichier STL",command=go,font=("Segoe UI",12,"bold"),
                bg="#ef6c1a",fg="white",activebackground="#c75712",relief="flat",
                padx=10,pady=7); b.pack(pady=14); btn_holder["b"]=b
    tk.Label(root,text="La 1re génération construit le couvercle (~1 min de plus).",
             bg=BG,fg="#6b7280",font=("Segoe UI",8)).pack()
    root.mainloop()

if __name__=="__main__":
    if len(sys.argv)>1:   # CLI : python perso_app.py "DAD" "JULIEN" coeur
        a=sys.argv+["","",""]
        print(generate([a[1],a[2]], a[3], os.path.join(HERE,"STL"), print, color_split=True))
    else:
        run_gui()
