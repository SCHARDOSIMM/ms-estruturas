import copy
import math
import unittest
from estrutural.core.analise import analisar
from estrutural.core.exemplos import biblioteca
from estrutural.core.exibicao import Formatador
from estrutural.core.cargas import integrar,intensidade
from estrutural.core.apoios import angulo_visual


class Calculo05(unittest.TestCase):
    def test_movel_em_rampa(self):
        m={'tipo':'Viga','nos':[{'x':0,'y':0,'apoio':[1,1,0]},{'x':4,'y':3,'apoio':[0,1,0],'apoio_angulo':math.degrees(math.atan2(.8,-.6))}], 'barras':[{'i':0,'j':1,'EA':1e6,'EI':20000,'q':-10}]}
        r=analisar(m)
        self.assertAlmostEqual(r['reacoes'][1][0],-15);self.assertAlmostEqual(r['reacoes'][1][1],20)
        self.assertLess(max(map(abs,r['equilibrio'])),1e-8)
        d=r['deslocamentos'][1];self.assertAlmostEqual(-.6*d[0]+.8*d[1],0)
        self.assertAlmostEqual(max(p['M'] for p in r['barras'][0]['pontos']),31.25)
    def test_engaste_automatico_e_visual(self):
        m=biblioteca()[1]['modelo'];m['nos'][1].update(x=0,y=3)
        self.assertAlmostEqual(angulo_visual(m,0),-90)
        r=analisar(m);m['nos'][0]['apoio_visual']=90;self.assertEqual(r,analisar(m));self.assertAlmostEqual(angulo_visual(m,0),-180)
    def test_pontos_equivalem_triangular(self):
        m=biblioteca()[0]['modelo'];m['barras'][0].update(q=0,distribuidas=[{'a':0,'b':6,'pontos':[[0,0],[3,-5],[6,-10]]}]);r=analisar(m)
        self.assertAlmostEqual(r['reacoes'][0][1],10);self.assertAlmostEqual(r['reacoes'][1][1],20)
        ch=m['barras'][0]['distribuidas'][0];self.assertAlmostEqual(integrar(ch,6,lambda x:1),-30)
        self.assertAlmostEqual(integrar(ch,6,lambda x:x)/-30,4)
    def test_pontos_com_quebra(self):
        ch={'a':0,'b':4,'pontos':[[0,0],[1,-8],[4,0]]}
        self.assertAlmostEqual(integrar(ch,4,lambda x:1),-16)
        self.assertAlmostEqual(integrar(ch,4,lambda x:x)/-16,5/3)
    def test_formula_notacao_comum(self):self.assertAlmostEqual(intensidade({'funcao':'-10*(x/L)^2'},3,6),-2.5)
    def test_flecha_uniforme_e_pontual(self):
        m=biblioteca()[0]['modelo'];r=analisar(m);points=r['barras'][0]['deformacoes'];p=max(points,key=lambda p:p['norma'])
        self.assertAlmostEqual(p['x'],3,places=5);self.assertAlmostEqual(p['uy'],-5*10*6**4/(384*20000),places=10)
        m['barras'][0].update(q=0,pontuais=[{'x':3,'fy':-10}]);r=analisar(m);p=max(r['barras'][0]['deformacoes'],key=lambda p:p['norma'])
        self.assertAlmostEqual(p['uy'],-10*6**3/(48*20000),places=10)
    def test_zero_exibicao_sem_alterar_motor(self):
        r=analisar(biblioteca()[0]['modelo']);before=copy.deepcopy(r);f=Formatador(r)
        self.assertEqual(f.esforco(-2.1e-15),'0');self.assertEqual(f.esforco(-.000009),'0');self.assertNotEqual(f.esforco(.00001),'0')
        self.assertEqual(f.desloc(-1e-18),'0');self.assertEqual(r,before)
        tiny={'deslocamentos':[[0,-1e-11,0]],'barras':[]};f=Formatador(tiny)
        self.assertNotEqual(f.desloc(-1e-11),'0');self.assertNotEqual(f.desloc(-1e-11),'-0')


