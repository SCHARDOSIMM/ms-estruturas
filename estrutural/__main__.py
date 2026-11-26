"""Inicialização da aplicação desktop."""
import ctypes
import sys

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from estrutural.ui.editor import Editor


def main():
    if sys.platform == 'win32':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('MS.Estruturas')
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName('MS Estruturas');app.setApplicationVersion('1.0.5')
    app.setApplicationDisplayName('MS Estruturas')
    app.setFont(QFont('Segoe UI', 9))
    if len(sys.argv)==3 and sys.argv[1]=='--verificar-instalacao':
        from estrutural.verificacao import verificar_instalacao
        return verificar_instalacao(sys.argv[2],app)
    janela = Editor()
    app.setWindowIcon(janela.logo)
    janela.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
