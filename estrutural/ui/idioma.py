"""Translation at the presentation boundary; saved model identifiers stay stable."""
import re
from PyQt5.QtCore import QObject, QEvent, QLocale, QTranslator, QLibraryInfo, pyqtSignal, Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel as LabelBase, QAbstractButton,
    QComboBox as ComboBase, QLineEdit, QGroupBox, QTableWidget, QTreeWidget,
    QListWidget, QFileDialog as FileBase, QPushButton as ButtonBase, QCheckBox as CheckBase)
from PyQt5.QtWidgets import QInputDialog as InputBase
from PyQt5.QtWidgets import QDialogButtonBox as BoxBase
from estrutural.core.idiomas import traduzir

_idioma = 'pt_BR'
_filtro = None


def tr(texto):
    return traduzir(str(texto), _idioma)


class TextoTraduzido:
    """Translate live labels at assignment, without polling the widget tree."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.setText(super().text())

    def setText(self,texto):
        self.setProperty('_fonte_texto',texto)
        value=tr(texto);self.setProperty('_trad_texto',value)
        super().setText(value)

    def texto_bruto(self,texto):
        super().setText(texto)


class QLabel(TextoTraduzido,LabelBase): pass
class QPushButton(TextoTraduzido,ButtonBase): pass
class QCheckBox(TextoTraduzido,CheckBase): pass


class QDialogButtonBox(BoxBase):
    def changeEvent(self,event):
        fontes=[(b,b.property('_fonte_texto') or b.text()) for b in self.buttons()]
        super().changeEvent(event)
        if event.type()==QEvent.LanguageChange:
            # Qt retranslates standard buttons on language changes; preserve
            # application-specific action labels such as Apply load/section.
            for b,source in fontes:
                b.setText(tr(source));b.setProperty('_fonte_texto',source);b.setProperty('_trad_texto',tr(source))


class QComboBox(ComboBase):
    """Translated display with Portuguese semantic values and stable signals."""
    textoAlterado = pyqtSignal(str)

    @property
    def currentTextChanged(self):
        return self.textoAlterado

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currentIndexChanged.connect(lambda _: self.textoAlterado.emit(self.currentText()))

    def addItem(self, texto, userData=None):
        super().addItem(tr(texto), userData)
        self.setItemData(self.count()-1, texto, Qt.UserRole+1)

    def addItems(self, textos):
        for texto in textos:
            self.addItem(texto)

    def currentText(self):
        return self.itemData(self.currentIndex(), Qt.UserRole+1) or super().currentText()

    def setCurrentText(self, texto):
        for i in range(self.count()):
            if self.itemData(i, Qt.UserRole+1) == texto:
                self.setCurrentIndex(i)
                return
        super().setCurrentText(texto)

    def retraduzir(self):
        for i in range(self.count()):
            source = self.itemData(i, Qt.UserRole+1)
            if source is not None and self.itemText(i) != tr(source):
                self.setItemText(i, tr(source))


def _campo(obj, getter, setter, chave):
    atual = getter()
    anterior = obj.property('_trad_'+chave)
    source = obj.property('_fonte_'+chave) if atual == anterior else atual
    if source is None:
        source = atual
    novo = tr(source)
    if obj.property('_fonte_'+chave) != source: obj.setProperty('_fonte_'+chave, source)
    if anterior != novo: obj.setProperty('_trad_'+chave, novo)
    if atual != novo:
        setter(novo)


def atualizar(raiz):
    """Reversible translation, including windows already open during a switch.

    Editable text and project data are deliberately excluded: language changes
    must never rewrite a user's project name, formula or material name.
    """
    locale = QLocale('en_US' if _idioma == 'en_US' else 'pt_BR')
    for w in [raiz] + raiz.findChildren(QWidget):
        if w.locale() != locale:
            w.setLocale(locale)
        for key, get, put in [('titulo', w.windowTitle, w.setWindowTitle),
                             ('dica', w.toolTip, w.setToolTip),
                             ('acesso', w.accessibleName, w.setAccessibleName),
                             ('descricao', w.accessibleDescription, w.setAccessibleDescription)]:
            _campo(w, get, put, key)
        if isinstance(w, (LabelBase, QAbstractButton)):
            _campo(w, w.text, getattr(w,'texto_bruto',w.setText), 'texto')
        if isinstance(w, QGroupBox):
            _campo(w, w.title, w.setTitle, 'grupo')
        if isinstance(w, QLineEdit):
            _campo(w, w.placeholderText, w.setPlaceholderText, 'placeholder')
        if isinstance(w, QComboBox):
            w.retraduzir()
        if isinstance(w, QTableWidget):
            blocked=w.blockSignals(True)
            for j in range(w.columnCount()):
                item = w.horizontalHeaderItem(j)
                if item: _item(item, 0)
            for i in range(w.rowCount()):
                for j in range(w.columnCount()):
                    item = w.item(i, j)
                    if item: _item(item, 0)
            w.blockSignals(blocked)
        if isinstance(w, QListWidget):
            for i in range(w.count()): _item(w.item(i), 0)
        if isinstance(w, QTreeWidget):
            blocked=w.blockSignals(True)
            def walk(item):
                for col in range(w.columnCount()): _item(item, col, True)
                for i in range(item.childCount()): walk(item.child(i))
            for i in range(w.topLevelItemCount()): walk(w.topLevelItem(i))
            w.blockSignals(blocked)


def _item(item, col, tree=False):
    for role in (Qt.DisplayRole, Qt.ToolTipRole):
        current = item.data(col, role) if tree else item.data(role)
        if not isinstance(current, str): continue
        srcrole = Qt.UserRole+100+role
        previousrole = Qt.UserRole+200+role
        previous = item.data(col, previousrole) if tree else item.data(previousrole)
        source = (item.data(col, srcrole) if tree else item.data(srcrole)) if previous == current else current
        value = tr(source)
        if value == current and previous == value: continue
        if value == current and previous is None: continue
        if tree:
            item.setData(col, srcrole, source); item.setData(col, previousrole, value)
            if current != value: item.setData(col, role, value)
        else:
            item.setData(srcrole, source); item.setData(previousrole, value)
            if current != value: item.setData(role, value)


class TradutorQt(QTranslator):
    def translate(self, context, sourceText, disambiguation=None, n=-1):
        # Translate Qt's own buttons and non-native file dialogs as well.
        result = tr(sourceText)
        if _idioma == 'pt_BR':
            result = {'Cancel':'Cancelar', '&Cancel':'&Cancelar', 'Close':'Fechar',
                      'Open':'Abrir', '&Open':'&Abrir', 'Save':'Salvar', '&Save':'&Salvar',
                      'OK':'OK', 'Yes':'Sim', 'No':'Não'}.get(sourceText, sourceText)
        # A Python empty string becomes a non-null empty QString: Qt accepts it
        # as a translation and renders standard buttons (notably OK) blank.
        if result == sourceText and _idioma == 'pt_BR' and hasattr(self,'fallback'):
            return self.fallback.translate(context,sourceText,disambiguation,n) or sourceText
        return result


class FiltroIdioma(QObject):
    def __init__(self, app):
        super().__init__(app); self.busy = False
        self.qt_pt=QTranslator(self)
        self.qt_pt.load('qt_pt',QLibraryInfo.location(QLibraryInfo.TranslationsPath))
        self.pt_instalado=False
        self.qt = TradutorQt(self);self.qt.fallback=self.qt_pt; app.installTranslator(self.qt)

    def eventFilter(self, obj, event):
        if not self.busy and isinstance(obj, QWidget) and obj.isWindow() and event.type()==QEvent.Show:
            self.busy = True
            try: atualizar(obj.window())
            finally: self.busy = False
        return False


def definir(idioma):
    global _idioma, _filtro
    _idioma = 'en_US' if idioma == 'en_US' else 'pt_BR'
    app = QApplication.instance()
    QLocale.setDefault(QLocale(_idioma))
    if app:
        if _filtro is None:
            _filtro = FiltroIdioma(app); app.installEventFilter(_filtro)
        if _idioma=='pt_BR' and not _filtro.pt_instalado:
            app.installTranslator(_filtro.qt_pt);_filtro.pt_instalado=True
            app.removeTranslator(_filtro.qt);app.installTranslator(_filtro.qt)
        elif _idioma=='en_US' and _filtro.pt_instalado:
            app.removeTranslator(_filtro.qt_pt);_filtro.pt_instalado=False
        _filtro.busy = True
        try:
            for w in app.topLevelWidgets(): atualizar(w)
        finally: _filtro.busy = False


class QFileDialog:
    """Localize native-independent dialogs while returning stable filter IDs."""
    @staticmethod
    def _abrir(method, parent, title, directory='', filters=''):
        from estrutural.ui.arquivos import pasta_inicial,lembrar_pasta
        originais = filters.split(';;'); exibidos = [tr(f) for f in originais]
        if not directory:directory=pasta_inicial(parent)
        path, selected = method(parent, tr(title), directory, ';;'.join(exibidos),
                                options=FileBase.DontUseNativeDialog)
        lembrar_pasta(parent,path)
        return path, originais[exibidos.index(selected)] if selected in exibidos else selected

    @staticmethod
    def getOpenFileName(*args): return QFileDialog._abrir(FileBase.getOpenFileName, *args)

    @staticmethod
    def getSaveFileName(parent,title,directory='',filters=''):
        from estrutural.ui.arquivos import DialogoSalvar
        from estrutural.ui.arquivos import pasta_inicial,lembrar_pasta
        originais=filters.split(';;');exibidos=[tr(f) for f in originais]
        if not directory:directory=pasta_inicial(parent,salvar=True)
        dialog=DialogoSalvar(parent,tr(title),directory,exibidos)
        try:
            if dialog.exec_()!=dialog.Accepted:return '',''
            files=dialog.selectedFiles();selected=dialog.selectedNameFilter()
            path=files[0] if files else '';lembrar_pasta(parent,path)
            return path,originais[exibidos.index(selected)] if selected in exibidos else selected
        finally:dialog.deleteLater()


class QInputDialog:
    @staticmethod
    def getText(parent,title,label,*args,**kwargs):
        return InputBase.getText(parent,tr(title),tr(label),*args,**kwargs)

    @staticmethod
    def getItem(parent,title,label,items,*args,**kwargs):
        shown=[tr(s) for s in items]
        value,ok=InputBase.getItem(parent,tr(title),tr(label),shown,*args,**kwargs)
        return (items[shown.index(value)] if value in shown else value),ok
