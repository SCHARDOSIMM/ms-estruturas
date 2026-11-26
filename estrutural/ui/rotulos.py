"""Seleção de rótulos: o desenho compacto conserva as tabelas e o hit-test."""
import math


def arco_denso(modelo):
    return modelo['tipo']=='Arco' and len(modelo['barras'])>12


def nos_rotulados(modelo,selecionado=None):
    if not arco_denso(modelo):return set(range(len(modelo['nos'])))
    graus=[0]*len(modelo['nos']);especiais=set()
    for b in modelo['barras']:
        for k in ('i','j'):graus[b[k]]+=1
        for k,flag in (('i','rotula_i'),('j','rotula_j')):
            if b.get(flag):especiais.add(b[k])
    especiais.update(i for i,n in enumerate(modelo['nos']) if graus[i]!=2 or any(n.get('apoio',[])) or any(n.get('mola',[])))
    if selecionado is not None:especiais.add(selecionado)
    return especiais


def extremos_globais(resultado,key):
    values=[(bi,pi,p.get(key,0.)) for bi,b in enumerate(resultado['barras']) for pi,p in enumerate(b['pontos'])]
    if not values:return set()
    return {min(values,key=lambda x:x[2])[:2],max(values,key=lambda x:x[2])[:2]}


def cargas_projetadas(modelo):
    """Agrupa só cargas realmente uniformes por projeção em todas as barras.

    A intensidade armazenada continua sendo por metro real. A geometria e os
    valores são reavaliados, portanto editar uma barra desfaz o agrupamento.
    """
    if modelo['tipo']!='Arco' or len(modelo['barras'])<2:return []
    grouped=[]
    for eixo,coord,projecao in [('global_y','x','X'),('global_x','y','Y')]:
        values=[];valid=True
        for b in modelo['barras']:
            a,z=[modelo['nos'][b[k]] for k in ('i','j')];L=math.hypot(z['x']-a['x'],z['y']-a['y']);d=abs(z[coord]-a[coord])
            charges=[ch for ch in b.get('distribuidas',[]) if ch.get('eixo')==eixo]
            if not charges:valid=False;break
            q=0.
            for ch in charges:
                if ch.get('funcao') or ch.get('pontos') or ch.get('a',0)!=0 or abs(ch.get('b',L)-L)>1e-9 or abs(ch.get('qa',0)-ch.get('qb',ch.get('qa',0)))>1e-9:
                    valid=False;break
                q+=ch.get('qa',0)
            if not valid:break
            if d<1e-10:
                if abs(q)>1e-10:valid=False;break
            else:values.append(q*L/d)
        if valid and values and max(values)-min(values)<=1e-8*max(1,max(map(abs,values))):
            grouped.append(dict(eixo=eixo,q=values[0],projecao=projecao))
    return grouped
