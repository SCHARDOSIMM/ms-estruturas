"""Isometric projection of the XY modelling plane, with vertical global Z."""
import math
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPolygonF
from estrutural.core.apoios import direcao_barra


def projetar(x, y, z=0):
    return QPointF(math.sqrt(3)/2*(x-y), .5*(x+y)-z)


def inverter(p):
    return p.y()+p.x()/math.sqrt(3), p.y()-p.x()/math.sqrt(3)


def angulo_apoio(modelo, idx):
    """Fixed support points into the connected member in the projected plane.

    Translational grillage supports restrain vertical Z, so their triangles
    remain upright rather than rotating with a beam in the XY plane.
    """
    no=modelo['nos'][idx];a=no.get('apoio',[])
    if len(a)>2 and all(a):
        delta=projetar(*direcao_barra(modelo,idx))
        return math.degrees(math.atan2(delta.y(),delta.x()))-no.get('apoio_visual',0)
    return -no.get('apoio_visual',0)


def arco_momento_grelha(eixo, valor, raio=20):
    """Projected relative arc points, shared by Qt and vector PDF drawing."""
    points=[]
    for j in range(25):
        angle=(.2+j/24*1.5*math.pi)*(1 if valor>0 else -1)
        a,b=math.cos(angle)*raio,math.sin(angle)*raio
        points.append(projetar(0 if eixo==1 else b,a if eixo==1 else 0,b if eixo==1 else a))
    return points


def momento_grelha(p, point, eixo, valor, raio=20):
    points=[point+delta for delta in arco_momento_grelha(eixo,valor,raio)]
    p.drawPolyline(QPolygonF(points))
    delta=points[-1]-points[-3];length=math.hypot(delta.x(),delta.y())
    if length:
        u=delta/length;normal=QPointF(-u.y(),u.x());tip=points[-1]
        p.drawLine(tip,tip-u*7+normal*3);p.drawLine(tip,tip-u*7-normal*3)
