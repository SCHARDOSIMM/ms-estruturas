"""Editor de cargas distribuídas com prévia, resultante e interpolação por pontos."""
from PyQt5.QtCore import Qt,QPointF
from PyQt5.QtGui import QPainter,QPen,QColor,QPolygonF,QPixmap,QIcon
from PyQt5.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QComboBox,QLabel,
    QWidget,QPushButton,QLineEdit,QTableWidget,QTableWidgetItem,QDialogButtonBox,QMessageBox)
from estrutural.ui.formularios import numero
from estrutural.core.cargas import intensidade,integrar
from estrutural.ui.idioma import QComboBox, QDialogButtonBox, QLabel, QPushButton, QCheckBox, tr

TIPOS=['Uniforme','Triangular crescente','Triangular decrescente','Trapezoidal','Parabólica','Senoidal','Por pontos']


def miniatura(name,color):
    import math
    pix=QPixmap(40,26);pix.fill(Qt.transparent);p=QPainter(pix);p.setRenderHint(QPainter.Antialiasing);p.setPen(QPen(color,1.5))
    vals=[]
    for i in range(21):
        t=i/20
        value={'Uniforme':.8,'Triangular crescente':t,'Triangular decrescente':1-t,'Trapezoidal':.4+.6*t,'Parabólica':4*t*(1-t),'Senoidal':math.sin(math.pi*t),'Por pontos':.5+.3*math.sin(3*math.pi*t)}[name]
        vals.append(QPointF(3+34*t,22-17*value))
    p.drawLine(QPointF(3,22),QPointF(37,22));p.drawPolyline(QPolygonF(vals));p.drawLine(vals[0],QPointF(3,22));p.drawLine(vals[-1],QPointF(37,22));p.end();return QIcon(pix)


class Grafico(QWidget):
    def __init__(self,d):super().__init__();self.d=d;self.setMinimumSize(300,220)
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        try:
            ch=self.d.montar();a,b=ch['a'],ch['b'];vals=[intensidade(ch,a+(b-a)*i/80,self.d.L) for i in range(81)];scale=max(map(abs,vals)) or 1
            pts=[QPointF(30+(self.width()-60)*i/80,self.height()/2-vals[i]/scale*(self.height()/2-40)) for i in range(81)]
            p.setPen(QPen(self.palette().mid().color(),1));p.drawLine(QPointF(30,self.height()/2),QPointF(self.width()-30,self.height()/2))
            color=self.palette().highlight().color();fill=QColor(color);fill.setAlpha(45);p.setBrush(fill);p.setPen(QPen(color,2));p.drawPolygon(QPolygonF([QPointF(30,self.height()/2)]+pts+[QPointF(self.width()-30,self.height()/2)]))
            p.setPen(self.palette().windowText().color());p.drawText(30,self.height()-10,tr(f'x = {a:g} a {b:g} m'));p.drawText(30,20,tr('q(x) [kN/m]'))
        except (ValueError,KeyError):p.drawText(self.rect(),Qt.AlignCenter,tr('Preencha os campos para visualizar a carga.'))
        finally:p.end()


