"""Exercise the real Qt save dialog and generated PDF, without opening a reader."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from PyQt5.QtWidgets import QApplication,QFileDialog as Base,QLineEdit,QMessageBox
from PyQt5.QtCore import QTimer,Qt
from PyQt5.QtTest import QTest
from estrutural.ui.idioma import QFileDialog,definir
from estrutural.ui.arquivos import nome_com_extensao
from configuracao_teste import editor_isolado as Editor
from estrutural.core.exibicao import PADRAO


class Salvamento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_names(self):
        for nome,esperado in [('relatorio','relatorio.pdf'),('relatorio.PDF','relatorio.PDF'),('modelo.v1','modelo.v1.pdf'),('relatorio.txt','relatorio.txt.pdf'),('relatorio.','relatorio.pdf')]:
            self.assertEqual(nome_com_extensao(nome,'Relatório PDF (*.pdf)'),esperado)
        self.assertEqual(nome_com_extensao('','Relatório PDF (*.pdf)'),'')

    def preencher(self,directory,name,filtro=None):
        d=self.app.activeModalWidget();self.assertIsInstance(d,Base)
        d.setDirectory(str(directory))
        if filtro:d.selectNameFilter(filtro)
        d.findChild(QLineEdit,'fileNameEdit').setText(name);d.accept()

    def test_extension_follows_current_filter_in_both_languages(self):
        try:
            with tempfile.TemporaryDirectory() as folder:
                directory=Path(folder).resolve()
                for lang,pdf,csv in [('pt_BR','Relatório PDF (*.pdf)','Resultados (*.csv)'),('en_US','PDF report (*.pdf)','Results (*.csv)')]:
                    definir(lang)
                    for chosen,extension in [(pdf,'.pdf'),(csv,'.csv')]:
                        QTimer.singleShot(50,lambda f=chosen:self.preencher(directory,'modelo.v1',f))
                        path,selected=QFileDialog.getSaveFileName(None,'Exportar',folder,'Relatório PDF (*.pdf);;Resultados (*.csv)')
                        self.assertEqual(Path(path).name,'modelo.v1'+extension)
                        self.assertEqual(selected,'Relatório PDF (*.pdf)' if extension=='.pdf' else 'Resultados (*.csv)')
        finally:definir('pt_BR')

    def test_overwrite_checks_the_final_pdf_name(self):
        with tempfile.TemporaryDirectory() as folder:
            directory=Path(folder).resolve();target=directory/'existente.pdf';target.write_bytes(b'original')
            def recusar():
                box=self.app.activeModalWidget();self.assertIsInstance(box,QMessageBox)
                box.done(QMessageBox.No)
                QTimer.singleShot(30,lambda:self.app.activeModalWidget().reject())
            if self.app.platformName()=='offscreen':
                # Qt's Windows standard-messagebox icon can crash the offscreen
                # platform. Native Windows runs also exercise the real prompt.
                with patch('estrutural.ui.arquivos.QMessageBox.question',return_value=QMessageBox.No) as pergunta:
                    def cancelar():
                        self.preencher(directory,'existente');self.app.activeModalWidget().reject()
                    QTimer.singleShot(50,cancelar)
                    path,_=QFileDialog.getSaveFileName(None,'Salvar',folder,'Relatório PDF (*.pdf)')
                    self.assertTrue(pergunta.called);self.assertIn('existente.pdf',pergunta.call_args.args[2])
            else:
                QTimer.singleShot(50,lambda:(QTimer.singleShot(80,recusar),self.preencher(directory,'existente')))
                path,_=QFileDialog.getSaveFileName(None,'Salvar',folder,'Relatório PDF (*.pdf)')
            self.assertEqual(path,'');self.assertEqual(target.read_bytes(),b'original')

    def test_report_button_produces_named_valid_pdf(self):
        w=Editor();saved=w.preferencias.copy();night=w.noturno.isChecked();w.aplicar_preferencias(PADRAO,gravar=False)
        try:
            w.exemplo();w.calcular()
            with tempfile.TemporaryDirectory() as folder:
                directory=Path(folder).resolve()
                QTimer.singleShot(50,lambda:self.preencher(directory,'ensaio'))
                w.relatorio_pdf();target=directory/'ensaio.pdf'
                self.assertTrue(target.exists());self.assertFalse((directory/'ensaio').exists())
                data=target.read_bytes();self.assertTrue(data.startswith(b'%PDF-'));self.assertTrue(data.rstrip().endswith(b'%%EOF'))
                self.assertGreater(len(data),10000)
        finally:w.aplicar_preferencias(saved,gravar=False);w.noturno.setChecked(night);w.close()
