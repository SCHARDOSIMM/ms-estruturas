"""Seleção e inspeção de seção; dimensões na UI, armazenamento sempre SI."""
import math
from PyQt5.QtCore import Qt,QRectF,QPointF
from PyQt5.QtGui import QPainter,QColor,QPen,QPainterPath,QPolygonF,QFont,QFontMetricsF
from PyQt5.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QComboBox,
    QLabel,QLineEdit,QCheckBox,QPushButton,QDialogButtonBox,QWidget,QScrollArea)
from estrutural.ui.formularios import numero
from estrutural.ui import tema
from estrutural.core.secoes import FAMILIAS,calcular_secao,retangulos
from estrutural.ui.idioma import QComboBox, QDialogButtonBox, QLabel, QPushButton, QCheckBox, tr

CATALOGO={
    'Genérico — personalizar':None,
    'IPE 80 — dimensões nominais':('I/H',{'h':.080,'b':.046,'tw':.0038,'tf':.0052}),
    'IPE 100 — dimensões nominais':('I/H',{'h':.100,'b':.055,'tw':.0041,'tf':.0057}),
    'UPE 80 — dimensões nominais':('U',{'h':.080,'b':.050,'tw':.004,'tf':.007}),
    'UPE 100 — dimensões nominais':('U',{'h':.100,'b':.055,'tw':.0045,'tf':.0075}),
    'Madeira serrada — 6 × 12 cm':('Retangular',{'b':.06,'h':.12}),
    'Concreto — 20 × 40 cm':('Retangular',{'b':.20,'h':.40}),
}


