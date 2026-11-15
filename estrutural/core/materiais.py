"""Materiais elásticos isotrópicos equivalentes, sem dimensionamento normativo."""
import copy
import math

PRESETS={
    'Personalizado':dict(E_MPa=210000,nu=.3,gamma=78.5,alpha=1.2e-5),
    'Aço — referência didática':dict(E_MPa=210000,nu=.3,gamma=78.5,alpha=1.2e-5),
    'Concreto — referência didática':dict(E_MPa=30000,nu=.2,gamma=25,alpha=1e-5),
    'Madeira — equivalente isotrópico':dict(E_MPa=10000,nu=.3,gamma=6,alpha=5e-6),
    'Alumínio — referência didática':dict(E_MPa=70000,nu=.33,gamma=27,alpha=2.3e-5),
}


def validar_material(m):
    if not all(math.isfinite(m[k]) for k in ('E_MPa','G_MPa','nu','gamma','alpha')):raise ValueError('As propriedades do material devem ser finitas.')
    if min(m['E_MPa'],m['G_MPa'])<=0:raise ValueError('E e G devem ser positivos.')
    if not -1<m['nu']<.5:raise ValueError('Coeficiente de Poisson deve estar entre −1 e 0,5 (exclusivos).')
    if m['gamma']<0:raise ValueError('Peso específico não pode ser negativo.')
    if not m.get('nome','').strip():raise ValueError('Informe o nome do material.')


def aplicar_material(barra,m):
    validar_material(m); b=copy.deepcopy(barra); b['material']=copy.deepcopy(m); b['alpha']=m['alpha']
    if b.get('secao'):
        from estrutural.core.secoes import aplicar_secao
        b['secao'].update(E_MPa=m['E_MPa'],G_MPa=m['G_MPa']); b=aplicar_secao(b,b['secao'])
    return b


def preparar_barra(b):
    if b.get('material'):return aplicar_material(b,b['material'])
    if b.get('secao'):
        from estrutural.core.secoes import aplicar_secao
        return aplicar_secao(b,b['secao'])
    return copy.deepcopy(b)