class Interface05(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
        from PyQt5.QtWidgets import QApplication
        cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        from configuracao_teste import editor_isolado as Editor
        self.w=Editor();self.w.show();self.app.processEvents()
    def tearDown(self):self.w.close()
    def test_cargas_sem_formula(self):
        from estrutural.ui.cargas_visuais import EditorCarga
        for tipo,R in [('Retangular',-60),('Triangular',-30),('Trapezoidal',-90)]:
            d=EditorCarga(self.w,6,tipo);self.assertFalse(d.avancado.isChecked());self.assertTrue(d.formula.isHidden() or d.painel_formula.isHidden());ch=d.montar();self.assertAlmostEqual(integrar(ch,6,lambda x:1),R);d.close()
        d=EditorCarga(self.w,6,'Função');self.assertEqual(d.tipo.currentText(),'Parabólica');self.assertAlmostEqual(integrar(d.montar(),6,lambda x:1),-40)
        d.tipo.setCurrentText('Por pontos');d.add_ponto();self.assertEqual([p[0] for p in d.montar()['pontos']],[0,3,6]);self.assertAlmostEqual(integrar(d.montar(),6,lambda x:1),-30);d.close()
    def test_popover_ancorado_e_escape(self):
        from PyQt5.QtTest import QTest
        from PyQt5.QtCore import Qt,QRect,QPoint
        self.w.menu_exemplos();self.app.processEvents();p=self.w.exemplos_pop
        bounds=QRect(self.w.mapToGlobal(QPoint(0,0)),self.w.size());self.assertTrue(bounds.contains(p.geometry()));self.assertGreaterEqual(p.y(),self.w.botao_exemplos.mapToGlobal(QPoint(0,0)).y())
        QTest.keyClick(p.tree,Qt.Key_Escape);self.assertFalse(p.isVisible())
        self.w.menu_exemplos();self.app.processEvents();p=self.w.exemplos_pop;QTest.mouseClick(self.w.canvas,Qt.LeftButton,pos=self.w.canvas.rect().bottomRight());self.assertFalse(p.isVisible())
    def test_deformada_tem_valores_e_hits(self):
        self.w.exemplo();self.w.calcular();self.w.escolher_diagrama('Deformada');self.w.canvas.grab()
        self.assertTrue(self.w.canvas.diagrama_hits);self.assertTrue(all(row[3]=='norma' for row in self.w.canvas.diagrama_hits));self.assertIn('mm',self.w.tabela.horizontalHeaderItem(1).text());self.assertIn('×',self.w.legenda.text())
        self.assertTrue(any(float(self.w.tabela.item(i,2).text())!=0 for i in range(self.w.tabela.rowCount())) is False) # nós biapoiados têm v=0; flecha está entre nós.
        self.assertGreater(self.w.formatador().max_desloc,0)
        self.w.modelo['barras'][0]['rotula_i']=True;self.w.calcular();self.assertEqual(self.w.tabela.item(0,3).text(),'livre')
    def test_configuracoes_sem_codigo_visivel(self):
        from estrutural.ui.preferencias import Preferencias
        d=Preferencias(self.w);self.assertFalse(d.avancado.isChecked());self.assertAlmostEqual(d.rel.value(),1e-6,places=12);self.assertTrue(all(n!='Propriedades' for b,n in self.w.botoes_icones));d.close()
    def test_apoio_movel_grelha_restringe_w(self):
        from PyQt5.QtTest import QTest
        from PyQt5.QtCore import Qt
        self.w.carregar({'tipo':'Grelha','nos':[{'x':0,'y':0,'apoio':[1,1,1]},{'x':3,'y':0}],'barras':[{'i':0,'j':1,'EI':20000,'GJ':10000}]})
        self.w.botoes_ferramentas['Apoio móvel'].click();QTest.mouseClick(self.w.canvas,Qt.LeftButton,pos=self.w.canvas.tela(3,0).toPoint())
        self.assertEqual(self.w.modelo['nos'][1]['apoio'],[True,False,False]);self.assertNotIn('apoio_angulo',self.w.modelo['nos'][1])
    def test_formato_csv_e_preferencias_nao_alteram_resultado(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        self.w.exemplo();self.w.calcular();before=copy.deepcopy(self.w.resultado)
        self.w.aplicar_preferencias({'forca':'N','deslocamento':'mm','tolerancia_zero':1e-5},gravar=False)
        self.assertEqual(before,self.w.resultado)
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path=Path(folder).resolve();self.assertEqual(path.parent,Path(__file__).parent.resolve());csv=path/'reacoes.csv'
            with patch('estrutural.ui.editor.QFileDialog.getSaveFileName',return_value=(str(csv),'Reações (*.csv)')):self.w.exportar()
            text=csv.read_text(encoding='utf-8-sig');self.assertIn('Rx_N',text);self.assertNotIn('e-15',text);self.assertIn('30000',text)
        self.assertEqual(before,self.w.resultado)
