import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from PyQt5.QtWidgets import QApplication
from configuracao_teste import editor_isolado as Editor
from estrutural.core.exemplos import biblioteca
from estrutural.core.apoios import angulo_visual
from estrutural.core.analise import analisar
from estrutural.core.exibicao import PADRAO


class Versao10(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def test_example_supports_and_didactic_loads(self):
        for item in biblioteca():
            m=item['modelo']
            with self.subTest(nome=item['nome']):
                for i,no in enumerate(m['nos']):
                    a=no.get('apoio',[])
                    if m['tipo']!='Grelha' and len(a)>=2 and a[0] and a[1] and not (len(a)>2 and a[2]):
                        self.assertAlmostEqual(angulo_visual(m,i),0,places=10)
                # Purely visual orientation must never change the solver.
                plain={**m,'nos':[{k:v for k,v in no.items() if k!='apoio_visual'} for no in m['nos']]}
                self.assertEqual(analisar(m),analisar(plain))
        item=next(e for e in biblioteca() if e['nome']=='Pórtico inclinado')
        self.assertNotIn('referência',item['nome'].lower())
        for no in item['modelo']['nos']:
            for value in no.get('carga_pontual',[]):self.assertEqual(value,round(value))
        for bar in item['modelo']['barras']:
            for c in bar.get('distribuidas',[]):self.assertEqual(c['qa'],round(c['qa']))
    def test_control_rows_share_heights(self):
        w=Editor();saved=w.preferencias.copy();night=w.noturno.isChecked();w.show()
        try:
            for lang in ('pt_BR','en_US','fr_FR'):
                w.aplicar_preferencias({**PADRAO,'idioma':lang},gravar=False)
                for width,height in [(1000,560),(1360,768),(1500,900)]:
                    w.resize(width,height);self.app.processEvents()
                    row=(w.ajustar_btn,w.xy_toggle,w.girar_btn,w.passo,w.escala)
                    self.assertEqual({c.height() for c in row},{30})
                    self.assertEqual(len({c.mapTo(w.centralWidget(),c.rect().topLeft()).y() for c in row}),1)
                    self.assertEqual(w.tema_btn.height(),w.analisar_btn.height())
                    self.assertLess(w.idioma_btn.geometry().right(),w.centralWidget().width())
                self.assertEqual(w.marca.font().family(),'Arial');self.assertTrue(w.marca.font().bold())
            self.assertTrue(any(a.data()=='mailto:schardosimmatheus@gmail.com' for a in w.menu_autor.actions()))
            for item in biblioteca():
                if item['nome'] in ('Parabólico triarticulado','Circular biarticulado'):
                    w.carregar(item['modelo']);self.assertAlmostEqual(w.canvas.carga_projetada_arco()[0],-10)
                    w.modelo['barras'][0]['distribuidas'][0]['qa']-=1
                    self.assertIsNone(w.canvas.carga_projetada_arco())
        finally:w.aplicar_preferencias(saved,gravar=False);w.noturno.setChecked(night);w.close()
