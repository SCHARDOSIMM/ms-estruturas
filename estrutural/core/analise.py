"""Rigidez direta de pórticos Euler-Bernoulli e treliças; kN, m, rad.

Forças nodais globais positivas em +x, +y e anti-horário.
N positivo em tração; V = força local esquerda; M positivo sagente.
"""
import math
from estrutural.core.cargas import integrar


class ErroModelo(ValueError):
    pass


def zeros(n, m):
    return [[0.0] * m for _ in range(n)]


def trans(a):
    return list(map(list, zip(*a)))


def mul(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def resolver(a, b):
    """Eliminação com pivoteamento e escalonamento das linhas."""
    n = len(b)
    a = [list(row) + [v] for row, v in zip(a, b)]
    for row in a:
        scale = max(map(abs, row[:-1]), default=0)
        if scale == 0:
            raise ErroModelo('Estrutura instável: grau de liberdade sem rigidez.')
        row[:] = [v/scale for v in row]
    for k in range(n):
        pivot = max(range(k, n), key=lambda i: abs(a[i][k]))
        if abs(a[pivot][k]) < 1e-12:
            raise ErroModelo('Matriz singular: verifique apoios e mecanismos internos.')
        a[k], a[pivot] = a[pivot], a[k]
        for i in range(k+1, n):
            f = a[i][k]/a[k][k]
            for j in range(k, n+1):
                a[i][j] -= f*a[k][j]
    x = [0.0]*n
    for i in reversed(range(n)):
        x[i] = (a[i][n]-sum(a[i][j]*x[j] for j in range(i+1, n)))/a[i][i]
    return x


def analisar(modelo):
    from estrutural.core.projetos import migrar
    from estrutural.core.materiais import preparar_barra
    modelo=migrar(modelo)
    modelo['barras']=[preparar_barra(b) for b in modelo['barras']]
    tipo = modelo.get('tipo', 'Pórtico plano')
    if modelo.get('segunda_ordem'):
        raise ErroModelo('Análise de segunda ordem ainda não validada e indisponível.')
    if tipo == 'Grelha':
        from estrutural.core.grelha import analisar_grelha
        from estrutural.core.deformacoes import completar
        return completar(modelo,analisar_grelha(modelo))
    nos, barras = modelo['nos'], modelo['barras']
    if not nos or not barras:
        raise ErroModelo('Insira ao menos dois nós e uma barra.')
    trelica = tipo == 'Treliça'
    g = 2 if trelica else 3
    n = g*len(nos)
    K, F = zeros(n, n), [0.0]*n
    fixos = {}
    molas = [0.0]*n
    for i, no in enumerate(nos):
        for j in range(g):
            F[g*i+j] = no.get('carga_pontual', [0, 0, 0])[j]
            if no.get('apoio', [False]*3)[j]:
                fixos[g*i+j] = no.get('recalque', [0, 0, 0])[j]
            molas[g*i+j] = no.get('mola', [0, 0, 0])[j]
            if molas[g*i+j] < 0:
                raise ErroModelo('Rigidez de mola deve ser não negativa.')
            K[g*i+j][g*i+j] += molas[g*i+j]
    elementos = []
    for b in barras:
        i, j = b['i'], b['j']
        if not (0 <= i < len(nos) and 0 <= j < len(nos)):
            raise ErroModelo('Barra referencia nó inexistente.')
        dx, dy = nos[j]['x']-nos[i]['x'], nos[j]['y']-nos[i]['y']
        L = math.hypot(dx, dy)
        if L < 1e-9:
            raise ErroModelo('Barra de comprimento zero: separe seus nós extremos.')
        c, s = dx/L, dy/L
        EA, EI = b.get('EA', 1.0), b.get('EI', 1.0)
        if EA <= 0 or EI <= 0:
            raise ErroModelo('EA e EI devem ser positivos, em kN e kN·m².')
        if trelica:
            if b.get('q', 0) or b.get('rotula_i') or b.get('rotula_j') or b.get('pontuais') or b.get('distribuidas'):
                raise ErroModelo('Treliça aceita cargas pontuais nos nós; barras já são biarticuladas.')
            T = [[c, s, 0, 0], [0, 0, c, s]]
            k = [[EA/L, -EA/L], [-EA/L, EA/L]]
            f = [-EA*b.get('alpha', 0)*b.get('delta_t', 0), EA*b.get('alpha', 0)*b.get('delta_t', 0)]
        else:
            a, z, h, d, e = EA/L, 12*EI/L**3, 6*EI/L**2, 4*EI/L, 2*EI/L
            k = [[a,0,0,-a,0,0],[0,z,h,0,-z,h],[0,h,d,0,-h,e],[-a,0,0,a,0,0],[0,-z,-h,0,z,-h],[0,h,e,0,-h,d]]
            T = [[c,s,0,0,0,0],[-s,c,0,0,0,0],[0,0,1,0,0,0],[0,0,0,c,s,0],[0,0,0,-s,c,0],[0,0,0,0,0,1]]
            q = b.get('q', 0)
            thermal = EA*b.get('alpha', 0)*b.get('delta_t', 0)
            f = [-thermal,q*L/2,q*L*L/12,thermal,q*L/2,-q*L*L/12]
            # Integração de Gauss para trechos lineares e forças nodais consistentes.
            def ajouter(x,fx,fy,m=0):
                t=x/L
                shape=[1-t,1-3*t*t+2*t**3,L*(t-2*t*t+t**3),t,3*t*t-2*t**3,L*(-t*t+t**3)]
                axial=[fx,fy,fy,fx,fy,fy]
                for u in range(6): f[u]+=shape[u]*axial[u]
                deriv=[0,(-6*t+6*t*t)/L,1-4*t+3*t*t,0,(6*t-6*t*t)/L,-2*t+3*t*t]
                for u in range(6): f[u]+=deriv[u]*m
            for charge in b.get('distribuidas',[]):
                if charge.get('eixo','local_y') not in ('local_y','global_y'):
                    raise ErroModelo('Eixo de carga aceita local_y ou global_y; cargas projetadas não estão implementadas.')
                start,end=charge.get('a',0),charge.get('b',L)
                if not 0<=start<end<=L: raise ErroModelo('Trecho de carga fora da barra.')
                for u in range(6):
                    def shape(x):
                        t=x/L
                        return [1-t,1-3*t*t+2*t**3,L*(t-2*t*t+t**3),t,3*t*t-2*t**3,L*(-t*t+t**3)][u]
                    axial = u in (0,3)
                    factor=(0 if axial else 1) if charge.get('eixo','local_y')=='local_y' else (s if axial else c)
                    if factor: f[u]+=factor*integrar(charge,L,shape)
            for charge in b.get('pontuais',[]):
                x=charge['x']
                if not 0<=x<=L: raise ErroModelo('Carga pontual fora da barra.')
                fx,fy=charge.get('fx',0),charge.get('fy',0)
                if charge.get('global',False): fx,fy=c*fx+s*fy,-s*fx+c*fy
                ajouter(x,fx,fy,charge.get('m',0))
        original_k, original_f = [r[:] for r in k], f[:]
        releases = [] if trelica else [r for r, name in [(2,'rotula_i'),(5,'rotula_j')] if b.get(name)]
        for r in releases:
            kr, fr = k[r][:], f[r]
            for u in range(len(k)):
                if u != r:
                    f[u] -= k[u][r]*fr/kr[r]
                    for v in range(len(k)):
                        if v != r:
                            k[u][v] -= k[u][r]*kr[v]/kr[r]
            for u in range(len(k)):
                k[u][r] = k[r][u] = 0
            f[r] = 0
        kg = mul(trans(T), mul(k, T))
        fg = [r[0] for r in mul(trans(T), [[v] for v in f])]
        ids = [g*i+t for t in range(g)] + [g*j+t for t in range(g)]
        for u, gu in enumerate(ids):
            F[gu] += fg[u]
            for v, gv in enumerate(ids):
                K[gu][gv] += kg[u][v]
        elementos.append((b,L,T,k,f,ids,original_k,original_f,releases))
    from estrutural.core.apoios import resolver_vinculos
    D=resolver_vinculos(K,F,fixos,nos,g,resolver)
    R = [sum(K[i][j]*D[j] for j in range(n))-F[i]-molas[i]*D[i] for i in range(n)]
    resultados = []
    for b,L,T,k,f,ids,ok,of,rel in elementos:
        dl = [r[0] for r in mul(T, [[D[i]] for i in ids])]
        if rel:
            vals = resolver([[ok[i][j] for j in rel] for i in rel], [of[i]-sum(ok[i][j]*dl[j] for j in range(6) if j not in rel) for i in rel])
            for i,v in zip(rel,vals): dl[i] = v
        ends = [sum(row[j]*dl[j] for j in range(len(dl)))-of[i] for i,row in enumerate(ok)]
        points = []
        positions={L*p/40 for p in range(41)}
        for ch in b.get('pontuais',[]):
            positions.update([max(0,ch['x']-1e-9*L),ch['x'],min(L,ch['x']+1e-9*L)])
        for ch in b.get('distribuidas',[]):
            positions.update([ch.get('a',0),ch.get('b',L)])
            positions.update(p[0] for p in ch.get('pontos',[]))
        for x in sorted(positions):
            N = -ends[0]
            V = 0 if trelica else ends[1]+b.get('q',0)*x
            M = 0 if trelica else -ends[2]+ends[1]*x+b.get('q',0)*x*x/2
            if not trelica:
                c,s=T[0][0],T[0][1]
                for ch in b.get('pontuais',[]):
                    if x>=ch['x']:
                        fx,fy=ch.get('fx',0),ch.get('fy',0)
                        if ch.get('global',False): fx,fy=c*fx+s*fy,-s*fx+c*fy
                        N-=fx; V+=fy; M+=fy*(x-ch['x'])-ch.get('m',0)
                for ch in b.get('distribuidas',[]):
                    a,z=ch.get('a',0),ch.get('b',L)
                    h=max(0,min(x,z)-a)
                    total=integrar(ch,L,lambda t:1,a,a+h)
                    moment=integrar(ch,L,lambda t:x-t,a,a+h)
                    fx,fy=(0,1) if ch.get('eixo','local_y')=='local_y' else (s,c)
                    N-=fx*total; V+=fy*total; M+=fy*moment
            points.append({'x':x,'N':N,'V':V,'M':M})
        resultados.append({'L':L,'extremos':ends,'pontos':points,'deslocamentos_locais':dl})
    total=[R[i]+F[i] for i in range(n)]
    equilibrio=[sum(total[g*i] for i in range(len(nos))),sum(total[g*i+1] for i in range(len(nos))),sum(nos[i]['x']*total[g*i+1]-nos[i]['y']*total[g*i]+(0 if trelica else total[g*i+2]) for i in range(len(nos)))]
    from estrutural.core.deformacoes import completar
    return completar(modelo,{'deslocamentos':[D[i:i+g] for i in range(0,n,g)], 'reacoes':[R[i:i+g] for i in range(0,n,g)], 'barras':resultados,'equilibrio':equilibrio})