class Esquema(QWidget):
    """Section and dimension lines share a centered, scalable drawing sheet."""
    def __init__(self,dialog):
        super().__init__(); self.dialog=dialog; self.setMinimumSize(300,300)

    def texto(self,p,centro,texto):
        metrics=QFontMetricsF(p.font())
        rect=QRectF(0,0,metrics.horizontalAdvance(texto)+8,metrics.height()+4)
        rect.moveCenter(centro)
        p.save();p.setPen(Qt.NoPen);p.setBrush(self.palette().window());p.drawRect(rect)
        p.setPen(self.palette().windowText().color());p.drawText(rect,Qt.AlignCenter,texto);p.restore()

    def cota(self,p,a,b,rotulo,centro=None):
        """True endpoints; external arrows keep thin walls legible without exaggerating them."""
        delta=b-a;length=math.hypot(delta.x(),delta.y())
        if length<=0:return
        u=delta/length;normal=QPointF(-u.y(),u.x());externa=length<24
        p.save();p.setPen(QPen(self.palette().windowText().color(),.9))
        p.drawLine(a-u*13 if externa else a,b+u*13 if externa else b)
        p.setBrush(self.palette().windowText());p.setPen(Qt.NoPen)
        for tip,direction in ((a,-1 if externa else 1),(b,1 if externa else -1)):
            base=tip+u*(5.5*direction)
            p.drawPolygon(QPolygonF([tip,base+normal*2.2,base-normal*2.2]))
        p.restore()
        if centro is None:centro=(a+b)/2-normal*14 if externa else (a+b)/2
        self.texto(p,centro,rotulo)

    def extensao(self,p,a,b):
        p.save();color=self.palette().windowText().color();color.setAlpha(125)
        p.setPen(QPen(color,.7));p.drawLine(a,b);p.restore()

    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        try:
            # A common sheet keeps the geometry, labels and legend aligned on resize/DPI changes.
            sheet=min(self.width()/300,self.height()/300)
            p.translate((self.width()-300*sheet)/2,(self.height()-300*sheet)/2);p.scale(sheet,sheet)
            font=QFont(self.font());font.setPixelSize(12);p.setFont(font)
            f=self.dialog.familia.currentText();dims=self.dialog.dimensoes()
            calcular_secao(f,dims)
            if f=='Arbitrário':
                p.drawText(QRectF(20,90,260,90),Qt.AlignCenter,tr('A, Ix, Iy e J\ninformados diretamente'));return
            path=QPainterPath()
            if f in ('Circular maciço','Tubo circular'):
                width=height=dims['d'];scale=170/width
                left,top=65.,50.;right,bottom=235.,220.
                path.addEllipse(QRectF(left,top,170,170))
                if f=='Tubo circular':
                    wall=dims['t']*scale
                    path.addEllipse(QRectF(left+wall,top+wall,170-2*wall,170-2*wall))
                # Odd-even fill leaves the bore empty in either theme.
                path.setFillRule(Qt.OddEvenFill)
            else:
                parts=retangulos(f,dims);width=max(x+b for x,y,b,h in parts);height=max(y+h for x,y,b,h in parts)
                scale=min(160/width,170/height);left=150-width*scale/2;top=135-height*scale/2
                right=300-left;bottom=270-top
                # Explicit contours avoid boolean-union gaps at floating-point shared edges.
                if f in ('Retangular','Quadrado','Caixão'):
                    path.addRect(QRectF(left,top,right-left,bottom-top))
                    if f=='Caixão':
                        wall=dims['t']*scale
                        path.addRect(QRectF(left+wall,top+wall,right-left-2*wall,bottom-top-2*wall))
                        path.setFillRule(Qt.OddEvenFill)
                else:
                    b,h=width,height;tw,tf=dims['tw'],dims['tf'];wl,wr=(b-tw)/2,(b+tw)/2
                    contours={
                        'I/H':[(0,0),(b,0),(b,tf),(wr,tf),(wr,h-tf),(b,h-tf),(b,h),(0,h),(0,h-tf),(wl,h-tf),(wl,tf),(0,tf)],
                        'U':[(0,0),(b,0),(b,tf),(tw,tf),(tw,h-tf),(b,h-tf),(b,h),(0,h)],
                        'T':[(wl,0),(wr,0),(wr,h-tf),(b,h-tf),(b,h),(0,h),(0,h-tf),(wl,h-tf)],
                        'L':[(0,0),(b,0),(b,tf),(tw,tf),(tw,h),(0,h)],
                    }
                    for i,(x,y) in enumerate(contours[f]):
                        point=QPointF(left+x*scale,bottom-y*scale)
                        if i==0:path.moveTo(point)
                        else:path.lineTo(point)
                    path.closeSubpath()
            dark=self.palette().window().color().lightness()<128
            fill=QColor(tema.DESTAQUE if dark else '#0078d7');fill.setAlpha(65 if dark else 45)
            p.setBrush(fill);p.setPen(QPen(self.palette().windowText().color(),1.3));p.drawPath(path)
            p.setBrush(Qt.NoBrush)
            # Overall dimensions: centered labels and projection lines from the exact boundaries.
            baseline=bottom+26
            for x in (left,right):self.extensao(p,QPointF(x,bottom+3),QPointF(x,baseline+5))
            self.cota(p,QPointF(left,baseline),QPointF(right,baseline),'d' if f in ('Circular maciço','Tubo circular') else 'b')
            if f not in ('Circular maciço','Tubo circular'):
                x=left-26
                for y in (top,bottom):self.extensao(p,QPointF(left-3,y),QPointF(x-5,y))
                self.cota(p,QPointF(x,top),QPointF(x,bottom),'b' if f=='Quadrado' else 'h',QPointF(x-12,135))
            if f in ('I/H','U','T','L'):
                web_left=150-dims['tw']*scale/2 if f in ('I/H','T') else left
                web_right=web_left+dims['tw']*scale
                self.cota(p,QPointF(web_left,135),QPointF(web_right,135),'tw',QPointF(web_right+28,135))
                # L's flange is at the bottom, unlike I/H, U and T.
                y1=bottom-dims['tf']*scale if f=='L' else top
                y2=bottom if f=='L' else top+dims['tf']*scale
                x=right+22
                for y in (y1,y2):self.extensao(p,QPointF(right+3,y),QPointF(x+5,y))
                self.cota(p,QPointF(x,y1),QPointF(x,y2),'tf',QPointF(x+17,(y1+y2)/2))
            elif f in ('Caixão','Tubo circular'):
                self.cota(p,QPointF(right-dims['t']*scale,135),QPointF(right,135),'t',QPointF(right+27,135))
            legendas={
                'Retangular':['b · largura    h · altura'], 'Quadrado':['b · lado'],
                'Circular maciço':['d · diâmetro'], 'Tubo circular':['d · diâmetro externo','t · espessura da parede'],
                'Caixão':['b · largura    h · altura','t · espessura da parede'],
            }.get(f,['b · largura    h · altura','tw · alma    tf · mesa'])
            font.setPixelSize(11);p.setFont(font)
            for i,line in enumerate(legendas):p.drawText(QRectF(8,270+i*15,284,16),Qt.AlignCenter,tr(line))
        except (ValueError,KeyError):p.drawText(QRectF(15,90,270,90),Qt.AlignCenter,tr('Verifique as dimensões'))
        finally: p.end()


