import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import copy
import unittest
from PyQt5.QtCore import Qt,QPointF
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from configuracao_teste import editor_isolado as Editor
from estrutural.ui.projecao_grelha import projetar,inverter,angulo_apoio
from estrutural.core.apoios import direcao_barra
import math
from estrutural.core.exemplos import biblioteca


class GrelhaIsometrica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_inversa_e_eixos(self):
        for x,y in ((0,0),(2,3),(-4,2),(1.234,-5.67)):
            a,b=inverter(projetar(x,y));self.assertAlmostEqual(a,x);self.assertAlmostEqual(b,y)
        self.assertGreater(projetar(1,0).x(),0);self.assertLess(projetar(0,1).x(),0)
        self.assertLess(projetar(0,0,1).y(),0)

    def test_engastes_dos_exemplos_apontam_para_a_barra(self):
        for item in biblioteca():
            m=item['modelo']
            if m['tipo']!='Grelha':continue
            for idx,n in enumerate(m['nos']):
                if not all(n.get('apoio',[])) or not n.get('apoio'):continue
                with self.subTest(exemplo=item['nome'],no=idx):
                    delta=projetar(*direcao_barra(m,idx));angle=math.radians(angulo_apoio(m,idx))
                    self.assertAlmostEqual(math.cos(angle),delta.x()/math.hypot(delta.x(),delta.y()))
                    self.assertAlmostEqual(math.sin(angle),delta.y()/math.hypot(delta.x(),delta.y()))
        m={'tipo':'Grelha','nos':[{'x':0,'y':0,'apoio':[True,False,False]},{'x':0,'y':2}], 'barras':[{'i':0,'j':1}]}
        self.assertEqual(angulo_apoio(m,0),0)

    def test_desenhar_mover_snap_desfazer(self):
        w=Editor();w.show();w.resize(1360,850);self.app.processEvents()
        try:
            w.carregar({'tipo':'Grelha','nos':[],'barras':[]});c=w.canvas
            c.origem=QPointF(400,100);c.zoom=60
            w.ferramenta.setCurrentText('Barra')
            for x,y in ((0,0),(3,0),(3,0),(3,2)):
                QTest.mouseClick(c,Qt.LeftButton,pos=c.tela(x,y).toPoint())
            self.assertEqual(len(w.modelo['nos']),3);self.assertEqual(len(w.modelo['barras']),2)
            self.assertEqual([(n['x'],n['y']) for n in w.modelo['nos']],[(0,0),(3,0),(3,2)])
            w.ferramenta.setCurrentText('Selecionar / editar')
            before=copy.deepcopy(w.modelo)
            QTest.mousePress(c,Qt.LeftButton,pos=c.tela(3,2).toPoint())
            target=c.tela(4,3).toPoint();c.mover_selecao(target);QTest.mouseRelease(c,Qt.LeftButton,pos=target)
            self.assertEqual((w.modelo['nos'][2]['x'],w.modelo['nos'][2]['y']),(4,3))
            w.undo();self.assertEqual(w.modelo,before)
            w.snap.setChecked(False)
            for x,y in ((-2.3,1.7),(4.8,-.3)):
                a,b=c.mundo(c.tela(x,y));self.assertAlmostEqual(a,x);self.assertAlmostEqual(b,y)
        finally:w.close()

    def test_exemplos_resultados_e_enquadramento(self):
        w=Editor();w.show();w.resize(1360,850);self.app.processEvents()
        try:
            for item in biblioteca():
                if item['modelo']['tipo']!='Grelha':continue
                w.carregar(item['modelo']);w.calcular();w.ajustar_vista()
                model=copy.deepcopy(w.modelo);result=copy.deepcopy(w.resultado)
                for n in w.modelo['nos']:self.assertTrue(w.canvas.rect().contains(w.canvas.tela(n['x'],n['y']).toPoint()))
                for mode in ('Estrutura','V','M','T','Deformada'):
                    w.escolher_diagrama(mode);self.app.processEvents();self.assertFalse(w.canvas.grab().isNull())
                self.assertEqual(w.modelo,model);self.assertEqual(w.resultado,result)
            w.carregar({'tipo':'Viga','nos':[],'barras':[]})
            c=w.canvas
            self.assertEqual(c.tela(2,3),c.origem+QPointF(2*c.zoom,-3*c.zoom))
            self.assertFalse(hasattr(w,'vista_grelha_btn'))
        finally:w.close()
