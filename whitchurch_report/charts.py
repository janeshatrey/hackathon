import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from PIL import Image
R=json.load(open('model.json'))
OUT='/home/user/hackathon/whitchurch_report/figs/'
INK='#0b0b0b'; INK2='#52514e'; GRID='#e6e5e1'
BLUE='#2a78d6'; ORANGE='#eb6834'; AQUA='#1baf7a'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':INK2,'axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2})
# ---- Fig 1 annotated plans
fig,axs=plt.subplots(1,2,figsize=(6.6,4.0))
def panel(ax,f,name,bbox,title,extra=None):
    im=np.array(Image.open(f).convert('RGB')).astype(float)
    m=np.load(f'plans/gifa_{name}.npy')
    ov=im.copy()
    ov[m]=0.55*ov[m]+0.45*np.array([42,120,214])
    x0,x1,y0,y1=bbox
    ax.imshow(ov[y0:y1,x0:x1].astype(np.uint8)); ax.axis('off'); ax.set_title(title,fontsize=8.5,color=INK,loc='left')
    return x0,y0
panel(axs[0],'plans/p-24.png','GF',(900,2620,290,2170),f"Ground floor: GIFA {R['gifa']['GF']:,} m²")
x0,y0=panel(axs[1],'plans/p-25.png','FF',(900,2620,290,2170),f"First floor: GIFA {R['gifa']['FF']:,} m²")
# void annotation on FF
axs[1].text((1700-900),(1650-290),'Void over pool hall\n(excluded)',ha='center',va='center',fontsize=7.5,color=INK2,bbox=dict(fc='white',ec='none',alpha=0.8,pad=1.5))
fig.legend(handles=[Patch(fc=BLUE,alpha=0.55,label='Measured as GIFA (to internal wall faces)')],loc='lower center',frameon=False,fontsize=7.5,ncol=1)
fig.tight_layout(rect=(0,0.06,1,0.97))
fig.savefig(OUT+'fig1_gifa.png',dpi=220); plt.close(fig)
# ---- Fig 2 tornado
sens=R['sens']; base=R['est']['tot']
rows=sorted(sens,key=lambda s:-(abs(s[3])+abs(s[4])))
fig,ax=plt.subplots(figsize=(6.6,3.2))
for i,s in enumerate(rows[::-1]):
    ax.barh(i,s[3]/1e6,color=ORANGE,height=0.5)
    ax.barh(i,s[4]/1e6,color=BLUE,height=0.5)
    ax.text(min(s[3],0)/1e6-0.04,i,f'{s[1]}',ha='right',va='center',fontsize=7.2,color=INK2)
    ax.text(max(s[4],0)/1e6+0.04,i,f'{s[2]}',ha='left',va='center',fontsize=7.2,color=INK2)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([s[0] for s in rows[::-1]],color=INK)
ax.axvline(0,color=INK2,lw=0.8)
ax.set_xlim(-3.0,1.7); ax.set_xlabel('Change in cost limit incl. inflation (£m), base £11.95m')
ax.grid(axis='x',color=GRID,lw=0.6); ax.set_axisbelow(True)
for sp in ('top','right','left'): ax.spines[sp].set_visible(False)
ax.legend(handles=[Patch(fc=ORANGE,label='Downside value (lower cost)'),Patch(fc=BLUE,label='Upside value (higher cost)')],frameon=False,fontsize=7.5,loc='upper center',bbox_to_anchor=(0.5,-0.2),ncol=2)
fig.tight_layout(); fig.savefig(OUT+'fig2_sens.png',dpi=220); plt.close(fig)
# ---- Fig 3 S-curve
E=R['evm']; per=[0]+[e['p'] for e in E]
pv=[0]+[e['PV']/1e6 for e in E]; ev=[0]+[e['EV']/1e6 for e in E]; ac=[0]+[e['AC']/1e6 for e in E]
fig,ax=plt.subplots(figsize=(6.6,3.4))
ax.plot(per,pv,color=BLUE,lw=2,marker='o',ms=5,mfc=BLUE,mec='white',mew=1.2)
ax.plot(per,ev,color=AQUA,lw=2,marker='o',ms=5,mfc=AQUA,mec='white',mew=1.2)
ax.plot(per,ac,color=ORANGE,lw=2,marker='o',ms=5,mfc=ORANGE,mec='white',mew=1.2)
ax.axhline(14.4,color=INK2,lw=0.8,ls=(0,(4,3))); ax.text(0.05,14.55,'BAC £14.40m',fontsize=7.5,color=INK2)
ax.text(6.08,14.4,'PV 14.40',fontsize=7.5,color=BLUE,va='bottom'); ax.text(6.08,13.05,'AC 13.05',fontsize=7.5,color=ORANGE,va='center')
#,fontsize=8,color=BLUE,ha='right',fontweight='bold')
ax.set_xlim(0,6.7); ax.set_ylim(0,15.5); ax.set_xticks(range(0,7)); ax.set_xlabel('Period'); ax.set_ylabel('Cumulative value (£m)')
ax.grid(color=GRID,lw=0.6); ax.set_axisbelow(True)
for sp in ('top','right'): ax.spines[sp].set_visible(False)
ax.legend(handles=[plt.Line2D([0],[0],color=c,lw=2,label=l) for c,l in ((BLUE,'Planned value (PV)'),(AQUA,'Earned value (EV)'),(ORANGE,'Actual cost (AC)'))],frameon=False,fontsize=7.5,loc='upper left',bbox_to_anchor=(0,0.93))
fig.tight_layout(); fig.savefig(OUT+'fig3_scurve.png',dpi=220); plt.close(fig)
# ---- Fig 4 SPI CPI
fig,ax=plt.subplots(figsize=(6.6,3.0))
p=[e['p'] for e in E]; spi=[e['SPI'] for e in E]; cpi=[e['CPI'] for e in E]
ax.axhline(1.0,color=INK2,lw=0.9,ls=(0,(4,3))); ax.text(0.62,1.008,'On plan = 1.00',fontsize=7.5,color=INK2)
ax.plot(p,spi,color=BLUE,lw=2,marker='o',ms=5,mec='white',mew=1.2)
ax.plot(p,cpi,color=ORANGE,lw=2,marker='o',ms=5,mec='white',mew=1.2)
for x,y in zip(p,spi):
    if x>1: ax.text(x,y-0.027,f'{y:.2f}',ha='center',fontsize=7.2,color=INK2)
for x,y in zip(p,cpi):
    ax.text(x,y+0.016,f'{y:.2f}' if x>1 else 'SPI 0.80 / CPI 0.79',ha='center' if x>1 else 'left',fontsize=7.2,color=INK2)
ax.text(6.12,1.0,'SPI',color=BLUE,fontsize=8,fontweight='bold',va='top'); ax.text(6.12,1.103,'CPI',color=ORANGE,fontsize=8,fontweight='bold',va='bottom')
ax.set_xlim(0.5,6.5); ax.set_ylim(0.72,1.17); ax.set_xticks(p); ax.set_xlabel('Period'); ax.set_ylabel('Index')
ax.grid(color=GRID,lw=0.6); ax.set_axisbelow(True)
for sp in ('top','right'): ax.spines[sp].set_visible(False)
fig.tight_layout(); fig.savefig(OUT+'fig4_idx.png',dpi=220); plt.close(fig)
print('ok')
