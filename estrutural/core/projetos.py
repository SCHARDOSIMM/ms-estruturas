"""Normalização retrocompatível de projetos, sem alterar o documento original."""
import copy
import math


def migrar(projeto):
    m=copy.deepcopy(projeto)
    # Discard metadata from the retired checks panel when reading old projects.
    # The original project/file is not modified by migration.
    m.pop('verificacoes',None)
    # Identificador atual: carga_pontual. Aceita o campo genérico e rótulos legados.
    for no in m.get('nos',[]):
        for antiga in ('carga','carga_nodal','Carga nodal','Carga pontual'):
            if antiga in no:
                no.setdefault('carga_pontual',no.pop(antiga))
    return m


def inserir_no(m,x,y):
    if not all(math.isfinite(v) for v in (x,y)): raise ValueError('Coordenadas devem ser finitas.')
    for i,no in enumerate(m['nos']):
        if math.hypot(no['x']-x,no['y']-y)<1e-8:
            raise ValueError(f'Já existe um nó nessa posição: nó {i+1}.')
    m['nos'].append({'x':x,'y':y})
    return len(m['nos'])-1


def inserir_barra(m,i,j):
    if i==j: raise ValueError('Os nós extremos devem ser diferentes.')
    if not (0<=i<len(m['nos']) and 0<=j<len(m['nos'])): raise ValueError('Nó inexistente.')
    a,b=m['nos'][i],m['nos'][j]
    if math.hypot(a['x']-b['x'],a['y']-b['y'])<1e-8: raise ValueError('Barra de comprimento nulo.')
    if any({b['i'],b['j']}=={i,j} for b in m['barras']): raise ValueError('Já existe barra entre esses nós.')
    m['barras'].append({'i':i,'j':j,'EA':1.,'EI':1.})
