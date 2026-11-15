import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import json
import tempfile
import unittest
import subprocess
import sys
from pathlib import Path
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication
from estrutural.ui.editor import Editor
from estrutural.core.exibicao import PADRAO
from estrutural.ui.persistencia import carregar_preferencias


class Persistencia(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.pasta=tempfile.TemporaryDirectory();self.path=str(Path(self.pasta.name)/'preferencias.ini');self.janelas=[]
    def tearDown(self):
        for w in self.janelas:w.close()
        self.pasta.cleanup()
    def config(self):return QSettings(self.path,QSettings.IniFormat)
    def abrir(self):
        w=Editor(config=self.config());self.janelas.append(w);return w
    def test_primeiro_uso_tem_padrao_pedido(self):
        w=self.abrir()
        self.assertTrue(w.grade_check.isChecked());self.assertTrue(w.canvas.grade)
        self.assertTrue(w.snap.isChecked());self.assertFalse(w.noturno.isChecked())
        self.assertEqual(w.preferencias['idioma'],'pt_BR');self.assertEqual(w.idioma_btn.text(),'EN')
    def test_controles_salvam_imediatamente_e_reabrem(self):
        w=self.abrir();w.grade_check.setChecked(False);w.snap.setChecked(False);w.tema_btn.click();w.idioma_btn.click();w.passo.setValue(.25);w.xy_toggle.setChecked(False)
        # A distinct settings instance sees all changes before window close.
        op=carregar_preferencias(self.config())
        self.assertFalse(op['grade']);self.assertFalse(op['snap']);self.assertTrue(op['escuro']);self.assertEqual(op['idioma'],'en_US')
        w.close();outro=self.abrir()
        self.assertFalse(outro.grade_check.isChecked());self.assertFalse(outro.canvas.grade)
        self.assertFalse(outro.snap.isChecked());self.assertTrue(outro.noturno.isChecked());self.assertTrue(outro.tema_btn.isChecked())
        self.assertEqual(outro.preferencias['idioma'],'en_US');self.assertEqual(outro.passo.value(),.25);self.assertFalse(outro.xy_toggle.isChecked())
        outro.grade_check.setChecked(True);outro.snap.setChecked(True);outro.tema_btn.click();outro.idioma_btn.click();outro.close()
        terceiro=self.abrir();self.assertTrue(terceiro.grade_check.isChecked());self.assertTrue(terceiro.snap.isChecked())
        self.assertFalse(terceiro.noturno.isChecked());self.assertEqual(terceiro.preferencias['idioma'],'pt_BR')
    def test_configuracoes_e_escalas_independentes(self):
        w=self.abrir();op={**PADRAO,'forca':'N','deslocamento':'cm','decimais':2,'tolerancia_zero':.001,'relativo_desloc':1e-7,'mostrar_valores':False,'escala_deformada':1500.}
        w.aplicar_preferencias(op);w.escala.setValue(85);w.escolher_diagrama('Deformada');self.assertEqual(w.escala.value(),1500)
        w.escala.setValue(2000);w.escolher_diagrama('M');self.assertEqual(w.escala.value(),85)
        w.close();outro=self.abrir()
        self.assertEqual(outro.escala.value(),85);self.assertEqual(outro.preferencias['escala_deformada'],2000)
        for key in ('forca','deslocamento','decimais','tolerancia_zero','relativo_desloc','mostrar_valores'):self.assertEqual(outro.preferencias[key],op[key])
    def test_carregamento_nao_regrava_estados_intermediarios(self):
        w=self.abrir();w.tema_btn.click();w.snap.setChecked(False)
        antes=self.config().value('preferencias');legacy=self.config().value('modo_noturno',type=bool)
        w.aplicar_preferencias(PADRAO,gravar=False)
        self.assertEqual(self.config().value('preferencias'),antes)
        self.assertEqual(self.config().value('modo_noturno',type=bool),legacy)
    def test_migracao_de_tema_antigo_e_config_invalida(self):
        c=self.config();c.setValue('preferencias',json.dumps({'idioma':'en_US','escuro':False,'snap':False}));c.setValue('modo_noturno',True);c.sync()
        w=self.abrir();self.assertTrue(w.noturno.isChecked());self.assertFalse(w.snap.isChecked());self.assertEqual(w.preferencias['idioma'],'en_US')
        c.setValue('preferencias','json invalido');c.remove('modo_noturno');c.sync()
        op=carregar_preferencias(self.config());self.assertEqual(op,PADRAO)
    def test_valores_invalidos_usam_padrao_sem_erro(self):
        c=self.config();c.setValue('preferencias',json.dumps({'grade':'false','snap':None,'idioma':'x','escuro':12,'passo':-99,'forca':'kg','decimais':'x'}));c.sync()
        w=self.abrir();self.assertTrue(w.grade_check.isChecked());self.assertTrue(w.snap.isChecked());self.assertFalse(w.noturno.isChecked())
        self.assertEqual(w.passo.value(),.01);self.assertEqual(w.preferencias['forca'],'kN');self.assertEqual(w.preferencias['idioma'],'pt_BR')
    def test_reabertura_em_outro_processo(self):
        codigo='''
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings
from estrutural.ui.editor import Editor
app=QApplication([])
w=Editor(config=QSettings(sys.argv[1],QSettings.IniFormat))
if sys.argv[2]=='gravar':
    assert w.grade_check.isChecked() and w.snap.isChecked()
    assert not w.noturno.isChecked() and w.preferencias['idioma']=='pt_BR'
    w.grade_check.setChecked(False);w.snap.setChecked(False)
    w.tema_btn.click();w.idioma_btn.click()
else:
    assert not w.grade_check.isChecked() and not w.canvas.grade
    assert not w.snap.isChecked() and w.noturno.isChecked()
    assert w.preferencias['idioma']=='en_US'
w.close()
'''
        env={**os.environ,'QT_QPA_PLATFORM':'offscreen'}
        for modo in ('gravar','ler'):
            with self.subTest(processo=modo):
                result=subprocess.run([sys.executable,'-c',codigo,self.path,modo],capture_output=True,text=True,env=env,timeout=30)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
