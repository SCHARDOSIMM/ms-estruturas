"""Preferências comuns, com acesso a JSON explicitamente avançado e recolhido."""
from PyQt5.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QLineEdit,QComboBox,QSpinBox,QCheckBox,QPushButton,QWidget,QDialogButtonBox,QLabel
from estrutural.ui.formularios import numero
from estrutural.core.idiomas import IDIOMAS
from estrutural.ui.idioma import QComboBox, QDialogButtonBox, QLabel, QPushButton, QCheckBox, tr


class Preferencias(QDialog):
    def __init__(self,parent):
        super().__init__(parent);self.setWindowTitle('Configurações');self.resize(590,620);self.resultado=None
        v=QVBoxLayout(self);f=QFormLayout();v.addLayout(f);op=parent.preferencias
        self.idioma=QComboBox();self.idioma.addItems(['Português (Brasil)','English','Français']);self.idioma.setCurrentIndex(IDIOMAS.index(op.get('idioma','pt_BR')));f.addRow('Idioma',self.idioma)
        self.nome=QLineEdit(parent.modelo.get('nome') or tr(parent.modelo.get('exemplo',{}).get('nome') or op['nome_projeto']));f.addRow('Nome do projeto',self.nome)
        self.forca=QComboBox();self.forca.addItems(['kN','N']);self.forca.setCurrentText(op['forca']);f.addRow('Forças e momentos nos resultados',self.forca)
        self.desloc=QComboBox();self.desloc.addItems(['mm','cm','m']);self.desloc.setCurrentText(op['deslocamento']);f.addRow('Deslocamentos nos resultados',self.desloc)
        self.decimais=QSpinBox();self.decimais.setRange(0,10);self.decimais.setValue(op['decimais']);f.addRow('Casas decimais',self.decimais)
        self.tol=numero(op['tolerancia_zero'],0,1e3);self.tol.setDecimals(10);f.addRow('Zero de esforços/reação (kN, kN·m)',self.tol)
        self.rel=numero(op['relativo_desloc'],0,.1);self.rel.setDecimals(12);self.rel.setValue(op['relativo_desloc']);f.addRow('Zero relativo dos deslocamentos',self.rel)
        self.grade=QCheckBox('Exibir grade');self.grade.setChecked(parent.canvas.grade);f.addRow(self.grade)
        self.snap=QCheckBox('Capturar pontos na grade (snap)');self.snap.setChecked(parent.snap.isChecked());f.addRow(self.snap)
        self.passo=numero(parent.passo.value(),.01,100);f.addRow('Passo da grade (m)',self.passo)
        self.escala=numero(op['escala_deformada'],.01,1e12);f.addRow('Amplificação da deformada (×)',self.escala)
        self.valores=QCheckBox('Mostrar valores nos diagramas');self.valores.setChecked(op['mostrar_valores']);f.addRow(self.valores)
        self.escuro=QCheckBox('Modo noturno');self.escuro.setChecked(parent.noturno.isChecked());f.addRow(self.escuro)
        note=QLabel('Geometria e entrada de coordenadas permanecem em metros. As unidades acima são de apresentação; não alteram o modelo ou a precisão do cálculo.');note.setWordWrap(True);v.addWidget(note)
        self.avancado=QPushButton('Avançado');self.avancado.setCheckable(True);v.addWidget(self.avancado)
        panel=QWidget();pv=QVBoxLayout(panel);pv.addWidget(QLabel('Editor de dados para diagnóstico. Use somente se necessário.'))
        json_btn=QPushButton('Abrir editor JSON do projeto');json_btn.clicked.connect(parent.editar_modelo);pv.addWidget(json_btn);panel.hide();v.addWidget(panel);self.avancado.toggled.connect(panel.setVisible)
        b=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);b.button(QDialogButtonBox.Ok).setText('Aplicar preferências');b.button(QDialogButtonBox.Cancel).setText('Cancelar');v.addWidget(b);b.accepted.connect(self.aplicar);b.rejected.connect(self.reject)
    def aplicar(self):
        self.resultado=dict(nome_projeto=self.nome.text().strip() or 'Sem título',forca=self.forca.currentText(),deslocamento=self.desloc.currentText(),decimais=self.decimais.value(),tolerancia_zero=self.tol.value(),relativo_desloc=self.rel.value(),grade=self.grade.isChecked(),snap=self.snap.isChecked(),passo=self.passo.value(),escala_deformada=self.escala.value(),mostrar_valores=self.valores.isChecked(),escuro=self.escuro.isChecked(),idioma=IDIOMAS[self.idioma.currentIndex()],entrada_xy=self.parentWidget().xy_toggle.isChecked());self.accept()
