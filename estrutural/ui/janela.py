"""Layout inicial; ferramentas numéricas serão conectadas nas próximas etapas."""
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox, QSplitter,
    QTabWidget, QTableWidget, QHeaderView, QDoubleSpinBox, QScrollArea,
)
from estrutural.core.modelo import Projeto, Tipologia
from estrutural.ui import tema
from estrutural.ui.estilos import QSS_BASE


def grupo(titulo, conteudo):
    caixa = QFrame()
    caixa.setObjectName('grupoBox')
    layout = QVBoxLayout(caixa)
    layout.setContentsMargins(10, 6, 10, 10)
    layout.setSpacing(6)
    rotulo = QLabel(titulo.upper())
    rotulo.setObjectName('grupo')
    layout.addWidget(rotulo)
    layout.addWidget(conteudo) if isinstance(conteudo, QWidget) else layout.addLayout(conteudo)
    return caixa


class Canvas(QWidget):
    """Grade de referência em pixels, ainda sem edição ou escala física."""
    def __init__(self):
        super().__init__()
        self.escuro = False
        self.grade = True
        self.setMinimumSize(360, 260)

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(tema.CAMPO if self.escuro else '#ffffff'))
        if self.grade:
            p.setPen(QPen(QColor(tema.BORDA if self.escuro else '#dcdcdc'), 1))
            for x in range(0, self.width(), 25):
                for y in range(0, self.height(), 25):
                    p.drawPoint(x, y)
        p.setPen(QColor(tema.TEXTO_SUAVE if self.escuro else '#3c3c3c'))
        p.drawText(self.rect(), Qt.AlignCenter,
                   'ÁREA DE MODELAGEM\n\nProjeto vazio · edição disponível na etapa 2')
        p.end()


