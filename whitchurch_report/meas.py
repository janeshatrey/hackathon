import json, numpy as np
from PIL import Image
from scipy import ndimage
S=45.7
im24=np.array(Image.open('plans/p-24.png').convert('RGB')).astype(int); im24[:240]=255; im24[2200:]=255
im25=np.array(Image.open('plans/p-25.png').convert('RGB')).astype(int); im25[:240]=255; im25[2200:]=255
gf=np.load('plans/sil_GF.npy'); ff0=np.load('plans/sil_FF.npy')
yy,xx=np.mgrid[0:ff0.shape[0],0:ff0.shape[1]]
ffcut=lambda x,y: ((x<1655)&(y<1226))|((x>=1655)&(y<1290))
ff=ff0&ffcut(xx,yy)
def gifa(im,sil,t=20):
    dark=(im.sum(axis=2)<330)
    er=ndimage.binary_erosion(sil,structure=np.ones((3,3),bool),iterations=t)
    wall=(sil&~er)&dark
    return (sil.sum()-wall.sum())/S**2, sil.sum()/S**2
GF,gfe=gifa(im24,gf); FF,ffe=gifa(im25,ff)
def near(im,c,t=9): return (abs(im[:,:,0]-c[0])<=t)&(abs(im[:,:,1]-c[1])<=t)&(abs(im[:,:,2]-c[2])<=t)
# pool hall incl tank
m=near(im24,(220,235,250)); lab,n=ndimage.label(m); k=np.argmax(ndimage.sum(m,lab,range(1,n+1)))+1
filled=ndimage.binary_fill_holes(lab==k); poolhall=filled.sum()/S**2
# fitness (pink) first floor: sum of pink components in column x<1400
pk=near(im25,(250,218,212)); pk[:, 1400:]=False
lab,n=ndimage.label(pk); sz=ndimage.sum(pk,lab,range(1,n+1))
fit=sum(s for s in sz if s>5000)/S**2
od=near(im25,(252,210,170)); od[:, :1500]=False
# studio 2 is right half
lab,n=ndimage.label(od); sz=ndimage.sum(od,lab,range(1,n+1)); st=max(sz)/S**2
bd=lambda s: s&~ndimage.binary_erosion(s,structure=ndimage.generate_binary_structure(2,1))
b=bd(gf); ys,xs=np.where(b)
M=dict(S=S,GF=GF,FF=FF,gf_footprint=gfe,ff_footprint=ffe,roof_plan=(gf|ff).sum()/S**2,
 block_perim=(ys<=1290).sum()/S,pool_perim=(ys>1290).sum()/S,poolhall=poolhall,fitness=fit,studio=st)
json.dump(M,open('meas.json','w'),indent=1); print(M)
