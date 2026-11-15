"""Biblioteca didática: cargas em kN, comprimentos em m, EA=1e6 e EI=2e4."""
import math
import copy
from estrutural.core.propriedades import arco


def modelo(tipo,coords,edges,apoios,cargas=None,q=0):
    m={'tipo':tipo,'nos':[dict(x=x,y=y) for x,y in coords], 'barras':[{'i':i,'j':j,'EA':1e6,'EI':20000,'GJ':10000,'q':q} for i,j in edges]}
    for i,a in apoios.items(): m['nos'][i]['apoio']=a
    for i,c in (cargas or {}).items(): m['nos'][i]['carga_pontual']=c
    return m


def biblioteca():
    itens=[]
    def add(nome,m,descricao,referencia):
        itens.append(dict(nome=nome,modelo=m,descricao=descricao,referencia=referencia))
    add('Biapoiada — carga uniforme',modelo('Viga',[(0,0),(6,0)],[(0,1)],{0:[1,1,0],1:[0,1,0]},q=-10),'Vão 6 m, q=10 kN/m.','Ry=30 kN em cada apoio; Mmáx=qL²/8=45 kN·m.')
    add('Balanço — força na ponta',modelo('Viga',[(0,0),(3,0)],[(0,1)],{0:[1,1,1]},{1:[0,-10,0]}),'Balanço de 3 m, P=10 kN.','Ry=10 kN; M=30 kN·m; v=-PL³/3EI=-0,0045 m.')
    add('Contínua — dois vãos',modelo('Viga',[(0,0),(6,0),(12,0)],[(0,1),(1,2)],{0:[1,1,0],1:[0,1,0],2:[0,1,0]},q=-10),'Dois vãos de 6 m e q=10 kN/m.','Reações 22,5 / 75 / 22,5 kN; momento no apoio central −45 kN·m.')
    add('Portal biengastado',modelo('Pórtico plano',[(0,0),(0,3),(4,3),(4,0)],[(0,1),(1,2),(3,2)],{0:[1,1,1],3:[1,1,1]},{1:[10,0,0]}),'Portal de 4×3 m com força horizontal de 10 kN.','ΣRx=-10 kN; ΣRy=0; equilíbrio de momento externo 30 kN·m.')
    add('Portal — duas águas',modelo('Pórtico plano',[(0,0),(0,3),(3,4.5),(6,3),(6,0)],[(0,1),(1,2),(2,3),(4,3)],{0:[1,1,1],4:[1,1,1]},{2:[0,-20,0]}),'Cobertura simétrica com força vertical na cumeeira.','Por simetria: Ry=10 kN em cada base; deslocamento horizontal da cumeeira nulo.')
    add('Pórtico — dois pavimentos',modelo('Pórtico plano',[(0,0),(4,0),(0,3),(4,3),(0,6),(4,6)],[(0,2),(1,3),(2,3),(2,4),(3,5),(4,5)],{0:[1,1,1],1:[1,1,1]},{2:[5,-10,0],3:[0,-10,0],4:[10,-10,0],5:[0,-10,0]}),'Dois pavimentos de 3 m; forças horizontais e verticais.','ΣRx=-15 kN; ΣRy=40 kN; verificar equilíbrio e reciprocidade.')
    add('Triangular simples',modelo('Treliça',[(0,0),(4,0),(2,2)],[(0,1),(0,2),(1,2)],{0:[1,1],1:[0,1]},{2:[0,-10]}),'Triângulo isostático, P=10 kN no vértice.','Banzo inferior +5 kN; diagonais −5√2 kN; reações +5 kN.')
    for nome in ('Pratt','Howe'):
        coords=[(i*2,0) for i in range(5)]+[(i*2,2) for i in (1,2,3)]
        edges=[(i,i+1) for i in range(4)]+[(5,6),(6,7),(0,5),(7,4),(1,5),(2,6),(3,7)]
        edges+= [(1,6),(3,6)] if nome=='Pratt' else [(5,2),(7,2)]
        add(nome,modelo('Treliça',coords,edges,{0:[1,1],4:[0,1]},{i:[0,-10] for i in (5,6,7)}),'Quatro painéis de 2 m; altura 2 m; 10 kN por nó superior.','Ry=15 kN por apoio; esforços conferidos por equilíbrio de cada nó (isostática).')
    coords=[(i*2,0) for i in range(5)]+[(1+i*2,2) for i in range(4)]
    edges=[(i,i+1) for i in range(4)]+[(i,i+1) for i in range(5,8)]+[(i,5+i) for i in range(4)]+[(i+1,5+i) for i in range(4)]
    add('Warren',modelo('Treliça',coords,edges,{0:[1,1],4:[0,1]},{i:[0,-10] for i in range(5,9)}),'Triângulos alternados com cargas de 10 kN nos nós superiores.','Ry=20 kN por apoio; esforços conferidos por equilíbrio de cada nó.')
    for nome,forma,carga in [('Parabólico triarticulado','parabola','uniforme'),('Circular biarticulado','circulo','uniforme'),('Arco — carga no centro','parabola','pontual')]:
        m=arco((0,0),(6,0),2,16)
        if forma=='circulo':
            R=3.25; yc=-1.25
            ang=math.atan2(1.25,3)
            m['nos']=[{'x':3+R*math.cos(math.pi-ang-(math.pi-2*ang)*i/16),'y':yc+R*math.sin(math.pi-ang-(math.pi-2*ang)*i/16)} for i in range(17)]
        m['nos'][0]['apoio']=m['nos'][-1]['apoio']=[1,1,0]
        for b in m['barras']:
            b.update(EA=1e6,EI=20000)
            a,z=[m['nos'][b[k]] for k in ('i','j')]; ll=math.hypot(z['x']-a['x'],z['y']-a['y'])
            if carga=='uniforme': b['distribuidas']=[{'a':0,'b':ll,'qa':-10*abs(z['x']-a['x'])/ll,'eixo':'global_y'}]
        if forma=='parabola': m['barras'][7]['rotula_j']=True
        if carga=='pontual': m['nos'][8]['carga_pontual']=[0,-20,0]
        descricao='Vão 6 m, flecha 2 m; 16 segmentos retos. '+('Força vertical de 20 kN no centro.' if carga=='pontual' else 'Carga uniforme de 10 kN/m por projeção horizontal.')
        add(nome,m,descricao, 'Uniforme: Ry=30 kN por apoio; triarticulado H=qL²/8f=22,5 kN.' if carga=='uniforme' and forma=='parabola' else ('P=20 kN: Ry=10 kN; H=PL/4f=15 kN.' if carga=='pontual' else 'Ry=30 kN por apoio; simetria, equilíbrio e convergência de discretização.'))
    add('Grelha em L',modelo('Grelha',[(0,0),(3,0),(3,2)],[(0,1),(1,2)],{0:[1,1,1]},{2:[-10,0,0]}),'Balanço em L; Fz=-10 kN na ponta.','Rz=10 kN; Mx=20 kN·m; My=-30 kN·m; w ponta=−0,01783333 m (energia).')
    coords=[(x,y) for y in (0,2,4) for x in (0,2,4)]
    edges=[(3*y+x,3*y+x+1) for y in range(3) for x in range(2)]+[(3*y+x,3*(y+1)+x) for y in range(2) for x in range(3)]
    add('Malha 2×2',modelo('Grelha',coords,edges,{i:[1,1,1] for i in (0,2,6,8)},q=-2),'Quatro células de 2×2 m, qz=-2 kN/m em todas as barras.','Comprimento total 24 m; ΣRz=48 kN; simetria entre quatro cantos.')
    add('Grelha — viga transversal',modelo('Grelha',[(0,0),(3,0),(6,0),(3,-2),(3,2)],[(0,1),(1,2),(1,3),(1,4)],{0:[1,1,1],2:[1,1,1]},{3:[-10,0,0],4:[-10,0,0]}),'Viga principal biengastada e dois balanços transversais.','Rz=10 kN por base; simetria; ΣRz=20 kN.')
    # Round didactic loads in kN; the image supplies geometry, not load units.
    # The UDL is per horizontal metre: q_global = -10 * |dx|/L.
    # G's couple acts on GH; the inclined FG end is moment-released.
    m=modelo('Pórtico plano',[(0,0),(0,3),(2,4.5),(4,6),(8,6),(10,6),(8,3),(8,0),(6,3)],
             [(0,1),(1,2),(2,3),(3,4),(4,5),(7,6),(6,4),(8,6)],
             {0:[1,1,0],7:[1,1,0]},
             {2:[0,-20,0],3:[0,0,60],5:[0,-20,0],8:[0,-40,0]})
    m['barras'][2]['rotula_j']=True
    for k in (1,2,3):
        b=m['barras'][k];a,z=[m['nos'][b[end]] for end in ('i','j')];L=math.hypot(z['x']-a['x'],z['y']-a['y'])
        b['distribuidas']=[dict(a=0,b=L,qa=-10*abs(z['x']-a['x'])/L,eixo='global_y')]
    add('Pórtico inclinado',m,
        'Painéis de 2 m, níveis de 3 m e rótula em G. Carga de 10 kN/m por projeção horizontal em C–G–H; forças de 20 kN em F/I e 40 kN em D. Momento de 60 kN·m anti-horário no lado horizontal de G.',
        'A: Rx=+25 kN, Ry=+67,5 kN. B: Rx=−25 kN, Ry=+92,5 kN. Momento nulo no fim de FG.')
    itens[-1]['rotulos_nos']=['A','C','F','G','H','I','E','B','D']
    # Pinned supports stand on a horizontal ground line in these teaching
    # examples. This is drawing metadata only: no restraints are rotated.
    from estrutural.core.apoios import direcao_barra
    for item in itens:
        model=item['modelo']
        if model['tipo']=='Grelha':continue
        for i,no in enumerate(model['nos']):
            a=no.get('apoio',[])
            if len(a)>=2 and a[0] and a[1] and not (len(a)>2 and a[2]):
                dx,dy=direcao_barra(model,i);no['apoio_visual']=-math.degrees(math.atan2(dy,dx))
    return copy.deepcopy(itens)