class JanelaPrincipal(QMainWindow):
    def __init__(self,config=None):
        super().__init__()
        self.projeto = Projeto()
        self.config = config if config is not None else QSettings('Ecoplan', 'Estrutural')
        from estrutural.ui.persistencia import carregar_preferencias
        self.preferencias_iniciais=carregar_preferencias(self.config)
        self.paleta_clara = QApplication.style().standardPalette()
        self.setWindowTitle('Estrutural  0.1.0')
        self.resize(1280, 820)
        self.setMinimumSize(1000, 680)
        raiz = QWidget()
        self.setCentralWidget(raiz)
        layout = QVBoxLayout(raiz)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        topo = QHBoxLayout()
        marca = QLabel('ESTRUTURAL')
        marca.setObjectName('marca')
        topo.addWidget(marca)
        subtitulo = QLabel('Análise de estruturas reticuladas · Etapa 1')
        subtitulo.setObjectName('sub')
        topo.addWidget(subtitulo)
        topo.addStretch()
        self.noturno = QCheckBox('Modo noturno')
        self.noturno.setChecked(self.preferencias_iniciais['escuro'])
        self.noturno.toggled.connect(self.aplicar_tema)
        topo.addWidget(self.noturno)
        layout.addLayout(topo)

        acoes = QHBoxLayout()
        calcular = QPushButton('Calcular')
        calcular.setObjectName('gerar')
        calcular.setCheckable(True)
        calcular.setChecked(True)
        calcular.clicked.connect(self.aviso_calculo)
        calcular.setToolTip('O motor de cálculo será implementado na etapa 3.')
        acoes.addWidget(calcular)
        acoes.addWidget(QLabel('Tipologia:'))
        self.tipologia = QComboBox()
        self.tipologia.addItems([t.value for t in Tipologia])
        self.tipologia.setCurrentText(self.projeto.tipologia.value)
        self.tipologia.currentTextChanged.connect(self.atualizar_tipologia)
        acoes.addWidget(self.tipologia)
        self.gdl = QLabel()
        acoes.addWidget(self.gdl)
        acoes.addStretch()
        acoes.addWidget(QLabel('Unidades: kN · m · kN·m · MPa'))
        layout.addLayout(acoes)

        divisor = QSplitter(Qt.Horizontal)
        ferramentas = QWidget()
        paleta = QVBoxLayout(ferramentas)
        paleta.setContentsMargins(0, 0, 0, 0)
        paleta.setSpacing(10)
        for titulo, nomes in [
            ('Edição', ['Selecionar', 'Mover / copiar', 'Apagar', 'Desfazer / refazer']),
            ('Geometria', ['Nó / ponto', 'Barra reta / inclinada', 'Arco']),
            ('Vínculos', ['Apoio fixo (2º gênero)', 'Apoio móvel (1º gênero)', 'Engaste', 'Mola', 'Rótula / liberações']),
            ('Carregamentos', ['Força / momento pontual', 'Distribuída uniforme', 'Triangular / trapezoidal', 'Carga inclinada', 'Recalque / temperatura']),
        ]:
            coluna = QVBoxLayout()
            for nome in nomes:
                botao = QPushButton(nome)
                botao.setEnabled(False)
                botao.setToolTip('Previsto nas próximas etapas de implementação.')
                coluna.addWidget(botao)
            paleta.addWidget(grupo(titulo, coluna))
        paleta.addStretch()
        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        rolagem.setWidget(ferramentas)
        divisor.addWidget(rolagem)

        centro = QWidget()
        coluna = QVBoxLayout(centro)
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setSpacing(10)
        opcoes = QHBoxLayout()
        grade = QCheckBox('Grade')
        grade.setChecked(True)
        self.canvas = Canvas()
        grade.toggled.connect(self.alternar_grade)
        opcoes.addWidget(grade)
        snap = QCheckBox('Snap')
        snap.setEnabled(False)
        opcoes.addWidget(snap)
        passo = QDoubleSpinBox()
        passo.setSuffix(' m')
        passo.setValue(0.5)
        passo.setEnabled(False)
        opcoes.addWidget(passo)
        opcoes.addStretch()
        opcoes.addWidget(QLabel('Zoom / pan: etapa 2'))
        coluna.addLayout(opcoes)
        coluna.addWidget(self.canvas, 1)
        abas = QTabWidget()
        for nome, cabecalhos in [
            ('Reações', ['Nó', 'Rx (kN)', 'Ry (kN)', 'M (kN·m)']),
            ('Esforços', ['Barra', 'x (m)', 'N (kN)', 'V (kN)', 'M (kN·m)', 'T (kN·m)']),
            ('Deformada', ['Nó', 'u / w (m)', 'v / θx', 'θ / θy (rad)']),
        ]:
            tabela = QTableWidget(0, len(cabecalhos))
            tabela.setHorizontalHeaderLabels(cabecalhos)
            tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            abas.addTab(tabela, nome)
        abas.insertTab(2, QLabel('Diagramas disponíveis após a implementação do motor e validação.'), 'Diagramas')
        abas.setMaximumHeight(190)
        coluna.addWidget(abas)
        divisor.addWidget(centro)

        propriedades = QWidget()
        props = QVBoxLayout(propriedades)
        props.setContentsMargins(0, 0, 0, 0)
        texto = QLabel('Nenhum elemento selecionado.\n\nCoordenadas, material, seção e cargas\nserão editados neste painel.')
        texto.setWordWrap(True)
        props.addWidget(grupo('Propriedades', texto))
        resumo = QLabel('0 nós · 0 barras\n\nModelo ainda sem vínculos ou cargas.\n\nNenhuma análise foi realizada.')
        resumo.setWordWrap(True)
        props.addWidget(grupo('Modelo', resumo))
        props.addStretch()
        divisor.addWidget(propriedades)
        divisor.setSizes([220, 750, 250])
        divisor.setStretchFactor(1, 1)
        layout.addWidget(divisor, 1)
        self.status = QLabel('Layout inicial pronto. As ferramentas de modelagem serão habilitadas na etapa 2.')
        self.status.setObjectName('status')
        layout.addWidget(grupo('Estado do projeto', self.status))
        self.atualizar_tipologia(self.tipologia.currentText())
        self.aplicar_tema(self.noturno.isChecked())

    def aviso_calculo(self):
        self.status.setText('Cálculo indisponível: motor previsto na etapa 3. Nenhum resultado foi gerado.')

    def atualizar_tipologia(self, nome):
        self.projeto.tipologia = Tipologia(nome)
        self.gdl.setText('GDL: ' + ', '.join(self.projeto.tipologia.graus_de_liberdade))

    def alternar_grade(self, ativa):
        self.canvas.grade = ativa
        self.canvas.update()

    def aplicar_tema(self, escuro):
        app = QApplication.instance()
        app.setPalette(tema.paleta_escura() if escuro else self.paleta_clara)
        # Abas não constam no guia: reutilizam tokens de painel, seleção e borda.
        fundo = tema.PAINEL if escuro else '#f0f0f0'
        texto = tema.TEXTO if escuro else '#000000'
        borda = tema.BORDA if escuro else '#dcdcdc'
        selecao = tema.SELECAO if escuro else '#cce4f7'
        qss_app = f'''
        QTabWidget::pane {{ border: 1px solid {borda}; }}
        QTabBar::tab {{ background: {fundo}; color: {texto};
                        border: 1px solid {borda}; padding: 6px 10px; }}
        QTabBar::tab:selected {{ background: {selecao}; }}
        QTabBar::tab:hover {{ border-color: {tema.DESTAQUE if escuro else '#0078d7'}; }}
        '''
        app.setStyleSheet(QSS_BASE + qss_app + (tema.QSS_ESCURO if escuro else ''))
        self.canvas.escuro = escuro
        self.canvas.update()
        if not getattr(self,'_aplicando_preferencias',False):self.config.setValue('modo_noturno', escuro)
