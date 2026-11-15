"""Per-user display preferences, shared by startup and interactive controls."""
import json
import math
from estrutural.core.exibicao import PADRAO


def carregar_preferencias(config):
    try:
        dados=json.loads(config.value('preferencias','{}'))
        if not isinstance(dados,dict):dados={}
    except (ValueError,TypeError):dados={}
    op=PADRAO.copy()
    for key,default in PADRAO.items():
        value=dados.get(key,default)
        if isinstance(default,bool):valido=isinstance(value,bool)
        elif isinstance(default,int):valido=isinstance(value,int) and not isinstance(value,bool)
        elif isinstance(default,float):valido=isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
        else:valido=isinstance(value,type(default))
        if valido:op[key]=value
    # Older versions recorded toolbar theme changes only in this key. It is
    # authoritative for migration; new writes keep both representations in sync.
    if config.contains('modo_noturno'):
        op['escuro']=config.value('modo_noturno',False,type=bool)
    for key,lo,hi in [('decimais',0,10),('passo',.01,100),('escala_diagrama',1,300),('escala_deformada',.01,1e12),('tolerancia_zero',0,1e3),('relativo_desloc',0,.1)]:
        op[key]=max(lo,min(hi,op[key]))
    for key,validos in [('idioma',('pt_BR','en_US')),('forca',('kN','N')),('deslocamento',('mm','cm','m'))]:
        if op[key] not in validos:op[key]=PADRAO[key]
    return op


def gravar_preferencias(config,op):
    config.setValue('preferencias',json.dumps(op,ensure_ascii=False,allow_nan=False))
    config.setValue('modo_noturno',op['escuro'])
    config.sync()
