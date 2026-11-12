import json, math
R={}
# ---------- measurement
M=json.load(open('meas.json'))
GF=M['GF']; FF=M['FF']
gifa=round(round(GF)+round(FF))
R['gifa']={'GF':round(GF),'FF':round(FF),'total':gifa}
R['gf_footprint']=round(M['gf_footprint']); R['roof_plan']=round(M['roof_plan']); R['meas']=M
R['pool_water']=25*13
# ---------- benchmark
bench_total=6155000/1543
R['bench_total']=bench_total
fees=1.12; ext=1.12
b_works=bench_total/fees           # incl ext works
b_building=b_works/ext             # building works incl prelims+OHP
prel_b=1.12; ohp=1.053
b_net=b_building/(prel_b*ohp)
idx=(1.032/1.007)*(1.155**(0.1))   # 3Q25->2Q26 then 2 quarters at 2.9% pa
loc=0.96; qual=1.04
rate=b_net*idx*loc*qual
R['rates']={'bench_total':bench_total,'less_fees':b_works,'less_ext':b_building,'net_of_prelim_ohp':b_net,'idx':idx,'loc':loc,'qual':qual,'adj_rate':rate}
def estimate(gifa=gifa,rate_mult=1.0,loc_f=loc,prel=0.15,risk=(0.08,0.03,0.02,0.01),infl_pa=0.0290,abn_mult=1.0,detail=False):
    r=b_net*idx*loc_f*qual*rate_mult
    building=r*gifa
    movfloor=225000
    fac=400000
    abn=(325*round(M['gf_footprint'])+120000)*abn_mult
    extw=0.15*building
    sub=building+movfloor+fac+abn+extw
    pre=prel*sub
    ohpv=ohp_rate*(sub+pre)
    works=sub+pre+ohpv
    fee=0.12*works
    other=250000
    base=works+fee+other
    rk=[base*x for x in risk]
    limit=base+sum(rk)
    q=(1+infl_pa)**0.25-1
    ti=limit*((1+q)**3-1)
    ci=(limit+ti)*((1+q)**4-1)
    tot=limit+ti+ci
    if detail:
        return dict(rate=r,building=building,movfloor=movfloor,fac=fac,abn=abn,extw=extw,sub=sub,pre=pre,ohp=ohpv,works=works,fee=fee,other=other,base=base,risk=rk,limit=limit,ti=ti,ci=ci,tot=tot)
    return tot
ohp_rate=0.053
D=estimate(detail=True)
R['est']=D
R['per_m2']={'works':D['works']/gifa,'base':D['base']/gifa,'limit':D['limit']/gifa,'tot':D['tot']/gifa}
R['vat']=D['tot']*0.2
# ---------- sensitivity
base=D['tot']
sens=[]
def add(name,lo_label,hi_label,lo,hi): sens.append((name,lo_label,hi_label,lo-base,hi-base))
add('GIFA','-5%','+5%',estimate(gifa=gifa*0.95),estimate(gifa=gifa*1.05))
b2=(13000000/3906)/(6155000/1543)   # composite sports-centre benchmark ratio
add('Benchmark rate','Sports-centre £3,328/m²','+10%',estimate(rate_mult=b2),estimate(rate_mult=1.10))
add('Location factor','0.92','1.00',estimate(loc_f=0.92),estimate(loc_f=1.00))
add('Preliminaries','12%','18%',estimate(prel=0.12),estimate(prel=0.18))
add('Risk allowance','10% total','20% total',estimate(risk=(0.05,0.02,0.02,0.01)),estimate(risk=(0.11,0.05,0.03,0.01)))
add('Inflation (p.a.)','2.0%','4.0%',estimate(infl_pa=0.02),estimate(infl_pa=0.04))
add('Abnormals','-50%','+50%',estimate(abn_mult=0.5),estimate(abn_mult=1.5))
R['sens']=sens
R['b2']=b2
lowc=estimate(rate_mult=b2,loc_f=0.92,prel=0.12,risk=(0.05,0.02,0.02,0.01),infl_pa=0.02,abn_mult=0.5)
highc=estimate(rate_mult=1.10,loc_f=1.0,prel=0.18,risk=(0.11,0.05,0.03,0.01),infl_pa=0.04,abn_mult=1.5)
R['range']=(lowc,highc)
# ---------- VE1
water=325
rc=2600*water
ve1_cap=0.10*rc
prelweek=D['pre']/78
ve1_prog=6*prelweek
ve1_pile=0.10*325*round(M['gf_footprint'])
ve1_tot=ve1_cap+ve1_prog+ve1_pile
def npv(cfs,r=0.035): return sum(cf/(1+r)**t for t,cf in cfs)
# LCC: RC maintenance 6000/yr, refurb yr25 180k ; SS 3000/yr, reline yr25 110k
rc_l=npv([(t,6000) for t in range(1,31)]+[(25,180000)])
ss_l=npv([(t,3000) for t in range(1,31)]+[(25,110000)])
R['ve1']=dict(rc=rc,cap=ve1_cap,prog=ve1_prog,pile=ve1_pile,total=ve1_tot,prelweek=prelweek,rc_lcc=rc_l,ss_lcc=ss_l,lcc_saving=rc_l-ss_l,combined=ve1_tot+rc_l-ss_l)
# ---------- VE2
pv_kwp=80; pv_cap=pv_kwp*1150
tariff=0.25
yield_=900
pv_cfs=[]
for t in range(1,31):
    gen=pv_kwp*yield_*(0.995**(t-1))
    val=gen*0.9*tariff+gen*0.1*0.08-1200
    if t==15: val-=14000
    pv_cfs.append((t,val))
