"""French localization must leave engineering and editable project data intact."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PyQt5.QtCore import QCoreApplication, QLocale, QSettings
from PyQt5.QtWidgets import QApplication, QComboBox as ComboBase, QDialogButtonBox, QDialog, QVBoxLayout
from configuracao_teste import editor_isolado as Editor
from estrutural.core.idiomas import CATALOGO, traduzir
from estrutural.core.idiomas_fr import CATALOGO_FR
from estrutural.ui.idioma import definir, QFileDialog
from estrutural.ui.persistencia import carregar_preferencias


class IdiomaFrances(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def tearDown(self):
        definir('pt_BR')

    def test_catalogo_completo_e_termos_tecnicos(self):
        self.assertFalse(set(CATALOGO) - set(CATALOGO_FR))
        self.assertTrue(all(CATALOGO_FR.values()))
        for source, expected in [('Apoio fixo', 'Appui articulé'), ('Apoio móvel', 'Appui simple'),
                                 ('Engaste', 'Encastrement'), ('Esforço cortante', 'Effort tranchant'),
                                 ('Momento fletor', 'Moment fléchissant'), ('Grelha', 'Gril de poutres')]:
            self.assertEqual(traduzir(source, 'fr_FR'), expected)
        self.assertEqual(traduzir('Reações (*.csv)', 'fr_FR'), 'Réactions (*.csv)')
        self.assertEqual(traduzir('<b>Nó</b> 3: 2 a 6 m', 'fr_FR'), '<b>Nœud</b> 3: 2 à 6 m')
        self.assertEqual(traduzir('Nó123 abcNó', 'fr_FR'), 'Nœud123 abcNó')
        source = 'x em metros desde o nó inicial; L = comprimento total. Use x^2, sin(pi*x/L), etc.'
        self.assertIn('L = longueur totale', traduzir(source, 'fr_FR'))
        self.assertEqual(traduzir('sin(pi*x/L) + 2.5', 'fr_FR'), 'sin(pi*x/L) + 2.5')

    def test_ciclo_persistencia_e_configuracoes(self):
        from estrutural.ui.preferencias import Preferencias
        w = Editor()
        try:
            for expected, button in [('en_US', 'FR'), ('fr_FR', 'PT'), ('pt_BR', 'EN'), ('en_US', 'FR'), ('fr_FR', 'PT')]:
                w.idioma_btn.click()
                self.assertEqual(w.preferencias['idioma'], expected)
                self.assertEqual(w.idioma_btn.text(), button)
                self.assertEqual(carregar_preferencias(w.config)['idioma'], expected)
            d = Preferencias(w)
            self.assertEqual(d.idioma.count(), 3)
            self.assertEqual(d.idioma.currentText(), 'Français')
            d.aplicar()
            self.assertEqual(d.resultado['idioma'], 'fr_FR')
            self.assertEqual(w.cabecalho_csv(['barra', 'perfil', 'no', 'N_kN']), ['barre', 'section', 'nœud', 'N_kN'])
            reopened = type(w)(config=QSettings(w.config.fileName(), QSettings.IniFormat))
            try:
                self.assertEqual(reopened.preferencias['idioma'], 'fr_FR')
                self.assertEqual(ComboBase.currentText(reopened.tipo), traduzir(reopened.tipo.currentText(), 'fr_FR'))
            finally:
                reopened.close()
        finally:
            w.close()

    def test_janelas_abertas_sem_alterar_modelo_resultados_ou_entradas(self):
        from estrutural.ui.cargas_visuais import EditorCarga
        w = Editor()
        d = None
        try:
            w.exemplo(); w.calcular(); w.coordenadas()
            w.modelo['nome'] = 'Projeto pessoal — Nó / Beam'
            original = copy.deepcopy(w.modelo)
            results = copy.deepcopy(w.resultado)
            history = len(w.historico)
            d = EditorCarga(w, 6, 'Triangular'); d.show()
            for lang, title, load in [('fr_FR', 'Saisie des coordonnées — Ctrl+E', 'Appliquer la charge'),
                                      ('en_US', 'Coordinate entry — Ctrl+E', 'Apply load'),
                                      ('pt_BR', 'Entrada de coordenadas — Ctrl+E', 'Aplicar carga'),
                                      ('fr_FR', 'Saisie des coordonnées — Ctrl+E', 'Appliquer la charge')]:
                w.aplicar_preferencias({**w.preferencias, 'idioma': lang}, gravar=False)
                self.app.processEvents()
                self.assertEqual(w.painel_coordenadas.windowTitle(), title)
                self.assertEqual(d.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok).text(), load)
                self.assertEqual(d.tipo.currentText(), 'Triangular crescente')
                self.assertEqual(w.modelo, original)
                self.assertEqual(w.resultado, results)
                self.assertEqual(len(w.historico), history)
                self.assertEqual(w.tipo.currentText(), 'Viga')
            self.assertEqual(ComboBase.currentText(w.tipo), 'Poutre')
            self.assertEqual(QLocale().name(), 'fr_FR')
            self.assertEqual(QCoreApplication.translate('QPlatformTheme', 'Cancel'), 'Annuler')
            self.assertEqual(QCoreApplication.translate('QFileDialog', 'Look in:'), 'Voir dans :')
        finally:
            if d is not None: d.close()
            w.close()

    def test_filtros_e_relatorio_frances(self):
        from reportlab.platypus import Paragraph
        from estrutural.ui.relatorio import gerar_relatorio
        w = Editor()
        try:
            w.aplicar_preferencias({**w.preferencias, 'idioma': 'fr_FR'}, gravar=False)
            with patch('estrutural.ui.arquivos.DialogoSalvar') as factory:
                dialog = factory.return_value
                dialog.Accepted = 1; dialog.exec_.return_value = 1
                dialog.selectedFiles.return_value = ['essai.pdf']
                dialog.selectedNameFilter.return_value = 'Rapport PDF (*.pdf)'
                self.assertEqual(QFileDialog.getSaveFileName(w, 'Exportar', '', 'Relatório PDF (*.pdf);;Resultados (*.csv)'),
                                 ('essai.pdf', 'Relatório PDF (*.pdf)'))
                self.assertEqual(factory.call_args.args[1], 'Exporter')
            w.exemplo(); w.calcular()
            texts = []
            original_init = Paragraph.__init__
            def capture(paragraph, text, *args, **kwargs):
                texts.append(text)
                original_init(paragraph, text, *args, **kwargs)
            with tempfile.TemporaryDirectory() as folder, patch.object(Paragraph, '__init__', capture):
                path = Path(folder) / 'essai-fr.pdf'
                gerar_relatorio(str(path), w.modelo, w.resultado, w.preferencias)
                self.assertTrue(path.read_bytes().startswith(b'%PDF-'))
                self.assertGreater(path.stat().st_size, 10000)
            content = '\n'.join(texts)
            self.assertIn('RÉACTIONS D’APPUI', content)
            self.assertIn('Moment fléchissant', content)
            self.assertNotIn('Reações de apoio', content)
        finally:
            w.close()

    def test_botoes_padrao_qt_em_janela_aberta(self):
        from estrutural.ui.idioma import atualizar
        d = QDialog()
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, d)
        layout = QVBoxLayout(d); layout.addWidget(buttons)
        d.show()
        try:
            for lang, expected in [('en_US','Cancel'), ('fr_FR','Annuler'), ('pt_BR','Cancelar'), ('fr_FR','Annuler'), ('en_US','Cancel')]:
                definir(lang); atualizar(d); self.app.processEvents()
                self.assertEqual(buttons.button(QDialogButtonBox.Cancel).text().replace('&',''), expected)
                self.assertEqual(buttons.button(QDialogButtonBox.Ok).text().replace('&',''), 'OK')
        finally:
            d.close()
