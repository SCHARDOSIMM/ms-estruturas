"""Geometria guiada de arco com prévia antes de inserir no modelo."""
import math
from PyQt5.QtCore import Qt,QPointF
from PyQt5.QtGui import QPainter,QPen,QPolygonF
from PyQt5.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QComboBox,QLabel,QSpinBox,QDialogButtonBox,QWidget,QMessageBox
from estrutural.ui.formularios import numero
from estrutural.core.propriedades import arco
from estrutural.ui.idioma import QComboBox, QDialogButtonBox, QLabel, QPushButton, QCheckBox, tr


def gerar_arco(inicio,fim,flecha,segmentos,forma):
    m=arco(inicio,fim,flecha,segmentos)
    if forma=='Circular':
        dx,dy=fim[0]-inicio[0],fim[1]-inicio[1];L=math.hypot(dx,dy)
        if flecha<=0 or flecha>L/2:raise ValueError('Para arco circular use 0 < flecha ≤ metade da distância entre extremos.')
        R=L*L/(8*flecha)+flecha/2;offset=R-flecha;angle=math.atan2(L/2,offset)
        for i,n in enumerate(m['nos']):
            phi=-angle+2*angle*i/segmentos;u=L/2+R*math.sin(phi);v=R*math.cos(phi)-offset
            n.update(x=inicio[0]+dx/L*u-dy/L*v,y=inicio[1]+dy/L*u+dx/L*v)
    return m


class Previa(QWidget):
    def __init__(self,d):super().__init__();self.d=d;self.setMinimumHeight(190)
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.setPen(QPen(self.palette().highlight().color(),2))
        try:
            m=self.d.modelo();nos=m['nos'];xmin=min(n['x'] for n in nos);xmax=max(n['x'] for n in nos);ymin=min(n['y'] for n in nos);ymax=max(n['y'] for n in nos)
            scale=min((self.width()-60)/max(xmax-xmin,.1),(self.height()-45)/max(ymax-ymin,.1));pts=[QPointF(30+(n['x']-xmin)*scale,self.height()-25-(n['y']-ymin)*scale) for n in nos]
            p.drawPolyline(QPolygonF(pts))
            for pt in pts:p.drawEllipse(pt,2,2)
        except ValueError:p.drawText(self.rect(),Qt.AlignCenter,tr('Ajuste os parâmetros para visualizar o arco.'))
        finally:p.end()


class DialogoArco(QDialog):
    def __init__(self,parent):
        super().__init__(parent);self.setWindowTitle('Desenhar arco');self.resize(530,640);self.resultado=None
        v=QVBoxLayout(self);f=QFormLayout();v.addLayout(f);self.forma=QComboBox();self.forma.addItems(['Parabólico','Circular']);f.addRow('Forma do arco',self.forma)
        self.campos={}
        for key,label,val in [('xi','X inicial (m)',0),('yi','Y inicial (m)',0),('xf','X final (m)',6),('yf','Y final (m)',0),('flecha','Flecha normal à corda (m)',2)]:
            w=numero(val);self.campos[key]=w;f.addRow(label,w)
        self.segmentos=QSpinBox();self.segmentos.setRange(2,200);self.segmentos.setValue(96);f.addRow('Número de segmentos',self.segmentos)
        info=QLabel('O arco será acrescentado ao desenho. Extremos coincidentes com nós existentes serão unidos.\nA geometria é aproximada por barras retas. Use malhas sucessivas para conferir a convergência. Apoios, seção, material e cargas são definidos após inserir.');info.setWordWrap(True);v.addWidget(info)
        self.previa=Previa(self);v.addWidget(self.previa)
        for w in self.campos.values():w.valueChanged.connect(lambda:self.previa.update())
        self.forma.currentTextChanged.connect(lambda:self.previa.update());self.segmentos.valueChanged.connect(lambda:self.previa.update())
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);buttons.button(QDialogButtonBox.Ok).setText('Inserir arco');buttons.button(QDialogButtonBox.Cancel).setText('Cancelar');buttons.accepted.connect(self.aplicar);buttons.rejected.connect(self.reject);v.addWidget(buttons)
    def modelo(self):
        c={k:w.value() for k,w in self.campos.items()}
        if c['flecha']<=0:raise ValueError('A flecha deve ser positiva.')
        return gerar_arco((c['xi'],c['yi']),(c['xf'],c['yf']),c['flecha'],self.segmentos.value(),self.forma.currentText())
    def aplicar(self):
        try:self.resultado=self.modelo();self.accept()
        except ValueError as e:QMessageBox.warning(self,'Verifique o arco',str(e))
