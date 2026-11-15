"""Canvas selection and transactional group movement (one undo per drag)."""
import copy
import math
from PyQt5.QtCore import Qt,QPointF,QRectF
from PyQt5.QtGui import QColor,QPen
from estrutural.ui.idioma import tr
from estrutural.ui import tema


class Selecao:
    def iniciar_selecao(self):
        self.nos_selecionados=set();self.barras_selecionadas=set();self.gesto=None

    def nos_do_grupo(self):
        indices=set(self.nos_selecionados)
        for i in self.barras_selecionadas:
            b=self.editor.modelo['barras'][i];indices.update((b['i'],b['j']))
        return indices

    def pressionar_selecao(self,e,near):
        hit=None if near is not None else self.barra_proxima(e.pos())
        add=bool(e.modifiers() & (Qt.ControlModifier|Qt.ShiftModifier))
        if near is None and hit is None:
            if not add:self.nos_selecionados.clear();self.barras_selecionadas.clear()
            self.gesto=dict(tipo='area',inicio=QPointF(e.pos()),fim=QPointF(e.pos()),nos=set(self.nos_selecionados),barras=set(self.barras_selecionadas))
        else:
            grupo=self.nos_selecionados if near is not None else self.barras_selecionadas
            idx=near if near is not None else hit
            if add:
                grupo.symmetric_difference_update({idx});self.gesto=None;self.update();return
            selected=(near in self.nos_do_grupo()) if near is not None else hit in grupo
            if not selected:
                self.nos_selecionados.clear();self.barras_selecionadas.clear();grupo.add(idx)
            self.gesto=dict(tipo='mover',inicio=QPointF(e.pos()),modelo=copy.deepcopy(self.editor.modelo),resultado=self.editor.resultado,nos=self.nos_do_grupo(),alterado=False)
        self.editor.ajuda.setText('Arraste para selecionar ou mover. Ctrl/Shift combina seleções; duplo clique edita. Esc cancela.')
        self.update()

    def mover_selecao(self,pos):
        g=self.gesto
        if not g:return False
        if g['tipo']=='area':
            g['fim']=QPointF(pos);r=QRectF(g['inicio'],g['fim']).normalized()
            self.nos_selecionados=g['nos']|{i for i,n in enumerate(self.editor.modelo['nos']) if r.contains(self.tela(n['x'],n['y']))}
            self.barras_selecionadas=g['barras']|{i for i,b in enumerate(self.editor.modelo['barras']) if all(r.contains(self.tela(self.editor.modelo['nos'][b[k]]['x'],self.editor.modelo['nos'][b[k]]['y'])) for k in ('i','j'))}
        else:
            d=QPointF(pos)-g['inicio']
            if not g['alterado'] and d.manhattanLength()<5:return True
            dx,dy=d.x()/self.zoom,-d.y()/self.zoom
            if self.editor.snap.isChecked():
                passo=self.editor.passo.value();dx=round(dx/passo)*passo;dy=round(dy/passo)*passo
            model=copy.deepcopy(g['modelo'])
            for i in g['nos']:
                model['nos'][i]['x']+=dx;model['nos'][i]['y']+=dy
            g['alterado']=model!=g['modelo'];self.editor.modelo=model
            self.editor.resultado=None;self.editor.tabela.setRowCount(0)
        self.update();return True

    def finalizar_selecao(self,pos):
        if not self.gesto:return
        self.mover_selecao(pos);g=self.gesto;self.gesto=None;ed=self.editor
        if g['tipo']=='mover':
            candidate=ed.modelo;ed.modelo=g['modelo'];ed.resultado=g['resultado']
            if g['alterado']:
                try:
                    ed.validar(candidate)
                    for b in candidate['barras']:
                        a,z=[candidate['nos'][b[k]] for k in ('i','j')];L=math.hypot(z['x']-a['x'],z['y']-a['y'])
                        if any(not 0<=c['x']<=L for c in b.get('pontuais',[])) or any(not 0<=c.get('a',0)<c.get('b',L)<=L for c in b.get('distribuidas',[])):
                            raise ValueError('O movimento deixaria uma carga fora da barra.')
                    ed.registrar();ed.modelo=candidate;ed.invalidar()
                except (ValueError,KeyError,TypeError) as err:
                    ed.ajuda.setText('Movimento cancelado: '+str(err));ed.preencher_tabela()
            else:ed.preencher_tabela()
        self.update()

    def cancelar_selecao(self):
        if self.gesto and self.gesto['tipo']=='mover':
            self.editor.modelo=self.gesto['modelo'];self.editor.resultado=self.gesto['resultado'];self.editor.preencher_tabela()
        self.gesto=None;self.update()

    def desenhar_selecao(self,p):
        cor=QColor(tema.DESTAQUE_TEXTO if self.escuro else tema.DESTAQUE);p.save();p.setPen(QPen(cor,4));p.setBrush(Qt.NoBrush)
        for i in self.barras_selecionadas:
            if i>=len(self.editor.modelo['barras']):continue
            b=self.editor.modelo['barras'][i];a,z=[self.editor.modelo['nos'][b[k]] for k in ('i','j')];p.drawLine(self.tela(a['x'],a['y']),self.tela(z['x'],z['y']))
        p.setPen(QPen(cor,2))
        for i in self.nos_do_grupo():
            n=self.editor.modelo['nos'][i];p.drawEllipse(self.tela(n['x'],n['y']),8,8)
        if self.gesto and self.gesto['tipo']=='area':
            fill=QColor(cor);fill.setAlpha(35);p.setBrush(fill);p.setPen(QPen(cor,1,Qt.DashLine));p.drawRect(QRectF(self.gesto['inicio'],self.gesto['fim']).normalized())
        p.restore()