class SeletorPerfil(QDialog):
    def __init__(self,parent,barra=None):
        super().__init__(parent); self.setWindowTitle('Perfil e propriedades geométricas'); self.resize(850,680)
        self.resultado=None; self.busy=False; self.factor=.001
        outer=QVBoxLayout(self); scroll=QScrollArea(); scroll.setWidgetResizable(True); outer.addWidget(scroll)
        root=QWidget(); scroll.setWidget(root); v=QVBoxLayout(root)
        self.catalogo=QComboBox(); self.catalogo.addItems(CATALOGO); v.addWidget(self.catalogo)
        nota=QLabel('Perfis nominais IPE/UPE: dimensões ArcelorMittal; cálculo com cantos vivos, sem raios.\nPropriedades geométricas aproximadas, diferentes das tabelas de laminação. E e G são dados do material.'); nota.setWordWrap(True); v.addWidget(nota)
        body=QHBoxLayout(); v.addLayout(body); form=QFormLayout(); body.addLayout(form)
        self.familia=QComboBox(); self.familia.addItems(FAMILIAS); form.addRow('Família',self.familia)
        self.unidade=QComboBox(); self.unidade.addItems(['mm','cm','m']); form.addRow('Unidade das dimensões',self.unidade)
        self.campos={}
        for key,val in [('b',200),('h',300),('d',200),('t',10),('tw',10),('tf',15)]:
            w=numero(val,.00000001,1e9); w.setDecimals(10); self.campos[key]=w; form.addRow(key,w); w.valueChanged.connect(self.atualizar)
        self.E=numero(210000,.001,1e9); self.G=numero(80769.23077,.001,1e9)
        form.addRow('E (MPa)',self.E); form.addRow('G (MPa)',self.G)
        self.eixo=QComboBox(); self.eixo.addItems(['Ix','Iy']); form.addRow('Inércia de flexão usada',self.eixo)
        self.esquema=Esquema(self); body.addWidget(self.esquema,1)
        self.valores=QLabel(); self.valores.setWordWrap(True); v.addWidget(self.valores)
        self.overrides={}; self.checks={}; override_form=QFormLayout(); v.addLayout(override_form)
        for key in ('A','Ix','Iy','J'):
            line=QLineEdit(); check=QCheckBox('Sobrescrever '+key); self.overrides[key]=line; self.checks[key]=check
            override_form.addRow(check,line); line.setEnabled(False)
            check.toggled.connect(line.setEnabled); check.toggled.connect(self.atualizar); line.textChanged.connect(self.atualizar)
        restore=QPushButton('Restaurar valores calculados'); v.addWidget(restore); restore.clicked.connect(self.restaurar)
        self.como=QPushButton('Como foi calculado'); self.como.setCheckable(True); v.addWidget(self.como)
        self.formulas=QLabel(); self.formulas.setWordWrap(True); self.formulas.hide(); v.addWidget(self.formulas); self.como.toggled.connect(self.formulas.setVisible)
        self.catalogo.currentTextChanged.connect(self.preset); self.familia.currentTextChanged.connect(self.atualizar); self.unidade.currentTextChanged.connect(self.converter)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); buttons.button(QDialogButtonBox.Ok).setText('Aplicar perfil');buttons.button(QDialogButtonBox.Cancel).setText('Cancelar');outer.addWidget(buttons); buttons.accepted.connect(self.aplicar); buttons.rejected.connect(self.reject)
        conf=(barra or {}).get('secao')
        if conf:
            self.busy=True; self.familia.setCurrentText(conf['familia'])
            for k,val in conf['dimensoes'].items():
                if k in self.campos: self.campos[k].setValue(val/self.factor)
            self.E.setValue(conf['E_MPa']); self.G.setValue(conf['G_MPa']); self.eixo.setCurrentText(conf.get('eixo','Ix'))
            for k,val in conf.get('sobrescritos',{}).items(): self.overrides[k].setText(f'{val/self.factor**(2 if k=="A" else 4):.12g}'); self.checks[k].setChecked(True)
            if conf['familia']=='Arbitrário':
                for k in self.overrides: self.overrides[k].setText(f'{conf["dimensoes"][k]/self.factor**(2 if k=="A" else 4):.12g}')
            self.busy=False
        self.atualizar()
        if (barra or {}).get('material'):
            mat=barra['material'];self.E.setValue(mat['E_MPa']);self.G.setValue(mat['G_MPa']);self.E.setEnabled(False);self.G.setEnabled(False)
            self.E.setToolTip('Valor definido pelo material da barra. Use o botão Material para alterar.');self.G.setToolTip(self.E.toolTip())

    def dimensoes(self):
        if self.familia.currentText()=='Arbitrário': return {k:float(w.text())*self.factor**(2 if k=='A' else 4) for k,w in self.overrides.items()}
        return {k:w.value()*self.factor for k,w in self.campos.items()}
    def config(self):
        return {'familia':self.familia.currentText(),'dimensoes':self.dimensoes(),'E_MPa':self.E.value(),'G_MPa':self.G.value(),'eixo':self.eixo.currentText(),
                'sobrescritos':{k:float(w.text())*self.factor**(2 if k=='A' else 4) for k,w in self.overrides.items() if self.checks[k].isChecked() and self.familia.currentText()!='Arbitrário'},'nome':self.catalogo.currentText()}
    def preset(self,nome):
        preset=CATALOGO[nome]
        if preset:
            self.busy=True; self.familia.setCurrentText(preset[0])
            for k,v in preset[1].items(): self.campos[k].setValue(v/self.factor)
            for check in self.checks.values(): check.setChecked(False)
            self.busy=False; self.atualizar()
    def converter(self):
        new={'mm':.001,'cm':.01,'m':1}[self.unidade.currentText()]; old=self.factor
        self.busy=True
        for w in self.campos.values(): w.setValue(w.value()*old/new)
        for k,w in self.overrides.items():
            try: w.setText(f'{float(w.text())*(old/new)**(2 if k=="A" else 4):.12g}')
            except ValueError: pass
        self.factor=new; self.busy=False; self.atualizar()
    def restaurar(self):
        for check in self.checks.values(): check.setChecked(False)
        self.atualizar()
    def atualizar(self):
        if self.busy:return
        self.busy=True
        try:
            f=self.familia.currentText(); allowed={'Retangular':['b','h'],'Quadrado':['b'],'Circular maciço':['d'],'Tubo circular':['d','t'],'Caixão':['b','h','t'],'Arbitrário':[]}.get(f,['b','h','tw','tf'])
            for k,w in self.campos.items(): w.setEnabled(k in allowed)
            for k,w in self.overrides.items():
                self.checks[k].setText('Sobrescrever '+k+' ('+self.unidade.currentText()+('²' if k=='A' else '⁴')+')')
                w.setEnabled(f=='Arbitrário' or self.checks[k].isChecked()); self.checks[k].setEnabled(f!='Arbitrário')
                if f=='Arbitrário' and not w.text(): w.setText('1000' if k=='A' else '1000000')
            c=self.config(); p=calcular_secao(f,c['dimensoes'],c['sobrescritos'])
            if f!='Arbitrário':
                for k,w in self.overrides.items():
                    if not self.checks[k].isChecked(): w.setText(f'{p[k]/self.factor**(2 if k=="A" else 4):.12g}')
            powers={'A':2,'cx':1,'cy':1,'Ix':4,'Iy':4,'Wx':3,'Wy':3,'J':4,'rx':1,'ry':1}
            suffix={1:'',2:'²',3:'³',4:'⁴'}
            self.valores.setText(' | '.join(f'{k} = {v/self.factor**powers[k]:.6g} {self.unidade.currentText()}{suffix[powers[k]]}' for k,v in p.items() if k in powers and v is not None)+'\n'+p['aviso']+ ('\nVALORES SOBRESCRITOS: '+', '.join(c['sobrescritos']) if c['sobrescritos'] else ''))
            self.formulas.setText(p['formulas'])
        except (ValueError,KeyError) as e: self.valores.setText('Verifique: '+str(e))
        finally:self.busy=False; self.esquema.update()
    def aplicar(self):
        from PyQt5.QtWidgets import QMessageBox
        try:
            c=self.config(); calcular_secao(c['familia'],c['dimensoes'],c['sobrescritos']); self.resultado=c; self.accept()
        except ValueError as e: QMessageBox.warning(self,'Verifique o perfil',str(e))
