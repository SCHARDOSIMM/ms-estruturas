import unittest
from estrutural.core.analise import analisar, ErroModelo


class Validacao(unittest.TestCase):
    def viga(self):
        return {'tipo':'Viga','nos':[{'x':0,'y':0,'apoio':[1,1,0]}, {'x':6,'y':0,'apoio':[0,1,0]}], 'barras':[{'i':0,'j':1,'EA':1e6,'EI':20000,'q':-10}]}

    def test_uniforme(self):
        r=analisar(self.viga())
        self.assertAlmostEqual(r['reacoes'][0][1],30)
        self.assertAlmostEqual(r['reacoes'][1][1],30)
        self.assertAlmostEqual(r['barras'][0]['pontos'][20]['M'],45)

    def test_balanco(self):
        m=self.viga(); m['nos'][0]['apoio']=[1,1,1]; m['nos'][1]['apoio']=[0,0,0]; m['nos'][1]['carga']=[0,-10,0]; m['barras'][0]['q']=0
        r=analisar(m)
        self.assertAlmostEqual(r['reacoes'][0][2],60)
        self.assertAlmostEqual(r['deslocamentos'][1][1],-10*6**3/(3*20000))

    def test_dois_vaos(self):
        m=self.viga(); m['nos'].append({'x':12,'y':0,'apoio':[0,1,0]}); m['barras'].append(dict(m['barras'][0],i=1,j=2))
        r=analisar(m)
        self.assertAlmostEqual(r['reacoes'][1][1],75)
        self.assertAlmostEqual(r['barras'][0]['pontos'][-1]['M'],-45)

    def test_portico_rotacionado(self):
        m=self.viga(); m['nos'][0]['apoio']=[1,1,1]; m['nos'][1]={'x':0,'y':6,'carga':[10,0,0]}; m['barras'][0]['q']=0
        r=analisar(m)
        self.assertAlmostEqual(r['reacoes'][0][0],-10)
        self.assertAlmostEqual(r['deslocamentos'][1][0],10*6**3/(3*20000))

    def test_trelica(self):
        m={'tipo':'Treliça','nos':[{'x':0,'y':0,'apoio':[1,1]}, {'x':4,'y':0,'apoio':[0,1]}, {'x':2,'y':2,'carga':[0,-10]}], 'barras':[{'i':0,'j':1},{'i':0,'j':2},{'i':1,'j':2}]}
        r=analisar(m)
        self.assertAlmostEqual(r['barras'][0]['pontos'][0]['N'],5)
        self.assertAlmostEqual(r['barras'][1]['pontos'][0]['N'],-5*2**.5)

    def test_rotula(self):
        m=self.viga(); m['barras'][0]['rotula_i']=True
        r=analisar(m)
        self.assertAlmostEqual(r['barras'][0]['extremos'][2],0)
        self.assertAlmostEqual(r['barras'][0]['pontos'][20]['M'],45)

    def test_instavel(self):
        m=self.viga(); m['nos'][0]['apoio']=[0,0,0]
        with self.assertRaises(ErroModelo): analisar(m)

    def test_temperatura(self):
        m=self.viga(); m['nos'][1]['apoio']=[1,1,0]; m['barras'][0].update(q=0,alpha=1e-5,delta_t=20)
        r=analisar(m)
        self.assertAlmostEqual(r['barras'][0]['pontos'][0]['N'],-200)

    def test_pontual_intermediaria(self):
        m=self.viga(); m['barras'][0].update(q=0,pontuais=[{'x':3,'fy':-10}])
        r=analisar(m)
        self.assertAlmostEqual(r['reacoes'][0][1],5)
        self.assertAlmostEqual(max(p['M'] for p in r['barras'][0]['pontos']),15)
        for v in r['equilibrio']: self.assertAlmostEqual(v,0)

    def test_triangular(self):
        m=self.viga(); m['barras'][0].update(q=0,distribuidas=[{'a':0,'b':6,'qa':0,'qb':-10}])
        r=analisar(m)
        self.assertAlmostEqual(r['reacoes'][0][1],10)
        self.assertAlmostEqual(r['reacoes'][1][1],20)
        self.assertAlmostEqual(r['barras'][0]['pontos'][-1]['M'],0)

    def test_parcial(self):
        m=self.viga(); m['barras'][0].update(q=0,distribuidas=[{'a':0,'b':3,'qa':-10}])
        r=analisar(m)
        self.assertAlmostEqual(r['reacoes'][0][1],22.5)
        self.assertAlmostEqual(r['reacoes'][1][1],7.5)

    def test_recalque(self):
        m=self.viga(); m['nos'][1]['recalque']=[0,-.01,0]; m['barras'][0]['q']=0
        r=analisar(m)
        self.assertAlmostEqual(r['deslocamentos'][1][1],-.01)
        self.assertAlmostEqual(r['reacoes'][0][1],0)

    def test_grelha_balanco(self):
        m={'tipo':'Grelha','nos':[{'x':0,'y':0,'apoio':[1,1,1]}, {'x':3,'y':0,'carga':[-10,4,0]}], 'barras':[{'i':0,'j':1,'EI':20000,'GJ':10000}]}
        r=analisar(m)
        self.assertAlmostEqual(r['deslocamentos'][1][0],-10*27/(3*20000))
        self.assertAlmostEqual(r['deslocamentos'][1][1],4*3/10000)
        self.assertAlmostEqual(r['reacoes'][0][0],10)
        self.assertAlmostEqual(r['barras'][0]['pontos'][0]['T'],4)
        for v in r['equilibrio']: self.assertAlmostEqual(v,0)

    def test_funcao_parabolica(self):
        m=self.viga(); m['barras'][0].update(q=0,distribuidas=[{'a':0,'b':6,'funcao':'-10*(x/L)**2'}])
        r=analisar(m)
        self.assertAlmostEqual(r['reacoes'][0][1],5)
        self.assertAlmostEqual(r['reacoes'][1][1],15)
        self.assertAlmostEqual(r['barras'][0]['pontos'][-1]['M'],0)

    def test_funcao_senoidal(self):
        import math
        m=self.viga(); m['barras'][0].update(q=0,distribuidas=[{'a':0,'b':6,'funcao':'-10*sin(pi*x/L)'}])
        r=analisar(m)
        self.assertAlmostEqual(r['reacoes'][0][1],60/math.pi)
        self.assertAlmostEqual(r['barras'][0]['pontos'][20]['M'],360/math.pi**2)

    def test_expressao_restrita(self):
        from estrutural.core.cargas import intensidade
        for expr in ["__import__('os')",'x.__class__','[1]*100','10**1000000','1/0','sqrt(-1)']:
            with self.subTest(expr=expr),self.assertRaises(ValueError): intensidade({'funcao':expr},1,6)


if __name__=='__main__': unittest.main()
