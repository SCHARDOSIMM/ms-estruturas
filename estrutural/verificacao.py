"""Non-interactive installation diagnostics, isolated from user preferences."""
import csv
import json
import math
import traceback
from pathlib import Path
from PyQt5.QtCore import QSettings,Qt
from estrutural.core.analise import analisar
from estrutural.core.exemplos import biblioteca
from estrutural.core.projetos import migrar
from estrutural.ui.editor import Editor
from estrutural.ui.relatorio import gerar_relatorio
from estrutural.ui.idioma import QFileDialog


def verificar_instalacao(pasta,app):
    pasta=Path(pasta).resolve();pasta.mkdir(parents=True,exist_ok=True)
    resumo={'ok':False,'exemplos':[],'verificacoes':[]};janelas=[]
    def exigir(condicao,nome):
        if not condicao:raise RuntimeError(nome)
        resumo['verificacoes'].append(nome)
    try:
        for item in biblioteca():
            r=analisar(item['modelo'])
            erro=max(map(abs,r['equilibrio']))
            exigir(erro<1e-7,'equilibrio: '+item['nome'])
            exigir(all(math.isfinite(v) for d in r['deslocamentos'] for v in d),'deslocamentos finitos: '+item['nome'])
            resumo['exemplos'].append({'nome':item['nome'],'erro_equilibrio':erro})
        cfg=lambda:QSettings(str(pasta/'preferencias-teste.ini'),QSettings.IniFormat)
        limpa=cfg();limpa.clear();limpa.sync()
        w=Editor(config=cfg());janelas.append(w)
        w.setAttribute(Qt.WA_DontShowOnScreen);w.resize(1360,768);w.show();app.processEvents()
        exigir(w.snap.isChecked() and w.grade_check.isChecked(),'padrao: grade e snap')
        exigir(not w.noturno.isChecked() and w.preferencias['idioma']=='pt_BR','padrao: claro e portugues')
        exigir(not w.windowIcon().isNull(),'icone da janela')
        exigir(all(not b.icon().isNull() for b,_ in w.botoes_icones),'icones das ferramentas')
        w.abrir_exemplo(next(e for e in biblioteca() if e['nome']=='Pórtico inclinado'))
        for modo in ('Reações','Esforços','Deformada'):
            w.exibir_resultado(modo);app.processEvents();exigir(w.tabela.rowCount()>0,'tabela: '+modo)
        for modo in ('N','V','M','T','Estrutura'):
            w.escolher_diagrama(modo);app.processEvents();exigir(not w.canvas.grab().isNull(),'desenho: '+modo)
        w.escolher_diagrama('M');app.processEvents()
        exigir(w.canvas.grab().save(str(pasta/'diagrama.png'),'PNG'),'exportacao PNG')
        projeto=pasta/'projeto.json';projeto.write_text(json.dumps(w.modelo,ensure_ascii=False),encoding='utf-8')
        exigir(analisar(migrar(json.loads(projeto.read_text(encoding='utf-8'))))['reacoes']==w.resultado['reacoes'],'projeto JSON')
        gerar_relatorio(pasta/'relatorio.pdf',w.modelo,w.resultado,w.preferencias)
        exigir((pasta/'relatorio.pdf').read_bytes().startswith(b'%PDF-'),'exportacao PDF')
        original=QFileDialog.getSaveFileName
        try:
            QFileDialog.getSaveFileName=staticmethod(lambda *a:(str(pasta/'reacoes.csv'),'Reações (*.csv)'))
            w.exibir_resultado('Reações');w.exportar()
        finally:QFileDialog.getSaveFileName=staticmethod(original)
        with (pasta/'reacoes.csv').open(encoding='utf-8-sig',newline='') as f:exigir(len(list(csv.reader(f,delimiter=';')))>2,'exportacao CSV')
        w.grade_check.setChecked(False);w.snap.setChecked(False);w.tema_btn.click();w.idioma_btn.click();w.close()
        outra=Editor(config=cfg());janelas.append(outra)
        exigir(not outra.snap.isChecked() and not outra.grade_check.isChecked(),'preferencias: grade e snap')
        exigir(outra.noturno.isChecked() and outra.preferencias['idioma']=='en_US','preferencias: tema e idioma')
        exigir(outra.menu_autor.actions()[-1].data()=='mailto:schardosimmatheus@gmail.com','link de e-mail')
        resumo.update(ok=True,pdf_bytes=(pasta/'relatorio.pdf').stat().st_size,versao=app.applicationVersion(),preferencias_restauradas=True,recursos_graficos=True)
    except Exception:
        resumo['erro']=traceback.format_exc()
    finally:
        for w in janelas:w.close()
        (pasta/'verificacao.json').write_text(json.dumps(resumo,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if resumo['ok'] else 1
