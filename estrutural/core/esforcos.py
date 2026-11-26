"""Solicitações por equilíbrio e pontos críticos entre amostras do desenho.

Para cargas lineares por trechos, V é quadrático e suas raízes são analíticas.
Expressões arbitrárias usam busca numérica: não se promete capturar oscilações
mais rápidas que a subdivisão da busca. Saltos são delimitados antes de buscar.
"""
import math
from estrutural.core.cargas import integrar,intensidade,componentes_locais


def avaliar(b,ends,L,x,c=1.,s=0.,tipo='Pórtico plano',lado='direita'):
    if tipo=='Treliça':return dict(x=x,N=-ends[0],V=0.,M=0.)
    grid=tipo=='Grelha';q=b.get('q',0);v0=ends[0 if grid else 1]
    N=0. if grid else -ends[0];V=v0+q*x;M=-ends[2]+v0*x+q*x*x/2
    for ch in b.get('pontuais',[]):
        if x>ch['x'] or (x==ch['x'] and lado=='direita'):
            fx,fy=ch.get('fx',0),ch.get('fy',0)
            if ch.get('global'):fx,fy=c*fx+s*fy,-s*fx+c*fy
            N-=fx;V+=fy;M+=fy*(x-ch['x'])-ch.get('m',0)
    for ch in b.get('distribuidas',[]):
        a,z=ch.get('a',0),min(x,ch.get('b',L))
        if z<=a:continue
        fx,fy=componentes_locais(ch,c,s)
        total=integrar(ch,L,lambda t:1,a,z)
        N-=fx*total;V+=fy*total
        if fy:M+=fy*integrar(ch,L,lambda t:x-t,a,z)
    result=dict(x=x,N=N,V=V,M=M)
    if grid:result['T']=-ends[1]
    return result


def raizes_quadraticas(a,b,c):
    """Raízes reais, com escala relativa e sem cancelamento da raiz pequena."""
    scale=max(abs(a),abs(b),abs(c))
    if not scale:return []
    a,b,c=a/scale,b/scale,c/scale
    if abs(a)<1e-14:return [-c/b] if abs(b)>=1e-14 else []
    disc=b*b-4*a*c
    if disc<-1e-14:return []
    root=math.sqrt(max(0.,disc));q=-.5*(b+math.copysign(root,b))
    return [q/a,c/q] if q else [-b/(2*a)]


def _raizes_numericas(func,a,b):
    """Não atravessa saltos: a,b delimitam um trecho contínuo."""
    points=[a+(b-a)*i/128 for i in range(129)];vals=[func(x) for x in points]
    roots=[]
    for x,y,fx,fy in zip(points,points[1:],vals,vals[1:]):
        if fx==0 and fy!=0:roots.append(x)
        if (fx<0<fy) or (fy<0<fx):
            lo,hi=x,y
            for _ in range(45):
                mid=(lo+hi)/2;fm=func(mid)
                if fm==0:lo=hi=mid;break
                if (fx<0<fm) or (fm<0<fx):hi=mid
                else:lo=mid;fx=fm
            roots.append((lo+hi)/2)
    return roots


def amostrar(b,ends,L,c=1.,s=0.,tipo='Pórtico plano'):
    """Conserva a malha visual e acrescenta extremos e limites de cada trecho."""
    breaks={0.,L};positions={L*i/40 for i in range(41)};saltos=set()
    for ch in b.get('pontuais',[]):
        x=ch['x'];breaks.add(x)
        if any(ch.get(k,0) for k in ('fx','fy','m')):saltos.add(x)
    for ch in b.get('distribuidas',[]):
        a,z=ch.get('a',0),ch.get('b',L);breaks.update([a,z])
        breaks.update(p[0] for p in ch.get('pontos',[]) if a<p[0]<z)
    positions.update(breaks)
    def ev(x):return avaliar(b,ends,L,x,c,s,tipo)
    def insert(x):
        if not 0<x<L:return
        if all(abs(x-y)>1e-10*L for y in positions):positions.add(x)
    if tipo!='Treliça':
        for a,z in zip(sorted(breaks),sorted(breaks)[1:]):
            h=z-a;mid=(a+z)/2
            active=[ch for ch in b.get('distribuidas',[]) if ch.get('a',0)<mid<ch.get('b',L)]
            def load(x,component):
                return (b.get('q',0) if component==1 else 0.)+sum(componentes_locais(ch,c,s)[component]*intensidade(ch,x,L) for ch in active)
            if any(ch.get('funcao') for ch in active):
                # The right endpoint may carry a point force/couple; use the
                # continuous left limit there, rather than bracketing its jump.
                end=math.nextafter(z,a)
                for fun in (lambda x:ev(x)['V'],lambda x:load(x,0),lambda x:load(x,1)):
                    for x in _raizes_numericas(fun,a,end):insert(x)
                continue
            qa,qz=load(a,1),load(z,1)
            # t=(x-a)/h: V(t)=V(a)+qa*h*t+(qz-qa)*h*t²/2.
            for t in raizes_quadraticas((qz-qa)*h/2,qa*h,ev(a)['V']):
                if 0<t<1:insert(a+h*t)
            # V'=qy and N'=-qx. Include their extrema as well as those of M.
            for component in (0,1):
                q0,q1=load(a,component),load(z,component)
                if q0!=q1:
                    t=-q0/(q1-q0)
                    if 0<t<1:insert(a+h*t)
    points=[]
    for x in sorted(positions):
        if x in saltos:
            left=avaliar(b,ends,L,x,c,s,tipo,lado='esquerda')
            left['lado']='esquerda';points.append(left)
        right=ev(x)
        if x in saltos:right['lado']='direita'
        points.append(right)
    return points
