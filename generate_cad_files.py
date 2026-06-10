#!/usr/bin/env python3
"""Genere le contour du blason (medaille SUPER PAPA) aux cotes reelles, en DXF + SVG,
pour import dans Fusion 360. Unites = millimetres.
Seul le contour de l'ecusson est exporte (courbe complexe) ; le reste (texte, fente,
lisere, cartouche) se fait nativement dans Fusion pour rester parametrique/modifiable.
"""

# ---- cotes de la medaille (mm) ----
H = 75.0          # hauteur du blason
W = 60.0          # largeur du blason
CX = W / 2.0
SHOULDER = 0.50 * H   # hauteur des epaules (cotes droits)

def cubic(p0, p1, p2, p3, n=48):
    pts = []
    for i in range(1, n + 1):           # on saute le 1er point (continuite)
        t = i / n
        mt = 1 - t
        x = mt**3*p0[0] + 3*mt*mt*t*p1[0] + 3*mt*t*t*p2[0] + t**3*p3[0]
        y = mt**3*p0[1] + 3*mt*mt*t*p1[1] + 3*mt*t*t*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts

# ---- points du contour (repere image : y vers le bas, 0 = haut) ----
pts = [(0.0, 0.0), (W, 0.0), (W, SHOULDER)]
pts += cubic((W, SHOULDER), (W, 0.82*H), (CX + 0.34*W, 0.965*H), (CX, H))   # bas droit -> pointe
pts += cubic((CX, H), (CX - 0.34*W, 0.965*H), (0.0, 0.82*H), (0.0, SHOULDER))  # pointe -> bas gauche
# (le retour (0,SHOULDER)->(0,0) est implicite par la fermeture)

# ================= DXF (LWPOLYLINE fermee, y vers le haut) =================
def write_dxf(path):
    lines = ["0", "SECTION", "2", "ENTITIES",
             "0", "LWPOLYLINE", "8", "0", "100", "AcDbPolyline",
             "90", str(len(pts)), "70", "1"]      # 70=1 -> polyligne fermee
    for (x, y) in pts:
        lines += ["10", f"{x:.4f}", "20", f"{(H - y):.4f}"]   # y_dxf = H - y (point en bas)
    lines += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

# ================= SVG (path, y vers le bas, en mm) =================
def write_svg(path):
    d = f"M {pts[0][0]:.3f},{pts[0][1]:.3f} "
    for (x, y) in pts[1:]:
        d += f"L {x:.3f},{y:.3f} "
    d += "Z"
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">
  <path d="{d}" fill="none" stroke="#000000" stroke-width="0.3"/>
</svg>
'''
    with open(path, "w") as f:
        f.write(svg)

if __name__ == "__main__":
    write_dxf("/home/user/logiciel-3d/medaille_blason.dxf")
    write_svg("/home/user/logiciel-3d/medaille_blason.svg")
    print(f"OK : blason {W:.0f}x{H:.0f} mm, {len(pts)} points -> medaille_blason.dxf / .svg")
