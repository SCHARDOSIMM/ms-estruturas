import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import copy
import unittest
from unittest.mock import patch
from PyQt5.QtWidgets import QApplication,QDialog,QVBoxLayout,QDialogButtonBox as BoxBase
from PyQt5.QtCore import Qt,QPoint,QEvent,QPointF
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtTest import QTest
from configuracao_teste import editor_isolado as Editor
from estrutural.ui.idioma import definir,QDialogButtonBox,TradutorQt
from estrutural.core.exibicao import PADRAO


class Refinamentos07(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.w=Editor();self.op=self.w.preferencias.copy();self.saved=self.w.noturno.isChecked()
        self.config=self.w.config.value('preferencias',None)
        self.w.aplicar_preferencias(PADRAO,gravar=False);self.w.show();self.app.processEvents()
        self.w.carregar({'tipo':'Pórtico plano','nos':[dict(x=0,y=0),dict(x=2,y=0),dict(x=4,y=0)],'barras':[dict(i=0,j=1,EA=1,EI=1),dict(i=1,j=2,EA=1,EI=1)]})
        self.c=self.w.canvas;self.c.origem=QPointF(100,140);self.c.zoom=60
    def tearDown(self):
        self.w.aplicar_preferencias(self.op,gravar=False);self.w.noturno.setChecked(self.saved)
        if self.config is None:self.w.config.remove('preferencias')
        else:self.w.config.setValue('preferencias',self.config)
        self.w.close()
    def move(self,pos):
        e=QMouseEvent(QEvent.MouseMove,QPointF(pos),Qt.NoButton,Qt.LeftButton,Qt.NoModifier)
        QApplication.sendEvent(self.c,e)
    def drag(self,a,b):
        QTest.mousePress(self.c,Qt.LeftButton,pos=a);self.move(b);QTest.mouseRelease(self.c,Qt.LeftButton,pos=b);self.app.processEvents()
    def test_marquee_group_move_and_undo(self):
        before=copy.deepcopy(self.w.modelo)
        self.drag(QPoint(75,110),QPoint(240,165))
        self.assertEqual(self.c.nos_selecionados,{0,1});self.assertEqual(self.c.barras_selecionadas,{0})
        count=len(self.w.historico)
        self.drag(QPoint(160,140),QPoint(190,110))
        self.assertEqual(len(self.w.historico),count+1)
        self.assertAlmostEqual(self.w.modelo['nos'][0]['x'],.5);self.assertAlmostEqual(self.w.modelo['nos'][1]['y'],.5)
        self.assertEqual(self.w.modelo['nos'][2],before['nos'][2]);self.assertIsNone(self.w.resultado)
        self.w.undo();self.assertEqual(self.w.modelo,before);self.w.redo();self.assertEqual(self.w.modelo['nos'][0]['x'],.5)
    def test_ctrl_selection_escape_and_collision(self):
        QTest.mouseClick(self.c,Qt.LeftButton,pos=QPoint(100,140))
        QTest.mouseClick(self.c,Qt.LeftButton,Qt.ControlModifier,pos=QPoint(220,140))
        self.assertEqual(self.c.nos_selecionados,{0,1})
        before=copy.deepcopy(self.w.modelo)
        QTest.mousePress(self.c,Qt.LeftButton,pos=QPoint(100,140));self.move(QPoint(130,110));QTest.keyClick(self.c,Qt.Key_Escape)
        self.assertEqual(self.w.modelo,before)
        count=len(self.w.historico);self.drag(QPoint(100,140),QPoint(220,140))
        self.assertEqual(self.w.modelo,before);self.assertEqual(len(self.w.historico),count)
        self.assertIn('cancelado',self.w.ajuda.text())
    def test_numeric_entry_toggle_chain_and_undo(self):
        self.w.novo();self.w.tipo_xy.setCurrentText('Barra')
        for x,y in [(1.123456,2.345678),(4.123456,2.345678)]:
            self.w.x_entrada.setValue(x);self.w.y_entrada.setValue(y);self.w.y_entrada.setFocus();QTest.keyClick(self.w.y_entrada,Qt.Key_Return)
        self.assertEqual(len(self.w.modelo['barras']),1)
        self.assertAlmostEqual(self.w.modelo['nos'][0]['x'],1.123456)
        self.w.xy_toggle.click();self.assertFalse(self.w.entrada_xy.isVisible());self.assertIsNone(self.c.inicio)
        self.w.xy_toggle.click();self.assertTrue(self.w.entrada_xy.isVisible())
        self.w.undo();self.assertEqual(len(self.w.modelo['barras']),0)
    def test_ok_not_blank_after_language_switches(self):
        d=QDialog(self.w);layout=QVBoxLayout(d);b=QDialogButtonBox(BoxBase.Ok|BoxBase.Cancel);layout.addWidget(b);d.show()
        for lang in ['en_US','pt_BR','en_US','pt_BR']:
            definir(lang);self.app.processEvents()
            self.assertEqual(b.button(BoxBase.Ok).text().replace('&',''),'OK')
            self.assertTrue(b.button(BoxBase.Cancel).text())
        d.close()
        translator=TradutorQt();self.assertEqual(translator.translate('QDialogButtonBox','OK'),'OK')
    def test_brand_credit_and_window_size(self):
        self.assertFalse(self.w.windowIcon().isNull());self.assertEqual(self.w.marca.text(),'MS Estruturas')
        for lang,text in [('en_US','Created by Matheus Schardosim'),('pt_BR','Criado por Matheus Schardosim')]:
            self.w.aplicar_preferencias({**PADRAO,'idioma':lang},gravar=False);self.app.processEvents()
            from PyQt5.QtGui import QTextDocument
            doc=QTextDocument();doc.setHtml(self.w.credito.text());self.assertEqual(doc.toPlainText(),text)
        self.w.resize(1000,560);self.app.processEvents()
        self.assertEqual(self.w.scroll_paleta.verticalScrollBar().maximum(),0)
        self.assertLess(self.w.idioma_btn.geometry().right(),self.w.width())
