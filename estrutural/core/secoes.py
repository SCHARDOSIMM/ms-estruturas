"""Geometria de seções em metros. Torção aberta por parede fina, sem empenamento."""
import math

FAMILIAS=['Retangular','Quadrado','Circular maciço','Tubo circular','Caixão','I/H','U','T','L','Arbitrário']


def retangulos(f,d):
    b,h=d.get('b',.2),d.get('h',.3); tw,tf=d.get('tw',.01),d.get('tf',.015)
    if min(b,h)<=0: raise ValueError('b e h devem ser positivos.')
    if f=='Quadrado': h=b
    if f in ('Retangular','Quadrado'): return [(0,0,b,h)]
    if f=='Caixão':
        t=d.get('t',.01)
        if not 0<t<min(b,h)/2: raise ValueError('t deve ser positivo e menor que b/2 e h/2.')
        return [(0,0,b,t),(0,h-t,b,t),(0,t,t,h-2*t),(b-t,t,t,h-2*t)]
    if not 0<tw<b or not 0<tf<h/2: raise ValueError('Exige 0 < tw < b e 0 < tf < h/2.')
    if f=='I/H': return [(0,0,b,tf),(0,h-tf,b,tf),((b-tw)/2,tf,tw,h-2*tf)]
    if f=='U': return [(0,0,b,tf),(0,h-tf,b,tf),(0,tf,tw,h-2*tf)]
    if f=='T': return [(0,h-tf,b,tf),((b-tw)/2,0,tw,h-tf)]
    if f=='L': return [(0,0,b,tf),(0,tf,tw,h-tf)]
    return []


def calcular_secao(f,d,sobrescritos=None):
    if any(not math.isfinite(v) for v in d.values()): raise ValueError('Dimensões devem ser finitas.')
    formulas='A=ΣAi; cx=ΣAi·xi/A; cy=ΣAi·yi/A; Ix=Σ(bi·hi³/12+Ai·Δyi²); Iy=Σ(hi·bi³/12+Ai·Δxi²).'
    aviso=''
    if f=='Arbitrário':
        A,Ix,Iy,J=[d.get(k,0) for k in ('A','Ix','Iy','J')]
        if min(A,Ix,Iy,J)<=0: raise ValueError('A, Ix, Iy e J arbitrários devem ser positivos.')
        cx=cy=None; Wx=Wy=None; formulas='Valores arbitrários informados pelo usuário. Centroide e W exigem geometria e não são inferidos.'
    elif f in ('Circular maciço','Tubo circular'):
        dia=d.get('d',.2); t=d.get('t',.01); di=0 if f=='Circular maciço' else dia-2*t
        if dia<=0 or (f=='Tubo circular' and not 0<t<dia/2): raise ValueError('Exige d > 0 e, no tubo, 0 < t < d/2.')
        A=math.pi*(dia**2-di**2)/4; Ix=Iy=math.pi*(dia**4-di**4)/64; J=2*Ix; cx=cy=dia/2; Wx=Wy=Ix/(dia/2)
        formulas='A=π(d⁲−di²)/4; Ix=Iy=π(d⁴−di⁴)/64; J=2I; W=I/(d/2).'
    else:
        parts=retangulos(f,d)
        if not parts: raise ValueError('Família de seção desconhecida.')
        A=sum(b*h for x,y,b,h in parts); cx=sum(b*h*(x+b/2) for x,y,b,h in parts)/A; cy=sum(b*h*(y+h/2) for x,y,b,h in parts)/A
        Ix=sum(b*h**3/12+b*h*(y+h/2-cy)**2 for x,y,b,h in parts); Iy=sum(h*b**3/12+b*h*(x+b/2-cx)**2 for x,y,b,h in parts)
        width=max(x+b for x,y,b,h in parts); height=max(y+h for x,y,b,h in parts)
        Wx=Ix/max(cy,height-cy); Wy=Iy/max(cx,width-cx)
        if f=='Caixão':
            t=d['t']; bm=width-t; hm=height-t; J=4*(bm*hm)**2/(2*(bm+hm)/t)
            aviso='J aproximado por Bredt para parede fina fechada; cantos vivos.'
            formulas+=' J≈4Am²/∮(ds/t).'
        elif f in ('Retangular','Quadrado'):
            a,b=sorted((width,height)); J=b*a**3/3*(1-192*a/(math.pi**5*b)*sum(math.tanh(k*math.pi*b/(2*a))/k**5 for k in range(1,200,2)))
            formulas+=' J=ba³/3·[1−192a/(π⁵b)Σ(tanh(nπb/2a)/n⁵)], n ímpar (100 termos).'
        else:
            J=sum(max(b,h)*min(b,h)**3/3 for x,y,b,h in parts)
            aviso='J aproximado Σ(l·t³/3), parede fina aberta; sem raios de concordância ou empenamento.'
            if f=='L':aviso+=' Cantoneira: Ix/Iy geométricos não são eixos principais; o motor plano não inclui flexão acoplada.'
            formulas+=' J≈Σ(l·t³/3).'
    values={'A':A,'cx':cx,'cy':cy,'Ix':Ix,'Iy':Iy,'Wx':Wx,'Wy':Wy,'J':J}
    for key,v in (sobrescritos or {}).items():
        if key not in ('A','Ix','Iy','J') or not math.isfinite(v) or v<=0: raise ValueError('Sobrescritas exigem A/Ix/Iy/J positivos e finitos.')
        values[key]=v
    if sobrescritos:
        if Wx is not None: values['Wx']=values['Ix']/(Ix/Wx)
        if Wy is not None: values['Wy']=values['Iy']/(Iy/Wy)
    values.update(rx=math.sqrt(values['Ix']/values['A']),ry=math.sqrt(values['Iy']/values['A']),formulas=formulas+' W=I/cmáx; r=√(I/A).',aviso=aviso)
    return values


def aplicar_secao(b,config):
    import copy
    b=copy.deepcopy(b);config=copy.deepcopy(config)
    if b.get('material'):config.update(E_MPa=b['material']['E_MPa'],G_MPa=b['material']['G_MPa'])
    p=calcular_secao(config['familia'],config['dimensoes'],config.get('sobrescritos'))
    E,G=config['E_MPa']*1000,config['G_MPa']*1000
    if not all(math.isfinite(v) and v>0 for v in (E,G)): raise ValueError('E e G devem ser positivos e finitos.')
    b.update(secao=copy.deepcopy(config),EA=E*p['A'],EI=E*p[config.get('eixo','Ix')],GJ=G*p['J'])
    return b
