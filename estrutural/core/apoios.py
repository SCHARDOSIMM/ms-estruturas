"""Direções físicas de vínculos e orientação visual independente do solver."""
import math


def movel_inclinado(no):
    apoio=no.get('apoio',[False,False])
    return len(apoio)>=2 and not apoio[0] and apoio[1] and 'apoio_angulo' in no


def resolver_vinculos(K,F,fixos,nos,g,resolver):
    """Transforma cada nó móvel para [tangente, normal, θ], resolve e retorna global."""
    n=len(F);A=[row[:] for row in K];b=F[:];rotacoes=[]
    for i,no in enumerate(nos):
        if not movel_inclinado(no):continue
        angle=no['apoio_angulo']
        if not math.isfinite(angle):raise ValueError('Ângulo de apoio deve ser finito.')
        c,s=math.cos(math.radians(angle)),math.sin(math.radians(angle));u,v=g*i,g*i+1
        for row in A:
            a,z=row[u],row[v];row[u],row[v]=s*a-c*z,c*a+s*z
        for j in range(n):
            a,z=A[u][j],A[v][j];A[u][j],A[v][j]=s*a-c*z,c*a+s*z
        a,z=b[u],b[v];b[u],b[v]=s*a-c*z,c*a+s*z
        rotacoes.append((u,v,c,s))
    livres=[i for i in range(n) if i not in fixos]
    for i in livres[:]:
        if g==3 and i%3==2 and max(map(abs,A[i]))<1e-14:
            if abs(b[i])>1e-12:raise ValueError('Momento aplicado em rotação totalmente liberada.')
            fixos[i]=0.;livres.remove(i)
    rhs=[b[i]-sum(A[i][j]*value for j,value in fixos.items()) for i in livres]
    sol=resolver([[A[i][j] for j in livres] for i in livres],rhs)
    d=[fixos.get(i,0.) for i in range(n)]
    for i,value in zip(livres,sol):d[i]=value
    for u,v,c,s in rotacoes:
        a,z=d[u],d[v];d[u],d[v]=s*a+c*z,-c*a+s*z
    return d


def direcao_barra(modelo,idx):
    no=modelo['nos'][idx];vetores=[]
    for b in modelo['barras']:
        if idx in (b['i'],b['j']):
            outro=modelo['nos'][b['j'] if b['i']==idx else b['i']]
            dx,dy=outro['x']-no['x'],outro['y']-no['y']
            if math.hypot(dx,dy)>1e-10:vetores.append((dx,dy))
    # Prioriza a barra mais horizontal; preserva o sentido para a hachura ficar fora.
    return min(vetores,key=lambda v:abs(math.atan2(abs(v[1]),abs(v[0])))) if vetores else (1,0)


def angulo_visual(modelo,idx):
    no=modelo['nos'][idx];a=no.get('apoio',[0,0,0]);dx,dy=direcao_barra(modelo,idx);bar=math.degrees(math.atan2(dy,dx))
    if len(a)>2 and all(a):return -bar-no.get('apoio_visual',0)
    if len(a)>=2 and not a[0] and a[1]:return 90-no.get('apoio_angulo',90)
    return -bar-no.get('apoio_visual',0)


def rotacao_livre(modelo,idx):
    """Rotação auxiliar de nó cujas extremidades conectadas foram todas liberadas."""
    if modelo['tipo'] in ('Treliça','Grelha'):return False
    no=modelo['nos'][idx]
    if (len(no.get('apoio',[]))>2 and no['apoio'][2]) or (len(no.get('mola',[]))>2 and no['mola'][2]):return False
    extremidades=[b.get('rotula_i' if b['i']==idx else 'rotula_j',False) for b in modelo['barras'] if idx in (b['i'],b['j'])]
    return bool(extremidades) and all(extremidades)