class EditorCarga(QDialog):
    def __init__(self,parent,L,tipo):
        super().__init__(parent);self.L=L;self.resultado=None;self.busy=False;self.percent=False;self.setWindowTitle('Carga distribuída');self.resize(830,650)
        v=QVBoxLayout(self);row=QHBoxLayout();v.addLayout(row);f=QFormLayout();row.addLayout(f)
        self.tipo=QComboBox();self.tipo.addItems(TIPOS);f.addRow('Formato',self.tipo)
        for i,name in enumerate(TIPOS):self.tipo.setItemIcon(i,miniatura(name,self.palette().highlight().color()))
        self.unidade=QComboBox();self.unidade.addItems(['Metros','% do comprimento']);f.addRow('Posições em',self.unidade)
        self.a=numero(0,0,L);self.b=numero(L,0,L);self.qa=numero(-10);self.qb=numero(-20);self.amp=numero(-10)
        for label,w in [('Início do trecho',self.a),('Fim do trecho',self.b),('q inicial (kN/m)',self.qa),('q final (kN/m)',self.qb),('Acréscimo no centro (kN/m)',self.amp)]:f.addRow(label,w)
        self.eixo=QComboBox();self.eixo.addItems(['Vertical global Y','Transversal local y']);f.addRow('Direção',self.eixo)
        self.grafico=Grafico(self);row.addWidget(self.grafico,1)
        self.resumo=QLabel();self.resumo.setObjectName('status');self.resumo.setWordWrap(True);v.addWidget(self.resumo)
        self.painel_pontos=QWidget();pv=QVBoxLayout(self.painel_pontos);self.tabela=QTableWidget(2,2);self.tabela.setHorizontalHeaderLabels(['x na barra (m)','q (kN/m)'])
        for i,(x,q) in enumerate([(0,0),(L,-10)]):
            self.tabela.setItem(i,0,QTableWidgetItem(str(x)));self.tabela.setItem(i,1,QTableWidgetItem(str(q)))
        pv.addWidget(self.tabela);actions=QHBoxLayout();pv.addLayout(actions)
        add=QPushButton('Adicionar ponto');remove=QPushButton('Remover ponto');actions.addWidget(add);actions.addWidget(remove);add.clicked.connect(self.add_ponto);remove.clicked.connect(self.remover_ponto);v.addWidget(self.painel_pontos)
        self.avancado=QPushButton('Fórmula (avançado)');self.avancado.setCheckable(True);v.addWidget(self.avancado)
        self.painel_formula=QWidget();fv=QVBoxLayout(self.painel_formula);fv.addWidget(QLabel('x em metros desde o nó inicial; L = comprimento total. Use x^2, sin(pi*x/L), etc.'))
        self.formula=QLineEdit('-10*sin(pi*x/L)');fv.addWidget(self.formula);example=QPushButton('Exemplo: parábola −10·(x/L)²');example.clicked.connect(lambda:self.formula.setText('-10*(x/L)^2'));fv.addWidget(example);self.painel_formula.hide();v.addWidget(self.painel_formula)
        self.avancado.toggled.connect(self.painel_formula.setVisible);self.avancado.toggled.connect(self.atualizar)
        help=QLabel('Valores negativos atuam em −Y ou −y, por metro real de barra (não por projeção). Na parábola/senoide, o acréscimo é somado à reta entre q inicial e final. Pontos são unidos por segmentos lineares.');help.setWordWrap(True);v.addWidget(help)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);buttons.button(QDialogButtonBox.Ok).setText('Aplicar carga');buttons.button(QDialogButtonBox.Cancel).setText('Cancelar');v.addWidget(buttons);buttons.accepted.connect(self.aplicar);buttons.rejected.connect(self.reject)
        self.tipo.currentTextChanged.connect(self.mudar_tipo);self.unidade.currentIndexChanged.connect(self.converter)
        for w in (self.a,self.b,self.qa,self.qb,self.amp):w.valueChanged.connect(self.atualizar)
        self.tabela.cellChanged.connect(self.atualizar);self.formula.textChanged.connect(self.atualizar);self.eixo.currentIndexChanged.connect(self.atualizar)
        self.tipo.setCurrentText({'Retangular':'Uniforme','Triangular':'Triangular crescente','Trapezoidal':'Trapezoidal','Função':'Parabólica'}.get(tipo,'Uniforme'));self.mudar_tipo()
    def add_ponto(self):
        # Insere no maior intervalo para evitar um ponto duplicado no fim da barra.
        pts=None
        try:
            pts=sorted((float(self.tabela.item(i,0).text().replace(',','.')),float(self.tabela.item(i,1).text().replace(',','.'))) for i in range(self.tabela.rowCount()))
            if len(pts)>=2:
                a,b=max(zip(pts,pts[1:]),key=lambda par:par[1][0]-par[0][0]);x,q=(a[0]+b[0])/2,(a[1]+b[1])/2
            else:x,q=self.L/2,0
        except (ValueError,AttributeError):x,q=self.L/2,0
        self.tabela.blockSignals(True)
        if pts is not None:
            pts=sorted(pts+[(x,q)]);self.tabela.setRowCount(len(pts))
            for i,(xx,qq) in enumerate(pts):self.tabela.setItem(i,0,QTableWidgetItem(str(xx)));self.tabela.setItem(i,1,QTableWidgetItem(str(qq)))
            i=pts.index((x,q))
        else:
            i=self.tabela.rowCount();self.tabela.insertRow(i);self.tabela.setItem(i,0,QTableWidgetItem(str(x)));self.tabela.setItem(i,1,QTableWidgetItem(str(q)))
        self.tabela.blockSignals(False);self.tabela.selectRow(i);self.atualizar()
    def remover_ponto(self):
        i=self.tabela.currentRow()
        if i>=0:self.tabela.removeRow(i);self.atualizar()
    def converter(self):
        new=self.unidade.currentIndex()==1
        if new!=self.percent:
            self.busy=True;factor=100/self.L if new else self.L/100
            for w in (self.a,self.b):value=w.value()*factor;w.setMaximum(100 if new else self.L);w.setValue(value)
            self.percent=new;self.busy=False;self.atualizar()
    def mudar_tipo(self):
        self.busy=True;name=self.tipo.currentText();self.avancado.setChecked(False)
        if name.startswith('Triangular'):self.qa.setValue(0 if name.endswith('crescente') and not name.endswith('decrescente') else -10);self.qb.setValue(-10 if name=='Triangular crescente' else 0)
        if name in ('Parabólica','Senoidal'):self.qa.setValue(0);self.qb.setValue(0)
        self.busy=False;self.atualizar()
    def montar(self):
        factor=self.L/100 if self.percent else 1;a,b=self.a.value()*factor,self.b.value()*factor;name=self.tipo.currentText()
        ch={'a':a,'b':b,'eixo':['global_y','local_y'][self.eixo.currentIndex()],'descricao':name}
        if name=='Por pontos' and not self.avancado.isChecked():
            try:pontos=sorted([float(self.tabela.item(i,j).text().replace(',','.')) for j in range(2)] for i in range(self.tabela.rowCount()))
            except (AttributeError,ValueError):raise ValueError('Preencha x e q em todas as linhas.')
            if len(pontos)<2:raise ValueError('Informe pelo menos dois pontos.')
            ch.update(pontos=pontos,a=pontos[0][0],b=pontos[-1][0]);a,b=ch['a'],ch['b']
        elif self.avancado.isChecked():
            if not self.formula.text().strip():raise ValueError('Informe uma expressão matemática.')
            ch.update(funcao=self.formula.text().strip(),descricao='Fórmula avançada')
        elif name in ('Parabólica','Senoidal'):
            t=f'((x-({a}))/{b-a})' if b>a else '0';base=f'({self.qa.value()})+({self.qb.value()-self.qa.value()})*{t}'
            ch['funcao']=base+f'+({self.amp.value()})*'+(f'4*{t}*(1-{t})' if name=='Parabólica' else f'sin(pi*{t})')
        else:ch.update(qa=self.qa.value(),qb=self.qa.value() if name=='Uniforme' else self.qb.value())
        if not 0<=a<b<=self.L:raise ValueError('O trecho deve satisfazer 0 ≤ início < fim ≤ comprimento da barra.')
        return ch
    def atualizar(self):
        if self.busy:return
        name=self.tipo.currentText();advanced=self.avancado.isChecked();points=name=='Por pontos' and not advanced;self.painel_pontos.setVisible(points)
        for w in (self.a,self.b):w.setEnabled(not points)
        self.qa.setEnabled(not advanced and not points and name!='Triangular crescente');self.qb.setEnabled(not advanced and not points and name not in ('Uniforme','Triangular decrescente'));self.amp.setEnabled(not advanced and name in ('Parabólica','Senoidal'))
        try:
            ch=self.montar();R=integrar(ch,self.L,lambda x:1);moment=integrar(ch,self.L,lambda x:x)
            from estrutural.core.exibicao import Formatador
            fmt=Formatador(opcoes=getattr(self.parentWidget(),'preferencias',None));self.resumo.setText(f'Resultante = {fmt.esforco(R)} {fmt.unidade("R")} | '+(f'Posição = {fmt.comprimento(moment/R)} m desde o início da barra.' if abs(R)>=max(1e-12,fmt.op['tolerancia_zero']) else 'Resultante nula: posição da resultante não definida.'))
        except (ValueError,KeyError) as e:self.resumo.setText('Verifique: '+str(e))
        self.grafico.update()
    def aplicar(self):
        try:
            ch=self.montar()
            for i in range(101):intensidade(ch,ch['a']+(ch['b']-ch['a'])*i/100,self.L)
            integrar(ch,self.L,lambda x:1);self.resultado=ch;self.accept()
        except ValueError as e:QMessageBox.warning(self,'Verifique a carga',str(e))
