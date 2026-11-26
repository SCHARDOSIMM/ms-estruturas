"""Convergência do arco carregado por projeção e desenho sem poluição de rótulos."""
import copy
import io
import math
import os
import unittest
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PyQt5.QtWidgets import QApplication
from reportlab.pdfgen.canvas import Canvas
from estrutural.core.analise import analisar
from estrutural.core.exibicao import Formatador
from estrutural.ui.rotulos import nos_rotulados,cargas_projetadas,extremos_globais
from estrutural.ui.relatorio_vetorial import Figura,fontes
from configuracao_teste import editor_isolado


def quarto_circular(n):
    nos=[{'x':4*(1-math.cos(math.pi*i/(2*n))),'y':4*math.sin(math.pi*i/(2*n))} for i in range(n+1)]
    nos[0]['apoio']=[1,1,0];nos[-1]['apoio']=[1,0,0];barras=[]
    for i,(a,b) in enumerate(zip(nos,nos[1:])):
        dx,dy=b['x']-a['x'],b['y']-a['y'];L=math.hypot(dx,dy)
        barras.append({'i':i,'j':i+1,'EA':1e6,'EI':20000,'distribuidas':[
            {'qa':-20*dx/L,'eixo':'global_y'},{'qa':30*dy/L,'eixo':'global_x'}]})
    return {'tipo':'Arco','nos':nos,'barras':barras}


class RecordingCanvas(Canvas):
    def __init__(self):self.textos=[];super().__init__(io.BytesIO())
    def drawString(self,x,y,text,*args,**kw):
        self.textos.append(str(text));return super().drawString(x,y,text,*args,**kw)


class ArcosExtremos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_carga_continua_e_convergencia_sem_mudar_apoios(self):
        erros=[]
        for n in (12,48,96):
            m=quarto_circular(n);snapshot=copy.deepcopy(m);r=analisar(m)
            self.assertEqual(m,snapshot)
            self.assertAlmostEqual(r['reacoes'][0][0],-20,places=6)
            self.assertAlmostEqual(r['reacoes'][0][1],80,places=6)
            self.assertAlmostEqual(r['reacoes'][-1][0],-100,places=6)
            erros.append(abs(max(p['M'] for b in r['barras'] for p in b['pontos'])-20))
            # α=30° is an existing section for each of these meshes.
            self.assertAlmostEqual(r['barras'][n//3-1]['pontos'][-1]['M'],20,places=6)
        self.assertLess(erros[1],erros[0]/10)
        self.assertLess(erros[2],erros[1]/3)
        self.assertLess(erros[2],.01)

    def test_rotulos_preservam_apoios_rotulas_e_selecao(self):
        m=quarto_circular(48);m['barras'][15]['rotula_j']=True
        self.assertEqual(nos_rotulados(m),{0,16,48})
        self.assertEqual(nos_rotulados(m,25),{0,16,25,48})
        m['tipo']='Pórtico plano'
        self.assertEqual(nos_rotulados(m),set(range(49)))

    def test_cargas_por_projecao_reavaliadas_apos_editar(self):
        m=quarto_circular(48);grupos=cargas_projetadas(m)
        self.assertEqual({c['eixo'] for c in grupos},{'global_y','global_x'})
        self.assertAlmostEqual(next(c['q'] for c in grupos if c['eixo']=='global_y'),-20)
        self.assertAlmostEqual(next(c['q'] for c in grupos if c['eixo']=='global_x'),30)
        m['barras'][4]['distribuidas'][1]['qa']*=2
        self.assertEqual([c['eixo'] for c in cargas_projetadas(m)],['global_y'])
        m['nos'][4]['x']+=.01
        self.assertEqual(cargas_projetadas(m),[])

    def test_editor_mostra_extremos_e_mantem_consulta_de_todas_as_barras(self):
        w=editor_isolado()
        try:
            w.resize(1360,850);w.show();w.carregar(quarto_circular(48));w.calcular();w.ajustar_vista();w.escolher_diagrama('M');self.app.processEvents();w.canvas.grab()
            self.assertEqual(len(extremos_globais(w.resultado,'M')),2)
            self.assertLessEqual(len(w.canvas.chaves_valores),2)
            self.assertEqual({hit[2] for hit in w.canvas.diagrama_hits},set(range(48)))
            w.no_selecionado=20;self.app.processEvents();w.canvas.grab()
            self.assertEqual(len(w.resultado['barras']),48)
        finally:w.close()

    def test_pdf_da_estrutura_e_dos_esforcos_com_poucos_rotulos(self):
        m=quarto_circular(48);r=analisar(m);f=Formatador(r);fontes()
        c=RecordingCanvas();Figura(m,r,f,height=290).drawOn(c,0,0)
        self.assertLess(len(c.textos),12)
        self.assertTrue(any('projeção X' in t for t in c.textos))
        self.assertTrue(any('projeção Y' in t for t in c.textos))
        c=RecordingCanvas();Figura(m,r,f,'M').drawOn(c,0,0)
        self.assertLessEqual(len([t for t in c.textos if t.startswith('B')]),2)

    def test_editor_oferece_carga_horizontal(self):
        from estrutural.ui.cargas_visuais import EditorCarga
        from estrutural.ui.arcos import DialogoArco
        w=editor_isolado()
        try:
            d=EditorCarga(w,5,'Retangular');d.eixo.setCurrentText('Horizontal global X');d.qa.setValue(7)
            self.assertEqual(d.montar()['eixo'],'global_x');self.assertEqual(d.montar()['qa'],7);d.close()
            a=DialogoArco(w);self.assertGreaterEqual(a.segmentos.value(),48);self.assertGreaterEqual(a.segmentos.maximum(),192);a.close()
        finally:w.close()


if __name__=='__main__':unittest.main()
