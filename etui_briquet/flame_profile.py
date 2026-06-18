import numpy as np

# Flamme : goutte effilee qui monte, pointe principale nette + 1 langue laterale.
# Sens horaire depuis la base droite. 'S' = sommet pointu (cusp).
PTS = [
    (7.5, 0.0),
    (10.5, 5.5),
    (8.5, 11.0),
    (10.0, 17.0),
    (5.5, 23.0),
    (5.0, 29.0),
    (1.0, 36.0, 'S'),     # POINTE principale
    (-3.5, 28.0),
    (-7.5, 22.0),
    (-4.0, 17.5),         # creux
    (-11.0, 12.5, 'S'),   # langue laterale gauche (pointue)
    (-6.5, 8.0),          # creux
    (-9.0, 2.5),
    (-8.0, 0.0),
]

def _catmull(P, n_per=26):
    P=np.array(P,float); P=np.vstack([P[-1],P,P[0],P[1]]); out=[]
    for i in range(1,len(P)-2):
        p0,p1,p2,p3=P[i-1],P[i],P[i+1],P[i+2]
        for t in np.linspace(0,1,n_per,endpoint=False):
            t2,t3=t*t,t*t*t
            out.append(0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t2+(-p0+3*p1-3*p2+p3)*t3))
    return np.array(out)

def flame_outline(n_per=26, height=32.0):
    seq=[]
    for p in PTS:
        seq.append((p[0],p[1]))
        if len(p)==3:
            seq.append((p[0],p[1])); seq.append((p[0],p[1]))  # cusp net
    pts=_catmull(seq,n_per)
    pts[:,1]-=pts[:,1].min(); pts*=height/pts[:,1].max()
    return pts

if __name__=="__main__":
    from PIL import Image, ImageDraw
    pts=flame_outline(); S=9; pad=20
    xs,zs=pts[:,0],pts[:,1]
    W=int((xs.max()-xs.min())*S)+2*pad; H=int((zs.max()-zs.min())*S)+2*pad
    img=Image.new("RGB",(W,H),(28,32,40)); d=ImageDraw.Draw(img)
    def tp(p): return (pad+(p[0]-xs.min())*S, H-pad-(p[1]-zs.min())*S)
    d.polygon([tp(p) for p in pts], fill=(255,150,40), outline=(255,210,120))
    img.save("apercu_flamme.png")
    print("ok largeur",round(xs.max()-xs.min(),1),"hauteur",round(zs.max()-zs.min(),1))
