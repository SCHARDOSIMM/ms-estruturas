"""Saving names and overwrite checks must use the final selected extension."""
import re
from PyQt5.QtWidgets import QFileDialog,QLineEdit,QMessageBox
from PyQt5.QtCore import QStandardPaths


def pasta_inicial(parent,salvar=False):
    from pathlib import Path
    config=getattr(parent,'config',None)
    anterior=config.value('pasta_arquivos','') if config is not None else ''
    if anterior and Path(anterior).is_dir():return anterior
    documentos=Path(QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) or str(Path.home()))
    pasta=documentos/'MS Estruturas'
    if salvar:
        try:pasta.mkdir(parents=True,exist_ok=True)
        except OSError:return str(documentos)
    return str(pasta if pasta.is_dir() else documentos)


def lembrar_pasta(parent,path):
    from pathlib import Path
    config=getattr(parent,'config',None)
    if config is not None and path:
        config.setValue('pasta_arquivos',str(Path(path).parent));config.sync()


def nome_com_extensao(path,filtro):
    if not path:return path
    match=re.search(r'\(\*\.([a-zA-Z0-9]+)\)',filtro)
    if not match:return path
    extensao='.'+match.group(1).lower()
    nome=path.rstrip(' .')
    return nome if nome.lower().endswith(extensao) else nome+extensao


class DialogoSalvar(QFileDialog):
    def __init__(self,parent,title,directory,filters):
        super().__init__(parent,title,directory)
        self.setOption(QFileDialog.DontUseNativeDialog,True)
        self.setOption(QFileDialog.DontConfirmOverwrite,True)
        self.setAcceptMode(QFileDialog.AcceptSave)
        self.setFileMode(QFileDialog.AnyFile)
        self.setNameFilters(filters)

    def accept(self):
        files=self.selectedFiles()
        if files:
            from pathlib import Path
            if Path(files[0]).is_dir():
                # Clicking a folder or leaving the filename empty must retain
                # QFileDialog's directory-navigation behavior.
                super().accept();return
            original=files[0];destino=nome_com_extensao(original,self.selectedNameFilter())
            if Path(destino).is_file():
                from estrutural.ui.idioma import tr
                resposta=QMessageBox.question(self,tr('Substituir arquivo?'),tr('Já existe um arquivo com este nome:')+'\n'+Path(destino).name+'\n\n'+tr('Deseja substituí-lo?'),QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
                if resposta!=QMessageBox.Yes:return
            if destino!=original:
                # selectFile alone does not reliably update the filename edit
                # once the non-native Qt dialog is visible. Set the actual edit
                # before Qt checks existence and asks about overwriting.
                campo=self.findChild(QLineEdit,'fileNameEdit')
                if campo is not None:campo.setText(Path(destino).name)
                else:self.selectFile(destino)
        super().accept()
