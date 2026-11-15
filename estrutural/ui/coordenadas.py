"""Painel persistente para entrada exata e edição bidirecional de nós."""
import math
from PyQt5.QtCore import Qt,QEvent
from PyQt5.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QLabel,QPushButton,QComboBox,QTableWidget,QTableWidgetItem,QSpinBox
from estrutural.ui.formularios import numero
from estrutural.core.projetos import inserir_no,inserir_barra
from estrutural.ui.idioma import QComboBox, QLabel, QPushButton, QCheckBox, tr


class Coordenadas(QDialog):
    def __init__(self,editor):
        super().__init__(editor); self.ed=editor; self.setWindowTitle('Entrada de coordenadas — Ctrl+E'); self.resize(520,570)
        v=QVBoxLayout(self); self.modo=QComboBox(); self.modo.addItems(['Absolutas X, Y','Relativas Δx, Δy ao último nó','Polares: comprimento, ângulo (graus)']); v.addWidget(self.modo)
        f=QFormLayout(); v.addLayout(f); self.x=numero(); self.y=numero(); f.addRow('X / Δx / L (m)',self.x); f.addRow('Y / Δy (m) / ângulo (°)',self.y)
        self.x.setDecimals(10);self.y.setDecimals(10)
        for w in (self.x,self.y): w.installEventFilter(self)
        add=QPushButton('Inserir nó (Enter)'); add.setAutoDefault(False); add.clicked.connect(self.inserir); v.addWidget(add)
        v.addWidget(QLabel('Entrada exata, independente do snap. Edite X/Y na tabela abaixo.'))
        self.tabela=QTableWidget(0,3); self.tabela.setHorizontalHeaderLabels(['Nó','X (m)','Y (m)']); self.tabela.cellChanged.connect(self.editar); v.addWidget(self.tabela)
        row=QHBoxLayout(); self.i=QSpinBox(); self.j=QSpinBox(); self.i.setMinimum(1); self.j.setMinimum(1)
        row.addWidget(QLabel('Nó inicial')); row.addWidget(self.i); row.addWidget(QLabel('Nó final')); row.addWidget(self.j); v.addLayout(row)
        bar=QPushButton('Criar barra entre nós'); bar.setAutoDefault(False); bar.clicked.connect(self.barra); v.addWidget(bar)
        self.aviso=QLabel(); self.aviso.setWordWrap(True); self.aviso.setObjectName('status'); v.addWidget(self.aviso); self.atualizar()
    def eventFilter(self,obj,e):
        if obj in (self.x,self.y) and e.type()==QEvent.KeyPress and e.key() in (Qt.Key_Return,Qt.Key_Enter): self.inserir(); return True
        return super().eventFilter(obj,e)
    def atualizar(self):
        self.tabela.blockSignals(True); self.tabela.setRowCount(len(self.ed.modelo['nos']))
        for i,n in enumerate(self.ed.modelo['nos']):
            for j,value in enumerate([i+1,n['x'],n['y']]):
                item=QTableWidgetItem(f'{value:.12g}')
                if j==0:item.setFlags(item.flags()&~Qt.ItemIsEditable)
                self.tabela.setItem(i,j,item)
        self.tabela.blockSignals(False); count=max(1,len(self.ed.modelo['nos'])); self.i.setMaximum(count); self.j.setMaximum(count)
    def inserir(self):
        try:
            self.x.interpretText(); self.y.interpretText(); x,y=self.x.value(),self.y.value()
            if self.modo.currentIndex():
                if not self.ed.modelo['nos']:raise ValueError('Insira um nó absoluto antes de usar coordenadas relativas.')
                base=self.ed.modelo['nos'][-1]
                if self.modo.currentIndex()==2:
                    if x<=0:raise ValueError('Comprimento polar deve ser positivo.')
                    x,y=x*math.cos(math.radians(y)),x*math.sin(math.radians(y))
                x+=base['x']; y+=base['y']
            import copy
            m=copy.deepcopy(self.ed.modelo); idx=inserir_no(m,x,y)
            self.ed.registrar(); self.ed.carregar(m); self.aviso.setText(f'Nó {idx+1} inserido: ({x:g}, {y:g}) m.'); self.x.setFocus(); self.x.selectAll()
        except ValueError as e:self.aviso.setText(str(e))
    def editar(self,row,col):
        if col==0:return
        try:
            import copy
            m=copy.deepcopy(self.ed.modelo); x=float(self.tabela.item(row,1).text().replace(',','.')); y=float(self.tabela.item(row,2).text().replace(',','.'))
            if not math.isfinite(x) or not math.isfinite(y):raise ValueError('Coordenadas devem ser finitas.')
            if any(i!=row and math.hypot(n['x']-x,n['y']-y)<1e-8 for i,n in enumerate(m['nos'])):raise ValueError('Já existe nó nessa posição; edição cancelada.')
            m['nos'][row].update(x=x,y=y); self.ed.registrar(); self.ed.carregar(m); self.aviso.setText('Coordenadas atualizadas.')
        except ValueError as e:self.aviso.setText(str(e)); self.atualizar()
    def barra(self):
        try:
            import copy
            m=copy.deepcopy(self.ed.modelo); inserir_barra(m,self.i.value()-1,self.j.value()-1)
            self.ed.registrar(); self.ed.carregar(m); self.aviso.setText('Barra criada.')
        except ValueError as e:self.aviso.setText(str(e))
