"""Símbolos vetoriais de engenharia, sem dependência de fontes de ícones."""
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QPolygonF,QGuiApplication


def icone(nome, cor):
    app=QGuiApplication.instance();dpr=app.devicePixelRatio() if app else 1
    pix = QPixmap(round(28*dpr),round(28*dpr));pix.setDevicePixelRatio(dpr); pix.fill(Qt.transparent)
    from pathlib import Path
    from PyQt5.QtSvg import QSvgRenderer
    from PyQt5.QtCore import QByteArray
    arquivos={'Salvar':'salvar','Abrir':'abrir','Reações':'reacoes','Esforços':'esforcos','Diagramas':'diagramas','Deformada':'deformada','Coordenadas':'coordenadas','Perfil':'perfil','Exemplos':'exemplos','Material':'material','Relatório PDF':'relatorio','Configurações':'configuracoes'}
    arquivos.update({'Selecionar / editar':'selecionar','Nó':'no','Barra':'barra','Sol':'sol','Lua':'lua','Modo noturno':'lua'})
    if nome in arquivos:
        svg=Path(__file__).with_name('assets')/(arquivos[nome]+'.svg')
        renderer=QSvgRenderer(QByteArray(svg.read_text(encoding='utf-8').replace('#000000',cor).encode()))
        result=QIcon()
        # Render at the actual widget icon sizes so horizontal/vertical strokes
        # share the same raster alignment, including fractional display scaling.
        for lado in (22,26,28):
            alvo=QPixmap(round(lado*dpr),round(lado*dpr));alvo.setDevicePixelRatio(dpr);alvo.fill(Qt.transparent)
            p=QPainter(alvo);p.setRenderHint(QPainter.Antialiasing);renderer.render(p,QRectF(0,0,lado,lado));p.end();result.addPixmap(alvo)
        return result
    p = QPainter(pix); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(cor),1.8)); p.setBrush(Qt.NoBrush)
    def line(x,y,a,b): p.drawLine(QPointF(x,y),QPointF(a,b))
    if nome in ('Apoio fixo','Apoio móvel'):
        p.drawPolygon(QPolygonF([QPointF(14,4),QPointF(5,18),QPointF(23,18)]))
        if nome=='Apoio móvel':
            p.drawEllipse(QPointF(9,22),2,2); p.drawEllipse(QPointF(19,22),2,2)
            line(3,26,25,26)
        if nome=='Apoio fixo':
            line(3,19,25,19)
            for x in (6,11,16,21,26): line(x,19,x-4,24)
    elif nome=='Rótula':
        line(2,14,10,14); line(18,14,26,14); p.drawEllipse(QPointF(14,14),4,4)
    elif nome=='Mola':
        pts=[QPointF(2,14),QPointF(5,14)]+[QPointF(7+i*2,9 if i%2 else 19) for i in range(8)]+[QPointF(24,14),QPointF(27,14)]
        p.drawPolyline(QPolygonF(pts))
    elif nome in ('Retangular','Triangular','Trapezoidal','Função'):
        import math
        line(2,25,26,25)
        last=None
        for i,x in enumerate(range(3,27,4)):
            y=5 if nome=='Retangular' else (22-i*3 if nome=='Triangular' else (13-i*1.5 if nome=='Trapezoidal' else 18-12*math.sin(math.pi*i/6)))
            if last: line(*last,x,y)
            line(x,y,x,23); line(x,23,x-2,20); line(x,23,x+2,20); last=(x,y)
    elif nome=='Engaste':
        line(10,3,10,25); line(10,14,26,14)
        for y in range(4,26,5): line(10,y,3,y+4)
    elif nome=='Carga pontual':
        line(14,3,14,23); line(14,23,7,15); line(14,23,21,15)
    elif nome=='Apagar nó':
        line(5,7,23,7); line(10,3,18,3); line(8,7,9,25); line(20,7,19,25); line(9,25,19,25); line(12,11,12,21); line(16,11,16,21)
    elif nome=='Arco': p.drawArc(QRectF(3,5,22,34),0,180*16)
    elif nome in ('N','V','M','T','Deformada','Estrutura'):
        font=p.font();font.setFamily('Segoe UI');font.setPixelSize(11);font.setBold(True);p.setFont(font)
        line(3,23,25,23)
        if nome=='M':
            from PyQt5.QtGui import QPainterPath
            path=QPainterPath(QPointF(3,13));path.quadTo(QPointF(14,30),QPointF(25,13));p.drawPath(path);line(3,13,3,23);line(25,13,25,23)
        elif nome=='V':
            line(3,7,14,7);line(14,7,14,17);line(14,17,25,17);line(3,7,3,23);line(25,17,25,23)
        elif nome=='Deformada': p.drawArc(QRectF(2,8,24,20),0,180*16)
        elif nome=='Estrutura': line(4,22,4,6); line(4,6,24,6); line(24,6,24,22)
        else: p.drawText(QRectF(2,1,24,20),Qt.AlignCenter,nome)
        if nome in ('V','M'):
            font=p.font();font.setFamily('Segoe UI');font.setPixelSize(11);font.setBold(True);p.setFont(font)
            # Letter occupies the clear area above the right-hand diagram branch.
            p.drawText(QRectF(15,0,12,12),Qt.AlignCenter,nome)
    elif nome=='Ajustar vista':
        p.drawRect(QRectF(5,5,18,18)); line(1,14,9,14); line(19,14,27,14); line(14,1,14,9); line(14,19,14,27)
    else:
        symbols={'Novo':'+','Abrir':'↗','Salvar':'▣','Exemplo':'▤','Propriedades':'⚙','Desfazer':'↶','Refazer':'↷','Calcular':'▶','Exportar':'⇩'}
        font=p.font(); font.setPixelSize(23); p.setFont(font)
        p.drawText(QRectF(0,0,28,28),Qt.AlignCenter,symbols.get(nome,nome[:1]))
    p.end()
    return QIcon(pix)
