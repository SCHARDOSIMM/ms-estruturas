"""Language is a display choice, never an edit to engineering data."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import copy
import unittest
from unittest.mock import patch
from PyQt5.QtWidgets import QApplication,QComboBox as ComboBase,QDialogButtonBox
from PyQt5.QtCore import QPointF,Qt
from configuracao_teste import editor_isolado as Editor
from estrutural.core.exibicao import PADRAO
from estrutural.core.idiomas import traduzir
from estrutural.ui.idioma import atualizar,definir


class Refinamentos06(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.w=Editor();self.op=copy.deepcopy(self.w.preferencias);self.dark=self.w.noturno.isChecked()
        self.w.aplicar_preferencias(PADRAO,gravar=False);self.w.show();self.app.processEvents()
    def tearDown(self):
        self.w.aplicar_preferencias(self.op,gravar=False);self.w.noturno.setChecked(self.dark);self.w.close()
    def en(self):
        self.w.aplicar_preferencias({**self.w.preferencias,'idioma':'en_US'},gravar=False);self.app.processEvents()
    def test_language_preserves_engine_and_selection(self):
        self.w.exemplo();self.w.calcular();model=copy.deepcopy(self.w.modelo);r=copy.deepcopy(self.w.resultado)
        self.w.coordenadas();c=self.w.painel_coordenadas;history=len(self.w.historico)
        self.en()
        self.assertEqual(self.w.tipo.currentText(),'Viga')
        self.assertEqual(ComboBase.currentText(self.w.tipo),'Beam')
        self.assertEqual(self.w.modelo,model);self.assertEqual(self.w.resultado,r)
        self.assertEqual(len(self.w.historico),history)
        self.assertEqual(c.windowTitle(),'Coordinate entry — Ctrl+E')
        self.assertEqual(c.tabela.horizontalHeaderItem(0).text(),'Node')
        self.w.exibir_resultado('Reações');self.assertTrue(self.w.grupo_resultados.buttons()[0].isChecked())
        self.w.escolher_diagrama('M');self.assertEqual(self.w.diagrama.currentText(),'M')
        self.w.calcular();self.assertEqual(self.w.resultado,r)
        self.w.aplicar_preferencias(PADRAO,gravar=False)
        self.assertEqual(c.windowTitle(),'Entrada de coordenadas — Ctrl+E');c.close()
    def test_technical_terms_and_live_dialog(self):
        from estrutural.ui.cargas_visuais import EditorCarga
        from estrutural.ui.materiais import SeletorMaterial
        from estrutural.ui.perfis import SeletorPerfil
        d=EditorCarga(self.w,6,'Triangular');d.show();self.en()
        self.assertEqual(d.windowTitle(),'Distributed load')
        self.assertEqual(d.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok).text(),'Apply load')
        self.assertEqual(d.tipo.currentText(),'Triangular crescente')
        self.assertEqual(ComboBase.currentText(d.tipo),'Triangular — increasing')
        d.tipo.setCurrentText('Trapezoidal');d.qa.setValue(-5);d.qb.setValue(-15)
        self.assertIn('Resultant',d.resumo.text());self.assertIn('Position',d.resumo.text())
        d.aplicar();self.assertEqual(d.resultado['qa'],-5)
        p=SeletorPerfil(self.w);p.show();self.app.processEvents();p.familia.setCurrentText('Caixão')
        self.assertEqual(p.familia.currentText(),'Caixão');self.assertEqual(ComboBase.currentText(p.familia),'Rectangular hollow')
        p.aplicar();self.assertEqual(p.resultado['familia'],'Caixão');p.close()
        m=SeletorMaterial(self.w);m.show();self.app.processEvents()
        self.assertIn('Steel',m.nome.text());m.aplicar();self.assertGreater(m.resultado['E_MPa'],0)
        for pt,en in [('Apoio fixo','Pinned support'),('Engaste','Fixed support'),('Esforços','Member forces'),('Esforço cortante','Shear force'),('Momento fletor','Bending moment'),('Grelha','Grillage')]:
            self.assertEqual(traduzir(pt,'en_US'),en)
    def test_compact_sidebar_and_header(self):
        self.w.exemplo();self.w.calcular();self.en()
        for width,height in [(1360,768),(1000,680),(1000,560)]:
            self.w.resize(width,height);self.app.processEvents()
            self.assertEqual(self.w.scroll_paleta.verticalScrollBar().maximum(),0)
            self.assertEqual(self.w.tabela.horizontalScrollBar().maximum(),0)
            for b in self.w.paleta.findChildren(__import__('PyQt5.QtWidgets',fromlist=['QPushButton']).QPushButton):
                self.assertEqual((b.width(),b.height()),(32,28))
            buttons=[b for b,_ in self.w.botoes_icones if b.parentWidget()==self.w.centralWidget() and b.property('acao')!='Ajustar vista']+[self.w.idioma_btn]
            tops={b.mapTo(self.w.centralWidget(),b.rect().topLeft()).y() for b in buttons}
            self.assertEqual(len(tops),1)
            self.assertTrue(all(b.height()==34 for b in buttons))
            self.assertLess(max(b.geometry().right() for b in buttons),self.w.centralWidget().width())
        self.assertFalse(self.w.noturno.isVisible())
        self.w.tema_btn.click();self.assertEqual(self.w.tema_btn.isChecked(),self.w.noturno.isChecked())
    def test_moment_arrowheads_both_signs(self):
        from estrutural.ui.simbolos import desenhar_momento
        class Painter:
            def __init__(self):self.head=None
            def drawArc(self,*args):self.arc=args
            def save(self):pass
            def restore(self):pass
            def setBrush(self,*args):pass
            def pen(self):return self
            def color(self):return Qt.black
            def drawPolygon(self,points):self.head=list(points)
        for sign in [-1,1]:
            p=Painter();desenhar_momento(p,QPointF(50,50),30,sign)
            self.assertEqual(len(p.head),3);tip=p.head[0]
            import math
            self.assertAlmostEqual(math.hypot(tip.x()-50,tip.y()-50),30)
            self.assertGreater(p.arc[-1]*sign,0)
    def test_language_button_persists_choice(self):
        with patch.object(self.w.config,'setValue') as save:
            self.w.idioma_btn.click()
            self.assertEqual(self.w.preferencias['idioma'],'en_US')
            self.assertEqual(self.w.idioma_btn.text(),'PT')
            self.assertTrue(any('en_US' in str(c) for c in save.call_args_list))
        self.assertEqual(self.w.cabecalho_csv(['barra','perfil','no','N_kN']),['member','section','node','N_kN'])

    def test_file_filters_keep_semantic_identifiers(self):
        from estrutural.ui.idioma import QFileDialog
        self.en()
        with patch('estrutural.ui.arquivos.DialogoSalvar') as factory:
            dialog=factory.return_value;dialog.Accepted=1;dialog.exec_.return_value=1
            dialog.selectedFiles.return_value=['reactions.csv'];dialog.selectedNameFilter.return_value='Reactions (*.csv)'
            path,selected=QFileDialog.getSaveFileName(self.w,'Exportar','','Imagem (*.png);;Reações (*.csv)')
        self.assertEqual(selected,'Reações (*.csv)');self.assertEqual(path,'reactions.csv')
        self.assertEqual(factory.call_args.args[1],'Export')
        self.assertEqual(factory.call_args.args[3],['Image (*.png)','Reactions (*.csv)'])
