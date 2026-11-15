"""Seleção de material e inspeção de seus parâmetros físicos."""
from PyQt5.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QComboBox,QLineEdit,QCheckBox,QLabel,QDialogButtonBox,QMessageBox
from estrutural.core.materiais import PRESETS,validar_material
from estrutural.ui.formularios import numero
from estrutural.ui.idioma import QComboBox, QDialogButtonBox, QLabel, QPushButton, QCheckBox, tr


class SeletorMaterial(QDialog):
    def __init__(self,parent,barra=None):
        super().__init__(parent);self.setWindowTitle('Material e propriedades físicas');self.resize(570,510);self.resultado=None
        v=QVBoxLayout(self);self.preset=QComboBox();self.preset.addItems(PRESETS);v.addWidget(self.preset)
        f=QFormLayout();v.addLayout(f);self.nome=QLineEdit();f.addRow('Nome do material',self.nome);self.campos={}
        for key,label,value,lo,hi in [('E_MPa','Módulo de elasticidade E (MPa)',210000,.001,1e9),('G_MPa','Módulo de cisalhamento G (MPa)',80769,.001,1e9),('nu','Coeficiente de Poisson ν',.3,-.99,.49999),('gamma','Peso específico γ (kN/m³)',78.5,0,1e5),('alpha','Dilatação térmica α (1/°C)',1.2e-5,-1,1)]:
            w=numero(value,lo,hi);w.setDecimals(9 if key=='alpha' else 5);self.campos[key]=w;f.addRow(label,w)
        self.vincular=QCheckBox('Calcular G = E / [2(1 + ν)]');self.vincular.setChecked(True);v.addWidget(self.vincular)
        self.info=QLabel('E e G, junto da seção, definem EA, EI e GJ. α é usado na temperatura uniforme.\nγ é armazenado; o programa não aplica peso próprio automaticamente.\nPresets são referências didáticas editáveis, não valores normativos por classe.\nMadeira: modelo isotrópico equivalente; ortotropia não é considerada.');self.info.setWordWrap(True);v.addWidget(self.info)
        self.formula=QLabel();self.formula.setObjectName('status');v.addWidget(self.formula)
        for key in ('E_MPa','nu'):self.campos[key].valueChanged.connect(self.atualizar)
        self.vincular.toggled.connect(self.atualizar);self.preset.currentTextChanged.connect(self.carregar_preset)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);buttons.button(QDialogButtonBox.Ok).setText('Aplicar material');buttons.button(QDialogButtonBox.Cancel).setText('Cancelar');buttons.accepted.connect(self.aplicar);buttons.rejected.connect(self.reject);v.addWidget(buttons)
        m=(barra or {}).get('material')
        if m:
            self.preset.blockSignals(True);self.preset.setCurrentText(m['nome'] if m['nome'] in PRESETS else 'Personalizado');self.preset.blockSignals(False)
            self.nome.setText(m['nome']);self.vincular.setChecked(m.get('vincular_G',False))
            for k,w in self.campos.items():w.setValue(m[k])
        else:self.preset.setCurrentText('Aço — referência didática')
        self.atualizar()
    def carregar_preset(self,name):
        self.nome.setText(tr(name))
        for k,val in PRESETS[name].items():self.campos[k].setValue(val)
        self.vincular.setChecked(True);self.atualizar()
    def atualizar(self):
        self.campos['G_MPa'].setEnabled(not self.vincular.isChecked())
        if self.vincular.isChecked():self.campos['G_MPa'].setValue(self.campos['E_MPa'].value()/(2*(1+self.campos['nu'].value())))
        self.formula.setText('Unidades internas: E/G × 1000 → kN/m². Sem seção atribuída, EA/EI/GJ existentes são mantidos.');self.formula.setWordWrap(True)
    def aplicar(self):
        try:
            m={k:w.value() for k,w in self.campos.items()};m.update(nome=self.nome.text(),vincular_G=self.vincular.isChecked());validar_material(m);self.resultado=m;self.accept()
        except ValueError as e:QMessageBox.warning(self,'Verifique o material',str(e))
