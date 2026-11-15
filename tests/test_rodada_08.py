import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from unittest.mock import patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont,QFontDatabase
from configuracao_teste import editor_isolado as Editor
from estrutural.core.exemplos import biblioteca
from estrutural.core.analise import analisar
from estrutural.core.exibicao import PADRAO
from estrutural.core.idiomas import traduzir


class Refinamentos08(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([]);cls.fonte=cls.app.font()
        cls.font_id=QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf')
        cls.app.setFont(QFont('Segoe UI',9))
    @classmethod
    def tearDownClass(cls):cls.app.setFont(cls.fonte)
    def test_reference_frame_equilibrium_and_hinge(self):
        item=next(e for e in biblioteca() if e['nome']=='Pórtico inclinado');m=item['modelo'];r=analisar(m)
        for idx,rx,ry in [(0,25,67.5),(7,-25,92.5)]:
            self.assertAlmostEqual(r['reacoes'][idx][0],rx,places=9)
            self.assertAlmostEqual(r['reacoes'][idx][1],ry,places=9)
            self.assertAlmostEqual(r['reacoes'][idx][2],0,places=9)
        self.assertLess(max(map(abs,r['equilibrio'])),1e-8)
        self.assertAlmostEqual(r['barras'][2]['pontos'][-1]['M'],0,places=9)
        from estrutural.core.cargas import integrar
        resultante=sum(integrar(c,r['barras'][i]['L'],lambda x:1) for i,b in enumerate(m['barras']) for c in b.get('distribuidas',[]))
        self.assertAlmostEqual(resultante,-80,places=9)
        self.assertTrue(traduzir(item['descricao'],'en_US').startswith('2 m panels'))
    def test_links_alignment_and_brand(self):
        w=Editor();saved=w.preferencias.copy();night=w.noturno.isChecked();w.show()
        try:
            self.assertEqual(w.marca.text(),'MS Estruturas')
            self.assertEqual(w.marca.font().family(),'Arial');self.assertTrue(w.marca.font().bold())
            for lang in ('pt_BR','en_US'):
                w.aplicar_preferencias({**PADRAO,'idioma':lang},gravar=False)
                for width,height in [(1000,560),(1180,680),(1360,768),(1500,900)]:
                    w.resize(width,height);self.app.processEvents()
                    self.assertLess(w.idioma_btn.geometry().right(),w.centralWidget().width())
                    self.assertEqual(w.scroll_paleta.verticalScrollBar().maximum(),0)
                    self.assertTrue(w.marca.isVisible())
                    if width>=1180:
                        self.assertEqual(w.analisar_btn.width(),108)
                        text=w.analisar_btn.fontMetrics().horizontalAdvance(w.analisar_btn.text())
                        if self.font_id>=0:self.assertGreater(w.analisar_btn.width()-text-w.analisar_btn.iconSize().width(),18)
                self.assertIn('Created by' if lang=='en_US' else 'Criado por',w.credito.text())
            with patch('estrutural.ui.editor.QDesktopServices.openUrl',return_value=True) as abrir:
                actions=w.menu_autor.actions();self.assertEqual([a.text() for a in actions],['GitHub','LinkedIn','E-mail'])
                for a in actions:a.trigger()
                self.assertEqual([c.args[0].toString() for c in abrir.call_args_list],['https://github.com/SCHARDOSIMM','https://www.linkedin.com/in/matheus-schardosim/','mailto:schardosimmatheus@gmail.com'])
            item=next(e for e in biblioteca() if e['nome']=='Pórtico inclinado');w.abrir_exemplo(item)
            self.assertEqual(w.modelo['exemplo']['rotulos_nos'][3],'G');self.assertFalse(w.canvas.grab().isNull())
        finally:
            w.aplicar_preferencias(saved,gravar=False);w.noturno.setChecked(night);w.close()
