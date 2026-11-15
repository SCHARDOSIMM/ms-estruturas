import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PyQt5.QtCore import QSettings
from estrutural.ui.arquivos import pasta_inicial,lembrar_pasta


class PastasUsuario(unittest.TestCase):
    def test_documentos_e_ultima_pasta_sem_usar_instalacao(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);docs=root/'Documentos';docs.mkdir()
            parent=SimpleNamespace(config=QSettings(str(root/'preferencias.ini'),QSettings.IniFormat))
            with patch('estrutural.ui.arquivos.QStandardPaths.writableLocation',return_value=str(docs)):
                self.assertEqual(Path(pasta_inicial(parent)),docs)
                self.assertFalse((docs/'MS Estruturas').exists())
                self.assertEqual(Path(pasta_inicial(parent,salvar=True)),docs/'MS Estruturas')
                self.assertTrue((docs/'MS Estruturas').is_dir())
                escolhida=root/'Projetos';escolhida.mkdir();lembrar_pasta(parent,str(escolhida/'modelo.json'))
                self.assertEqual(Path(pasta_inicial(parent,salvar=True)),escolhida)
