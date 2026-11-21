"""Relatório de resultados em PDF vetorial, com estilo extraído do modelo DOCX."""
import math
import os
from datetime import datetime,timezone,timedelta
from pathlib import Path
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo,ZoneInfoNotFoundError
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Flowable,KeepTogether
from estrutural.core.exibicao import Formatador
from estrutural.core.idiomas import traduzir
from estrutural.core.apoios import angulo_visual
from estrutural.core.cargas import intensidade
from estrutural.ui.projecao_grelha import projetar,angulo_apoio,arco_momento_grelha

INK='#0B1220';BODY='#1E293B';BLUE='#0077B6';CYAN='#00B4D8';SOFT='#64748B';BORDER='#CBD5E1'
PALETTE={'N':'#0077B6','V':'#8040A0','M':'#00796B','T':'#805000','D':'#0077B6'}


def fontes():
    if 'EstruturalBody' in pdfmetrics.getRegisteredFontNames():return
    import reportlab
    windows=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts';fallback=Path(reportlab.__file__).parent/'fonts'
    for name,file,vera in [('EstruturalBody','segoeui.ttf','Vera.ttf'),('EstruturalBold','seguisb.ttf','VeraBd.ttf'),('EstruturalMono','consola.ttf','Vera.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(windows/file if (windows/file).exists() else fallback/vera)))


def cor(v):return colors.HexColor(v)


class Paginas(Canvas):
    def __init__(self,*args,**kw):super().__init__(*args,**kw);self.states=[]
    def showPage(self):self.states.append(dict(self.__dict__));self._startPage()
    def save(self):
        tr=lambda text:traduzir(text,getattr(self,'idioma','pt_BR'))
        total=len(self.states)
        for state in self.states:
            self.__dict__.update(state);self.setFont('EstruturalMono',7);self.setFillColor(cor(SOFT))
            self.setFillColor(cor(CYAN));self.rect(54,28,4,4,fill=1,stroke=0);self.setFillColor(cor(SOFT));self.drawString(64,28,tr('Estrutural // resultados'))
            self.drawRightString(letter[0]-54,28,tr(f'PÁG. {self._pageNumber} / {total}'))
            Canvas.showPage(self)
        Canvas.save(self)


def cabecalho(canvas,doc):
    canvas.idioma=getattr(doc,'idioma','pt_BR')
    tr=lambda text:traduzir(text,canvas.idioma)
    if doc.page==1:return
    canvas.saveState();canvas.setFillColor(cor(INK));canvas.setFont('EstruturalMono',7.5);canvas.drawString(54,letter[1]-30,tr('ESTRUTURAL // RESULTADOS'))
    canvas.setFillColor(cor(SOFT));canvas.drawRightString(letter[0]-54,letter[1]-30,tr('v1.0.4'));canvas.setStrokeColor(cor(BORDER));canvas.setLineWidth(.5);canvas.line(54,letter[1]-36,letter[0]-54,letter[1]-36);canvas.restoreState()


class ProjecaoFigura:
    """PDF coordinates have +Y up; the editor projection has +Y down."""
    def __init__(self,modelo,width,height):
        self.grid=modelo['tipo']=='Grelha';self.width=width;self.height=height
        coords=[self.base(n['x'],n['y']) for n in modelo['nos']]
        xmin,xmax=min(p[0] for p in coords),max(p[0] for p in coords)
        ymin,ymax=min(p[1] for p in coords),max(p[1] for p in coords)
        self.scale=min((width-110)/max(xmax-xmin,1),(height-(100 if self.grid else 90))/max(ymax-ymin,1))
        self.cx=(xmin+xmax)/2;self.cy=(ymin+ymax)/2

    def base(self,x,y,z=0):
        if self.grid:
            point=projetar(x,y,z);return point.x(),-point.y()
        return x,y

    def point(self,x,y,z=0):
        u,v=self.base(x,y,z)
        return self.width/2+(u-self.cx)*self.scale,self.height/2+(v-self.cy)*self.scale


class Figura(Flowable):
    def __init__(self,m,r,f,key=None,width=504,height=290):super().__init__();self.m=m;self.r=r;self.f=f;self.key=key;self.width=width;self.height=height
    def draw(self):
        tr=lambda text:traduzir(text,self.f.op.get('idioma','pt_BR'))
        c=self.canv;c.saveState();m,r,f,key=self.m,self.r,self.f,self.key;W,H=self.width,self.height
        c.setStrokeColor(cor(BORDER));c.setLineWidth(.5);c.rect(0,0,W,H)
        nos=m['nos'];grid=m['tipo']=='Grelha';view=ProjecaoFigura(m,W,H);point=view.point;scale=view.scale
        def poly(points,fill=False,stroke=True):
            if not points:return
            p=c.beginPath();p.moveTo(*points[0])
            for P in points[1:]:p.lineTo(*P)
            if fill:p.close()
            c.drawPath(p,fill=int(fill),stroke=int(stroke))
        tol=f.op['tolerancia_zero'];maxval=max((abs(p.get(key,0)) for b in r['barras'] for p in b['pontos'] if abs(p.get(key,0))>=tol),default=1) if key in ('N','V','M','T') else 1
        maxval=maxval or 1;maxdisp=f.max_desloc or 1
        labels=set();def_label=None
        if key in ('N','V','M','T'):
            valores=[(bi,pi,p.get(key,0)) for bi,bar in enumerate(r['barras']) for pi,p in enumerate(bar['pontos'])]
            labels={min(valores,key=lambda t:t[2])[:2],max(valores,key=lambda t:t[2])[:2]}
        elif key=='D':def_label=max(((bi,pi,p['norma']) for bi,bar in enumerate(r['barras']) for pi,p in enumerate(bar['deformacoes'])),key=lambda t:t[2])[:2]
        def arrow(tail,tip):
            c.line(*tail,*tip);dx,dy=tip[0]-tail[0],tip[1]-tail[1];l=math.hypot(dx,dy)
            if l:
                u,v=dx/l,dy/l;c.line(*tip,tip[0]-u*5-v*2,tip[1]-v*5+u*2);c.line(*tip,tip[0]-u*5+v*2,tip[1]-v*5-u*2)
        def moment(P,valor,eixo=None,raio=13):
            if eixo is not None:
                points=[(P[0]+q.x(),P[1]-q.y()) for q in arco_momento_grelha(eixo,valor,raio)]
            else:
                angles=[math.radians(30+j/24*(280 if valor>0 else -280)) for j in range(25)]
                points=[(P[0]+raio*math.cos(a),P[1]+raio*math.sin(a)) for a in angles]
            poly(points);arrow(points[-3],points[-1])
        boxes=[(3,4,58,55)] if grid else []
        for node in nos:
            x,y=point(node['x'],node['y']);boxes.append((x-3,y-3,18,17))
        def label(anchor,text,color):
            """Bounded white-backed labels keep values readable over diagrams."""
            text=tr(text);width=min(W-8,pdfmetrics.stringWidth(text,'EstruturalBody',7)+6);height=13
            ax,ay=anchor;chosen=None
            for dy in (8,-20,22,-34,36,-48,50):
                for dx in (5,-width-5,25,-width-25):
                    x=max(4,min(W-width-4,ax+dx));y=max(4,min(H-height-4,ay+dy))
                    if not any(x<bx+bw and x+width>bx and y<by+bh and y+height>by for bx,by,bw,bh in boxes):
                        chosen=(x,y);break
                if chosen is not None:break
            x,y=chosen or (max(4,min(W-width-4,ax+5)),max(4,min(H-height-4,ay+8)))
            boxes.append((x-2,y-2,width+4,height+4));c.saveState();c.setStrokeColor(cor(color));c.setLineWidth(.4)
            nearest=(max(x,min(ax,x+width)),max(y,min(ay,y+height)))
            if math.hypot(nearest[0]-ax,nearest[1]-ay)>8:c.line(ax,ay,*nearest)
            c.setFillColor(colors.white);c.setFillAlpha(.94);c.rect(x,y,width,height,stroke=0,fill=1);c.setFillAlpha(1)
            c.setFillColor(cor(color));c.setFont('EstruturalBody',7);c.drawString(x+3,y+3,text);c.restoreState()
        same_q=grid and key is None and bool(m['barras']) and bool(m['barras'][0].get('q')) and all(b.get('q')==m['barras'][0].get('q') and not b.get('distribuidas') for b in m['barras'])
        if same_q:
            c.setFont('EstruturalBody',7);c.setFillColor(cor(BLUE));text=tr('qz='+f.esforco(m['barras'][0]['q'])+' '+f.op['forca']+'/m (todas as barras)');c.drawString(10,H-16,text)
            boxes.append((8,H-20,pdfmetrics.stringWidth(text,'EstruturalBody',7)+6,14))
        for i,b in enumerate(m['barras']):
            a,z=nos[b['i']],nos[b['j']];A,B=point(a['x'],a['y']),point(z['x'],z['y']);L=r['barras'][i]['L'];ux,uy=(z['x']-a['x'])/L,(z['y']-a['y'])/L
            c.setStrokeColor(cor(INK));c.setLineWidth(1);c.setDash();c.line(*A,*B);c.setFillColor(cor(SOFT));c.setFont('EstruturalBody',7);c.drawString((A[0]+B[0])/2+3,(A[1]+B[1])/2-13,tr(f'B{i+1}'))
            boxes.append(((A[0]+B[0])/2+2,(A[1]+B[1])/2-15,18,10))
            for flag,P,direction in [('rotula_i',A,1),('rotula_j',B,-1)]:
                if b.get(flag):c.setFillColor(colors.white);c.circle(P[0]+direction*ux*7,P[1]+direction*uy*7,3,stroke=1,fill=1)
            if key in ('N','V','M','T'):
                data=r['barras'][i]['pontos'];curve=[]
                for p in data:
                    P=point(a['x']+ux*p['x'],a['y']+uy*p['x']);v=p.get(key,0);off=(v if abs(v)>=tol else 0)/maxval*45*(-1 if key=='M' else 1);curve.append((P[0],P[1]+off) if grid else (P[0]-uy*off,P[1]+ux*off))
                c.setFillColor(cor(PALETTE[key]));c.setFillAlpha(.13);poly([A]+curve+[B],True,False);c.setFillAlpha(1);c.setStrokeColor(cor(PALETTE[key]));c.setLineWidth(1.1);poly(curve)
                c.setDash(2,2);c.line(*A,*curve[0]);c.line(*B,*curve[-1]);c.setDash();c.setFillColor(cor(PALETTE[key]))
                for k in [pi for bi,pi in labels if bi==i]:
                    x,y=curve[k];label((x,y),f'B{i+1}: {f.esforco(data[k].get(key,0))} {f.unidade(key)}',PALETTE[key])
            elif key=='D':
                data=r['barras'][i]['deformacoes'];curve=[]
                for d in data:
                    x,y=point(a['x']+ux*d['x'],a['y']+uy*d['x']);curve.append((x if grid else x+d['ux']/maxdisp*42,y+d['uy']/maxdisp*42))
                c.setStrokeColor(cor(BLUE));c.setLineWidth(1.2);poly(curve);c.setFillColor(cor(BLUE))
                if def_label[0]==i:
                    k=def_label[1];x,y=curve[k];c.circle(x,y,2,fill=1,stroke=0);label((x,y),f'B{i+1}: |δ|={f.desloc(data[k]["norma"])} {f.op["deslocamento"]}; x={f.comprimento(data[k]["x"])} m',BLUE)
            elif key is None:
                cargas=list(b.get('distribuidas',[]))
                if b.get('q'):cargas.append(dict(a=0,b=L,qa=b['q'],eixo='local_y'))
                for carga in cargas:
                    start,end=carga.get('a',0),carga.get('b',L);vals=[intensidade(carga,start+(end-start)*j/8,L) for j in range(9)];mag=max(map(abs,vals)) or 1
                    vx,vy=(0,1) if grid else (-uy,ux) if carga.get('eixo','local_y')=='local_y' else (0,1);c.setStrokeColor(cor(BLUE));c.setLineWidth(.7);tails=[]
                    for j,q in enumerate(vals):
                        x=start+(end-start)*j/8;tip=point(a['x']+ux*x,a['y']+uy*x);tail=(tip[0]-vx*q/mag*27,tip[1]-vy*q/mag*27);tails.append(tail)
                        if q and abs(q)>=tol:arrow(tail,tip)
                    poly(tails)
                    c.setFillColor(cor(BLUE));load_text=(carga.get('descricao','q(x)')+': ' if carga.get('funcao') or carga.get('pontos') else 'q: ')+f.esforco(min(vals))+' a '+f.esforco(max(vals))+' '+f.op['forca']+'/m'
                    if not same_q:label(((A[0]+B[0])/2,(A[1]+B[1])/2+(-27 if sum(vals)>=0 else 27)),load_text,BLUE)
                for carga in b.get('pontuais',[]):
                    x=carga['x'];tip=point(a['x']+ux*x,a['y']+uy*x);fx,fy=carga.get('fx',0),carga.get('fy',0)
                    if not carga.get('global'):fx,fy=ux*fx-uy*fy,uy*fx+ux*fy
                    mag=math.hypot(fx,fy)
                    if mag>=tol and mag:c.setStrokeColor(cor(BLUE));arrow((tip[0]-fx/mag*30,tip[1]-fy/mag*30),tip);label(tip,f.esforco(mag)+' '+f.unidade('R'),BLUE)
                    if carga.get('m',0) and abs(carga['m'])>=tol:
                        c.setStrokeColor(cor(BLUE));moment(tip,carga['m']);label(tip,f.esforco(carga['m'])+' '+f.unidade('M'),BLUE)
        for i,n in enumerate(nos):
            x,y=point(n['x'],n['y']);c.setStrokeColor(cor(INK));c.setFillColor(colors.white);c.circle(x,y,2,fill=1,stroke=1);c.setFillColor(cor(INK));c.setFont('EstruturalBody',7);c.drawString(x+4,y+5,tr(str(i+1)))
            a=n.get('apoio',[])
            if any(a):
                c.saveState();c.translate(x,y);c.rotate(-(angulo_apoio(m,i) if grid else angulo_visual(m,i)));c.setLineWidth(.9)
                if len(a)>2 and all(a):
                    c.line(0,-11,0,11)
                    for yy in range(-11,12,4):c.line(0,yy,-5,yy-3)
                else:
                    poly([(0,0),(-7,-12),(7,-12),(0,0)])
                    rolos=(m['tipo']=='Grelha' and n.get('apoio_visual_tipo')=='Apoio móvel') or (m['tipo']!='Grelha' and not a[0] and a[1])
                    if rolos:c.circle(-4,-15,1.5);c.circle(4,-15,1.5);yy=-18
                    else:yy=-14
                    c.line(-10,yy,10,yy)
                c.restoreState()
            for j,k in enumerate(n.get('mola',[])):
                if not k:continue
                c.setStrokeColor(cor(INK));c.setLineWidth(.8)
                if grid and j in (1,2):poly([(x+q.x(),y-q.y()) for q in arco_momento_grelha(j,1,9)]);continue
                if j==2:c.arc(x-9,y-9,x+9,y+9,20,300);continue
                from estrutural.core.apoios import direcao_barra
                dx,dy=direcao_barra(m,i);ux,uy=((-1 if dx>=0 else 1),0) if j==0 and m['tipo']!='Grelha' else (0,(-1 if dy>=0 else 1));vx,vy=-uy,ux
                pts=[(x,y),(x+ux*4,y+uy*4)]+[(x+ux*(6+t*2)+vx*(3 if t%2 else -3),y+uy*(6+t*2)+vy*(3 if t%2 else -3)) for t in range(7)]+[(x+ux*24,y+uy*24)]
                poly(pts);c.line(x+ux*24-vx*6,y+uy*24-vy*6,x+ux*24+vx*6,y+uy*24+vy*6)
            if key is None:
                values=(n.get('carga_pontual',[0,0,0])+[0]*3)[:3];c.setStrokeColor(cor(BLUE));c.setFillColor(cor(BLUE))
                for fx,fy in [(values[0],0),(0,values[1])] if m['tipo']!='Grelha' else [(0,values[0])]:
                    mag=math.hypot(fx,fy)
                    if mag and mag>=tol:
                        tail=(x-fx/mag*30,y-fy/mag*30);arrow(tail,(x,y));label(tail,('Fz=' if grid else '')+f.esforco(fx or fy)+' '+f.unidade('R'),BLUE)
                if grid:
                    for j,name in ((1,'Mx'),(2,'My')):
                        if values[j] and abs(values[j])>=tol:
                            moment((x,y),values[j],j);label((x+10,y-15),name+'='+f.esforco(values[j])+' '+f.unidade('M'),BLUE)
                elif values[2] and abs(values[2])>=tol:
                    moment((x,y),values[2]);label((x+10,y+12),f.esforco(values[2])+' '+f.unidade('M'),BLUE)
        if grid:
            origin=(25,28);c.setFont('EstruturalBody',7)
            for name,delta,color in [('X',projetar(20,0),'#B45309'),('Y',projetar(0,20),'#15803D'),('Z',projetar(0,0,20),'#2563EB')]:
                tip=(origin[0]+delta.x(),origin[1]-delta.y());c.setStrokeColor(cor(color));c.setFillColor(cor(color));arrow(origin,tip);c.drawString(tip[0]+3,tip[1]+2,name)
        if key=='D':c.setFont('EstruturalMono',7);c.setFillColor(cor(SOFT));c.drawString(10,H-16,tr(f'Amplificação ×{42/(maxdisp*scale) if f.max_desloc else 1:.4g}'))
        c.restoreState()


def gerar_relatorio(path,modelo,resultado,opcoes=None):
    if not modelo.get('nos') or not resultado:raise ValueError('Calcule um modelo antes de emitir o relatório.')
    fontes();f=Formatador(resultado,opcoes);W=letter[0]-108
    styles={
        'title':ParagraphStyle('Title',fontName='EstruturalBold',fontSize=24,leading=29,textColor=cor(INK),spaceAfter=8),
        'body':ParagraphStyle('Body',fontName='EstruturalBody',fontSize=9,leading=12,textColor=cor(BODY),spaceAfter=8),
        'mono':ParagraphStyle('Mono',fontName='EstruturalMono',fontSize=8,leading=11,textColor=cor(SOFT),spaceAfter=6),
        'section':ParagraphStyle('Section',fontName='EstruturalBold',fontSize=12,leading=16,textColor=cor(INK),spaceBefore=12,spaceAfter=9),
        'cell':ParagraphStyle('Cell',fontName='EstruturalBody',fontSize=8,leading=11,textColor=cor(BODY)),
        'head':ParagraphStyle('Head',fontName='EstruturalMono',fontSize=7.5,leading=10,textColor=colors.white)}
    def p(txt,style='body',traduz=True):return Paragraph(escape(traduzir(str(txt),f.op.get('idioma','pt_BR')) if traduz else str(txt)),styles[style])
    def sec(num,txt):return Paragraph(f'<font color="{CYAN}">{num:02d}</font> <font color="#94A3B8"> // </font> '+escape(traduzir(txt,f.op.get('idioma','pt_BR')).upper()),styles['section'])
    def table(headers,rows,widths=None):
        widths=widths or [W/len(headers)]*len(headers)
        data=[[p(x,'head') for x in headers]]+[[p(x,'cell') for x in row] for row in rows]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),cor(INK)),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,cor('#F1F5F9')]),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),1,cor(CYAN))]));return t
    try:date=datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y')
    except ZoneInfoNotFoundError:date=datetime.now(timezone(timedelta(hours=-3))).strftime('%d/%m/%Y')
    date=(opcoes or {}).get('data_relatorio',date)
    nome=modelo.get('nome') or traduzir(modelo.get('exemplo',{}).get('nome') or 'Sem título',f.op.get('idioma','pt_BR'));grid=modelo['tipo']=='Grelha'
    story=[p('■  RELATÓRIO DE RESULTADOS // ESTRUTURAL','mono'),p(nome,'title',traduz=False),p(f'{date}  |  {modelo["tipo"]}  |  v1.0.4','mono'),sec(1,'Estrutura'),Figura(modelo,resultado,f,height=230 if grid else 160),Spacer(1,6)]
    story.append(p('FIG. 01 // Modelo, apoios e cargas. Geometria em m.','mono'))
    story.append(sec(2,'Reações de apoio'))
    force=f.op['forca'];moment=force+'·m'
    headers=['Nó','Rz ('+force+')','Mx ('+moment+')','My ('+moment+')'] if grid else ['Nó','Rx ('+force+')','Ry ('+force+')','M ('+moment+')']
    rows=[[i+1]+[f.esforco(v) for v in r]+(['0'] if len(r)==2 else []) for i,r in enumerate(resultado['reacoes']) if any(modelo['nos'][i].get('apoio',[])) or any(modelo['nos'][i].get('mola',[]))]
    story.append(table(headers,rows or [['—','0','0','0']]))
    keys=['N'] if modelo['tipo']=='Treliça' else ['V','M','T'] if grid else ['N','V','M'];keys+=['D'];summary=[]
    blocos=[]
    for num,key in enumerate(keys,4):
        name={'N':'Esforço normal','V':'Esforço cortante','M':'Momento fletor','T':'Momento torçor','D':'Deformada'}[key]
        bloco=[sec(num,name)]
        legenda='N+ tração · V+ face esquerda · M+ sagente · T pela mão direita.' if key!='D' else 'Módulo |δ| em '+f.op['deslocamento']+'; deformada ampliada para leitura.'
        if grid:legenda='Grelha: +w em Z; θx/θy e torção pela mão direita. Reações: Rz, Mx, My. Diagramas amostrados.' if key!='D' else 'Módulo |δ| em '+f.op['deslocamento']+'; deformada ampliada para leitura. w em Z, fora do plano XY; geometria original sem amplificação.'
        elif key=='D':legenda+=' δx/δy globais.'
        bloco.append(p(legenda,'mono'));bloco.append(Figura(modelo,resultado,f,key,height=250 if grid else 180));bloco.append(Spacer(1,6))
        extrema=[]
        for i,b in enumerate(resultado['barras']):
            data=b['deformacoes'] if key=='D' else b['pontos'];value='norma' if key=='D' else key
            lo=min(data,key=lambda x:x.get(value,0));hi=max(data,key=lambda x:x.get(value,0));format_value=f.desloc if key=='D' else f.esforco
            extrema.append([i+1,format_value(lo.get(value,0)),f.comprimento(lo['x']),format_value(hi.get(value,0)),f.comprimento(hi['x'])])
            summary.append((name,i+1,lo.get(value,0),lo['x'],hi.get(value,0),hi['x'],key))
        unit=f.op['deslocamento'] if key=='D' else f.unidade(key)
        bloco.append(table(['Barra','Mín. ('+unit+')','x mín. (m)','Máx. ('+unit+')','x máx. (m)'],extrema));blocos.append(bloco)
    story.append(sec(3,'Resumo de máximos e mínimos'))
    rows=[]
    for name in dict.fromkeys(row[0] for row in summary):
        matches=[row for row in summary if row[0]==name];lo=min(matches,key=lambda row:row[2]);hi=max(matches,key=lambda row:row[4]);key=lo[-1];format_value=f.desloc if key=='D' else f.esforco;unit=f.op['deslocamento'] if key=='D' else f.unidade(key)
        rows.append([name+(' |δ|' if key=='D' else '')+' ('+unit+')',format_value(lo[2]),f'B{lo[1]} / x={f.comprimento(lo[3])} m',format_value(hi[4]),f'B{hi[1]} / x={f.comprimento(hi[5])} m'])
    story.append(table(['Resultado','Mínimo','Posição','Máximo','Posição'],rows,[120,65,120,65,134]))
    story.append(Spacer(1,2 if grid else 10));story.append(p('Extremos da discretização/interpolação. x medido desde o início de cada barra.','mono'))
    for i,bloco in enumerate(blocos):
        if i%2==0:story.append(PageBreak())
        story.append(KeepTogether(bloco))
    doc=SimpleDocTemplate(str(path),pagesize=letter,rightMargin=54,leftMargin=54,topMargin=54,bottomMargin=54,title=nome,author='Estrutural')
    doc.idioma=f.op.get('idioma','pt_BR')
    doc.build(story,onFirstPage=cabecalho,onLaterPages=cabecalho,canvasmaker=Paginas)
    if not Path(path).exists() or Path(path).stat().st_size<100:raise OSError('O relatório PDF não foi gravado.')
