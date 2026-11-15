# Build with: .venv/Scripts/python -m PyInstaller --noconfirm "empacotamento/MS Estruturas.spec"
from pathlib import Path
from importlib.metadata import distribution

ROOT=Path(SPECPATH).parent
site=Path(distribution('PyQt5').locate_file(''))
assets=ROOT/'estrutural'/'ui'/'assets'
datas=[(str(p),'estrutural/ui/assets') for p in assets.iterdir() if p.suffix in ('.svg','.ico') and p.name!='marca-ms.svg']
datas += [(str(site/'PyQt5'/'Qt5'/'translations'/'qt_pt.qm'),'PyQt5/Qt5/translations')]
for name in ('Vera.ttf','VeraBd.ttf','bitstream-vera-license.txt'):
    datas.append((str(site/'reportlab'/'fonts'/name),'reportlab/fonts'))
datas.append((str(ROOT/'empacotamento'/'avisos'),'Licencas'))

a=Analysis([str(ROOT/'estrutural'/'__main__.py')],pathex=[str(ROOT)],binaries=[],datas=datas,
    hiddenimports=[],hookspath=[],hooksconfig={},runtime_hooks=[],
    excludes=['tkinter','_tkinter','unittest','pytest','numpy','scipy','matplotlib','pandas','IPython',
              'PyQt5.QtWebEngineWidgets','PyQt5.QtWebEngineCore','PyQt5.QtWebEngine',
              'PyQt5.QtQml','PyQt5.QtQuick','PyQt5.QtMultimedia','PyQt5.QtDesigner',
              'PyQt5.QtHelp','PyQt5.QtSql','PyQt5.QtTest','PyQt5.QtOpenGL','PyQt5.QtQuickWidgets',
              'PIL.AvifImagePlugin','PIL._avif'],
    noarchive=False,optimize=1)

# Qt's general hooks include other languages and a software OpenGL renderer.
# This application uses raster QPainter only, with no QOpenGLWidget or Qt Quick.
removidos=[]
def manter(entry):
    nome=entry[0].replace('\\','/');base=Path(nome).name.lower()
    if base in ('opengl32sw.dll','d3dcompiler_47.dll','libegl.dll','libglesv2.dll'):
        removidos.append(nome);return False
    if base.startswith('qt5') and base.endswith('.dll') and base not in ('qt5core.dll','qt5gui.dll','qt5widgets.dll','qt5svg.dll'):
        removidos.append(nome);return False
    if '/translations/' in nome and base!='qt_pt.qm':
        removidos.append(nome);return False
    if '/plugins/' in nome and not any('/'+p+'/' in nome for p in ('platforms','styles','imageformats','iconengines')):
        removidos.append(nome);return False
    if '/platforms/' in nome and base!='qwindows.dll':
        removidos.append(nome);return False
    return True
a.binaries=[e for e in a.binaries if manter(e)]
a.datas=[e for e in a.datas if manter(e)]
(ROOT/'build').mkdir(exist_ok=True)
(ROOT/'build'/'dependencias-removidas.txt').write_text('\n'.join(removidos),encoding='utf-8')
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='MS Estruturas',debug=False,
    bootloader_ignore_signals=False,strip=False,upx=False,console=False,
    disable_windowed_traceback=False,argv_emulation=False,target_arch=None,
    codesign_identity=None,entitlements_file=None,icon=str(assets/'ms-estruturas.ico'),
    version=str(ROOT/'empacotamento'/'versao.txt'))
coll=COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name='MS Estruturas')
