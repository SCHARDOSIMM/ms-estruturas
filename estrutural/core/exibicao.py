"""Formatação central: nunca arredonda nem altera dados do motor."""
import math

PADRAO=dict(decimais=4,tolerancia_zero=1e-5,relativo_desloc=1e-6,forca='kN',deslocamento='mm',grade=True,snap=True,passo=.5,escala_diagrama=60.,escala_deformada=60.,mostrar_valores=True,nome_projeto='Sem título',idioma='pt_BR',entrada_xy=True,escuro=False)


class Formatador:
    def __init__(self,resultado=None,opcoes=None):
        self.op={**PADRAO,**(opcoes or {})};r=resultado or {};self.max_desloc=0;self.max_rotacao=0
        grid=r.get('tipologia')=='Grelha'
        for d in r.get('deslocamentos',[]):
            self.max_desloc=max(self.max_desloc,abs(d[0]) if grid else math.hypot(*d[:2]))
            self.max_rotacao=max(self.max_rotacao,max(map(abs,d[1:])) if grid else (abs(d[2]) if len(d)>2 else 0))
        for bar in r.get('barras',[]):
            for d in bar.get('deformacoes',[]):self.max_desloc=max(self.max_desloc,d['norma']);self.max_rotacao=max(self.max_rotacao,abs(d.get('rotacao',0)))
    def numero(self,v):
        if not v:return '0'
        n=self.op['decimais']
        if abs(v)<10**(-n) or abs(v)>=1e6:return f'{v:.{n}e}'
        return f'{v:.{n}f}'.rstrip('0').rstrip('.') if n else f'{v:.0f}'
    def esforco(self,v):
        if abs(v)<self.op['tolerancia_zero']:v=0.
        return self.numero(v*(1000 if self.op['forca']=='N' else 1))
    def desloc(self,v):
        # Teste feito em mm e relativo ao maior deslocamento, sem limite absoluto em m.
        if abs(v*1000)<self.max_desloc*1000*self.op['relativo_desloc']:v=0.
        return self.numero(v*{'mm':1000,'cm':100,'m':1}[self.op['deslocamento']])
    def rotacao(self,v):
        if abs(v)<self.max_rotacao*self.op['relativo_desloc']:v=0.
        return self.numero(v)
    def comprimento(self,v):return self.numero(v)
    def unidade(self,key):return self.op['forca'] if key in ('N','V','R') else self.op['forca']+'·m'
