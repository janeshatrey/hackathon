from PIL import Image
import numpy as np
from scipy import ndimage
S=float(__import__('sys').argv[1]) if len(__import__('sys').argv)>1 else 46.0
def run(f,name,cut=None,t=20):
    im=np.array(Image.open(f).convert('RGB')).astype(int)
    im[:240,:]=255; im[2200:,:]=255
    sil=np.load(f'plans/sil_{name}.npy')
    if cut is not None:
        yy,xx=np.mgrid[0:sil.shape[0],0:sil.shape[1]]
        keep=cut(xx,yy)
        sil=sil&keep
    dark=(im.sum(axis=2)<330)
    er=ndimage.binary_erosion(sil,structure=np.ones((3,3),bool),iterations=t)
    band=sil&~er
    wall=band&dark
    # perimeter length (px) approx = boundary pixel count of sil (4-neigh)
    bd=sil&~ndimage.binary_erosion(sil,structure=ndimage.generate_binary_structure(2,1))
    per=bd.sum()
    ext_area=sil.sum()/S**2
    wall_area=wall.sum()/S**2
    gifa=ext_area-wall_area
    print(name,'external-face area %.1f m2; ext wall dark in band %.1f m2; GIFA approx %.1f m2; perimeter %.1f m'%(ext_area,wall_area,gifa,per/S))
    np.save(f'plans/gifa_{name}.npy',sil&~wall)
    return sil
sg=run('plans/p-24.png','GF')
sf=run('plans/p-25.png','FF',cut=lambda x,y: ((x<1655)&(y<1226))|((x>=1655)&(y<1290)))
