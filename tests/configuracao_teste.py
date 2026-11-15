"""UI tests must never change the real user's saved preferences."""
from tempfile import TemporaryDirectory
import atexit
from pathlib import Path
from PyQt5.QtCore import QSettings


def editor_isolado():
    from estrutural.ui.editor import Editor
    pasta=TemporaryDirectory(prefix='ms-estruturas-teste-')
    atexit.register(pasta.cleanup)
    config=QSettings(str(Path(pasta.name)/'preferencias.ini'),QSettings.IniFormat)
    config.setValue('pasta_arquivos',pasta.name)
    editor=Editor(config=config);editor._pasta_config_teste=pasta
    return editor
