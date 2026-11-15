"""Entradas de engenharia com unidades e validação antes de aplicar."""
from PyQt5.QtWidgets import (QDialog,QVBoxLayout,QFormLayout,QDoubleSpinBox,
    QComboBox,QLineEdit,QLabel,QDialogButtonBox,QMessageBox,QSpinBox,QPushButton,QWidget,QScrollArea)
from estrutural.core.cargas import intensidade,integrar
from estrutural.ui.idioma import QComboBox, QDialogButtonBox, QLabel, QPushButton, QCheckBox, tr


def numero(valor=0,minimo=-1e9,maximo=1e9):
    w=QDoubleSpinBox(); w.setDecimals(5); w.setRange(minimo,maximo); w.setValue(valor); return w


def carga_distribuida(parent,L,tipo):
    from estrutural.ui.cargas_visuais import EditorCarga
    d=EditorCarga(parent,L,tipo)
    return d.resultado if d.exec_()==QDialog.Accepted else None


def editar_no(parent,no,tipo):
    import copy
    d=QDialog(parent); d.setWindowTitle('Propriedades do nó');d.resize(620,760);outer=QVBoxLayout(d);scroll=QScrollArea();scroll.setWidgetResizable(True);root=QWidget();scroll.setWidget(root);outer.addWidget(scroll);v=QVBoxLayout(root);f=QFormLayout();v.addLayout(f)
    x,y=numero(no['x']),numero(no['y']); f.addRow('Coordenada x (m)',x); f.addRow('Coordenada y (m)',y)
    x.setDecimals(10);y.setDecimals(10)
    labels=['Fz (kN)','Mx (kN·m)','My (kN·m)'] if tipo=='Grelha' else ['Fx (kN)','Fy (kN)','Momento (kN·m)']
    loads=[]
    for i,label in enumerate(labels):
        w=numero((no.get('carga_pontual',[0,0,0])+[0]*3)[i]); loads.append(w); f.addRow(label,w)
    from PyQt5.QtWidgets import QCheckBox
    checks=[]
    for i,label in enumerate(['Restringir w','Restringir θx','Restringir θy'] if tipo=='Grelha' else ['Restringir u','Restringir v','Restringir θ']):
        w=QCheckBox(label); w.setChecked(bool((no.get('apoio',[0,0,0])+[0]*3)[i])); checks.append(w); f.addRow(w)
    if tipo=='Treliça': loads[2].setEnabled(False); checks[2].setEnabled(False)
    angle=numero(no.get('apoio_angulo',90),-360,360);f.addRow('Direção restringida do móvel (° de +X)',angle)
    angle.setToolTip('Ângulo da normal ao plano de rolamento. Padrão 90° = restrição vertical. Esta direção influencia o cálculo.')
    visual=[no.get('apoio_visual',0)];girar=QPushButton('Girar 90°');f.addRow(girar)
    info=QLabel();info.setWordWrap(True);v.addWidget(info)
    def orientar():
        movable=not checks[0].isChecked() and checks[1].isChecked() and tipo!='Grelha'
        angle.setEnabled(movable);angle.setVisible(movable);f.labelForField(angle).setVisible(movable)
        info.setText('Apoio móvel: o ângulo define a direção física da restrição (normal à rampa), usado no cálculo.' if movable else 'Engaste e apoio fixo: a orientação é somente visual. As restrições globais em X/Y e, no engaste, rotação, não mudam ao girar.')
        if tipo=='Grelha':info.setText('Grelha: os graus de liberdade são w, θx e θy. A orientação do símbolo é apenas visual; w atua fora do plano.')
    def girar_simbolo():
        if angle.isEnabled():angle.setValue((angle.value()+90)%360)
        else:visual[0]=(visual[0]+90)%360
    girar.clicked.connect(girar_simbolo)
    for c in checks:c.toggled.connect(orientar)
    orientar()
    molas=[]
    for i,label in enumerate(['Mola w (kN/m)','Mola θx (kN·m/rad)','Mola θy (kN·m/rad)'] if tipo=='Grelha' else ['Mola X (kN/m)','Mola Y (kN/m)','Mola θ (kN·m/rad)']):
        w=numero((no.get('mola',[0,0,0])+[0]*3)[i],0,1e15);molas.append(w);f.addRow(label,w)
        if tipo=='Treliça' and i==2:w.setEnabled(False)
    buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); v.addWidget(buttons); buttons.accepted.connect(d.accept); buttons.rejected.connect(d.reject)
    if d.exec_()==QDialog.Accepted:
        result=copy.deepcopy(no); result.update(x=x.value(),y=y.value(),carga_pontual=[w.value() for w in loads],apoio=[w.isChecked() for w in checks],mola=[w.value() for w in molas],apoio_visual=visual[0])
        if angle.isEnabled():result['apoio_angulo']=angle.value()
        else:result.pop('apoio_angulo',None)
        return result


