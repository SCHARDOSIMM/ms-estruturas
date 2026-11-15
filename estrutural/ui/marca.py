"""Native Arial Bold brand, without stretching or vector substitutions."""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from estrutural.ui.idioma import QLabel


class Marca(QLabel):
    def __init__(self):
        super().__init__('MS Estruturas');self.setAccessibleName('MS Estruturas')
        self.setFont(QFont('Arial',12,QFont.Bold));self.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.setStyleSheet('font-family: Arial; font-size: 16px; font-weight: 700;')
        self.setFixedSize(130,34)
