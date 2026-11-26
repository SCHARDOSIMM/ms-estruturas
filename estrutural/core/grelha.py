"""Grelha linear Euler-Bernoulli: w, θx, θy; torção Saint-Venant."""
import math
from estrutural.core.analise import zeros, mul, trans, resolver, ErroModelo


def analisar_grelha(m):
    nos=m['nos']; barras=m['barras']; n=3*len(nos)
    if not nos or not barras: raise ErroModelo('Grelha sem nós ou barras.')
    K=zeros(n,n); F=[0.]*n; fixos={}; springs=[0.]*n; elems=[]
    for i,no in enumerate(nos):
        for j in range(3):
            F[3*i+j]=no.get('carga_pontual',[0,0,0])[j]
            if no.get('apoio',[0,0,0])[j]: fixos[3*i+j]=no.get('recalque',[0,0,0])[j]
            springs[3*i+j]=no.get('mola',[0,0,0])[j]
            K[3*i+j][3*i+j]+=springs[3*i+j]
    for b in barras:
        if any(b.get(k) for k in ['pontuais','distribuidas','rotula_i','rotula_j','delta_t']):
            raise ErroModelo('Grelha: esta versão aceita apenas cargas pontuais nos nós e uniformes locais.')
        i,j=b['i'],b['j']; dx=nos[j]['x']-nos[i]['x']; dy=nos[j]['y']-nos[i]['y']; L=math.hypot(dx,dy)
        EI,GJ=b.get('EI',1),b.get('GJ',1)
        if min(L,EI,GJ)<=0: raise ErroModelo('Grelha exige comprimento, EI e GJ positivos.')
        c,s=dx/L,dy/L
        # Rotação de flexão positiva φ = -θy local; dw/dx = φ.
        T=[[1,0,0,0,0,0],[0,c,s,0,0,0],[0,s,-c,0,0,0],[0,0,0,1,0,0],[0,0,0,0,c,s],[0,0,0,0,s,-c]]
        k=zeros(6,6)
        inds=[0,2,3,5]
        flex=[[12*EI/L**3,6*EI/L**2,-12*EI/L**3,6*EI/L**2],[6*EI/L**2,4*EI/L,-6*EI/L**2,2*EI/L],[-12*EI/L**3,-6*EI/L**2,12*EI/L**3,-6*EI/L**2],[6*EI/L**2,2*EI/L,-6*EI/L**2,4*EI/L]]
        for u in range(4):
            for v in range(4): k[inds[u]][inds[v]]=flex[u][v]
        k[1][1]=k[4][4]=GJ/L; k[1][4]=k[4][1]=-GJ/L
        q=b.get('q',0); f=[q*L/2,0,q*L*L/12,q*L/2,0,-q*L*L/12]
        kg=mul(trans(T),mul(k,T)); fg=mul(trans(T),[[v] for v in f]); ids=[3*i+t for t in range(3)]+[3*j+t for t in range(3)]
        for u,gu in enumerate(ids):
            F[gu]+=fg[u][0]
            for v,gv in enumerate(ids): K[gu][gv]+=kg[u][v]
        elems.append((b,L,T,k,f,ids))
    livres=[i for i in range(n) if i not in fixos]
    d=[fixos.get(i,0) for i in range(n)]
    x=resolver([[K[i][j] for j in livres] for i in livres],[F[i]-sum(K[i][j]*v for j,v in fixos.items()) for i in livres])
    for i,v in zip(livres,x): d[i]=v
    r=[sum(K[i][j]*d[j] for j in range(n))-F[i]-springs[i]*d[i] for i in range(n)]
    result=[]
    for b,L,T,k,f,ids in elems:
        dl=[v[0] for v in mul(T,[[d[i]] for i in ids])]
        ends=[sum(k[i][j]*dl[j] for j in range(6))-f[i] for i in range(6)]
        from estrutural.core.esforcos import amostrar
        pts=amostrar(b,ends,L,tipo='Grelha')
        result.append({'L':L,'extremos':ends,'pontos':pts,'deslocamentos_locais':dl})
    total=[r[i]+F[i] for i in range(n)]
    eq=[sum(total[3*i] for i in range(len(nos))),sum(total[3*i+1]+nos[i]['y']*total[3*i] for i in range(len(nos))),sum(total[3*i+2]-nos[i]['x']*total[3*i] for i in range(len(nos)))]
    return {'deslocamentos':[d[i:i+3] for i in range(0,n,3)],'reacoes':[r[i:i+3] for i in range(0,n,3)],'barras':result,'equilibrio':eq}
