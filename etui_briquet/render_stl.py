import numpy as np, trimesh
from PIL import Image

def _rot(ax, ay, az):
    ax,ay,az=np.radians([ax,ay,az])
    Rx=np.array([[1,0,0],[0,np.cos(ax),-np.sin(ax)],[0,np.sin(ax),np.cos(ax)]])
    Ry=np.array([[np.cos(ay),0,np.sin(ay)],[0,1,0],[-np.sin(ay),0,np.cos(ay)]])
    Rz=np.array([[np.cos(az),-np.sin(az),0],[np.sin(az),np.cos(az),0],[0,0,1]])
    return Rz@Ry@Rx

def render(path, out, rot=(-65,0,25), size=520, base=(255,150,40), bg=(28,32,40)):
    m=trimesh.load(path); 
    if isinstance(m, trimesh.Scene): m=m.dump(concatenate=True)
    V=np.asarray(m.vertices); F=np.asarray(m.faces)
    R=_rot(*rot); Vr=V@R.T
    # vue physiquement correcte depuis +Y : right=-X, up=+Z, profondeur=Y
    sx,sy=-Vr[:,0],Vr[:,2]; depth=Vr[:,1]
    pad=30
    minx,maxx,miny,maxy=sx.min(),sx.max(),sy.min(),sy.max()
    sc=(size-2*pad)/max(maxx-minx,maxy-miny)
    px=pad+(sx-minx)*sc; py=size-pad-(sy-miny)*sc
    # normales
    tri=Vr[F]
    n=np.cross(tri[:,1]-tri[:,0], tri[:,2]-tri[:,0])
    ln=np.linalg.norm(n,axis=1); ln[ln==0]=1; n=n/ln[:,None]
    light=np.array([0.3,-0.7,0.6]); light/=np.linalg.norm(light)
    sh=np.clip(n@light,0,1)*0.8+0.2
    order=np.argsort(tri[:,:,1].mean(axis=1))  # loin -> pres
    img=Image.new("RGB",(size,size),bg)
    pix=img.load()
    # rasterisation simple par PIL polygon (peintre)
    from PIL import ImageDraw
    d=ImageDraw.Draw(img)
    for f in order:
        a,b,c=F[f]
        if n[f,1]>0.02:  # face arriere (normale vers camera -Y => n_y<0 visible)
            continue
        col=tuple(int(base[k]*sh[f]) for k in range(3))
        d.polygon([(px[a],py[a]),(px[b],py[b]),(px[c],py[c])], fill=col)
    img.save(out); return out

if __name__=="__main__":
    import sys
    render(sys.argv[1], sys.argv[2], rot=eval(sys.argv[3]) if len(sys.argv)>3 else (-65,0,25))
    print("ok", sys.argv[2])
