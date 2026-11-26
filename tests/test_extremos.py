"""Regressões analíticas: extremos fora da malha visual e cargas globais."""
import copy
import math
import unittest
from estrutural.core.analise import analisar
from estrutural.core.deformacoes import avaliar


def viga():
    return {'tipo':'Viga','nos':[{'x':0,'y':0,'apoio':[1,1,0]},{'x':6,'y':0,'apoio':[0,1,0]}],
            'barras':[{'i':0,'j':1,'EA':1e6,'EI':20000}]}


class Extremos(unittest.TestCase):
    def test_triangular_com_balanco_e_rotula(self):
        # V_AG=50-10*x²; M_AG=-60+50*x-(10/3)*x³.
        m={'tipo':'Viga','nos':[{'x':0,'y':0,'carga_pontual':[0,-40,0]},
            {'x':3,'y':0,'apoio':[0,1,0],'carga_pontual':[0,0,-60]},
            {'x':6,'y':0},{'x':7.5,'y':0,'carga_pontual':[0,-40,0]},
            {'x':9,'y':0,'apoio':[1,1,1]}],
            'barras':[{'i':i,'j':i+1,'EA':1e6,'EI':20000} for i in range(4)]}
        m['barras'][1].update(rotula_j=True,distribuidas=[{'qa':0,'qb':-60}])
        r=analisar(m);p=max(r['barras'][1]['pontos'],key=lambda p:p['M'])
        self.assertAlmostEqual(p['x'],math.sqrt(5),places=10)
        self.assertAlmostEqual(p['M'],14.53559924999299,places=9)
        self.assertAlmostEqual(p['V'],0,places=9)
        self.assertAlmostEqual(r['reacoes'][1][1],90)

    def test_pequeno_maximo_positivo_perto_da_rotula(self):
        # Portal da auditoria: qh projetado, qv triangular e momento no pilar.
        L=math.sqrt(20)
        m={'tipo':'Pórtico plano','nos':[{'x':0,'y':0,'apoio':[1,1,0]},
            {'x':2,'y':4},{'x':5,'y':4},{'x':5,'y':2,'carga_pontual':[0,0,50]},
            {'x':5,'y':0,'apoio':[1,1,0]}],
            'barras':[{'i':i,'j':i+1,'EA':1e6,'EI':20000} for i in range(4)]}
        m['barras'][0].update(rotula_j=True,distribuidas=[{'qa':80/L,'eixo':'global_x'}])
        m['barras'][1]['distribuidas']=[{'qa':-40,'qb':0}]
        r=analisar(m);p=max(r['barras'][1]['pontos'],key=lambda p:p['M'])
        self.assertAlmostEqual(p['x'],3-math.sqrt(8.7),places=10)
        self.assertAlmostEqual(p['M'],.050281309020294,places=9)
        self.assertAlmostEqual(p['V'],0,places=9)

    def test_grelha_raiz_fora_das_41_posicoes(self):
        m={'tipo':'Grelha','nos':[{'x':0,'y':0,'apoio':[1,1,0],'carga_pontual':[0,0,-10]},
            {'x':6,'y':0,'apoio':[1,0,0]}],
            'barras':[{'i':0,'j':1,'EI':20000,'GJ':10000,'q':-10}]}
        p=max(analisar(m)['barras'][0]['pontos'],key=lambda p:p['M'])
        self.assertAlmostEqual(p['x'],19/6)
        self.assertAlmostEqual(p['M'],40.138888888888886)

    def test_funcao_parabolica_raiz_numerica(self):
        m=viga();m['barras'][0]['distribuidas']=[{'qa':0,'funcao':'-10*(x/L)**2'}]
        p=max(analisar(m)['barras'][0]['pontos'],key=lambda p:p['M'])
        x=54**(1/3)
        self.assertAlmostEqual(p['x'],x,places=8)
        self.assertAlmostEqual(p['M'],3.75*x,places=8)

    def test_tabela_linear_por_trechos(self):
        a=viga();b=copy.deepcopy(a)
        a['barras'][0]['distribuidas']=[{'qa':0,'qb':-10}]
        b['barras'][0]['distribuidas']=[{'pontos':[[0,0],[1.3,-13/6],[6,-10]]}]
        ra,rb=analisar(a),analisar(b)
        for r in (ra,rb):
            p=max(r['barras'][0]['pontos'],key=lambda p:p['M'])
            self.assertAlmostEqual(p['x'],math.sqrt(12),places=9)
            self.assertAlmostEqual(p['M'],40*math.sqrt(3)/3,places=8)

    def test_salto_cortante_nao_e_raiz_falsa(self):
        m=viga();m['barras'][0].update(distribuidas=[{'a':1,'b':4,'qa':0,'qb':-8}],
                                               pontuais=[{'x':2.5,'fy':-10}])
        data=analisar(m)['barras'][0]['pontos'];p=max(data,key=lambda p:p['M'])
        self.assertAlmostEqual(p['x'],2.5)
        self.assertGreater(min(data,key=lambda p:abs(p['V']))['V']**2,1)

    def test_dois_lados_do_momento_concentrado_sem_deslocar_a_secao(self):
        m=viga();m['barras'][0]['pontuais']=[{'x':2.123456789,'m':1e6}]
        r=analisar(m);data=r['barras'][0]['pontos'];cut=[p for p in data if p['x']==2.123456789]
        self.assertEqual([p['lado'] for p in cut],['esquerda','direita'])
        self.assertAlmostEqual(cut[0]['M']-cut[1]['M'],1e6)
        # The left limit is the exact peak, not an epsilon-shortened location.
        p=max(data,key=lambda p:p['M'])
        self.assertEqual(p['x'],2.123456789)
        self.assertAlmostEqual(p['M'],1e6*p['x']/6,places=6)

    def test_extremo_normal_em_carga_horizontal_que_muda_de_sinal(self):
        m=viga();m['nos'][0]['apoio']=[1,1,1];m['nos'][1].pop('apoio');m['nos'][1]['x']=3
        m['barras'][0]['distribuidas']=[{'qa':7,'qb':-11,'eixo':'global_x'}]
        p=min(analisar(m)['barras'][0]['pontos'],key=lambda p:p['N'])
        self.assertAlmostEqual(p['x'],7/6)
        self.assertAlmostEqual(p['N'],-121/12)

    def test_magnitudes_pequenas_conservam_extremos(self):
        m=viga();m['barras'][0]['distribuidas']=[{'qa':0,'qb':-1e-8}]
        p=max(analisar(m)['barras'][0]['pontos'],key=lambda p:p['M'])
        self.assertAlmostEqual(p['x'],math.sqrt(12),places=9)
        self.assertAlmostEqual(p['M']/1e-9,40*math.sqrt(3)/3,places=8)

    def test_global_x_monta_forcas_e_deformacoes_consistentes(self):
        m={'tipo':'Pórtico plano','nos':[{'x':0,'y':0,'apoio':[1,1,1]},{'x':4,'y':3}],
            'barras':[{'i':0,'j':1,'EA':1e6,'EI':20000,'distribuidas':[{'qa':5,'eixo':'global_x'}]}]}
        r=analisar(m);rx,ry,mz=r['reacoes'][0]
        self.assertAlmostEqual(rx,-25);self.assertAlmostEqual(ry,0);self.assertAlmostEqual(mz,37.5)
        for x in (0,1.7,5):
            u=4*(5*x-x*x/2)/1e6;v=-3*x*x*(6*25-4*5*x+x*x)/(24*20000)
            d=avaliar(m['barras'][0],r['barras'][0],x,.8,.6,m['tipo'])
            self.assertAlmostEqual(d['ux'],.8*u-.6*v,places=10)
            self.assertAlmostEqual(d['uy'],.6*u+.8*v,places=10)
        for v in r['equilibrio']:self.assertAlmostEqual(v,0)

    def test_eixo_desconhecido_continua_rejeitado(self):
        m=viga();m['barras'][0]['distribuidas']=[{'qa':-10,'eixo':'projecao_inexistente'}]
        with self.assertRaises(ValueError):analisar(m)


if __name__=='__main__':unittest.main()
