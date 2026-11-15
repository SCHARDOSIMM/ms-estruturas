"""Copy installed dependency notices into the staged distribution."""
from pathlib import Path
from importlib.metadata import distribution
import shutil
import sys

destino=Path(__file__).with_name('avisos');destino.mkdir(exist_ok=True)
for pacote in ('PyQt5-Qt5','PyQt5-sip','reportlab','pillow','charset-normalizer'):
    dist=distribution(pacote)
    for f in dist.files:
        if f.name=='LICENSE' and '.dist-info' in str(f):
            shutil.copyfile(dist.locate_file(f),destino/(pacote+'-LICENSE.txt'))
shutil.copyfile(Path(sys.base_prefix)/'LICENSE.txt',destino/'Python-LICENSE.txt')
dist=distribution('pyinstaller')
copiando=next(f for f in dist.files if f.name=='COPYING.txt')
shutil.copyfile(dist.locate_file(copiando),destino/'PyInstaller-COPYING.txt')
