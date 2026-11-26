"""Funções de carga com sintaxe restrita e quadratura numérica verificada."""
import ast
import math
from functools import lru_cache

FUNCOES={n:getattr(math,n) for n in ('sin','cos','tan','exp','sqrt','log')}
FUNCOES['abs']=abs


def componentes_locais(ch,c,s):
    """Componentes de uma carga unitária por metro real da barra."""
    eixo=ch.get('eixo','local_y')
    if eixo=='local_y':return 0.,1.
    if eixo=='global_y':return s,c
    if eixo=='global_x':return c,-s
    raise ValueError('Eixo de carga aceita local_y, global_y ou global_x; use intensidades por metro real da barra.')


@lru_cache(maxsize=128)
def compilar(expressao):
    expressao=expressao.replace('^','**')
    if len(expressao)>200: raise ValueError('Função muito longa (máximo 200 caracteres).')
    tree=ast.parse(expressao,mode='eval')
    if len(list(ast.walk(tree)))>80: raise ValueError('Função muito complexa.')
    for node in ast.walk(tree):
        if not isinstance(node,(ast.Expression,ast.BinOp,ast.UnaryOp,ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow,ast.UAdd,ast.USub,ast.Constant,ast.Name,ast.Load,ast.Call)):
            raise ValueError('Use apenas números, x, L, pi, operadores e funções permitidas.')
        if isinstance(node,ast.Constant) and (type(node.value) not in (int,float) or abs(node.value)>1e12): raise ValueError('Constante inválida.')
        if isinstance(node,ast.Name) and node.id not in {'x','L','pi',*FUNCOES}: raise ValueError('Nome desconhecido na função: '+node.id)
        if isinstance(node,ast.Call) and (not isinstance(node.func,ast.Name) or node.func.id not in FUNCOES or len(node.args)!=1 or node.keywords): raise ValueError('Função não permitida.')
        if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Pow):
            if not isinstance(node.right,ast.Constant) or type(node.right.value) not in (int,float) or not 0<=node.right.value<=12: raise ValueError('Expoente deve ser constante entre 0 e 12.')
    return compile(tree,'<carga>','eval')


def intensidade(ch,x,L):
    try:
        if ch.get('pontos'):
            pontos=sorted(ch['pontos'])
            if len(pontos)<2 or any(not math.isfinite(v) for p in pontos for v in p) or any(pontos[i][0]>=pontos[i+1][0] for i in range(len(pontos)-1)):raise ValueError('Use pelo menos dois pontos finitos com x crescente e distinto.')
            j=next((j for j in range(len(pontos)-1) if x<=pontos[j+1][0]),len(pontos)-2)
            (a,qa),(b,qb)=pontos[j],pontos[j+1];v=qa+(qb-qa)*(x-a)/(b-a)
        elif ch.get('funcao'):
            v=eval(compilar(ch['funcao']),{'__builtins__':{}},{**FUNCOES,'pi':math.pi,'x':x,'L':L})
        else:
            a,b=ch.get('a',0),ch.get('b',L)
            v=ch['qa']+(ch.get('qb',ch['qa'])-ch['qa'])*(x-a)/(b-a)
        if not isinstance(v,(int,float)) or not math.isfinite(v) or abs(v)>1e100: raise ValueError('Resultado não finito.')
        return v
    except (SyntaxError,ArithmeticError,TypeError,ValueError) as e:
        raise ValueError(f'Função de carga inválida em x={x:.5g} m: {e}') from e


GAUSS=[(-.906179845938664,.236926885056189),(-.538469310105683,.478628670499366),(0,.568888888888889),(.538469310105683,.478628670499366),(.906179845938664,.236926885056189)]


def integrar(ch,L,func,a=None,b=None):
    a=ch.get('a',0) if a is None else a
    b=ch.get('b',L) if b is None else b
    if b<=a: return 0.
    if ch.get('pontos'):
        limites=[a]+[p[0] for p in sorted(ch['pontos']) if a<p[0]<b]+[b]
        return sum((z-y)/2*w*intensidade(ch,(y+z)/2+t*(z-y)/2,L)*func((y+z)/2+t*(z-y)/2) for y,z in zip(limites,limites[1:]) for t,w in GAUSS)
    # Cargas lineares são integradas exatamente para as funções de forma cúbicas.
    def quadratura(n):
        h=(b-a)/n
        return sum(w*h/2*intensidade(ch,a+(i+.5)*h+t*h/2,L)*func(a+(i+.5)*h+t*h/2) for i in range(n) for t,w in GAUSS)
    if not ch.get('funcao'): return quadratura(1)
    prev=quadratura(16)
    for n in (32,64,128,256):
        current=quadratura(n)
        if abs(current-prev)<=1e-8*(1+abs(current)): return current
        prev=current
    raise ValueError('Integração da carga não convergiu. Simplifique a função ou divida o trecho.')
