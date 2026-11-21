"""Projects saved with the retired panel must still open normally."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import copy
import unittest
from PyQt5.QtWidgets import QApplication,QPushButton
from configuracao_teste import editor_isolado as Editor
from estrutural.core.projetos import migrar
from estrutural.core.analise import analisar
from estrutural.core.exemplos import biblioteca


class RemocaoVerificacoes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_projeto_legado_preserva_modelo_e_resultados(self):
        original=copy.deepcopy(biblioteca()[0]['modelo'])
        expected=analisar(original)
        legacy=copy.deepcopy(original);legacy['verificacoes']={'versao':1,'limites':[{'metrica':'euler'}]}
        self.assertEqual(migrar(legacy),original)
        self.assertIn('verificacoes',legacy)
        w=Editor()
        try:
            w.carregar(legacy);w.validar(w.modelo)
            self.assertNotIn('verificacoes',w.modelo)
            self.assertFalse(hasattr(w,'verificacoes_btn'))
            self.assertFalse(hasattr(w,'abrir_verificacoes'))
            self.assertFalse(any('Verificações' in b.text() for b in w.findChildren(QPushButton)))
            self.assertEqual(analisar(w.modelo),expected)
        finally:w.close()
