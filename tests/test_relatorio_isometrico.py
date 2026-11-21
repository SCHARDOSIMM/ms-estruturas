"""Exercise actual PDF vector paths, not only the projection helper."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import copy
from io import BytesIO
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from reportlab.pdfgen.canvas import Canvas
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase,QImage
from configuracao_teste import editor_isolado as Editor
from estrutural.core.analise import analisar
from estrutural.core.exemplos import biblioteca
from estrutural.core.exibicao import Formatador,PADRAO
from estrutural.ui.projecao_grelha import projetar,angulo_apoio
from estrutural.ui.relatorio_vetorial import Figura,ProjecaoFigura,fontes,gerar_relatorio


class CanvasGravado(Canvas):
    def __init__(self):
        super().__init__(BytesIO());self.linhas=[];self.caminhos=[];self.angulos=[];self.textos=[]
    def line(self,*args):self.linhas.append(args);return super().line(*args)
    def rotate(self,angle):self.angulos.append(angle);return super().rotate(angle)
    def drawString(self,x,y,text,*args,**kwargs):self.textos.append(text);return super().drawString(x,y,text,*args,**kwargs)
    def beginPath(self):
        path=super().beginPath();points=[];self.caminhos.append(points)
        move,line=path.moveTo,path.lineTo
        def moveto(x,y):points.append((x,y));move(x,y)
        def lineto(x,y):points.append((x,y));line(x,y)
        path.moveTo=moveto;path.lineTo=lineto
        return path


class RelatorioIsometrico(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf');fontes()

    def grelha(self):return copy.deepcopy(next(i['modelo'] for i in biblioteca() if i['nome']=='Grelha em L'))

    def render(self,m,r,key=None):
        c=CanvasGravado();fig=Figura(m,r,Formatador(r),key,height=250);fig.canv=c;fig.draw();return c

    def test_barras_e_engastes_projetados_no_pdf(self):
        m=self.grelha();r=analisar(m);c=self.render(m,r);view=ProjecaoFigura(m,504,250)
        for b in m['barras']:
            a,z=[m['nos'][b[k]] for k in ('i','j')]
            self.assertIn((*view.point(a['x'],a['y']),*view.point(z['x'],z['y'])),c.linhas)
        self.assertAlmostEqual(c.angulos[0],-angulo_apoio(m,0))
        dx,dy=[view.point(*v) for v in ((1,0),(0,1))]
        self.assertGreater(dx[0],dy[0]);self.assertAlmostEqual(dx[1],dy[1])
        w=Editor()
        try:
            w.carregar(m);w.canvas.zoom=1
            origin=w.canvas.tela(0,0)
            for n in m['nos']:
                screen=w.canvas.tela(n['x'],n['y'])-origin
                pdf=view.point(n['x'],n['y']);zero=view.point(0,0)
                self.assertAlmostEqual((pdf[0]-zero[0])/view.scale,screen.x())
                self.assertAlmostEqual((pdf[1]-zero[1])/view.scale,-screen.y())
        finally:w.close()

    def test_diagramas_e_deformada_deslocam_em_z(self):
        m=self.grelha();r=analisar(m);view=ProjecaoFigura(m,504,250)
        for key in ('V','M','T','D'):
            with self.subTest(diagrama=key):
                c=self.render(m,r,key)
                curves=[p for p in c.caminhos if len(p)>=80] if key=='D' else [p for p in c.caminhos if len(p)==41]
                self.assertEqual(len(curves),len(m['barras']))
                for i,b in enumerate(m['barras']):
                    a,z=[m['nos'][b[k]] for k in ('i','j')];L=r['barras'][i]['L']
                    data=r['barras'][i]['deformacoes' if key=='D' else 'pontos']
                    for P,v in zip(curves[i],data):
                        base=view.point(a['x']+(z['x']-a['x'])*v['x']/L,a['y']+(z['y']-a['y'])*v['x']/L)
                        self.assertAlmostEqual(P[0],base[0])
                        if key=='D':self.assertAlmostEqual(P[1]-base[1],v['uy']/Formatador(r).max_desloc*42)

    def test_momentos_nodais_e_cargas_nulas_com_tolerancia_zero(self):
        m=self.grelha();m['nos'][2]['carga_pontual']=[0,3,-4];r=analisar(m)
        c=CanvasGravado();fig=Figura(m,r,Formatador(r,{**PADRAO,'tolerancia_zero':0}),height=250);fig.canv=c;fig.draw()
        self.assertTrue(any('Mx=3' in text for text in c.textos));self.assertTrue(any('My=-4' in text for text in c.textos))
        self.assertGreaterEqual(len([p for p in c.caminhos if len(p)==25]),2)

    def test_relatorios_vetoriais_em_todos_os_idiomas_sem_alterar_resultados(self):
        with tempfile.TemporaryDirectory() as folder:
            for item in biblioteca():
                if item['modelo']['tipo']!='Grelha':continue
                m=copy.deepcopy(item['modelo']);r=analisar(m);before=copy.deepcopy((m,r))
                for lang in ('pt_BR','en_US','fr_FR'):
                    target=Path(folder)/'relatorio.pdf';gerar_relatorio(target,m,r,{**PADRAO,'idioma':lang,'tolerancia_zero':0})
                    data=target.read_bytes();self.assertTrue(data.startswith(b'%PDF-'));self.assertNotIn(b'/Subtype /Image',data)
                self.assertEqual((m,r),before)

    def test_momento_concentrado_na_barra_aparece_com_sinal(self):
        for sign in (-1,1):
            m={'tipo':'Viga','nos':[{'x':0,'y':0,'apoio':[1,1,1]},{'x':3,'y':0}],
               'barras':[{'i':0,'j':1,'EA':1e6,'EI':20000,'pontuais':[{'x':1.5,'m':7*sign}]}]}
            c=self.render(m,analisar(m))
            self.assertIn(str(7*sign)+' kN·m',c.textos)
            self.assertTrue(any(len(path)==25 for path in c.caminhos))

    def test_png_exportado_e_o_proprio_canvas_isometrico(self):
        w=Editor();w.show();w.resize(1000,680);self.app.processEvents()
        try:
            w.carregar(self.grelha());w.calcular();w.ajustar_vista();self.app.processEvents()
            with tempfile.TemporaryDirectory() as folder:
                target=Path(folder)/'grelha.png'
                with patch('estrutural.ui.editor.QFileDialog.getSaveFileName',return_value=(str(target),'Imagem (*.png)')):w.exportar()
                self.assertFalse(QImage(str(target)).isNull())
                self.assertEqual(QImage(str(target)).convertToFormat(QImage.Format_ARGB32),w.canvas.grab().toImage().convertToFormat(QImage.Format_ARGB32))
        finally:w.close()
