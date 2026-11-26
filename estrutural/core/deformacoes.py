"""Deformações por integração de N/EA e M/EI, com pontos críticos refinados."""
import math
from estrutural.core.cargas import integrar,componentes_locais


def avaliar(b,res,x,c,s,tipo):
    L=res['L'];dl=res['deslocamentos_locais'];ends=res['extremos'];EI=b.get('EI',1);EA=b.get('EA',1)
    if tipo=='Treliça':
        a,z=res['deslocamentos_globais'];ux=a[0]+(z[0]-a[0])*x/L;uy=a[1]+(z[1]-a[1])*x/L
        return dict(x=x,ux=ux,uy=uy,rotacao=0,norma=math.hypot(ux,uy),v=-s*ux+c*uy,duy=(z[1]-a[1])/L)
    if tipo=='Grelha':
        q=b.get('q',0);w=dl[0]+dl[2]*x+(-ends[2]*x*x/2+ends[0]*x**3/6+q*x**4/24)/EI
        theta=dl[2]+(-ends[2]*x+ends[0]*x*x/2+q*x**3/6)/EI
        return dict(x=x,ux=0,uy=w,w=w,rotacao=theta,norma=abs(w),v=w,duy=theta)
    u=dl[0]+(-ends[0]/EA+b.get('alpha',0)*b.get('delta_t',0))*x
    uprime=-ends[0]/EA+b.get('alpha',0)*b.get('delta_t',0)
    v=dl[1]+dl[2]*x+(-ends[2]*x*x/2+ends[1]*x**3/6+b.get('q',0)*x**4/24)/EI
    theta=dl[2]+(-ends[2]*x+ends[1]*x*x/2+b.get('q',0)*x**3/6)/EI
    for ch in b.get('pontuais',[]):
        h=max(0,x-ch['x']);fx,fy=ch.get('fx',0),ch.get('fy',0)
        if ch.get('global'):fx,fy=c*fx+s*fy,-s*fx+c*fy
        u-=fx*h/EA
        if x>ch['x']:uprime-=fx/EA
        v+=(fy*h**3/6-ch.get('m',0)*h*h/2)/EI;theta+=(fy*h*h/2-ch.get('m',0)*h)/EI
    for ch in b.get('distribuidas',[]):
        a,z=ch.get('a',0),min(x,ch.get('b',L));fx,fy=componentes_locais(ch,c,s)
        if z>a:
            if fx:u-=fx*integrar(ch,L,lambda t:x-t,a,z)/EA;uprime-=fx*integrar(ch,L,lambda t:1,a,z)/EA
            if fy:v+=fy*integrar(ch,L,lambda t:(x-t)**3/6,a,z)/EI;theta+=fy*integrar(ch,L,lambda t:(x-t)**2/2,a,z)/EI
    ux,uy=c*u-s*v,s*u+c*v
    return dict(x=x,ux=ux,uy=uy,rotacao=theta,norma=math.hypot(ux,uy),v=v,duy=s*uprime+c*theta)


def completar(modelo,resultado):
    tipo=modelo['tipo'];resultado['tipologia']=tipo
    for b,res in zip(modelo['barras'],resultado['barras']):
        a,z=[modelo['nos'][b[k]] for k in ('i','j')];L=res['L'];c,s=(z['x']-a['x'])/L,(z['y']-a['y'])/L
        res['deslocamentos_globais']=[resultado['deslocamentos'][b['i']],resultado['deslocamentos'][b['j']]]
        def ev(x):return avaliar(b,res,x,c,s,tipo)
        pontos=sorted({v['x'] for v in res['pontos']}|{L*i/80 for i in range(81)})
        values=[ev(x) for x in pontos];extras=[]
        for left,right in zip(values,values[1:]):
            if left['duy']*right['duy']<0:
                lo,hi=left['x'],right['x'];sign=left['duy']
                for _ in range(28):
                    mid=(lo+hi)/2
                    if ev(mid)['duy']*sign>0:lo=mid
                    else:hi=mid
                extras.append(ev((lo+hi)/2))
        for j in range(1,len(values)-1):
            if values[j]['norma']>values[j-1]['norma'] and values[j]['norma']>=values[j+1]['norma']:
                lo,hi=values[j-1]['x'],values[j+1]['x']
                for _ in range(30):
                    p=lo+(hi-lo)/3;q=hi-(hi-lo)/3
                    if ev(p)['norma']<ev(q)['norma']:lo=p
                    else:hi=q
                extras.append(ev((lo+hi)/2))
        res['deformacoes']=sorted(values+extras,key=lambda v:v['x'])
    return resultado
