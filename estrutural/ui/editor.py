"""Editor gráfico e persistência do modelo de análise."""
import copy
import csv
import json
import math
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, QSize, QEvent, QUrl
from PyQt5.QtGui import QColor, QPainter, QPen, QPolygonF, QFont,QDesktopServices
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QLabel, QFileDialog, QMessageBox, QInputDialog, QPlainTextEdit,
    QDialog, QDialogButtonBox, QTableWidget, QTableWidgetItem, QTabWidget,
    QCheckBox, QDoubleSpinBox, QButtonGroup, QFrame, QScrollArea, QHeaderView, QSizePolicy,QMenu)
from estrutural.core.analise import analisar, ErroModelo
from estrutural.ui.janela import JanelaPrincipal
from estrutural.ui import tema
from estrutural.ui.icones import icone
from estrutural.ui.formularios import carga_distribuida, editar_no, editar_barra
from estrutural.core.cargas import intensidade
from estrutural.core.projetos import migrar,inserir_barra,inserir_no
from estrutural.core.secoes import aplicar_secao,calcular_secao
from estrutural.core.exibicao import PADRAO,Formatador
from estrutural.core.idiomas import IDIOMAS
from estrutural.ui.projecao_grelha import projetar, inverter, momento_grelha, angulo_apoio
from estrutural.ui.simbolos import desenhar_apoio,desenhar_molas
from estrutural.ui.idioma import QComboBox, QFileDialog, QInputDialog, QDialogButtonBox, QLabel, QPushButton, QCheckBox, tr, definir, atualizar
from estrutural.ui.simbolos import desenhar_momento
from estrutural.ui.selecao import Selecao
from estrutural.ui.marca import Marca
from estrutural.ui.persistencia import gravar_preferencias

DESCRICOES={
    'Selecionar / editar':'Clique em um nó ou barra para editar propriedades. Na barra, também é possível remover cargas distribuídas.',
    'Nó':'Insere um ponto estrutural na posição clicada, respeitando o snap.',
    'Barra':'Liga dois pontos. Clique no início e no fim; Esc cancela o trecho.',
    'Apoio fixo':'Apoio articulado de 2º gênero: impede u e v e permite rotação. Clique em um nó.',
    'Apoio móvel':'Apoio de 1º gênero: impede v e permite u e rotação. Clique em um nó.',
    'Engaste':'Impede os deslocamentos e a rotação do nó.',
    'Rótula':'Libera ou restabelece o momento em uma extremidade de barra. Clique na barra e escolha o extremo.',
    'Carga pontual':'Define forças e momento no nó por formulário, com unidades.',
    'Retangular':'Carga distribuída constante (kN/m). Clique na barra e informe intensidade e trecho.',
    'Triangular':'Carga distribuída com uma extremidade nula. Clique na barra e escolha orientação e trecho.',
    'Trapezoidal':'Carga distribuída linear entre duas intensidades. Clique na barra e informe q inicial e final.',
    'Função':'Carga distribuída q(x) por expressão matemática. Clique na barra; x é a distância desde seu nó inicial.',
    'Apagar nó':'Remove o nó clicado e as barras conectadas. Desfazer recupera a operação.',
    'Estrutura':'Exibe a geometria e os carregamentos sem diagramas.',
    'N':'Exibe o diagrama de esforço normal, positivo em tração.',
    'V':'Exibe o diagrama de esforço cortante.', 'M':'Exibe o momento fletor, positivo sagente.',
    'T':'Exibe torção em grelhas.', 'Deformada':'Exibe deslocamentos ampliados pela escala indicada.',
    'Novo':'Inicia um modelo vazio. A operação pode ser desfeita.', 'Abrir':'Abre um projeto JSON salvo.',
    'Salvar':'Salva geometria, vínculos e cargas em JSON.', 'Exemplo':'Carrega uma viga biapoiada de 6 m com carga de 10 kN/m.',
    'Arco':'Cria um arco parabólico discretizado em barras.', 'Propriedades':'Editor avançado do modelo em JSON.',
    'Desfazer':'Reverte a última alteração do modelo.', 'Refazer':'Reaplica a alteração desfeita.',
    'Calcular':'Executa a análise linear e atualiza reações, deslocamentos e diagramas.',
    'Exportar':'Salva imagem PNG, esforços CSV ou relatório PDF.', 'Ajustar vista':'Enquadra todos os nós na área de desenho.'}
DESCRICOES.update({
    'Exemplos':'Biblioteca de modelos agrupados por tipologia, com descrição e resultados de referência.',
    'Perfil':'Escolhe uma seção e aplica suas propriedades a uma ou várias barras.',
    'Coordenadas':'Entrada exata de pontos e edição de nós em tabela (Ctrl+E).',
    'Reações':'Mostra reações proporcionais nos apoios, com valores e unidades.',
    'Esforços':'Mostra os esforços amostrados de todas as barras em tabela.',
    'Diagramas':'Mostra diagramas preenchidos. Escolha N, V, M ou T na paleta e passe o mouse para ler valores.'})
DESCRICOES.update({'Arco':'Desenha um arco circular ou parabólico por formulário, com prévia da geometria.',
    'Material':'Define E, G, Poisson, peso específico e dilatação térmica por barra ou conjunto de barras.',
    'Relatório PDF':'Salva um relatório paginado com modelo, reações, deslocamentos e diagramas.'})
DESCRICOES.update({'Configurações':'Preferências de unidades, precisão, tolerâncias, grade, snap, tema e deformada.',
    'Função':'Editor visual de carga personalizada: formatos, pontos, prévia e resultante. Fórmula opcional em Avançado.',
    'Apoio móvel':'Restringe uma direção física editável. Padrão vertical (90° de +X); selecione o nó para ajustar a rampa.',
    'Mola':'Define rigidezes elásticas globais X/Y e de rotação no nó selecionado.'})
DESCRICOES['Modo noturno']='Alternar entre os temas claro e escuro.'
DESCRICOES['Selecionar / editar']='Arraste para selecionar ou mover. Ctrl/Shift combina seleções; duplo clique edita. Esc cancela.'


def exemplo():
    return {'tipo':'Viga','nos':[
        {'x':0,'y':0,'apoio':[True,True,False]},
        {'x':6,'y':0,'apoio':[False,True,False]}],
        'barras':[{'i':0,'j':1,'EA':1000000,'EI':20000,'q':-10}]}


