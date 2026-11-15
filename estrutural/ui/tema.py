# -*- coding: utf-8 -*-
"""
tema.py
-------
Modo noturno dos apps Ecoplan (no estilo do VS Code: fundo azul-escuro,
destaque em azul).

O tema claro continua sendo o QSS base do app. O escuro é aplicado POR CIMA
dele: as regras daqui vêm depois e, com a mesma especificidade, prevalecem.
"""

from PyQt5.QtGui import QPalette, QColor

# --------------------------------------------------------------- paleta
FUNDO = "#1b1f27"        # janela
PAINEL = "#222731"       # blocos (painel, rodapé, eixo)
CAMPO = "#14171d"        # caixas de texto, tabelas, fundo da foto
BOTAO = "#2a303c"
BOTAO_HOVER = "#333a48"
BORDA = "#353c4a"
BORDA_BOTAO = "#3c4453"
TEXTO = "#d4d8de"
TEXTO_FORTE = "#ffffff"
TEXTO_SUAVE = "#8b93a1"
TEXTO_INFO = "#aab1bd"
DESTAQUE = "#007acc"     # azul do VS Code
DESTAQUE_BORDA = "#0062a3"
DESTAQUE_TEXTO = "#4fa3ff"
SELECAO = "#094771"

# cores que o código pinta à mão (visor, tabelas)
CORES = {
    "claro": {"texto": "#000000", "texto_suave": "#c9d3ff",
              "foto_fundo": "#0b1f78", "foto_borda": "#adadad"},
    "escuro": {"texto": TEXTO, "texto_suave": TEXTO_SUAVE,
               "foto_fundo": CAMPO, "foto_borda": BORDA},
}

QSS_ESCURO = """
QMainWindow, QWidget, QDialog { background: %(FUNDO)s; color: %(TEXTO)s; }
QLabel { color: %(TEXTO)s; }
#painel QLabel, #rodape QLabel, #eixoBox QLabel { background: transparent; }

#kmLabel { background: #252b36; color: %(TEXTO_FORTE)s;
           border: 1px solid %(BORDA)s; }
#fotoBox { background: %(CAMPO)s; border: 1px solid %(BORDA)s; }
#eixoBox, #painel, #rodape { background: %(PAINEL)s;
                             border: 1px solid %(BORDA)s; }
#grupoBox { background: transparent; border: 1px solid %(BORDA)s; }
#grupoBox QLabel { background: transparent; }
QPushButton:pressed { background: #3a4252; }
QPlainTextEdit:focus, QLineEdit:focus { border-color: %(DESTAQUE)s; }
QComboBox:hover { border-color: %(DESTAQUE)s; }

QLabel#campo  { color: #c5cad3; }
QLabel#grupo  { color: %(TEXTO_SUAVE)s; }
QLabel#info   { color: %(TEXTO_INFO)s; }
QLabel#status { color: %(DESTAQUE_TEXTO)s; }

QPushButton {
    background: %(BOTAO)s; border: 1px solid %(BORDA_BOTAO)s;
    color: %(TEXTO)s;
}
QPushButton:hover { background: %(BOTAO_HOVER)s; }
QPushButton:checked {
    background: %(DESTAQUE)s; border: 1px solid %(DESTAQUE_BORDA)s;
    color: #ffffff;
}
QPushButton:disabled { color: #5d6573; background: #232831;
                       border-color: #2f3541; }

QPushButton#setaFoto { background: transparent; border: none;
                       color: %(TEXTO)s; }
QPushButton#setaFoto:hover { background: #2f3644; }
QPushButton#setaFoto:pressed { background: #3a4252; }
QPushButton#setaFoto:disabled { color: #4a515e; background: transparent; }

QPlainTextEdit, QLineEdit, QSpinBox, QDoubleSpinBox {
    background: %(CAMPO)s; border: 1px solid %(BORDA_BOTAO)s;
    color: #e3e6ea; selection-background-color: #264f78;
}
QComboBox { background: %(BOTAO)s; border: 1px solid %(BORDA_BOTAO)s;
            color: %(TEXTO)s; }
QComboBox QAbstractItemView { background: %(PAINEL)s; color: %(TEXTO)s;
                              selection-background-color: %(SELECAO)s; }

QTableWidget, QTreeWidget {
    background: %(CAMPO)s; alternate-background-color: %(FUNDO)s;
    color: %(TEXTO)s; gridline-color: #2f3541;
    border: 1px solid %(BORDA)s;
    selection-background-color: %(SELECAO)s; selection-color: #ffffff;
}
QHeaderView::section {
    background: #252b36; color: %(TEXTO_INFO)s; border: 0;
    border-bottom: 1px solid %(BORDA)s; padding: 4px 6px;
}
QTableCornerButton::section { background: #252b36; border: 0; }

QMenuBar { background: %(FUNDO)s; color: %(TEXTO)s; }
QMenuBar::item { background: transparent; padding: 4px 10px; }
QMenuBar::item:selected { background: #2f3644; }
QMenu { background: %(PAINEL)s; color: %(TEXTO)s;
        border: 1px solid %(BORDA)s; }
QMenu::item { padding: 5px 26px 5px 24px; }
QMenu::item:selected { background: %(SELECAO)s; }
QMenu::item:disabled { color: #5d6573; }
QMenu::separator { height: 1px; background: %(BORDA)s; margin: 4px 8px; }

QToolTip { background: #252b36; color: #e3e6ea;
           border: 1px solid %(BORDA_BOTAO)s; }

QSplitter::handle { background: %(FUNDO)s; }
QSplitter::handle:hover { background: %(DESTAQUE)s; }

QScrollBar:vertical { background: %(FUNDO)s; width: 12px; margin: 0; }
QScrollBar::handle:vertical { background: %(BORDA_BOTAO)s; min-height: 24px;
                              border-radius: 4px; margin: 2px; }
QScrollBar:horizontal { background: %(FUNDO)s; height: 12px; margin: 0; }
QScrollBar::handle:horizontal { background: %(BORDA_BOTAO)s; min-width: 24px;
                                border-radius: 4px; margin: 2px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: none; }

QProgressBar { background: %(CAMPO)s; border: 1px solid %(BORDA)s;
               color: %(TEXTO)s; }
QProgressBar::chunk { background: %(DESTAQUE)s; }
""" % globals()

