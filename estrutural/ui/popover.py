"""Biblioteca de exemplos ancorada ao botão, contida na janela e na tela."""
from PyQt5.QtCore import Qt,QPoint,QRect,QEvent
from PyQt5.QtGui import QPainter,QPen,QPolygon,QGuiApplication
from PyQt5.QtWidgets import QFrame,QVBoxLayout,QLabel,QTreeWidget,QTreeWidgetItem,QApplication
from estrutural.core.exemplos import biblioteca
from estrutural.ui.idioma import QLabel


class ExemplosPopover(QFrame):
    def __init__(self,parent,botao,abrir):
        super().__init__(parent,Qt.Popup|Qt.FramelessWindowHint);self.botao=botao;self.abrir=abrir;self.abaixo=True;self.arrow_x=30
        self.setObjectName('exemplosPopover');self.setAttribute(Qt.WA_TranslucentBackground);self.setStyleSheet('QFrame#exemplosPopover { background: transparent; border: none; }')
        v=QVBoxLayout(self);v.setContentsMargins(12,20,12,18);v.setSpacing(10)
        titulo=QLabel('EXEMPLOS POR TIPOLOGIA');titulo.setObjectName('grupo');v.addWidget(titulo)
        self.tree=QTreeWidget();self.tree.setHeaderHidden(True);self.tree.setMouseTracking(True);v.addWidget(self.tree,1)
        for tipo in ('Viga','Pórtico plano','Treliça','Arco','Grelha'):
            grupo=QTreeWidgetItem([tipo]);self.tree.addTopLevelItem(grupo)
            for item in biblioteca():
                if item['modelo']['tipo']==tipo:
                    child=QTreeWidgetItem([item['nome']]);child.setData(0,Qt.UserRole,item);child.setToolTip(0,item['descricao']+'\n'+item['referencia']);grupo.addChild(child)
            grupo.setExpanded(True)
        self.info=QLabel('Escolha um exemplo para carregar e calcular. Esc fecha esta janela.');self.info.setWordWrap(True);self.info.setMinimumHeight(55);v.addWidget(self.info)
        self.tree.itemEntered.connect(self.descrever);self.tree.currentItemChanged.connect(lambda item,old:self.descrever(item));self.tree.itemClicked.connect(self.escolher);self.tree.itemActivated.connect(self.escolher)
        QApplication.instance().installEventFilter(self)
    def eventFilter(self,obj,event):
        if self.isVisible():
            if event.type()==QEvent.KeyPress and event.key()==Qt.Key_Escape:self.close();return True
            if event.type()==QEvent.MouseButtonPress and not self.geometry().contains(event.globalPos()):self.close();return True
        return super().eventFilter(obj,event)
    def closeEvent(self,e):
        QApplication.instance().removeEventFilter(self);super().closeEvent(e)
    def descrever(self,item,*args):
        if item and item.data(0,Qt.UserRole):
            e=item.data(0,Qt.UserRole);self.info.setText(e['descricao']+'\n'+e['referencia'])
    def escolher(self,item,*args):
        e=item.data(0,Qt.UserRole)
        if e:self.close();self.abrir(e)
    def ancorar(self):
        janela=self.parentWidget();bounds=QRect(janela.mapToGlobal(QPoint(0,0)),janela.size());anchor=QRect(self.botao.mapToGlobal(QPoint(0,0)),self.botao.size())
        screen=QGuiApplication.screenAt(anchor.center())
        if screen:bounds=bounds.intersected(screen.availableGeometry())
        abaixo=bounds.bottom()-anchor.bottom()-8;acima=anchor.top()-bounds.top()-8
        w=min(520,bounds.width()-16);h=min(540,bounds.height()-16,max(abaixo,acima))
        self.abaixo=bounds.bottom()-anchor.bottom()>=h
        if self.abaixo:y=anchor.bottom()+1
        elif anchor.top()-bounds.top()>=h:y=anchor.top()-h
        else:y=max(bounds.top()+8,min(anchor.bottom()+1,bounds.bottom()-h-8))
        x=max(bounds.left()+8,min(anchor.left(),bounds.right()-w-8));y=max(bounds.top()+8,min(y,bounds.bottom()-h-8))
        self.resize(w,h);self.move(x,y);self.arrow_x=max(18,min(w-18,anchor.center().x()-x));self.show();self.tree.setFocus()
    def keyPressEvent(self,e):
        if e.key()==Qt.Key_Escape:self.close()
        else:super().keyPressEvent(e)
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.setPen(QPen(self.palette().mid().color(),1));p.setBrush(self.palette().window())
        p.drawRect(0,8,self.width()-1,self.height()-17)
        x=self.arrow_x
        pts=[QPoint(x-8,8),QPoint(x,0),QPoint(x+8,8)] if self.abaixo else [QPoint(x-8,self.height()-9),QPoint(x,self.height()-1),QPoint(x+8,self.height()-9)]
        p.drawPolygon(QPolygon(pts));p.end()