class Desenho(Selecao,QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.escuro = False
        self.grade = True
        self.zoom = 70.0
        self.origem = QPointF(90,300)
        self.inicio = None
        self.pan = None
        self.cursor_mundo = None
        self.iniciar_selecao()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.setMinimumHeight(200)

    def tela(self,x,y,z=0):
        if self.editor.modelo['tipo']=='Grelha':
            return self.origem+projetar(x,y,z)*self.zoom
        return self.origem + QPointF(x*self.zoom,-y*self.zoom)

    def delta_mundo(self,p):
        if self.editor.modelo['tipo']=='Grelha':return inverter(p/self.zoom)
        return p.x()/self.zoom,-p.y()/self.zoom

    def mundo(self,p):
        x,y = self.delta_mundo(p-self.origem)
        if self.editor.snap.isChecked():
            passo = self.editor.passo.value()
            x,y = round(x/passo)*passo,round(y/passo)*passo
        return x,y

    def wheelEvent(self,e):
        old = self.zoom
        self.zoom = min(1000,max(5,self.zoom*(1.15 if e.angleDelta().y()>0 else 1/1.15)))
        self.origem = e.pos()-(e.pos()-self.origem)*(self.zoom/old)
        self.update()

    def mouseMoveEvent(self,e):
        if self.mover_selecao(e.pos()):return
        if self.pan is not None:
            self.origem += e.pos()-self.pan
            self.pan = e.pos()
            self.update()
        x,y = self.mundo(e.pos())
        self.cursor_mundo = (x,y)
        self.editor.coord.setText(f'x = {x:.3f} m   y = {y:.3f} m')
        if self.inicio is not None: self.update()
        from PyQt5.QtWidgets import QToolTip
        found=False
        for A,B,idx,key,va,vb in getattr(self,'diagrama_hits',[]):
            delta=B-A; l2=delta.x()**2+delta.y()**2
            if not l2: continue
            t=max(0,min(1,((e.pos().x()-A.x())*delta.x()+(e.pos().y()-A.y())*delta.y())/l2))
            point=A+delta*t
            if math.hypot(e.pos().x()-point.x(),e.pos().y()-point.y())<10:
                x=va['x']+(vb['x']-va['x'])*t; val=va.get(key,0)+(vb.get(key,0)-va.get(key,0))*t
                f=self.editor.formatador()
                if key=='norma':
                    ux=va['ux']+(vb['ux']-va['ux'])*t;uy=va['uy']+(vb['uy']-va['uy'])*t;theta=va['rotacao']+(vb['rotacao']-va['rotacao'])*t
                    text=f'Barra {idx+1} | x={f.comprimento(x)} m | δx={f.desloc(ux)}; δy/w={f.desloc(uy)} {f.op["deslocamento"]}; θ={f.rotacao(theta)} rad'
                else:text=f'Barra {idx+1} | x={f.comprimento(x)} m | {key}={f.esforco(val)} {f.unidade(key)}'
                QToolTip.showText(e.globalPos(),tr(text),self)
                found=True; break
        if not found: QToolTip.hideText()

    def keyPressEvent(self,e):
        if e.key()==Qt.Key_R:self.editor.girar_apoio()
        elif e.key()==Qt.Key_Escape:
            self.cancelar_selecao();self.nos_selecionados.clear();self.barras_selecionadas.clear()
            self.inicio=None
            self.editor.ferramenta.setCurrentText('Selecionar / editar')
            self.update()
        else: super().keyPressEvent(e)

    def mouseReleaseEvent(self,e):
        if e.button()==Qt.LeftButton:self.finalizar_selecao(e.pos())
        self.pan = None

    def mouseDoubleClickEvent(self,e):
        if e.button()!=Qt.LeftButton or self.editor.ferramenta.currentText()!='Selecionar / editar':return
        self.cancelar_selecao();ed=self.editor
        near=next((i for i,n in enumerate(ed.modelo['nos']) if (self.tela(n['x'],n['y'])-e.pos()).manhattanLength()<16),None)
        if near is not None:ed.editar_no(near)
        else:
            hit=self.barra_proxima(e.pos())
            if hit is not None:
                result=editar_barra(ed,ed.modelo['barras'][hit])
                if result is not None:ed.registrar();ed.modelo['barras'][hit]=result;ed.invalidar()

    def mousePressEvent(self,e):
        self.setFocus()
        if e.button()==Qt.RightButton:
            self.cancelar_selecao()
            self.inicio=None; self.update(); return
        if e.button() == Qt.MiddleButton:
            self.pan = e.pos()
            return
        if e.button() != Qt.LeftButton: return
        ed = self.editor
        x,y = self.mundo(e.pos())
        near = next((i for i,n in enumerate(ed.modelo['nos']) if (self.tela(n['x'],n['y'])-e.pos()).manhattanLength()<16),None)
        ed.no_selecionado=near
        tool = ed.ferramenta.currentText()
        if tool in ('Retangular','Triangular','Trapezoidal','Função','Rótula'):
            hit=self.barra_proxima(e.pos())
            if hit is None: ed.ajuda.setText('Clique sobre uma barra para aplicar '+tool.lower()+'.'); return
            ed.aplicar_na_barra(hit,tool); return
        if tool == 'Selecionar / editar':
            self.pressionar_selecao(e,near)
            return
        ed.registrar()
        if tool in ['Nó','Barra']:
            if near is None:
                # O snap pode coincidir com um nó fora do limiar de seleção em pixels.
                near=next((i for i,n in enumerate(ed.modelo['nos']) if math.hypot(n['x']-x,n['y']-y)<1e-8),None)
                if near is None: near=inserir_no(ed.modelo,x,y)
            if tool == 'Barra':
                if self.inicio is None: self.inicio = near
                elif self.inicio != near:
                    try: inserir_barra(ed.modelo,self.inicio,near)
                    except ValueError as err: ed.erro(err)
                    self.inicio = None
        elif near is not None:
            no = ed.modelo['nos'][near]
            supports = {'Apoio fixo':[True,True,False],'Apoio móvel':[False,True,False],'Engaste':[True,True,True]}
            if tool in supports:
                no['apoio'] = supports[tool]
                if ed.modelo['tipo']=='Grelha' and tool in ('Apoio fixo','Apoio móvel'):no['apoio']=[True,False,False]
                no['apoio_visual_tipo']=tool
                if tool=='Apoio móvel' and ed.modelo['tipo']!='Grelha':no['apoio_angulo']=90.
                else:no.pop('apoio_angulo',None)
            if tool in ('Carga pontual','Mola'):
                ed.editar_no(near)
                return
            if tool == 'Apagar nó':
                self.iniciar_selecao()
                ed.no_selecionado=None
                ed.modelo['nos'].pop(near)
                ed.modelo['barras'] = [b for b in ed.modelo['barras'] if near not in (b['i'],b['j'])]
                for b in ed.modelo['barras']:
                    b['i'] -= b['i']>near
                    b['j'] -= b['j']>near
        ed.invalidar()

    def barra_proxima(self,pos):
        melhor=None; distancia=14
        for i,b in enumerate(self.editor.modelo['barras']):
            ni,nj=[self.editor.modelo['nos'][b[k]] for k in ('i','j')]
            a,z=self.tela(ni['x'],ni['y']),self.tela(nj['x'],nj['y'])
            dx,dy=z.x()-a.x(),z.y()-a.y(); l2=dx*dx+dy*dy
            if not l2: continue
            t=max(0,min(1,((pos.x()-a.x())*dx+(pos.y()-a.y())*dy)/l2))
            d=math.hypot(pos.x()-a.x()-t*dx,pos.y()-a.y()-t*dy)
            if d<distancia: melhor,distancia=i,d
        return melhor

    def paintEvent(self,e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        self.diagrama_hits=[]
        self.rotulos_nodais=set()
        p.fillRect(self.rect(),QColor(tema.CAMPO if self.escuro else '#ffffff'))
        color = tema.TEXTO if self.escuro else '#000000'
        if self.grade and self.editor.modelo['tipo']=='Grelha':
            self.grade_isometrica(p)
        if self.grade and self.editor.modelo['tipo']!='Grelha':
            step = self.zoom*self.editor.passo.value()
            # Reduz a densidade visual ao afastar, sem alterar o snap físico.
            factor=1
            while step<12: step*=5; factor*=5
            for vertical,extent in [(True,self.width()),(False,self.height())]:
                origin=self.origem.x() if vertical else self.origem.y()
                start=math.ceil(-origin/step); end=math.floor((extent-origin)/step)
                for k in range(start,end+1):
                    major=(k*factor)%5==0
                    pen=QPen(QColor(tema.BORDA_BOTAO if self.escuro else '#adadad') if major else QColor(tema.BORDA if self.escuro else '#dcdcdc'))
                    pen.setWidthF(1 if major else .5); p.setPen(pen)
                    pos=origin+k*step
                    if vertical: p.drawLine(QPointF(pos,0),QPointF(pos,self.height()))
                    else: p.drawLine(QPointF(0,pos),QPointF(self.width(),pos))
        ed = self.editor
        mostrar_cargas=not ed.resultado or ed.modo_resultado not in ('Diagramas','Deformada') or (ed.modo_resultado=='Diagramas' and ed.diagrama.currentText()=='Estrutura')
        projecao_arco=self.carga_projetada_arco() if mostrar_cargas else None
        self.rotulos_valores=[];self.chaves_valores=set()
        for idx,no in enumerate(ed.modelo['nos']):
            pos=self.tela(no['x'],no['y'])
            self.rotulos_valores.append(QRectF(pos.x()+5,pos.y()-20,65,18))
        if self.inicio is not None and self.cursor_mundo and self.inicio<len(ed.modelo['nos']):
            no=ed.modelo['nos'][self.inicio]
            p.setPen(QPen(QColor(tema.DESTAQUE_TEXTO),1.5,Qt.DashLine))
            p.drawLine(self.tela(no['x'],no['y']),self.tela(*self.cursor_mundo))
        for i,b in enumerate(ed.modelo['barras']):
            try: a,z = [ed.modelo['nos'][b[k]] for k in ('i','j')]
            except (IndexError,KeyError): continue
            A,B = self.tela(a['x'],a['y']),self.tela(z['x'],z['y'])
            p.setPen(QPen(QColor(color),2))
            p.drawLine(A,B)
            p.drawText((A+B)/2+QPointF(0,18),tr(f'B{i+1}'))
            comprimento=math.hypot(z['x']-a['x'],z['y']-a['y'])
            if comprimento:
                c,s=(z['x']-a['x'])/comprimento,(z['y']-a['y'])/comprimento
                cargas=list(b.get('distribuidas',[])) if mostrar_cargas else []
                if b.get('q') and mostrar_cargas: cargas.insert(0,{'qa':b['q'],'a':0,'b':comprimento,'eixo':'local_y'})
                for carga in cargas:
                    aa,bb=carga.get('a',0),carga.get('b',comprimento)
                    try:
                        vals=[intensidade(carga,aa+(bb-aa)*j/16,comprimento) for j in range(17)]
                    except (ValueError,KeyError,ZeroDivisionError): continue
                    maxi=max(map(abs,vals)) or 1
                    vx,vy=(s,c) if carga.get('eixo','local_y')=='local_y' else (0,1)
                    # Direção global Y é vertical; direção local y = (-s,c).
                    vx=-s if carga.get('eixo','local_y')=='local_y' else 0
                    if ed.modelo['tipo']=='Grelha':vx,vy=0,1
                    last=None; p.setPen(QPen(QColor(tema.DESTAQUE_TEXTO if self.escuro else '#0078d7'),1.3))
                    for j,val in enumerate(vals):
                        xx=aa+(bb-aa)*j/16; tip=self.tela(a['x']+c*xx,a['y']+s*xx)
                        tail=tip+QPointF(-vx,vy)*(val/maxi*42)
                        if last is not None: p.drawLine(last,tail)
                        last=tail
                        if abs(val)>1e-12:
                            p.drawLine(tail,tip)
                            direction=(tip-tail); length=math.hypot(direction.x(),direction.y()); u=direction/length
                            p.drawLine(tip,tip-u*6+QPointF(-u.y(),u.x())*3)
                            p.drawLine(tip,tip-u*6-QPointF(-u.y(),u.x())*3)
                    uniforme=max(vals)-min(vals)<1e-9
                    texto=carga.get('descricao','Função personalizada') if carga.get('funcao') or carga.get('pontos') else (f'{vals[0]:g} kN/m' if uniforme else f'{vals[0]:g} → {vals[-1]:g} kN/m')
                    if projecao_arco is None:self.rotular_valor(p,self.tela(a['x']+c*(aa+bb)/2,a['y']+s*(aa+bb)/2)+QPointF(0,-42),texto)
                p.setPen(QPen(QColor(color),1.5)); p.setBrush(QColor(tema.CAMPO if self.escuro else '#ffffff'))
                for key,P,Q in [('rotula_i',A,B),('rotula_j',B,A)]:
                    if b.get(key):
                        delta=Q-P; dist=math.hypot(delta.x(),delta.y())
                        if dist: p.drawEllipse(P+delta/dist*10,5,5)
            if ed.resultado and ed.modo_resultado=='Deformada':
                self.desenhar_deformada(p,i,b,a,z,color)
            if ed.resultado and ed.diagrama.currentText() in ('N','V','M','T') and ed.modo_resultado=='Diagramas':
                key = ed.diagrama.currentText()
                pts = ed.resultado['barras'][i]['pontos']
                L = ed.resultado['barras'][i]['L']
                c,s = (z['x']-a['x'])/L,(z['y']-a['y'])/L
                tol=ed.preferencias['tolerancia_zero'];maximum=max((abs(v.get(key,0)) for bar in ed.resultado['barras'] for v in bar['pontos'] if abs(v.get(key,0))>=tol),default=1) or 1
                colors={'N':('#0078d7','#4fa3ff'),'V':('#8040a0','#c79bff'),'M':('#00796b','#55d6b1'),'T':('#805000','#e5ba73')}
                diagram_color=QColor(colors[key][int(self.escuro)])
                outline=[]; bases=[]
                for v in pts:
                    off=(v.get(key,0) if abs(v.get(key,0))>=tol else 0)/maximum*ed.escala.value()/self.zoom*(-1 if key=='M' else 1)
                    if ed.modelo['tipo']=='Grelha':outline.append(self.tela(a['x']+c*v['x'],a['y']+s*v['x'],off))
                    else:outline.append(self.tela(a['x']+c*v['x']-s*off,a['y']+s*v['x']+c*off))
                    bases.append(self.tela(a['x']+c*v['x'],a['y']+s*v['x']))
                fill=QColor(diagram_color); fill.setAlpha(52); p.setBrush(fill); p.setPen(Qt.NoPen)
                p.drawPolygon(QPolygonF([bases[0]]+outline+[bases[-1]]))
                p.setBrush(Qt.NoBrush); p.setPen(QPen(diagram_color,1.8)); p.drawPolyline(QPolygonF(outline))
                for k in (0,len(pts)-1):
                    p.setPen(QPen(diagram_color,1,Qt.DashLine)); p.drawLine(bases[k],outline[k])
                for k in range(len(pts)-1): self.diagrama_hits.append((outline[k],outline[k+1],i,key,pts[k],pts[k+1]))
                notable={0,len(pts)-1,min(range(len(pts)),key=lambda k:pts[k].get(key,0)),max(range(len(pts)),key=lambda k:pts[k].get(key,0))}
                for ch in b.get('pontuais',[]): notable.add(min(range(len(pts)),key=lambda k:abs(pts[k]['x']-ch['x'])))
                p.setPen(diagram_color)
                f=ed.formatador();unit=f.unidade(key)
                if ed.preferencias['mostrar_valores']:
                    for k in sorted(notable):self.rotular_valor(p,outline[k],f'{f.esforco(pts[k].get(key,0))} {unit}')
                from estrutural.ui.anotacoes import centroide,sinal
                for sign in (-1,1):
                    groups=[];current=[]
                    for k,v in enumerate(pts):
                        if v.get(key,0)*sign>0:current.append(k)
                        elif current:groups.append(current);current=[]
                    if current:groups.append(current)
                    for group in groups:
                        if max(abs(pts[k].get(key,0)) for k in group)<maximum*.12:continue
                        mid=centroide([bases[group[0]]]+[outline[k] for k in group]+[bases[group[-1]]])
                        if mid is not None:p.setBrush(self.palette().base());sinal(p,mid,'+' if sign==1 else '−',diagram_color);p.setBrush(Qt.NoBrush)
        if projecao_arco is not None:
            q,x,y=projecao_arco;p.setPen(QColor(tema.DESTAQUE_TEXTO if self.escuro else '#0078d7'))
            self.rotular_valor(p,self.tela(x,y)+QPointF(0,-42),f'{q:g} kN/m (projeção X)')
        for i,n in enumerate(ed.modelo['nos']):
            P = self.tela(n['x'],n['y'])
            p.setPen(QPen(QColor(color),1))
            p.setBrush(QColor(tema.DESTAQUE))
            p.drawEllipse(P,4,4)
            labels=ed.modelo.get('exemplo',{}).get('rotulos_nos',[])
            label=f'{labels[i]} ({i+1})' if i<len(labels) else str(i+1)
            p.drawText(P+QPointF(7,-7),tr(label))
            from estrutural.core.apoios import direcao_barra
            desenhar_apoio(p,ed.modelo,i,P,color,angulo=angulo_apoio(ed.modelo,i) if ed.modelo['tipo']=='Grelha' else None);desenhar_molas(p,n,P,color,direcao_barra(ed.modelo,i),ed.modelo['tipo']=='Grelha')
            if ed.no_selecionado==i:p.setBrush(Qt.NoBrush);p.setPen(QPen(QColor(tema.DESTAQUE_TEXTO),1.5));p.drawEllipse(P,8,8)
            if mostrar_cargas and any(n.get('carga_pontual',[])):
                carga=(n['carga_pontual']+[0,0,0])[:3]
                p.setPen(QPen(QColor(tema.DESTAQUE_TEXTO if self.escuro else '#0078d7'),1.8))
                if ed.modelo['tipo']=='Grelha':
                    self.rotular_valor(p,P+QPointF(5,34),f'Fz={carga[0]:g} kN; Mx={carga[1]:g}; My={carga[2]:g} kN·m')
                    if carga[0]:
                        u=QPointF(0,-1 if carga[0]>0 else 1);tail=P-u*48
                        p.drawLine(tail,P);p.drawLine(P,P-u*8+QPointF(-u.y(),u.x())*4);p.drawLine(P,P-u*8-QPointF(-u.y(),u.x())*4)
                    for eixo in (1,2):
                        if carga[eixo]:momento_grelha(p,P,eixo,carga[eixo])
                for fx,fy in ([] if ed.modelo['tipo']=='Grelha' else [(carga[0],0),(0,carga[1])]):
                    mag=math.hypot(fx,fy)
                    if mag:
                        u=QPointF(fx/mag,-fy/mag); tail=P-u*48
                        p.drawLine(tail,P); p.drawLine(P,P-u*8+QPointF(-u.y(),u.x())*4); p.drawLine(P,P-u*8-QPointF(-u.y(),u.x())*4)
                        self.rotular_valor(p,tail,f'{fx or fy:g} kN')
                if carga[2] and ed.modelo['tipo']!='Grelha':
                    desenhar_momento(p,P,20,carga[2])
                    self.rotular_valor(p,P+QPointF(20,-14),f'{carga[2]:g} kN·m')
        if ed.resultado and ed.modo_resultado=='Reações':
            reaction_color=QColor('#b04e00' if not self.escuro else '#ffc078'); p.setPen(QPen(reaction_color,2)); p.setBrush(Qt.NoBrush)
            maxforce=max((abs(r[j]) for r in ed.resultado['reacoes'] for j in range(1 if ed.modelo['tipo']=='Grelha' else 2)),default=1) or 1
            f=ed.formatador()
            for no,r in zip(ed.modelo['nos'],ed.resultado['reacoes']):
                P=self.tela(no['x'],no['y'])
                from estrutural.core.apoios import movel_inclinado
                inclinado=movel_inclinado(no) and ed.modelo['tipo']!='Grelha'
                if inclinado:
                    beta=math.radians(no['apoio_angulo']);normal=r[0]*math.cos(beta)+r[1]*math.sin(beta)
                    if abs(normal)>=ed.preferencias['tolerancia_zero']:
                        u=QPointF(math.cos(beta),-math.sin(beta))*(1 if normal>=0 else -1);tip=P+u*(25+45*abs(normal)/(maxforce or 1));p.drawLine(P,tip);p.drawLine(tip,tip-u*8+QPointF(-u.y(),u.x())*4);p.drawLine(tip,tip-u*8-QPointF(-u.y(),u.x())*4)
                        text=f'{f.esforco(normal)} {f.unidade("R")}';tx=max(6,min(self.width()-p.fontMetrics().horizontalAdvance(text)-6,tip.x()+5));ty=max(p.fontMetrics().height(),min(self.height()-8,tip.y()-5));p.drawText(QPointF(tx,ty),tr(text))
                for j in ([] if inclinado else range(1 if ed.modelo['tipo']=='Grelha' else 2)):
                    val=r[j]
                    if abs(val)<ed.preferencias['tolerancia_zero']: continue
                    u=(QPointF(0,-1) if ed.modelo['tipo']=='Grelha' or j==1 else QPointF(1,0))*(1 if val>0 else -1)
                    tip=P+u*(25+45*abs(val)/maxforce); p.drawLine(P,tip); p.drawLine(tip,tip-u*8+QPointF(-u.y(),u.x())*4); p.drawLine(tip,tip-u*8-QPointF(-u.y(),u.x())*4)
                    p.drawText(tip+QPointF(5,-5),tr(f'{f.esforco(val)} {f.unidade("R")}'))
                for j in ([1,2] if ed.modelo['tipo']=='Grelha' else ([2] if len(r)==3 else [])):
                    if abs(r[j])>=ed.preferencias['tolerancia_zero']:
                        radius=20+10*abs(r[j])/(max(abs(v[j]) for v in ed.resultado['reacoes']) or 1)
                        if ed.modelo['tipo']=='Grelha':momento_grelha(p,P,j,r[j],radius)
                        else:desenhar_momento(p,P,radius,r[j])
                        prefix=('Mx=' if j==1 else 'My=') if ed.modelo['tipo']=='Grelha' else ''
                        p.drawText(P+QPointF(25,30+16*(j-1)),tr(f'{prefix}{f.esforco(r[j])} {f.unidade("M")}'))
        self.desenhar_selecao(p)
        if ed.modelo['tipo']=='Grelha':self.eixos_grelha(p)
        p.end()

    def grade_isometrica(self,p):
        step=self.editor.passo.value()
        while step*self.zoom<16:step*=5
        corners=[self.delta_mundo(QPointF(x,y)-self.origem) for x in (0,self.width()) for y in (0,self.height())]
        xmin,xmax=min(v[0] for v in corners),max(v[0] for v in corners)
        ymin,ymax=min(v[1] for v in corners),max(v[1] for v in corners)
        for axis,lo,hi in ((0,xmin,xmax),(1,ymin,ymax)):
            for k in range(math.floor(lo/step),math.ceil(hi/step)+1):
                p.setPen(QPen(QColor(tema.BORDA_BOTAO if self.escuro else '#cbd5e1'),.8 if k%5==0 else .35))
                value=k*step
                if axis==0:p.drawLine(self.tela(value,ymin),self.tela(value,ymax))
                else:p.drawLine(self.tela(xmin,value),self.tela(xmax,value))

    def eixos_grelha(self,p):
        p.save();origin=QPointF(55,self.height()-48)
        for name,delta,color in [('X',projetar(36,0),'#c2410c'),('Y',projetar(0,36),'#15803d'),('Z',projetar(0,0,36),'#2563eb')]:
            p.setPen(QPen(QColor(color),2));tip=origin+delta;u=delta/36;normal=QPointF(-u.y(),u.x())
            p.drawLine(origin,tip);p.drawLine(tip,tip-u*7+normal*3);p.drawLine(tip,tip-u*7-normal*3);p.drawText(tip+QPointF(4,-3),name)
        p.restore()

    def rotular_valor(self,p,anchor,texto):
        """Place values without covering nearby node names or other values."""
        texto=tr(texto);chave=(round(anchor.x()/2),round(anchor.y()/2),texto)
        if chave in self.chaves_valores:return
        self.chaves_valores.add(chave);fm=p.fontMetrics();w=fm.horizontalAdvance(texto)+8;h=fm.height()+4
        base=QPointF(anchor.x()+5,anchor.y()-fm.ascent()-6)
        rect=None
        offsets=[(0,0)]+[(dx,dy*h) for dy in (0,-1,1,-2,2,-3,3,-4,4,-5,5,-6,6) for dx in (0,14,-w-12,w+14,-2*w-20,2*w+20,-3*w-28,3*w+28)]
        for dx,dy in offsets:
            candidate=QRectF(max(2,min(self.width()-w-2,base.x()+dx)),max(2,min(self.height()-h-2,base.y()+dy)),w,h)
            if not any(candidate.intersects(old) for old in self.rotulos_valores):rect=candidate;break
        if rect is None:rect=candidate
        self.rotulos_valores.append(rect.adjusted(-2,-2,2,2));p.save()
        nearest=QPointF(max(rect.left(),min(anchor.x(),rect.right())),max(rect.top(),min(anchor.y(),rect.bottom())))
        if (nearest-anchor).manhattanLength()>18:p.drawLine(anchor,nearest)
        bg=QColor(tema.CAMPO if self.escuro else '#ffffff');bg.setAlpha(225);p.fillRect(rect,bg)
        p.drawText(QPointF(rect.left()+4,rect.top()+2+fm.ascent()),texto);p.restore()

    def carga_projetada_arco(self):
        """Label a truly uniform projected arch load once, without rounding it.

        Recheck geometry and intensities each redraw. After editing geometry or
        loads, unequal projections automatically return to per-member labels.
        """
        m=self.editor.modelo
        if m['tipo']!='Arco' or len(m['barras'])<2:return None
        valores=[]
        for b in m['barras']:
            cargas=b.get('distribuidas',[])
            if b.get('q') or len(cargas)!=1:return None
            ch=cargas[0];a,z=[m['nos'][b[k]] for k in ('i','j')];dx=abs(z['x']-a['x']);L=math.hypot(dx,z['y']-a['y'])
            if dx<1e-10 or ch.get('eixo')!='global_y' or ch.get('funcao') or ch.get('pontos'):return None
            if ch.get('a',0)!=0 or abs(ch.get('b',L)-L)>1e-9 or abs(ch.get('qa',0)-ch.get('qb',ch.get('qa',0)))>1e-9:return None
            valores.append(ch.get('qa',0)*L/dx)
        if max(valores)-min(valores)>1e-8:return None
        return valores[0],(min(n['x'] for n in m['nos'])+max(n['x'] for n in m['nos']))/2,max(n['y'] for n in m['nos'])

    def desenhar_deformada(self,p,i,b,a,z,color):
        ed=self.editor;res=ed.resultado['barras'][i];L=res['L'];c,s=(z['x']-a['x'])/L,(z['y']-a['y'])/L;data=res['deformacoes'];amp=ed.escala.value();f=ed.formatador();outline=[]
        for d in data:
            if ed.modelo['tipo']=='Grelha':outline.append(self.tela(a['x']+c*d['x'],a['y']+s*d['x'],d['uy']*amp))
            else:outline.append(self.tela(a['x']+c*d['x']+d['ux']*amp,a['y']+s*d['x']+d['uy']*amp))
        p.setPen(QPen(QColor(tema.DESTAQUE_TEXTO if self.escuro else '#0078d7'),2));p.setBrush(Qt.NoBrush);p.drawPolyline(QPolygonF(outline))
        for k in range(len(data)-1):self.diagrama_hits.append((outline[k],outline[k+1],i,'norma',data[k],data[k+1]))
        if not ed.preferencias['mostrar_valores']:return
        for k in {0,len(data)-1,max(range(len(data)),key=lambda j:data[j]['norma']),min(range(len(data)),key=lambda j:data[j]['uy']),max(range(len(data)),key=lambda j:data[j]['uy'])}:
            d=data[k];P=outline[k];p.drawEllipse(P,3,3)
            if k in (0,len(data)-1):
                idx=b['i'] if k==0 else b['j']
                if idx in self.rotulos_nodais:continue
                self.rotulos_nodais.add(idx)
            theta='θext' if (k==0 and b.get('rotula_i')) or (k==len(data)-1 and b.get('rotula_j')) else 'θ'
            text=(f'w={f.desloc(d["uy"])} {f.op["deslocamento"]}; θlocal={f.rotacao(d["rotacao"])} rad' if ed.modelo['tipo']=='Grelha' else f'δx={f.desloc(d["ux"])}; δy={f.desloc(d["uy"])} {f.op["deslocamento"]}; {theta}={f.rotacao(d["rotacao"])} rad')
            if k not in (0,len(data)-1):text=f'B{i+1}: |δ|={f.desloc(d["norma"])} {f.op["deslocamento"]} em x={f.comprimento(d["x"])} m'
            text=tr(text);width=min(280,p.fontMetrics().horizontalAdvance(text)+12);r=p.boundingRect(QRectF(0,0,width-12,200),Qt.TextWordWrap,text);height=r.height()+8
            x=max(6,min(self.width()-width-6,P.x()+5));y=max(6,min(self.height()-height-6,P.y()+(24 if k==0 else -height-8 if k==len(data)-1 else 24)))
            p.save();bg=QColor(tema.CAMPO if self.escuro else '#ffffff');bg.setAlpha(230);p.fillRect(QRectF(x,y,width,height),bg);p.drawText(QRectF(x+6,y+4,width-12,height-8),Qt.TextWordWrap,tr(text));p.restore()


class Editor(JanelaPrincipal):
    def __init__(self,config=None):
        self._persistencia_pronta=False;self._aplicando_preferencias=True
        super().__init__(config=config)
        self.setWindowTitle('MS Estruturas  1.0.4');self.setMinimumSize(1000,560);self.resize(1360,900)
        from pathlib import Path
        from PyQt5.QtGui import QIcon
        self.logo=QIcon(str(Path(__file__).with_name('assets')/'ms-estruturas.svg'));self.setWindowIcon(self.logo)
        self.preferencias=self.preferencias_iniciais.copy()
        self.no_selecionado=None;self.escala_diagrama=60.
        self.modelo = {'tipo':'Pórtico plano','nos':[],'barras':[]}
        self.resultado = None
        self.modo_resultado='Diagramas'
        self.historico,self.futuro = [],[]
        self.botoes_icones=[]
        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)
        v.setContentsMargins(14,12,14,12)
        v.setSpacing(10)
        # One aligned command row. Labels collapse to icons on narrow screens;
        # every action retains its tooltip and keyboard/accessibility description.
        acoes = QHBoxLayout();acoes.setSpacing(6);self.cabecalho=acoes
        self.logo_label=QLabel();self.logo_label.setPixmap(self.logo.pixmap(30,30));self.logo_label.setFixedSize(32,34);acoes.addWidget(self.logo_label)
        marca=Marca();marca.setObjectName('marca');self.marca=marca;acoes.addWidget(marca)
        self.tipo = QComboBox()
        self.tipo.addItems(['Viga','Pórtico plano','Treliça','Arco','Grelha'])
        self.tipo.setCurrentText(self.modelo['tipo'])
        self.tipo.currentTextChanged.connect(self.mudar_tipo)
        self.tipo.setFixedSize(128,34);acoes.addWidget(self.tipo)
        self.noturno.setParent(root);self.noturno.hide()
        self.rotulos_cabecalho=[]
        for nome,callback in [('Novo',self.novo),('Abrir',self.abrir),('Salvar',self.salvar),('Exemplos',self.menu_exemplos),('Perfil',self.perfil),('Material',self.material),('Coordenadas',self.coordenadas),('Configurações',self.configuracoes),('Desfazer',self.undo),('Refazer',self.redo),('Calcular',self.calcular),('Exportar',self.exportar)]:
            btn = self.botao_simbolo(nome,callback)
            if nome=='Calcular': btn.setText('Calcular'); btn.setFixedWidth(108);self.analisar_btn=btn
            if nome=='Calcular':
                btn.setCheckable(True); btn.setChecked(True)
            acoes.addWidget(btn)
            if nome=='Exemplos':self.botao_exemplos=btn
        self.grupo_resultados=QButtonGroup(self)
        for nome in ('Reações','Esforços'):
            btn=self.botao_simbolo(nome,lambda checked=False,n=nome:self.exibir_resultado(n));btn.setCheckable(True)
            self.grupo_resultados.addButton(btn);acoes.addWidget(btn);self.rotulos_cabecalho.append((btn,nome,140 if nome=='Esforços' else 115))
        pdf=self.botao_simbolo('Relatório PDF',self.relatorio_pdf);acoes.addWidget(pdf);self.rotulos_cabecalho.append((pdf,'Relatório PDF',135))
        self.tema_btn=self.botao_simbolo('Modo noturno',lambda:self.noturno.setChecked(not self.noturno.isChecked()));self.tema_btn.setCheckable(True);self.tema_btn.setChecked(self.noturno.isChecked());acoes.addWidget(self.tema_btn)
        self.idioma_btn=QPushButton('EN');self.idioma_btn.setFixedSize(38,34);self.idioma_btn.setToolTip('Alternar entre português, inglês e francês.');self.idioma_btn.clicked.connect(self.alternar_idioma);acoes.addWidget(self.idioma_btn)
        acoes.addStretch();v.addLayout(acoes)
        tools = QHBoxLayout()
        self.ferramenta = QComboBox()
        self.ferramenta.addItems(['Selecionar / editar','Nó','Barra','Apoio fixo','Apoio móvel','Engaste','Rótula','Mola','Carga pontual','Retangular','Triangular','Trapezoidal','Função','Apagar nó'])
        self.ferramenta.hide()
        self.snap = QCheckBox('Snap'); self.snap.setChecked(True)
        tools.addWidget(self.snap)
        self.passo = QDoubleSpinBox(); self.passo.setRange(.01,100); self.passo.setValue(.5); self.passo.setSuffix(' m')
        tools.addWidget(self.passo)
        self.diagrama = QComboBox(); self.diagrama.addItems(['Estrutura','N','V','M','T','Deformada'])
        self.diagrama.hide()
        tools.addWidget(QLabel('Escala:'))
        self.escala = QDoubleSpinBox(); self.escala.setRange(1,300); self.escala.setValue(60); self.escala.setSuffix(' px')
        tools.addWidget(self.escala)
        self.coord = QLabel('X / Y (m)');self.coord.setToolTip('Roda: zoom · botão central: pan')
        self.coord.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred);self.coord.setMinimumWidth(0)
        tools.addWidget(self.coord)
        v.addLayout(tools)
        self.canvas = Desenho(self)
        corpo=QHBoxLayout(); corpo.setSpacing(10)
        lateral=QFrame(); lateral.setObjectName('painel'); lateral.setFixedWidth(116);self.paleta=lateral
        paleta=QVBoxLayout(lateral); paleta.setContentsMargins(6,4,6,6); paleta.setSpacing(4)
        self.grupo_ferramentas=QButtonGroup(self); self.grupo_ferramentas.setExclusive(True)
        self.botoes_ferramentas={}
        for titulo,nomes in [('DESENHAR',['Selecionar / editar','Nó','Barra','Arco','Apagar nó']),('VÍNCULOS',['Apoio fixo','Apoio móvel','Engaste','Rótula','Mola']),('CARGAS',['Carga pontual','Retangular','Triangular','Trapezoidal','Função'])]:
            label=QLabel(titulo); label.setObjectName('grupo'); paleta.addWidget(label)
            for pos,nome in enumerate(nomes):
                if pos%3==0:
                    linha=QHBoxLayout(); linha.setSpacing(4); paleta.addLayout(linha)
                btn=self.botao_simbolo(nome,self.criar_arco if nome=='Arco' else lambda checked=False,n=nome:self.ferramenta.setCurrentText(n))
                btn.setCheckable(nome!='Arco'); btn.setFixedSize(32,28);btn.setIconSize(QSize(22,22))
                if nome!='Arco':self.grupo_ferramentas.addButton(btn)
                self.botoes_ferramentas[nome]=btn; linha.addWidget(btn)
                if len(nomes)%3 and pos==len(nomes)-1: linha.addStretch()
        label=QLabel('RESULTADOS'); label.setObjectName('grupo'); paleta.addWidget(label)
        result_grid=QHBoxLayout(); result_grid.setSpacing(4)
        self.grupo_diagramas=QButtonGroup(self)
        for i,nome in enumerate(['Estrutura','N','V','M','T','Deformada']):
            if i%3==0:
                result_grid=QHBoxLayout(); result_grid.setSpacing(4); paleta.addLayout(result_grid)
            btn=self.botao_simbolo(nome,lambda checked=False,n=nome:self.escolher_diagrama(n)); btn.setFixedSize(32,28);btn.setIconSize(QSize(22,22)); btn.setCheckable(True)
            self.grupo_diagramas.addButton(btn); result_grid.addWidget(btn)
            if nome=='Estrutura': btn.setChecked(True)
        paleta.addStretch()
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(lateral); scroll.setFixedWidth(120); scroll.setFrameShape(QFrame.NoFrame);self.scroll_paleta=scroll
        # The palette spans the full work area, including the result footer.
        # Its visibility therefore does not depend on the table/legend height.
        painel_desenho=QWidget();conteudo=QVBoxLayout(painel_desenho);conteudo.setContentsMargins(0,0,0,0);conteudo.setSpacing(8)
        self.entrada_xy=QWidget();xy=QHBoxLayout(self.entrada_xy);xy.setContentsMargins(0,0,0,0)
        self.tipo_xy=QComboBox();self.tipo_xy.addItems(['Nó','Barra']);xy.addWidget(self.tipo_xy)
        self.tipo_xy.currentTextChanged.connect(lambda:self.cancelar_barra())
        from estrutural.ui.formularios import numero
        self.x_entrada=numero();self.y_entrada=numero()
        for nome,campo in [('X (m)',self.x_entrada),('Y (m)',self.y_entrada)]:
            campo.setDecimals(10);campo.setMaximumWidth(150);xy.addWidget(QLabel(nome));xy.addWidget(campo)
        inserir=QPushButton('Inserir (Enter)');inserir.clicked.connect(self.inserir_xy);xy.addWidget(inserir)
        reiniciar=QPushButton('Novo trecho');reiniciar.clicked.connect(self.cancelar_barra);xy.addWidget(reiniciar);xy.addStretch()
        for campo in (self.tipo_xy,self.x_entrada,self.y_entrada,inserir,reiniciar):campo.setFixedHeight(30)
        self.xy_toggle=QPushButton('X/Y');self.xy_toggle.setFixedSize(44,30);self.xy_toggle.setCheckable(True);self.xy_toggle.setToolTip('Mostrar ou ocultar entrada por coordenadas X/Y.');self.xy_toggle.toggled.connect(self.alternar_entrada_xy);tools.addWidget(self.xy_toggle)
        conteudo.addWidget(self.entrada_xy);conteudo.addWidget(self.canvas,1)
        corpo.addWidget(scroll); corpo.addWidget(painel_desenho,1)
        v.addLayout(corpo,1)
        self.ajuda=QLabel(); self.ajuda.setObjectName('info'); conteudo.addWidget(self.ajuda)
        self.legenda=QLabel('Sinais: N+ tração · M+ sagente (fibra inferior) · V+ força local esquerda · forças +X/+Y · momento anti-horário.'); self.legenda.setWordWrap(True); conteudo.addWidget(self.legenda)
        self.tabela = QTableWidget()
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setMaximumHeight(140)
        conteudo.addWidget(self.tabela)
        self.status = QLabel('EA/EI unitários por padrão. Edite rigidezes antes de analisar hiperestáticas.')
        self.status.setObjectName('status'); self.status.setWordWrap(True)
        rodape=QHBoxLayout();rodape.addWidget(self.status,1)
        self.credito=QLabel();self.credito.setAlignment(Qt.AlignRight|Qt.AlignVCenter);self.credito.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.LinksAccessibleByKeyboard);self.credito.setFocusPolicy(Qt.StrongFocus)
        self.credito.setToolTip('Abrir GitHub, LinkedIn ou e-mail de Matheus Schardosim.');self.credito.linkActivated.connect(self.abrir_perfis_autor)
        self.menu_autor=QMenu(self)
        for nome,url in [('GitHub','https://github.com/SCHARDOSIMM'),('LinkedIn','https://www.linkedin.com/in/matheus-schardosim/'),('E-mail','mailto:schardosimmatheus@gmail.com')]:
            action=self.menu_autor.addAction(nome);action.setData(url);action.triggered.connect(lambda checked=False,u=url:QDesktopServices.openUrl(QUrl(u)))
        self.atualizar_credito();rodape.addWidget(self.credito);conteudo.addLayout(rodape)
        self.diagrama.currentTextChanged.connect(lambda: self.canvas.update())
        self.escala.valueChanged.connect(self.atualizar_escala)
        self.passo.valueChanged.connect(lambda: self.canvas.update())
        self.ferramenta.currentTextChanged.connect(self.selecionar_ferramenta)
        grade=QCheckBox('Grade');self.grade_check=grade; grade.setChecked(True); tools.insertWidget(0,grade)
        grade.toggled.connect(lambda ativa: (setattr(self.canvas,'grade',ativa),self.canvas.update()))
        ajustar=self.botao_simbolo('Ajustar vista',self.ajustar_vista);ajustar.setFixedSize(38,30);ajustar.setIconSize(QSize(22,22));self.ajustar_btn=ajustar;tools.addWidget(ajustar)
        self.selecionar_ferramenta(self.ferramenta.currentText())
        self.aplicar_tema(self.noturno.isChecked())
        self.aplicar_preferencias(self.preferencias,gravar=False)
        girar=QPushButton('Girar apoio 90° (R)');girar.setFixedHeight(30);self.girar_btn=girar;girar.setToolTip('Selecione um nó com apoio. No móvel muda a direção física; nos demais apenas o desenho.');girar.clicked.connect(self.girar_apoio);tools.addWidget(girar)
        for campo in (self.passo,self.escala,self.snap,self.grade_check):campo.setFixedHeight(30)
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        for key,cb in [('Ctrl+S',self.salvar),('Ctrl+O',self.abrir),('Ctrl+E',self.coordenadas),('Ctrl+Z',self.undo),('Ctrl+Y',self.redo)]: QShortcut(QKeySequence(key),self,activated=cb)
        for key in ('Return','Enter'):QShortcut(QKeySequence(key),self.entrada_xy,activated=self.inserir_xy,context=Qt.WidgetWithChildrenShortcut)
        self.atualizar_idioma();self.compactar_cabecalho()
        self._aplicando_preferencias=False;self._persistencia_pronta=True
        self.grade_check.toggled.connect(self.salvar_preferencias_usuario)
        self.snap.toggled.connect(self.salvar_preferencias_usuario)
        self.passo.valueChanged.connect(self.salvar_preferencias_usuario)

    def closeEvent(self,event):
        self.config.sync()
        super().closeEvent(event)

    def salvar_preferencias_usuario(self,*args):
        if not self._persistencia_pronta or self._aplicando_preferencias:return
        self.preferencias.update(grade=self.grade_check.isChecked(),snap=self.snap.isChecked(),
            escuro=self.noturno.isChecked(),passo=self.passo.value(),entrada_xy=self.xy_toggle.isChecked(),
            escala_diagrama=self.escala_diagrama)
        gravar_preferencias(self.config,self.preferencias)

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'rotulos_cabecalho'):self.compactar_cabecalho()

    def compactar_cabecalho(self):
        amplo=self.width()>=1360
        estreito=self.width()<1180
        self.marca.show();self.tipo.setFixedWidth(100 if estreito else 128);self.cabecalho.setSpacing(3 if estreito else 6)
        self.analisar_btn.setText('' if estreito else 'Calcular');self.analisar_btn.setFixedWidth(38 if estreito else 108)
        for btn,nome,width in self.rotulos_cabecalho:
            rotulo=amplo and (nome!='Relatório PDF' or self.width()>=1500)
            btn.setText(nome if rotulo else '');btn.setFixedWidth(width if rotulo else 38)
        if hasattr(self,'tabela'):self.tabela.setMaximumHeight(100 if self.height()<780 else 140)
        atualizar(self)

    def alternar_entrada_xy(self,visivel):
        self.entrada_xy.setVisible(visivel)
        if not visivel:self.cancelar_barra()
        self.preferencias['entrada_xy']=visivel
        self.salvar_preferencias_usuario()

    def inserir_xy(self):
        try:
            self.x_entrada.interpretText();self.y_entrada.interpretText()
            model=copy.deepcopy(self.modelo);x,y=self.x_entrada.value(),self.y_entrada.value()
            idx=next((i for i,n in enumerate(model['nos']) if math.hypot(n['x']-x,n['y']-y)<1e-8),None)
            if idx is None:idx=inserir_no(model,x,y)
            inicio=self.canvas.inicio
            if self.tipo_xy.currentText()=='Barra' and inicio is not None:inserir_barra(model,inicio,idx)
            self.validar(model)
            if model!=self.modelo:self.registrar();self.modelo=model;self.invalidar()
            self.canvas.inicio=idx if self.tipo_xy.currentText()=='Barra' else None
            self.no_selecionado=idx;self.canvas.update();self.x_entrada.setFocus();self.x_entrada.selectAll()
            self.ajuda.setText('Coordenadas inseridas. Para barras, informe o próximo ponto ou use Novo trecho.')
        except (ValueError,KeyError,TypeError) as err:self.erro(err)

    def alternar_idioma(self):
        atual=self.preferencias.get('idioma','pt_BR')
        self.preferencias['idioma']=IDIOMAS[(IDIOMAS.index(atual)+1)%len(IDIOMAS)]
        self.atualizar_idioma();self.salvar_preferencias_usuario()

    def atualizar_credito(self):
        cor=tema.DESTAQUE_TEXTO if self.noturno.isChecked() else tema.DESTAQUE
        self.credito.setText('Criado por <a href="perfis" style="color:'+cor+'; text-decoration:underline;">Matheus Schardosim</a>')

    def abrir_perfis_autor(self,link='perfis'):
        if link=='perfis':self.menu_autor.popup(self.credito.mapToGlobal(QPoint(0,-self.menu_autor.sizeHint().height())))

    def atualizar_idioma(self):
        definir(self.preferencias.get('idioma','pt_BR'))
        self.idioma_btn.setText({'pt_BR':'EN','en_US':'FR','fr_FR':'PT'}[self.preferencias.get('idioma','pt_BR')])
        self.preencher_tabela();self.canvas.update()

    def botao_simbolo(self,nome,callback):
        btn=QPushButton();btn.setObjectName('simbolo'); btn.setFixedSize(38,34); btn.setIconSize(QSize(26,26))
        btn.setProperty('acao',nome);btn.setToolTip('<b>'+nome+'</b><br>'+DESCRICOES.get(nome,nome)); btn.setAccessibleName(nome); btn.setAccessibleDescription(DESCRICOES.get(nome,nome)); btn.clicked.connect(callback)
        btn.installEventFilter(self)
        if nome=='Salvar':btn.setToolTip('Salvar (Ctrl+S)')
        self.botoes_icones.append((btn,nome))
        btn.toggled.connect(lambda: self.atualizar_icones())
        return btn

    def exibir_resultado(self,nome):
        anterior=self.modo_resultado
        self.modo_resultado=nome
        blocked=self.escala.blockSignals(True)
        if nome=='Deformada' and anterior!='Deformada':
            self.escala_diagrama=self.escala.value();self.escala.setRange(.01,1e12);self.escala.setSuffix(' ×');self.escala.setValue(self.preferencias['escala_deformada'])
        elif nome!='Deformada' and anterior=='Deformada':self.escala.setRange(1,300);self.escala.setSuffix(' px');self.escala.setValue(self.escala_diagrama)
        self.escala.blockSignals(blocked)
        for group in (self.grupo_resultados,self.grupo_diagramas):
            group.setExclusive(False)
            for btn in group.buttons():btn.setChecked(btn.property('acao')==(nome if group==self.grupo_resultados else self.diagrama.currentText()) and (nome in ('Reações','Esforços') if group==self.grupo_resultados else nome in ('Diagramas','Deformada')))
            group.setExclusive(True)
        if nome=='Deformada':self.diagrama.setCurrentText('Deformada')
        elif self.diagrama.currentText()=='Deformada':self.diagrama.setCurrentText('M')
        if self.resultado:self.preencher_tabela()
        self.atualizar_legenda()
        self.canvas.update()

    def formatador(self):return Formatador(self.resultado,self.preferencias)

    def atualizar_escala(self):
        if self.modo_resultado=='Deformada':self.preferencias['escala_deformada']=self.escala.value()
        else:self.escala_diagrama=self.escala.value()
        self.salvar_preferencias_usuario()
        self.atualizar_legenda();self.canvas.update()

    def configuracoes(self):
        from estrutural.ui.preferencias import Preferencias
        dialog=Preferencias(self)
        if dialog.exec_():self.aplicar_preferencias(dialog.resultado)

    def aplicar_preferencias(self,op,gravar=True):
        anterior=self._aplicando_preferencias;self._aplicando_preferencias=True
        controles=(self.xy_toggle,self.grade_check,self.snap,self.passo,self.noturno,self.escala)
        sinais=[(w,w.blockSignals(True)) for w in controles]
        try:
            self.preferencias={**PADRAO,**self.preferencias,**op}
            self.xy_toggle.setChecked(self.preferencias['entrada_xy']);self.entrada_xy.setVisible(self.preferencias['entrada_xy'])
            self.grade_check.setChecked(self.preferencias['grade']);self.canvas.grade=self.preferencias['grade']
            self.snap.setChecked(self.preferencias['snap']);self.passo.setValue(self.preferencias['passo'])
            self.noturno.setChecked(self.preferencias['escuro']);self.aplicar_tema(self.noturno.isChecked())
            self.escala_diagrama=self.preferencias['escala_diagrama']
            self.escala.setValue(self.preferencias['escala_deformada'] if self.modo_resultado=='Deformada' else self.escala_diagrama)
            if hasattr(self,'idioma_btn'):self.atualizar_idioma()
            self.preencher_tabela();self.atualizar_legenda();self.canvas.update()
        finally:
            for w,blocked in sinais:w.blockSignals(blocked)
            self._aplicando_preferencias=anterior
        if gravar:
            self.modelo['nome']=self.preferencias['nome_projeto'];self.salvar_preferencias_usuario()

    def girar_apoio(self):
        i=self.no_selecionado
        if i is None or not 0<=i<len(self.modelo['nos']):self.ajuda.setText('Selecione primeiro um nó com apoio.');return
        no=self.modelo['nos'][i];a=no.get('apoio',[])
        if not any(a):self.ajuda.setText('O nó selecionado não tem apoio.');return
        self.registrar()
        if self.modelo['tipo']!='Grelha' and not a[0] and a[1]:no['apoio_angulo']=(no.get('apoio_angulo',90)+90)%360;self.invalidar();self.ajuda.setText('Direção física do apoio móvel alterada. Calcule novamente.')
        else:no['apoio_visual']=(no.get('apoio_visual',0)+90)%360;self.canvas.update();self.ajuda.setText('Apoio girado visualmente; as restrições e os resultados de cálculo não mudam.')

    def escolher_diagrama(self,nome):
        self.diagrama.setCurrentText(nome)
        modo='Deformada' if nome=='Deformada' else 'Diagramas'
        for btn in self.grupo_resultados.buttons():btn.setChecked(btn.text()==modo)
        self.exibir_resultado(modo)

    def preencher_tabela(self):
        if not self.resultado:return
        f=self.formatador();force=f.op['forca'];moment=force+'·m';disp=f.op['deslocamento'];grid=self.modelo['tipo']=='Grelha'
        if self.modo_resultado=='Esforços':
            self.tabela.setColumnCount(6); self.tabela.setHorizontalHeaderLabels(['Barra','x (m)',f'N ({force})',f'V ({force})',f'M ({moment})',f'T ({moment})'])
            rows=[[str(i+1),f.comprimento(p['x'])]+[f.esforco(p.get(k,0)) for k in ('N','V','M','T')] for i,b in enumerate(self.resultado['barras']) for p in b['pontos']]
        else:
            if self.modo_resultado=='Deformada':
                labels=['Nó',f'w ({disp})','θx (rad)','θy (rad)'] if grid else ['Nó',f'δx ({disp})',f'δy ({disp})','θ (rad)']
                rows=[[str(i+1)]+([f.desloc(d[0])]+[f.rotacao(v) for v in d[1:]] if grid else [f.desloc(v) for v in d[:2]]+([f.rotacao(d[2])] if len(d)>2 else ['—'])) for i,d in enumerate(self.resultado['deslocamentos'])]
            else:
                labels=['Nó',f'Rx ({force})',f'Ry ({force})',f'M ({moment})',f'δx ({disp})',f'δy ({disp})','θ (rad)'] if not grid else ['Nó',f'Rz ({force})',f'Mx ({moment})',f'My ({moment})',f'w ({disp})','θx (rad)','θy (rad)']
                rows=[[str(i+1)]+[f.esforco(v) for v in r]+(['—'] if len(r)==2 else [])+([f.desloc(d[0])]+[f.rotacao(v) for v in d[1:]] if grid else [f.desloc(v) for v in d[:2]]+([f.rotacao(d[2])] if len(d)>2 else ['—'])) for i,(r,d) in enumerate(zip(self.resultado['reacoes'],self.resultado['deslocamentos']))]
            self.tabela.setColumnCount(len(labels));self.tabela.setHorizontalHeaderLabels(labels)
            from estrutural.core.apoios import rotacao_livre
            for i,row in enumerate(rows):
                if rotacao_livre(self.modelo,i):row[-1]='livre'
        self.tabela.setRowCount(len(rows))
        for i,row in enumerate(rows):
            for j,val in enumerate(row):
                item=QTableWidgetItem(str(val));item.setTextAlignment(Qt.AlignCenter);self.tabela.setItem(i,j,item)
        atualizar(self.tabela)

    def eventFilter(self,obj,event):
        if hasattr(self,'ajuda') and isinstance(obj,QPushButton):
            if event.type()==QEvent.Enter:
                self.ajuda.setText(obj.accessibleName()+' · '+obj.accessibleDescription())
            elif event.type()==QEvent.Leave:
                nome=self.ferramenta.currentText(); self.ajuda.setText(nome+' · '+DESCRICOES.get(nome,''))
        return super().eventFilter(obj,event)

    def atualizar_icones(self):
        for btn,nome in getattr(self,'botoes_icones',[]):
            cor='#ffffff' if btn.isChecked() else (tema.TEXTO if self.noturno.isChecked() else '#000000')
            desenho=('Sol' if self.noturno.isChecked() else 'Lua') if nome=='Modo noturno' else nome
            btn.setIcon(icone(desenho,cor))

    def aplicar_tema(self,escuro):
        super().aplicar_tema(escuro)
        from PyQt5.QtWidgets import QApplication
        app=QApplication.instance();app.setStyleSheet(app.styleSheet()+'\nQPushButton#simbolo { padding: 0px; text-align: center; }')
        self.atualizar_icones()
        self.atualizar_legenda()
        if hasattr(self,'tema_btn'):
            self.tema_btn.blockSignals(True);self.tema_btn.setChecked(escuro);self.tema_btn.blockSignals(False)
            self.atualizar_icones()
        if hasattr(self,'credito'):self.atualizar_credito()
        self.salvar_preferencias_usuario()

    def atualizar_legenda(self):
        if not hasattr(self,'legenda'):return
        if self.modo_resultado=='Deformada':
            self.legenda.setText(f'Deformada ampliada ×{self.escala.value():g} | deslocamentos em {self.preferencias["deslocamento"]} | x desde o início da barra | '+('w em Z, fora do plano XY; geometria original sem amplificação.' if self.modelo['tipo']=='Grelha' else 'δx/δy globais; θ em rad. Passe o mouse sobre a curva.'));return
        if self.modelo['tipo']=='Grelha':
            self.legenda.setText('Grelha: +w em Z; θx/θy e torção pela mão direita. Reações: Rz, Mx, My. Diagramas amostrados.')
        else:
            colors=('#4fa3ff','#c79bff','#55d6b1') if self.noturno.isChecked() else ('#0078d7','#8040a0','#00796b')
            self.legenda.setText(f'Sinais: <span style="color:{colors[0]}">N+ tração</span> · <span style="color:{colors[1]}">V+ força local esquerda</span> · <span style="color:{colors[2]}">M+ sagente, fibra inferior</span> · momentos anti-horários.')
            self.legenda.setToolTip('Diagramas: escala comum por esforço; leitura interpolada entre amostras.')

    def selecionar_ferramenta(self,nome):
        self.canvas.cancelar_selecao()
        self.cancelar_barra()
        self.botoes_ferramentas[nome].setChecked(True)
        self.ajuda.setText(nome+' · '+DESCRICOES.get(nome,'')); self.ajuda.setWordWrap(True)
        self.canvas.setCursor(Qt.ArrowCursor if nome=='Selecionar / editar' else Qt.CrossCursor)
        self.canvas.update()

    def ajustar_vista(self):
        nos=self.modelo['nos']
        if not nos: return
        if self.modelo['tipo']=='Grelha':
            nos=[{'x':projetar(n['x'],n['y']).x(),'y':-projetar(n['x'],n['y']).y()} for n in nos]
        xmin,xmax=min(n['x'] for n in nos),max(n['x'] for n in nos)
        ymin,ymax=min(n['y'] for n in nos),max(n['y'] for n in nos)
        margem=min(110,max(50,min(self.canvas.width(),self.canvas.height())*.23))
        self.canvas.zoom=max(5,min(300,(self.canvas.width()-2*margem)/max(xmax-xmin,1),(self.canvas.height()-2*margem)/max(ymax-ymin,1)))
        self.canvas.origem=QPointF(self.canvas.width()/2-(xmin+xmax)/2*self.canvas.zoom,self.canvas.height()/2+(ymin+ymax)/2*self.canvas.zoom)
        self.canvas.update()

    def cancelar_barra(self): self.canvas.inicio = None
    def erro(self,text): QMessageBox.warning(self,'Verifique o modelo',str(text))
    def registrar(self):
        self.historico.append(copy.deepcopy(self.modelo)); self.futuro.clear()
    def invalidar(self):
        self.resultado = None; self.tabela.setRowCount(0); self.canvas.update()
        if hasattr(self,'painel_coordenadas'): self.painel_coordenadas.atualizar()
        self.atualizar_legenda()
        self.status.setText('Modelo alterado. Calcule novamente. Unidades internas: kN, m, rad; EA em kN; EI em kN·m².')
    def mudar_tipo(self,t):
        anterior=self.modelo['tipo'];self.registrar(); self.modelo['tipo']=t; self.invalidar()
        if 'Grelha' in (anterior,t):
            if self.modelo['nos']:self.ajustar_vista()
            elif t=='Grelha':self.canvas.origem=QPointF(self.canvas.width()/2,self.canvas.height()*.35)
    def carregar(self,m):
        self.canvas.cancelar_selecao();self.canvas.iniciar_selecao()
        self.modelo=migrar(m)
        self.no_selecionado=None
        self.tipo.blockSignals(True); self.tipo.setCurrentText(m['tipo']); self.tipo.blockSignals(False)
        self.canvas.inicio=None; self.invalidar()
    def novo(self):
        self.registrar(); self.carregar({'tipo':'Pórtico plano','nos':[],'barras':[]})
    def exemplo(self): self.registrar(); self.carregar(exemplo())
    def menu_exemplos(self):
        from estrutural.ui.popover import ExemplosPopover
        if hasattr(self,'exemplos_pop'):self.exemplos_pop.close()
        self.exemplos_pop=ExemplosPopover(self,self.botao_exemplos,self.abrir_exemplo);self.exemplos_pop.ancorar()
    def abrir_exemplo(self,item):
        m=copy.deepcopy(item['modelo']); m['exemplo']={k:item[k] for k in ('nome','descricao','referencia')}
        if 'rotulos_nos' in item:m['exemplo']['rotulos_nos']=list(item['rotulos_nos'])
        self.registrar(); self.carregar(m); self.ajustar_vista(); self.calcular()
        self.ajuda.setText(item['nome']+' · '+item['referencia'])
    def coordenadas(self):
        from estrutural.ui.coordenadas import Coordenadas
        if not hasattr(self,'painel_coordenadas'): self.painel_coordenadas=Coordenadas(self)
        self.painel_coordenadas.atualizar(); self.painel_coordenadas.show(); self.painel_coordenadas.raise_(); self.painel_coordenadas.x.setFocus()
    def perfil(self):
        from estrutural.ui.perfis import SeletorPerfil
        if not self.modelo['barras']: self.erro('Crie uma barra antes de atribuir um perfil.'); return
        texto,ok=QInputDialog.getText(self,'Aplicar perfil a barras','Números das barras separados por vírgula, ou * para todas:',text='*')
        if not ok:return
        try:
            ids=list(range(len(self.modelo['barras']))) if texto.strip()=='*' else sorted(set(int(n.strip())-1 for n in texto.split(',')))
            if not ids or any(not 0<=i<len(self.modelo['barras']) for i in ids):raise ValueError('Informe números de barras existentes.')
            d=SeletorPerfil(self,self.modelo['barras'][ids[0]])
            if d.exec_():
                changes={i:aplicar_secao(self.modelo['barras'][i],d.resultado) for i in ids}
                self.registrar()
                for i,b in changes.items():self.modelo['barras'][i]=b
                self.invalidar()
        except ValueError as e:self.erro(e)
    def criar_arco(self):
        from estrutural.ui.arcos import DialogoArco
        if self.modelo['tipo'] in ('Treliça','Grelha'):
            self.erro('Selecione Viga, Pórtico plano ou Arco antes de inserir esta geometria.');return
        try:
            dialog=DialogoArco(self)
            if dialog.exec_():
                m=copy.deepcopy(self.modelo);mapping={}
                for i,n in enumerate(dialog.resultado['nos']):
                    idx=next((j for j,v in enumerate(m['nos']) if math.hypot(v['x']-n['x'],v['y']-n['y'])<1e-8),None)
                    mapping[i]=inserir_no(m,n['x'],n['y']) if idx is None else idx
                for b in dialog.resultado['barras']:inserir_barra(m,mapping[b['i']],mapping[b['j']])
                if not self.modelo['nos']:m['tipo']='Arco'
                self.registrar();self.carregar(m);self.ajustar_vista()
        except (ValueError,TypeError,KeyError) as e: self.erro(e)

    def material(self):
        from estrutural.ui.materiais import SeletorMaterial
        from estrutural.core.materiais import aplicar_material
        if not self.modelo['barras']:self.erro('Crie uma barra antes de atribuir um material.');return
        texto,ok=QInputDialog.getText(self,'Aplicar material','Números das barras separados por vírgula, ou * para todas:',text='*')
        if not ok:return
        try:
            ids=list(range(len(self.modelo['barras']))) if texto.strip()=='*' else sorted(set(int(n.strip())-1 for n in texto.split(',')))
            if not ids or any(not 0<=i<len(self.modelo['barras']) for i in ids):raise ValueError('Informe barras existentes.')
            d=SeletorMaterial(self,self.modelo['barras'][ids[0]])
            if d.exec_():
                novos={i:aplicar_material(self.modelo['barras'][i],d.resultado) for i in ids};self.registrar()
                for i,b in novos.items():self.modelo['barras'][i]=b
                self.invalidar()
        except ValueError as e:self.erro(e)

    def relatorio_pdf(self):
        if not self.resultado:
            self.calcular()
            if not self.resultado:return
        path,_=QFileDialog.getSaveFileName(self,'Salvar relatório de análise','','Relatório PDF (*.pdf)')
        if path:
            try:
                from estrutural.ui.relatorio import gerar_relatorio
                gerar_relatorio(path,self.modelo,self.resultado,self.preferencias);self.status.setText('Relatório PDF salvo com tabelas e diagramas: '+path)
            except (OSError,ValueError) as e:self.erro(e)
    def undo(self):
        if self.historico:
            self.futuro.append(copy.deepcopy(self.modelo)); self.carregar(self.historico.pop())
    def redo(self):
        if self.futuro:
            self.historico.append(copy.deepcopy(self.modelo)); self.carregar(self.futuro.pop())
    def texto_json(self,titulo,obj):
        d=QDialog(self); d.setWindowTitle(titulo); d.resize(700,550)
        l=QVBoxLayout(d); edit=QPlainTextEdit(json.dumps(obj,ensure_ascii=False,indent=2)); edit.setFont(QFont('Consolas',9)); l.addWidget(edit)
        btn=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); l.addWidget(btn)
        btn.accepted.connect(d.accept); btn.rejected.connect(d.reject)
        if d.exec_(): return json.loads(edit.toPlainText())
    def editar_no(self,i):
        try:
            n=editar_no(self,self.modelo['nos'][i],self.modelo['tipo'])
            if n is not None:
                m=copy.deepcopy(self.modelo); m['nos'][i]=n; self.validar(m)
                self.registrar(); self.modelo['nos'][i]=n; self.invalidar()
        except (ValueError,TypeError) as e: self.erro(e)

    def aplicar_na_barra(self,i,tipo):
        b=self.modelo['barras'][i]
        if self.modelo['tipo'] in ('Treliça','Grelha'):
            self.erro('Estas ferramentas de carga e liberação são para vigas, pórticos e arcos. Treliças já são biarticuladas; grelhas mantêm as limitações descritas na documentação.'); return
        if tipo=='Rótula':
            itens=[f'Início — nó {b["i"]+1}',f'Fim — nó {b["j"]+1}']
            item,ok=QInputDialog.getItem(self,'Liberação de momento','Escolha a extremidade. Uma rótula existente será removida.',itens,editable=False)
            if ok:
                key='rotula_i' if item==itens[0] else 'rotula_j'
                self.registrar(); b[key]=not b.get(key,False); self.invalidar()
            return
        a,z=[self.modelo['nos'][b[k]] for k in ('i','j')]; L=math.hypot(z['x']-a['x'],z['y']-a['y'])
        if not L: self.erro('Barra de comprimento zero.'); return
        carga=carga_distribuida(self,L,tipo)
        if carga is not None:
            self.registrar(); b.setdefault('distribuidas',[]).append(carga); self.invalidar()
    def editar_modelo(self):
        try:
            m=self.texto_json('Modelo: índices i/j começam em zero; q local positivo em +y',self.modelo)
            if m is not None:
                self.validar(m); self.registrar(); self.carregar(m)
        except (ValueError,KeyError,TypeError) as e: self.erro(e)
    def validar(self,m):
        if set(m)-{'tipo','nos','barras','segunda_ordem','exemplo','nome'}:
            raise ValueError('Propriedade de projeto desconhecida. Consulte docs/VERSAO_02.md.')
        if m['tipo'] not in ['Viga','Pórtico plano','Treliça','Arco','Grelha']: raise ValueError('Tipologia inválida.')
        for n in m['nos']:
            if set(n)-{'x','y','carga_pontual','apoio','mola','recalque','apoio_angulo','apoio_visual','apoio_visual_tipo'}: raise ValueError('Propriedade nodal desconhecida.')
            for key in ('apoio_angulo','apoio_visual'):
                if key in n and not math.isfinite(n[key]):raise ValueError('Ângulo de apoio deve ser finito.')
            if not all(math.isfinite(n[k]) for k in ('x','y')): raise ValueError('Coordenada inválida.')
            for key in ('carga_pontual','apoio','mola','recalque'):
                if key in n and (len(n[key])<2 or len(n[key])>3 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in n[key])):
                    raise ValueError(f'{key}: use dois ou três valores numéricos finitos.')
                if key in n and m['tipo']!='Treliça' and len(n[key])!=3: raise ValueError(f'{key}: pórticos exigem três componentes.')
        for i,n in enumerate(m['nos']):
            if any(math.hypot(n['x']-o['x'],n['y']-o['y'])<1e-8 for o in m['nos'][:i]):raise ValueError('Há nós duplicados. Ajuste as coordenadas antes de continuar.')
        for b in m['barras']:
            if set(b)-{'i','j','EA','EI','GJ','q','alpha','delta_t','rotula_i','rotula_j','pontuais','distribuidas','secao','material'}:
                raise ValueError('Propriedade de barra desconhecida ou não implementada.')
            for key in ('EA','EI','GJ','q','alpha','delta_t'):
                if key in b and (not isinstance(b[key],(int,float)) or not math.isfinite(b[key])): raise ValueError(f'{key} deve ser numérico e finito.')
            if any(not isinstance(b[k],int) or not 0<=b[k]<len(m['nos']) for k in ('i','j')): raise ValueError('Índice de nó inválido.')
            a,z=[m['nos'][b[k]] for k in ('i','j')]
            if math.hypot(a['x']-z['x'],a['y']-z['y'])<1e-8:raise ValueError('Barra de comprimento zero.')
            if b.get('secao'): aplicar_secao(b,b['secao'])
            if b.get('material'):
                from estrutural.core.materiais import validar_material
                validar_material(b['material'])
    def abrir(self):
        path,_=QFileDialog.getOpenFileName(self,'Abrir projeto','','Projeto (*.json)')
        if path:
            try:
                with open(path,encoding='utf-8') as f: m=migrar(json.load(f))
                self.validar(m); self.registrar(); self.carregar(m)
            except (OSError,ValueError,KeyError,TypeError) as e: self.erro(e)
    def salvar(self):
        path,_=QFileDialog.getSaveFileName(self,'Salvar projeto','','Projeto (*.json)')
        if path:
            try:
                with open(path,'w',encoding='utf-8') as f: json.dump(self.modelo,f,ensure_ascii=False,indent=2,allow_nan=False)
            except (OSError,ValueError) as e: self.erro(e)
    def calcular(self):
        self.resultado=None
        self.tabela.setRowCount(0)
        try:
            self.validar(self.modelo)
            from estrutural.core.materiais import preparar_barra
            self.modelo['barras']=[preparar_barra(b) for b in self.modelo['barras']]
            self.resultado=analisar(self.modelo)
            eq=self.resultado['equilibrio'];f=self.formatador()
            nomes=('ΣFz','ΣMx','ΣMy') if self.modelo['tipo']=='Grelha' else ('ΣFx','ΣFy','ΣM')
            self.status.setText('Resíduos de equilíbrio: '+', '.join(n+'='+f.esforco(v) for n,v in zip(nomes,eq))+' | '+f.op['forca']+' / '+f.unidade('M'))
            self.preencher_tabela()
        except (ValueError,KeyError,TypeError,IndexError,ZeroDivisionError) as e: self.erro(e)
        self.canvas.update()
    def exportar(self):
        path,filtro=QFileDialog.getSaveFileName(self,'Exportar','','Imagem (*.png);;Resultados (*.csv);;Deslocamentos (*.csv);;Reações (*.csv);;Relatório (*.pdf)')
        if not path: return
        try:
            if filtro.startswith('Imagem'):
                if not self.canvas.grab().save(path,'PNG'): raise OSError('Não foi possível gravar a imagem.')
            elif not self.resultado: raise ValueError('Calcule o modelo antes de exportar resultados.')
            elif filtro.startswith('Resultados'):
                fmt=self.formatador();force=fmt.op['forca'];mom=force+'m'
                with open(path,'w',newline='',encoding='utf-8-sig') as f:
                    w=csv.writer(f,delimiter=';'); w.writerow(self.cabecalho_csv(['barra','x_m','N_'+force,'V_'+force,'M_'+mom,'T_'+mom,'perfil','A_m2','Ix_m4','Iy_m4','J_m4']))
                    for i,b in enumerate(self.resultado['barras']):
                        config=self.modelo['barras'][i].get('secao')
                        props=calcular_secao(config['familia'],config['dimensoes'],config.get('sobrescritos')) if config else {}
                        for p in b['pontos']: w.writerow([i+1,fmt.comprimento(p['x'])]+[fmt.esforco(p.get(k,0)) for k in ('N','V','M','T')]+[tr(config.get('nome',config['familia']) if config else 'Rigidez direta')]+[props.get(k,'') for k in ('A','Ix','Iy','J')])
            elif filtro.startswith(('Deslocamentos','Reações')):
                fmt=self.formatador();grid=self.modelo['tipo']=='Grelha';disp=fmt.op['deslocamento'];isdisp=filtro.startswith('Deslocamentos')
                headers=(['no','w_'+disp,'theta_x_rad','theta_y_rad'] if grid else ['no','dx_'+disp,'dy_'+disp,'theta_rad']) if isdisp else (['no','Rz_'+fmt.op['forca'],'Mx_'+fmt.op['forca']+'m','My_'+fmt.op['forca']+'m'] if grid else ['no','Rx_'+fmt.op['forca'],'Ry_'+fmt.op['forca'],'M_'+fmt.op['forca']+'m'])
                with open(path,'w',newline='',encoding='utf-8-sig') as file:
                    w=csv.writer(file,delimiter=';');w.writerow(self.cabecalho_csv(headers))
                    for i,row in enumerate(self.resultado['deslocamentos' if isdisp else 'reacoes']):
                        values=([fmt.desloc(row[0])]+[fmt.rotacao(v) for v in row[1:]] if grid else [fmt.desloc(v) for v in row[:2]]+([fmt.rotacao(row[2])] if len(row)>2 else ['0'])) if isdisp else [fmt.esforco(v) for v in row]+(['0'] if len(row)==2 else [])
                        from estrutural.core.apoios import rotacao_livre
                        if isdisp and rotacao_livre(self.modelo,i):values[-1]=tr('livre')
                        w.writerow([i+1]+values)
            else:
                from estrutural.ui.relatorio import gerar_relatorio
                gerar_relatorio(path,self.modelo,self.resultado,self.preferencias)
        except (OSError,ValueError) as e: self.erro(e)

    def cabecalho_csv(self,headers):
        nomes={'en_US':{'barra':'member','perfil':'section','no':'node'},
               'fr_FR':{'barra':'barre','perfil':'section','no':'nœud'}}.get(self.preferencias.get('idioma'),{})
        return [nomes.get(h,h) for h in headers]