pv_npv=npv(pv_cfs)-pv_cap
pv_save1=pv_cfs[0][1]
base_elec=400*gifa   # kWh
hr_save=base_elec*0.25*0.20
hr_val=hr_save*tariff
hr_cap=70000
hr_cfs=[(t,hr_val) for t in range(1,31)]
hr_npv=npv(hr_cfs)-hr_cap
pkg_cap=pv_cap+hr_cap
pkg_npv=pv_npv+hr_npv
pkg_ann=pv_save1+hr_val
R['ve2']=dict(pv_cap=pv_cap,pv_gen=pv_kwp*yield_,pv_save1=pv_save1,pv_npv=pv_npv,pv_payback=pv_cap/pv_save1,base_elec=base_elec,hr_save=hr_save,hr_val=hr_val,hr_cap=hr_cap,hr_npv=hr_npv,hr_payback=hr_cap/hr_val,pkg_cap=pkg_cap,pkg_npv=pkg_npv,pkg_ann=pkg_ann,pkg_payback=pkg_cap/pkg_ann,kwh_saved=pv_kwp*yield_*0.95+hr_save)
R['net_capex']=pkg_cap-ve1_tot
# ---------- design economics
R['ewa']={'block_perim':M['block_perim'],'pool_perim':M['pool_perim'],'ewa':M['block_perim']*8.6+M['pool_perim']*7.2}
R['ewa']['wfr']=R['ewa']['ewa']/gifa
# ---------- EVM
BAC=14.4e6
pp=[.10,.28,.50,.72,.90,1.00]; ep=[.08,.24,.46,.68,.88,1.00]
ac_inc=[1.45e6,2.35e6,2.55e6,2.65e6,2.35e6,1.70e6]
ac=[sum(ac_inc[:i+1]) for i in range(6)]
rows=[]
for i in range(6):
    PV=BAC*pp[i]; EV=BAC*ep[i]; AC=ac[i]
    SV=EV-PV; CV=EV-AC; SPI=EV/PV; CPI=EV/AC
    eac=BAC/CPI; eac2=AC+(BAC-EV); tcpi=(BAC-EV)/(BAC-AC) if BAC!=AC else float('nan')
    # earned schedule
    cum=[0]+pp
    k=max(j for j in range(7) if cum[j]<=ep[i]+1e-12)
    if k>=6: ES=6.0
    else: ES=k+(ep[i]-cum[k])/(cum[k+1]-cum[k])
    rows.append(dict(p=i+1,PV=PV,EV=EV,AC=AC,SV=SV,CV=CV,SPI=SPI,CPI=CPI,EAC=eac,EAC2=eac2,TCPI=tcpi,ES=ES,SPIt=ES/(i+1),VAC=BAC-eac,ACinc=ac_inc[i]))
R['evm']=rows
json.dump(R,open('model.json','w'),indent=1,default=float)
# print summary
def f(x): return f'{x:,.0f}'
print('GIFA',R['gifa']); print('rates',{k:round(v,3) for k,v in R['rates'].items()})
for k,v in D.items():
    print(k, [f(x) for x in v] if isinstance(v,list) else f(v))
print('per m2',{k:round(v) for k,v in R['per_m2'].items()},'VAT',f(R['vat']))
for s in sens: print(s[0],s[1],s[2],f(s[3]),f(s[4]))
print('range',f(lowc),f(highc))
print('VE1',{k:round(v) for k,v in R['ve1'].items()})
print('VE2',{k:round(v,2) for k,v in R['ve2'].items()})
print('net capex',f(R['net_capex']))
print('EWA',R['ewa'])
for r in rows: print({k:(round(v,3) if abs(v)<100 else round(v)) for k,v in r.items()})
