import unittest
from estrutural.core.materiais import aplicar_material,validar_material,preparar_barra
from estrutural.core.secoes import aplicar_secao
from estrutural.core.exemplos import biblioteca
from estrutural.core.analise import analisar
from estrutural.ui.arcos import gerar_arco


class MateriaisArcos(unittest.TestCase):
    def material(self):return dict(nome='Material de teste',E_MPa=100000,G_MPa=40000,nu=.25,gamma=25,alpha=1e-5)
    def test_material_antes_ou_depois_do_perfil(self):
        b={'i':0,'j':1,'EA':1,'EI':1};config={'familia':'Retangular','dimensoes':{'b':.2,'h':.3},'E_MPa':210000,'G_MPa':80000};m=self.material()
        a=aplicar_secao(aplicar_material(b,m),config);z=aplicar_material(aplicar_secao(b,config),m)
        self.assertEqual(a['EA'],z['EA']);self.assertEqual(a['EI'],z['EI']);self.assertEqual(a['GJ'],z['GJ'])
        model=biblioteca()[1]['modelo'];model['barras'][0]=a
        self.assertAlmostEqual(analisar(model)['deslocamentos'][1][1],-10*27/(3*a['EI']))
    def test_material_sem_secao_preserva_rigidez(self):
        b=aplicar_material({'EA':321,'EI':123},self.material());self.assertEqual(b['EI'],123);self.assertEqual(b['EA'],321);self.assertEqual(b['alpha'],1e-5)
        self.assertEqual(preparar_barra(b),b)
    def test_material_invalido(self):
        for key,val in [('E_MPa',0),('G_MPa',-1),('nu',.5),('gamma',-1)]:
            m=self.material();m[key]=val
            with self.assertRaises(ValueError):validar_material(m)
    def test_arcos_circular_e_parabolico(self):
        for forma in ('Circular','Parabólico'):
            m=gerar_arco((1,2),(7,2),2,20,forma)
            self.assertAlmostEqual(m['nos'][0]['x'],1);self.assertAlmostEqual(m['nos'][0]['y'],2)
            self.assertAlmostEqual(m['nos'][-1]['x'],7);self.assertAlmostEqual(m['nos'][10]['y'],4);self.assertEqual(len(m['barras']),20)
        with self.assertRaises(ValueError):gerar_arco((0,0),(2,0),2,20,'Circular')
