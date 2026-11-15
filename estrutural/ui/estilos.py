QSS_BASE = """
QMainWindow, QWidget { background: #f0f0f0; }
QLabel { color: #000000; }

QMenuBar { background: #ffffff; color: #000000; border-bottom: 1px solid #e5e5e5; }
QMenuBar::item { background: transparent; padding: 3px 8px; }
QMenuBar::item:selected { background: #e5f1fb; }
QMenu { background: #f9f9f9; color: #000000; border: 1px solid #cccccc; }
QMenu::item { padding: 4px 26px 4px 24px; }
QMenu::item:selected { background: #cce8ff; color: #000000; }
QMenu::item:disabled { color: #a0a0a0; }
QMenu::separator { height: 1px; background: #d7d7d7; margin: 3px 6px; }

#kmLabel { background: #ffffff; color: #000000; font-size: 34px; font-weight: 700;
           letter-spacing: 3px; padding: 4px 18px; border: 1px solid #adadad; border-radius: 0; }
#fotoBox { background: #0b1f78; border: 1px solid #adadad; }
#eixoBox, #painel, #rodape { background: #f0f0f0; border: 1px solid #dcdcdc; border-radius: 0; }
#grupoBox { background: transparent; border: 1px solid #dcdcdc; border-radius: 0; }
#painel QLabel, #rodape QLabel, #eixoBox QLabel, #grupoBox QLabel { background: transparent; }

QLabel#campo  { font-weight: 700; font-size: 12px; color: #000000; }
QLabel#grupo  { font-weight: 700; font-size: 11px; color: #3c3c3c; }
QLabel#info   { color: #1e1e1e; font-size: 14px; }
QLabel#status { color: #0050a0; font-size: 13px; }
QLabel#marca  { font-size: 18px; font-weight: 700; }
QLabel#sub    { font-size: 12px; }

QPushButton { background: #fdfdfd; border: 1px solid #adadad; border-radius: 2px;
              padding: 6px 10px; font-size: 12px; color: #000000; }
QPushButton:hover   { background: #e5f1fb; border-color: #0078d7; }
QPushButton:pressed { background: #cce4f7; border-color: #005499; }
QPushButton:checked { background: #0078d7; border: 1px solid #005499; color: #ffffff; font-weight: 700; }
QPushButton:disabled { color: #a0a0a0; background: #f4f4f4; border-color: #cccccc; }
QPushButton#nav   { font-size: 14px; font-weight: 700; padding: 6px 20px; }
QPushButton#gerar { font-size: 14px; font-weight: 700; padding: 8px 24px; }

QPushButton#setaFoto { background: transparent; border: none; color: #111315;
                       font-size: 21px; font-weight: 700; padding: 0; }
QPushButton#setaFoto:hover { background: #e5f1fb; border-radius: 2px; }
QPushButton#setaFoto:pressed { background: #cce4f7; }
QPushButton#setaFoto:disabled { color: #bcc1c6; background: transparent; }

QPlainTextEdit, QLineEdit { background: #ffffff; border: 1px solid #a0a0a0; border-radius: 0;
                            padding: 4px; font-size: 12px; }
QPlainTextEdit:focus, QLineEdit:focus { border-color: #0078d7; }
QComboBox { background: #fdfdfd; border: 1px solid #adadad; padding: 3px 6px; }
QComboBox:hover { border-color: #0078d7; }

QSplitter::handle { background: #f0f0f0; }
QSplitter::handle:hover { background: #cce4f7; }
QTableWidget { background: #ffffff; gridline-color: #e0e0e0; border: 1px solid #a0a0a0; }

QCheckBox { spacing: 8px; font-size: 12px; }
QProgressBar { min-height: 8px; max-height: 8px; }
"""
