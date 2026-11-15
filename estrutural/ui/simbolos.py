"""Desenho compartilhado entre canvas e relatório, com orientação dos vínculos."""
import math
from PyQt5.QtCore import QPointF,QRectF,Qt
from PyQt5.QtGui import QPen,QColor,QPolygonF
from estrutural.core.apoios import angulo_visual


def desenhar_apoio(p,modelo,idx,P,cor,size=1):
    a=modelo['nos'][idx].get('apoio',[])
    if not any(a):return
    p.save();p.translate(P);p.rotate(angulo_visual(modelo,idx));p.scale(size,size);p.setPen(QPen(QColor(cor),1.5));p.setBrush(Qt.NoBrush)
    if len(a)>2 and all(a):
        p.drawLine(QPointF(0,-14),QPointF(0,14));p.drawLine(QPointF(0,0),QPointF(14,0))
        for y in range(-14,15,5):p.drawLine(QPointF(0,y),QPointF(-7,y+4))
    else:
        p.drawPolygon(QPolygonF([QPointF(0,0),QPointF(-9,15),QPointF(9,15)]))
        rolos=(modelo['tipo']=='Grelha' and modelo['nos'][idx].get('apoio_visual_tipo')=='Apoio móvel') or (modelo['tipo']!='Grelha' and len(a)>1 and not a[0] and a[1])
        if rolos:
            p.drawEllipse(QPointF(-5,19),2,2);p.drawEllipse(QPointF(5,19),2,2);y=23
        else:y=17
        p.drawLine(QPointF(-12,y),QPointF(12,y))
        if not rolos:
            for x in range(-10,14,5):p.drawLine(QPointF(x,y),QPointF(x-4,y+5))
    p.restore()


def desenhar_molas(p,no,P,cor,direcao=(1,0),grelha=False):
    p.save();p.setPen(QPen(QColor(cor),1.3));p.setBrush(Qt.NoBrush)
    for j,k in enumerate(no.get('mola',[0,0,0])):
        if not k:continue
        if j==2 or (grelha and j==1):p.drawArc(QRectF(P.x()-13,P.y()-13,26,26),30*16,290*16);continue
        u=QPointF(-1 if direcao[0]>=0 else 1,0) if j==0 and not grelha else QPointF(0,1 if direcao[1]>=0 else -1);v=QPointF(-u.y(),u.x());pts=[P,P+u*5]
        for i in range(7):pts.append(P+u*(8+i*3)+v*(4 if i%2 else -4))
        pts.extend([P+u*30,P+u*36]);p.drawPolyline(QPolygonF(pts));p.drawLine(P+u*36-v*8,P+u*36+v*8)
    p.restore()
def desenhar_momento(p, centro, raio, valor):
    """Signed moment arrow in Qt screen coordinates, with a tangent arrowhead."""
    import math
    from PyQt5.QtCore import QPointF,QRectF
    from PyQt5.QtGui import QPolygonF
    inicio=30;arco=280 if valor>0 else -280
    p.drawArc(QRectF(centro.x()-raio,centro.y()-raio,2*raio,2*raio),inicio*16,arco*16)
    a=math.radians(inicio+arco);s=1 if arco>0 else -1
    tip=centro+QPointF(raio*math.cos(a),-raio*math.sin(a))
    tangent=QPointF(-s*math.sin(a),-s*math.cos(a));normal=QPointF(-tangent.y(),tangent.x())
    p.save();p.setBrush(p.pen().color());p.drawPolygon(QPolygonF([tip,tip-tangent*8+normal*3.5,tip-tangent*8-normal*3.5]));p.restore()

