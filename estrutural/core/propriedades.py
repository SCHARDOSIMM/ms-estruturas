"""Seções geométricas e conversões explícitas para kN/m."""
import math


def secao_retangular(b,h):
    if min(b,h)<=0: raise ValueError('Dimensões devem ser positivas.')
    a,c=sorted((b,h))
    return {'A':b*h,'I':b*h**3/12,'W':b*h*h/6,
            'J':c*a**3*(1/3-.21*a/c*(1-a**4/(12*c**4)))}


def secao_circular(d):
    if d<=0: raise ValueError('Diâmetro deve ser positivo.')
    return {'A':math.pi*d*d/4,'I':math.pi*d**4/64,'J':math.pi*d**4/32,'W':math.pi*d**3/32}


def arco(inicio,fim,flecha,segmentos=20):
    """Arco parabólico com flecha normal positiva ao vetor início→fim."""
    if segmentos<2 or segmentos>1000: raise ValueError('Use entre 2 e 1000 segmentos.')
    dx,dy=fim[0]-inicio[0],fim[1]-inicio[1]
    L=math.hypot(dx,dy)
    if L<=0: raise ValueError('Extremos do arco devem ser distintos.')
    nos=[]
    for i in range(segmentos+1):
        t=i/segmentos; h=4*flecha*t*(1-t)
        nos.append({'x':inicio[0]+dx*t-dy/L*h,'y':inicio[1]+dy*t+dx/L*h})
    return {'tipo':'Arco','nos':nos,'barras':[{'i':i,'j':i+1,'EA':1,'EI':1} for i in range(segmentos)]}


def para_interno(valor,unidade):
    fatores={'m':1,'cm':.01,'mm':.001,'kN':1,'N':.001,'MN':1000,
             'MPa':1000,'GPa':1e6,'kPa':1,'kN/m':1,'N/m':.001,'kN·m':1,'N·m':.001}
    return valor*fatores[unidade]
