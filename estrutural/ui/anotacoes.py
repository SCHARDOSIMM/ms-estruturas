"""Posicionamento geométrico de sinais e rótulos nas regiões dos diagramas."""
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPainterPath


def centroide(poligono):
    pares=list(zip(poligono,poligono[1:]+poligono[:1]));area=sum(a.x()*b.y()-b.x()*a.y() for a,b in pares)
    if abs(area)<1e-8:return None
    return QPointF(sum((a.x()+b.x())*(a.x()*b.y()-b.x()*a.y()) for a,b in pares)/(3*area),sum((a.y()+b.y())*(a.x()*b.y()-b.x()*a.y()) for a,b in pares)/(3*area))


def sinal(p,mid,text,color):
    p.save();p.drawEllipse(mid,8,8);path=QPainterPath();path.addText(QPointF(0,0),p.font(),text);r=path.boundingRect();p.translate(mid-r.center());p.fillPath(path,color);p.restore()
