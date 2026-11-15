import copy
import math
import unittest
from estrutural.core.analise import analisar
from estrutural.core.exemplos import biblioteca
from estrutural.core.secoes import calcular_secao,aplicar_secao
from estrutural.core.projetos import migrar,inserir_no,inserir_barra
from referencia_energia import referencia


class Refinamentos(unittest.TestCase):
    def test_todos_exemplos(self):
        self.assertEqual(len(biblioteca()),17)
        for item in biblioteca():
            with self.subTest(exemplo=item['nome']):
                m=item['modelo']; r=analisar(m)
                self.assertLess(max(map(abs,r['equilibrio'])),1e-8)
                self.assertTrue(all(math.isfinite(v) for d in r['deslocamentos'] for v in d))
                if m['tipo']!='Treliça':
                    dref,rref=referencia(m)
                    for got,want in zip(r['deslocamentos'],dref):
                        for a,b in zip(got,want):self.assertAlmostEqual(a,b,places=9)
                    for got,want in zip(r['reacoes'],rref):
                        for a,b in zip(got,want):self.assertAlmostEqual(a,b,places=7)
                else:
                    # Verificação independente por equilíbrio dos nós, não usa K.
                    forces=[[0.,0.] for _ in m['nos']]
                    for bar,res in zip(m['barras'],r['barras']):
                        i,j=bar['i'],bar['j']; a,z=m['nos'][i],m['nos'][j]; L=math.hypot(z['x']-a['x'],z['y']-a['y']); N=res['pontos'][0]['N']
                        for k,delta in enumerate([z['x']-a['x'],z['y']-a['y']]):forces[i][k]+=N*delta/L; forces[j][k]-=N*delta/L
                    for i,no in enumerate(m['nos']):
                        for k in range(2):self.assertAlmostEqual(forces[i][k]+r['reacoes'][i][k]+no.get('carga_pontual',[0,0])[k],0,places=8)

    def test_referencias_analiticas(self):
        b={e['nome']:analisar(e['modelo']) for e in biblioteca()}
        self.assertAlmostEqual(b['Portal — duas águas']['reacoes'][0][1],10)
        self.assertAlmostEqual(b['Parabólico triarticulado']['reacoes'][0][0],22.5)
        self.assertAlmostEqual(b['Arco — carga no centro']['reacoes'][0][0],15)
        self.assertAlmostEqual(b['Grelha em L']['deslocamentos'][-1][0],-(10*3**3/(3*20000)+10*2**2*3/10000+10*2**3/(3*20000)))
        self.assertAlmostEqual(b['Malha 2×2']['reacoes'][0][0],12)

    def test_formulas_secoes(self):
        p=calcular_secao('Retangular',{'b':.2,'h':.3});self.assertAlmostEqual(p['A'],.06); self.assertAlmostEqual(p['Ix'],.2*.3**3/12);self.assertAlmostEqual(p['cx'],.1);self.assertAlmostEqual(p['cy'],.15)
        p=calcular_secao('Circular maciço',{'d':.2});self.assertAlmostEqual(p['Ix'],math.pi*.2**4/64);self.assertAlmostEqual(p['J'],2*p['Ix'])
        p=calcular_secao('I/H',{'b':.15,'h':.3,'tw':.01,'tf':.02}); self.assertAlmostEqual(p['Ix'],(.15*.3**3-(.15-.01)*(.3-.04)**3)/12)
        p=calcular_secao('Tubo circular',{'d':.2,'t':.01});self.assertAlmostEqual(p['Ix'],math.pi*(.2**4-.18**4)/64)
        p=calcular_secao('Caixão',{'b':.2,'h':.3,'t':.01}); self.assertAlmostEqual(p['Ix'],(.2*.3**3-.18*.28**3)/12)
        for f in ('U','T','L','Quadrado'):
            p=calcular_secao(f,{'b':.2,'h':.3,'tw':.01,'tf':.02});self.assertGreater(p['J'],0)
    def test_dimensoes_invalidas(self):
        for f,d in [('Retangular',{'b':0,'h':1}),('I/H',{'b':.2,'h':.3,'tw':.01,'tf':.2}),('Tubo circular',{'d':.1,'t':.1}),('Caixão',{'b':.1,'h':.2,'t':.06})]:
            with self.assertRaises(ValueError):calcular_secao(f,d)
    def test_perfil_no_calculo(self):
        config={'familia':'Retangular','dimensoes':{'b':.2,'h':.3},'E_MPa':200000,'G_MPa':80000}
        item=biblioteca()[1]['modelo']; before=analisar(item)['deslocamentos'][-1][1]
        item['barras'][0]=aplicar_secao(item['barras'][0],config); p=calcular_secao('Retangular',config['dimensoes'])
        self.assertAlmostEqual(item['barras'][0]['EA'],200000000*p['A']); self.assertAlmostEqual(analisar(item)['deslocamentos'][-1][1],-10*27/(3*200000000*p['Ix']))
        self.assertNotEqual(before,analisar(item)['deslocamentos'][-1][1])
    def test_sobrescrita(self):
        dims={'b':.2,'h':.3};p=calcular_secao('Retangular',dims,{'Ix':.002});self.assertEqual(p['Ix'],.002);self.assertAlmostEqual(p['Wx'],.002/.15)
        self.assertAlmostEqual(calcular_secao('Retangular',dims)['Ix'],.2*.3**3/12)
    def test_compatibilidade(self):
        old=biblioteca()[1]['modelo']; expected=analisar(old);old['nos'][1]['carga_nodal']=old['nos'][1].pop('carga_pontual'); snapshot=copy.deepcopy(old)
        self.assertEqual(analisar(migrar(old)),expected); self.assertEqual(old,snapshot)
    def test_coordenadas(self):
        m={'nos':[],'barras':[]};self.assertEqual(inserir_no(m,.123456789,2),0)
        with self.assertRaises(ValueError):inserir_no(m,.123456789,2)
        inserir_no(m,3,2);inserir_barra(m,0,1)
        with self.assertRaises(ValueError):inserir_barra(m,1,0)
        with self.assertRaises(ValueError):inserir_barra(m,0,0)


if __name__=='__main__':unittest.main()
