"""Verificação independente: monta a energia de deformação por quadratura.

Não usa as matrizes de elemento nem condensação do motor. Rótulas recebem
rotações internas adicionais. A quadratura de Gauss integra a energia cúbica.
"""
import math
from estrutural.core.analise import resolver


def referencia(m):
    nos=m['nos']; grid=m['tipo']=='Grelha'; nd=3*len(nos); ends=[]
    for b in m['barras']:
        ids=[3*b['i']+k for k in range(3)]+[3*b['j']+k for k in range(3)]
        for k,key in ((2,'rotula_i'),(5,'rotula_j')):
            if b.get(key):ids[k]=nd; nd+=1
        ends.append(ids)
    K=[[0.]*nd for _ in range(nd)]; F=[0.]*nd; fixed={}
    for i,no in enumerate(nos):
        for j in range(3):
            F[3*i+j]=no.get('carga_pontual',[0,0,0])[j]
            if no.get('apoio',[0,0,0])[j]:fixed[3*i+j]=0
    for b,ids in zip(m['barras'],ends):
        a,z=nos[b['i']],nos[b['j']]; dx,dy=z['x']-a['x'],z['y']-a['y']; L=math.hypot(dx,dy); c,s=dx/L,dy/L
        # Cada coluna representa uma perturbação unitária global.
        local=[]
        for k in range(6):
            g=[0.]*6; g[k]=1
            if grid: local.append([g[0],c*g[1]+s*g[2],s*g[1]-c*g[2],g[3],c*g[4]+s*g[5],s*g[4]-c*g[5]])
            else:local.append([c*g[0]+s*g[1],-s*g[0]+c*g[1],g[2],c*g[3]+s*g[4],-s*g[3]+c*g[4],g[5]])
        for t in ((1-1/math.sqrt(3))/2,(1+1/math.sqrt(3))/2):
            if grid:
                axial=[(v[4]-v[1])/L for v in local]; bending=[(-6+12*t)/L**2*v[0]+(-4+6*t)/L*v[2]+(6-12*t)/L**2*v[3]+(-2+6*t)/L*v[5] for v in local]
                displacement=[(1-3*t*t+2*t**3)*v[0]+L*(t-2*t*t+t**3)*v[2]+(3*t*t-2*t**3)*v[3]+L*(-t*t+t**3)*v[5] for v in local]
                rigidity=b.get('GJ',1)
            else:
                axial=[(v[3]-v[0])/L for v in local]; bending=[(-6+12*t)/L**2*v[1]+(-4+6*t)/L*v[2]+(6-12*t)/L**2*v[4]+(-2+6*t)/L*v[5] for v in local]
                displacement=[(1-3*t*t+2*t**3)*v[1]+L*(t-2*t*t+t**3)*v[2]+(3*t*t-2*t**3)*v[4]+L*(-t*t+t**3)*v[5] for v in local]; rigidity=b.get('EA',1)
            q=b.get('q',0)
            for ch in b.get('distribuidas',[]):
                # Os exemplos de arco usam carregamento uniforme global_y em toda barra.
                assert ch.get('eixo')=='global_y' and ch.get('qa') is not None
                q+=ch['qa']*c
            for u,gu in enumerate(ids):
                F[gu]+=L/2*q*displacement[u]
                if not grid:
                    for ch in b.get('distribuidas',[]): F[gu]+=L/2*ch['qa']*s*((1-t)*local[u][0]+t*local[u][3])
                for v,gv in enumerate(ids):K[gu][gv]+=L/2*(rigidity*axial[u]*axial[v]+b.get('EI',1)*bending[u]*bending[v])
    for i in range(nd):
        if not any(abs(v)>1e-12 for v in K[i]):fixed[i]=0
    free=[i for i in range(nd) if i not in fixed]; x=resolver([[K[i][j] for j in free] for i in free],[F[i] for i in free]); d=[0.]*nd
    for i,v in zip(free,x):d[i]=v
    r=[sum(K[i][j]*d[j] for j in range(nd))-F[i] for i in range(nd)]
    return [d[i:i+3] for i in range(0,3*len(nos),3)],[r[i:i+3] for i in range(0,3*len(nos),3)]