def editar_barra(parent,barra):
    import copy
    from PyQt5.QtWidgets import QListWidget,QPushButton,QCheckBox
    result=copy.deepcopy(barra)
    d=QDialog(parent); d.setWindowTitle('Propriedades da barra'); d.resize(490,420)
    v=QVBoxLayout(d); f=QFormLayout(); v.addLayout(f)
    ea=numero(barra.get('EA',1),.00001,1e15); ei=numero(barra.get('EI',1),.00001,1e15)
    q=numero(barra.get('q',0)); f.addRow('Rigidez axial EA (kN)',ea); f.addRow('Rigidez à flexão EI (kN·m²)',ei); f.addRow('Carga uniforme local q (kN/m)',q)
    ri,rj=QCheckBox('Rótula no início'),QCheckBox('Rótula no fim'); ri.setChecked(barra.get('rotula_i',False)); rj.setChecked(barra.get('rotula_j',False)); f.addRow(ri); f.addRow(rj)
    if parent.modelo['tipo'] in ('Treliça','Grelha'):
        ri.setEnabled(False); rj.setEnabled(False)
        if parent.modelo['tipo']=='Treliça':q.setEnabled(False)
    perfil=QPushButton('Selecionar / editar perfil da seção'); v.addWidget(perfil)
    secao_label=QLabel(); secao_label.setWordWrap(True); v.addWidget(secao_label)
    def mostrar_secao():
        if result.get('secao'):
            from estrutural.core.secoes import calcular_secao
            c=result['secao']; p=calcular_secao(c['familia'],c['dimensoes'],c.get('sobrescritos'))
            secao_label.setText(c['familia']+f' · A={p["A"]:.6g} m² · Ix={p["Ix"]:.6g} m⁴ · Iy={p["Iy"]:.6g} m⁴ · J={p["J"]:.6g} m⁴')
            ea.setValue(result['EA']); ei.setValue(result['EI']); ea.setEnabled(False); ei.setEnabled(False)
    def selecionar():
        from estrutural.ui.perfis import SeletorPerfil
        from estrutural.core.secoes import aplicar_secao
        dialog=SeletorPerfil(d,result)
        if dialog.exec_(): result.update(aplicar_secao(result,dialog.resultado)); mostrar_secao()
    perfil.clicked.connect(selecionar); mostrar_secao()
    v.addWidget(QLabel('Cargas distribuídas adicionais (somadas à carga uniforme acima):'))
    lista=QListWidget(); v.addWidget(lista)
    def atualizar():
        lista.clear()
        for ch in result.get('distribuidas',[]):
            text=ch.get('descricao') or ('Fórmula avançada' if ch.get('funcao') else f'{ch.get("qa",0):g} → {ch.get("qb",ch.get("qa",0)):g}')
            lista.addItem(f'{text} kN/m | {ch.get("a",0):g} a {ch.get("b",0):g} m | {ch.get("eixo","local_y")}')
    atualizar()
    remover=QPushButton('Remover carga selecionada'); v.addWidget(remover)
    def apagar():
        i=lista.currentRow()
        if i>=0: result['distribuidas'].pop(i); atualizar()
    remover.clicked.connect(apagar)
    buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); v.addWidget(buttons); buttons.accepted.connect(d.accept); buttons.rejected.connect(d.reject)
    if d.exec_()==QDialog.Accepted:
        result.update(EA=ea.value(),EI=ei.value(),q=q.value(),rotula_i=ri.isChecked(),rotula_j=rj.isChecked()); return result
