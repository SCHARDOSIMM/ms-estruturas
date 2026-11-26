"""Fluxos integrados em Qt sem exigir exibição de janelas durante os testes."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from configuracao_teste import editor_isolado as Editor
from estrutural.ui.perfis import SeletorPerfil
from estrutural.core.exemplos import biblioteca


class Interface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):self.w=Editor();self.saved=self.w.noturno.isChecked();self.w.show();self.app.processEvents()
    def tearDown(self):self.w.noturno.setChecked(self.saved);self.w.close()
    def test_biblioteca_e_resultados(self):
        for e in biblioteca():
            with self.subTest(exemplo=e['nome']):
                self.w.abrir_exemplo(e);self.assertIsNotNone(self.w.resultado)
                for modo in ('Reações','Esforços','Diagramas','Deformada'):
                    self.w.exibir_resultado(modo);self.assertEqual(self.w.modo_resultado,modo);self.assertFalse(self.w.canvas.grab().isNull())
                self.w.escolher_diagrama('M');self.w.canvas.grab()
                self.assertTrue(self.w.canvas.diagrama_hits)
        for btn,nome in self.w.botoes_icones:self.assertNotIn('Carga nodal',btn.toolTip())
    def test_entrada_exata_e_bidirecional(self):
        self.w.coordenadas();c=self.w.painel_coordenadas
        c.x.setValue(1.12345);c.y.setValue(2.6789);QTest.keyClick(c.y,Qt.Key_Return)
        self.assertEqual(len(self.w.modelo['nos']),1)
        QTest.keyClick(c.y,Qt.Key_Return);self.assertEqual(len(self.w.modelo['nos']),1)
        c.x.setValue(4);QTest.keyClick(c.y,Qt.Key_Return);c.i.setValue(1);c.j.setValue(2);c.barra()
        self.assertEqual(len(self.w.modelo['barras']),1)
        c.tabela.item(0,1).setText('1.5');self.assertEqual(self.w.modelo['nos'][0]['x'],1.5)
        self.w.undo();self.assertAlmostEqual(float(c.tabela.item(0,1).text()),1.12345)
        c.close()
    def test_perfis_unidades_e_sobrescrita(self):
        d=SeletorPerfil(self.w)
        for f in ('Retangular','Quadrado','Circular maciço','Tubo circular','Caixão','I/H','U','T','L','Arbitrário'):
            d.familia.setCurrentText(f);self.assertFalse(d.esquema.grab().isNull())
        d.catalogo.setCurrentIndex(2);b=d.dimensoes()['b'];d.unidade.setCurrentText('m');self.assertAlmostEqual(d.dimensoes()['b'],b,places=10)
        d.checks['Ix'].setChecked(True);d.overrides['Ix'].setText('0.002');self.assertEqual(d.config()['sobrescritos']['Ix'],.002)
        d.restaurar();self.assertFalse(d.config()['sobrescritos']);d.close()
    def test_svg_temas_atalhos(self):
        for dark in (False,True):
            self.w.noturno.setChecked(dark)
            for btn,nome in self.w.botoes_icones:
                self.assertFalse(btn.icon().isNull())
                if nome=='Salvar':self.assertEqual(btn.toolTip(),'Salvar (Ctrl+S)')
            self.w.canvas.grab()
    def test_persistencia_e_exportacao_com_perfil(self):
        import tempfile,json,csv
        from pathlib import Path
        from unittest.mock import patch
        from estrutural.core.secoes import aplicar_secao
        self.w.exemplo()
        c={'familia':'Retangular','dimensoes':{'b':.2,'h':.3},'E_MPa':200000,'G_MPa':80000}
        self.w.modelo['barras'][0]=aplicar_secao(self.w.modelo['barras'][0],c);self.w.calcular()
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path=Path(folder).resolve();self.assertEqual(path.parent,Path(__file__).parent.resolve())
            project=path/'projeto.json';csvpath=path/'esforcos.csv'
            with patch('estrutural.ui.editor.QFileDialog.getSaveFileName',return_value=(str(project),'Projeto (*.json)')):self.w.salvar()
            original=json.loads(project.read_text(encoding='utf-8'));self.assertEqual(original['barras'][0]['secao'],c)
            # Formato anterior: campo carga sem sufixo.
            original['nos'][1]['carga']=[0,-5,0];project.write_text(json.dumps(original),encoding='utf-8')
            with patch('estrutural.ui.editor.QFileDialog.getOpenFileName',return_value=(str(project),'Projeto (*.json)')):self.w.abrir()
            self.assertEqual(self.w.modelo['nos'][1]['carga_pontual'],[0,-5,0]);self.w.calcular()
            with patch('estrutural.ui.editor.QFileDialog.getSaveFileName',return_value=(str(csvpath),'Resultados (*.csv)')):self.w.exportar()
            with csvpath.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f,delimiter=';'))
            self.assertIn('A_m2',rows[0]);self.assertIn('Retangular',rows[1]);self.assertGreater(len(rows),40)
    def test_arco_gui_preserva_estrutura_existente(self):
        from PyQt5.QtCore import QTimer
        from PyQt5.QtWidgets import QDialogButtonBox
        self.w.exemplo();original=self.w.modelo['barras'][0].copy()
        QTimer.singleShot(40,lambda:self.app.activeModalWidget().findChild(QDialogButtonBox).button(QDialogButtonBox.Ok).click())
        self.w.criar_arco();self.assertEqual(len(self.w.modelo['barras']),97);self.assertEqual(self.w.modelo['barras'][0],original)
        self.w.undo();self.assertEqual(len(self.w.modelo['barras']),1)
    def test_botoes_sem_duplicacao_e_material(self):
        from estrutural.ui.materiais import SeletorMaterial
        self.assertEqual([b.text() for b in self.w.grupo_resultados.buttons()],['Reações','Esforços'])
        self.assertIn('Arco',self.w.botoes_ferramentas)
        d=SeletorMaterial(self.w);d.campos['E_MPa'].setValue(200000);d.campos['nu'].setValue(.25)
        self.assertAlmostEqual(d.campos['G_MPa'].value(),80000)
        d.vincular.setChecked(False);d.campos['G_MPa'].setValue(70000);d.aplicar();self.assertEqual(d.resultado['G_MPa'],70000)
    def test_relatorio_pdf_paginado(self):
        import tempfile,re
        from pathlib import Path
        from estrutural.ui.relatorio import gerar_relatorio
        self.w.exemplo();self.w.calcular()
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path=Path(folder).resolve();self.assertEqual(path.parent,Path(__file__).parent.resolve())
            target=path/'relatorio.pdf';gerar_relatorio(target,self.w.modelo,self.w.resultado);data=target.read_bytes()
            self.assertTrue(data.startswith(b'%PDF'));self.assertEqual(len(re.findall(rb'/Type /Page\b',data)),3);self.assertNotIn(b'/Subtype /Image',data)


if __name__=='__main__':unittest.main()