# diálogo com lista/árvore (stylesheet próprio)
QSS_PASTAS_ESCURO = """
QDialog { background: %(FUNDO)s; }
QLabel#tituloDlg { color: %(TEXTO_FORTE)s; }
QLabel#subDlg, QLabel#contaDlg { color: %(TEXTO_SUAVE)s; }
QTreeWidget { background: %(CAMPO)s; border: 1px solid %(BORDA)s;
              color: %(TEXTO)s; alternate-background-color: %(FUNDO)s; }
QTreeWidget::item:selected { background: %(SELECAO)s; color: #ffffff; }
QHeaderView::section { background: #252b36; color: %(TEXTO_INFO)s;
                       border-bottom: 1px solid %(BORDA)s; }
""" % globals()

# tela inicial (escolha do módulo, cartões)
QSS_INICIO_ESCURO = """
QDialog { background: %(FUNDO)s; }
QLabel#marca { color: %(TEXTO_FORTE)s; }
QLabel#sub   { color: %(TEXTO_SUAVE)s; }
QFrame#cartao { background: %(PAINEL)s; border: 1px solid %(BORDA)s; }
QFrame#cartao:hover { border: 1px solid %(DESTAQUE)s; }
QLabel#tituloMod { color: %(TEXTO_FORTE)s; }
QLabel#descMod   { color: %(TEXTO_INFO)s; }
QPushButton#abrir { background: %(DESTAQUE)s; border-color: %(DESTAQUE_BORDA)s; }
QPushButton#abrir:hover { background: #1188dd; }
""" % globals()

# valores medidos / passos de um assistente
QSS_EXTRA_ESCURO = """
QLabel#medida { color: %(DESTAQUE_TEXTO)s; }
QLabel#passo  { color: %(TEXTO_SUAVE)s; }
QLabel#passo[ativo="sim"] { color: %(DESTAQUE_TEXTO)s; }
""" % globals()


def paleta_escura():
    """Paleta para o que o stylesheet não alcança (caixas de seleção etc.)."""
    p = QPalette()
    p.setColor(QPalette.Window, QColor(FUNDO))
    p.setColor(QPalette.WindowText, QColor(TEXTO))
    p.setColor(QPalette.Base, QColor(CAMPO))
    p.setColor(QPalette.AlternateBase, QColor(FUNDO))
    p.setColor(QPalette.ToolTipBase, QColor("#252b36"))
    p.setColor(QPalette.ToolTipText, QColor(TEXTO))
    p.setColor(QPalette.Text, QColor(TEXTO))
    p.setColor(QPalette.Button, QColor(BOTAO))
    p.setColor(QPalette.ButtonText, QColor(TEXTO))
    p.setColor(QPalette.BrightText, QColor("#ff5555"))
    p.setColor(QPalette.Highlight, QColor(SELECAO))
    p.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    p.setColor(QPalette.Link, QColor(DESTAQUE_TEXTO))
    p.setColor(QPalette.Disabled, QPalette.Text, QColor("#5d6573"))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#5d6573"))
    p.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#5d6573"))
    return p


def modo_noturno_salvo(app="CadastroDefeitos"):
    """Preferência guardada (claro/escuro)."""
    try:
        from PyQt5.QtCore import QSettings
        cfg = QSettings("Ecoplan", app)
        return cfg.value("modo_noturno", False, type=bool)
    except Exception:
        return False
