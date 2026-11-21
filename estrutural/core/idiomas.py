"""Engineering terminology shared by the desktop UI and exported reports.

Only presentation strings are translated. Model keys, section identifiers,
formulae and numerical values never pass through this catalog.
"""
import re
from estrutural.core.idiomas_fr import CATALOGO_FR

IDIOMAS = ('pt_BR', 'en_US', 'fr_FR')

# Long phrases precede short labels when translating composed strings.
CATALOGO = {
    'em x=': 'at x=',
    'b · largura    h · altura':'b · width    h · depth',
    'b · lado':'b · side length',
    'd · diâmetro':'d · diameter',
    'd · diâmetro externo':'d · outside diameter',
    't · espessura da parede':'t · wall thickness',
    'tw · alma    tf · mesa':'tw · web    tf · flange',
}


def _pares(texto):
    for linha in texto.strip().splitlines():
        pt, en = linha.split(' = ', 1)
        CATALOGO[pt] = en


_pares('''
Selecionar / editar = Select / edit
Nó = Node
Barra = Member
Apoio fixo = Pinned support
Apoio móvel = Roller support
Engaste = Fixed support
Rótula = Hinge
Mola = Spring
Carga pontual = Point load
Carga distribuída = Distributed load
Retangular = Rectangular
Triangular = Triangular
Trapezoidal = Trapezoidal
Função = Custom load
Apagar nó = Delete node
Estrutura = Structure
Deformada = Deflected shape
Novo = New
Abrir = Open
Salvar = Save
Exemplo = Example
Exemplos = Examples
Arco = Arch
Propriedades = Properties
Desfazer = Undo
Refazer = Redo
Calcular = Analyze
Exportar = Export
Ajustar vista = Fit view
Perfil = Section
Material = Material
Coordenadas = Coordinates
Reações = Reactions
Esforços = Member forces
Diagramas = Diagrams
Relatório PDF = PDF report
Configurações = Settings
Viga = Beam
Pórtico plano = Plane frame
Treliça = Truss
Grelha = Grillage
DESENHAR = DRAW
VÍNCULOS = RESTRAINTS
CARGAS = LOADS
RESULTADOS = RESULTS
Modo noturno = Dark mode
Modo claro = Light mode
Idioma = Language
Alternar entre português e inglês. = Switch between Portuguese and English.
Alternar entre os temas claro e escuro. = Switch between light and dark themes.
Clique em um nó ou barra para editar propriedades. Na barra, também é possível remover cargas distribuídas. = Click a node or member to edit its properties. Member properties also allow you to remove distributed loads.
Insere um ponto estrutural na posição clicada, respeitando o snap. = Add a node at the clicked position, using grid snapping when enabled.
Liga dois pontos. Clique no início e no fim; Esc cancela o trecho. = Connect two points. Click the start and end; press Esc to cancel.
Apoio articulado de 2º gênero: impede u e v e permite rotação. Clique em um nó. = Pinned support: restrains u and v while allowing rotation. Click a node.
Apoio de 1º gênero: impede v e permite u e rotação. Clique em um nó. = Roller support: restrains v while allowing u and rotation. Click a node.
Impede os deslocamentos e a rotação do nó. = Restrain all translations and rotation at a node.
Libera ou restabelece o momento em uma extremidade de barra. Clique na barra e escolha o extremo. = Release or restore bending moment transfer at a member end. Click the member and choose an end.
Define forças e momento no nó por formulário, com unidades. = Enter nodal forces and moment in a form with units.
Carga distribuída constante (kN/m). Clique na barra e informe intensidade e trecho. = Uniformly distributed load (kN/m). Click a member and enter the intensity and loaded interval.
Carga distribuída com uma extremidade nula. Clique na barra e escolha orientação e trecho. = Triangular distributed load with zero intensity at one end. Click a member and choose the direction and loaded interval.
Carga distribuída linear entre duas intensidades. Clique na barra e informe q inicial e final. = Linearly varying distributed load. Click a member and enter the start and end intensities.
Carga distribuída q(x) por expressão matemática. Clique na barra; x é a distância desde seu nó inicial. = Define q(x) with a mathematical expression. Click a member; x is measured from its start node.
Remove o nó clicado e as barras conectadas. Desfazer recupera a operação. = Delete the clicked node and connected members. Undo restores them.
Exibe a geometria e os carregamentos sem diagramas. = Show geometry, supports and loads.
Exibe o diagrama de esforço normal, positivo em tração. = Show the axial force diagram; tension is positive.
Exibe o diagrama de esforço cortante. = Show the shear force diagram.
Exibe o momento fletor, positivo sagente. = Show the bending moment diagram; sagging is positive.
Exibe torção em grelhas. = Show torsional moments in grillages.
Exibe deslocamentos ampliados pela escala indicada. = Show the deflected shape at the selected magnification.
Inicia um modelo vazio. A operação pode ser desfeita. = Start an empty model. This action can be undone.
Abre um projeto JSON salvo. = Open a saved JSON project.
Salva geometria, vínculos e cargas em JSON. = Save geometry, restraints and loads as JSON.
Carrega uma viga biapoiada de 6 m com carga de 10 kN/m. = Load a 6 m simply supported beam carrying 10 kN/m.
Cria um arco parabólico discretizado em barras. = Create a parabolic arch discretized into straight members.
Editor avançado do modelo em JSON. = Advanced JSON model editor.
Reverte a última alteração do modelo. = Undo the last model change.
Reaplica a alteração desfeita. = Redo the last undone change.
Executa a análise linear e atualiza reações, deslocamentos e diagramas. = Run linear analysis and update reactions, displacements and diagrams.
Salva imagem PNG, esforços CSV ou relatório PDF. = Export a PNG image, member forces as CSV or a PDF report.
Enquadra todos os nós na área de desenho. = Fit all nodes within the drawing area.
Biblioteca de modelos agrupados por tipologia, com descrição e resultados de referência. = Browse example models by structure type, with descriptions and reference results.
Escolhe uma seção e aplica suas propriedades a uma ou várias barras. = Select a cross-section and assign its properties to one or more members.
Entrada exata de pontos e edição de nós em tabela (Ctrl+E). = Enter exact coordinates and edit nodes in a table (Ctrl+E).
Mostra reações proporcionais nos apoios, com valores e unidades. = Show support reactions with proportional arrows, values and units.
Mostra os esforços amostrados de todas as barras em tabela. = Tabulate member forces at sampled positions along every member.
Mostra diagramas preenchidos. Escolha N, V, M ou T na paleta e passe o mouse para ler valores. = Show filled diagrams. Select N, V, M or T in the palette and hover over a diagram to read values.
Desenha um arco circular ou parabólico por formulário, com prévia da geometria. = Draw a circular or parabolic arch using a form with a live geometry preview.
Define E, G, Poisson, peso específico e dilatação térmica por barra ou conjunto de barras. = Assign Young’s modulus, shear modulus, Poisson’s ratio, unit weight and thermal expansion to one or more members.
Salva um relatório paginado com modelo, reações, deslocamentos e diagramas. = Save a paginated report with the model, reactions, displacements and diagrams.
Preferências de unidades, precisão, tolerâncias, grade, snap, tema e deformada. = Set display units, precision, tolerances, grid, snapping, theme and deflection magnification.
Editor visual de carga personalizada: formatos, pontos, prévia e resultante. Fórmula opcional em Avançado. = Visual load editor with shapes, tabulated points, a preview and the resultant. An optional expression is available under Advanced.
Restringe uma direção física editável. Padrão vertical (90° de +X); selecione o nó para ajustar a rampa. = Restrain translation in an adjustable direction. The default is vertical (90° from +X); select the node to set the support inclination.
Define rigidezes elásticas globais X/Y e de rotação no nó selecionado. = Set global X/Y translational and rotational spring stiffnesses at the selected node.
Escala: = Scale:
Grade = Grid
Roda: zoom · botão central: pan = Mouse wheel: zoom · middle button: pan
Girar apoio 90° (R) = Rotate support 90° (R)
Selecione um nó com apoio. No móvel muda a direção física; nos demais apenas o desenho. = Select a supported node. Rotating a roller changes its restraint direction; for other supports only the symbol rotates.
EA/EI unitários por padrão. Edite rigidezes antes de analisar hiperestáticas. = EA/EI default to unity. Set member stiffnesses before analyzing statically indeterminate structures.
Selecione primeiro um nó com apoio. = Select a supported node first.
O nó selecionado não tem apoio. = The selected node has no support.
Direção física do apoio móvel alterada. Calcule novamente. = Roller restraint direction changed. Run the analysis again.
Apoio girado visualmente; as restrições e os resultados de cálculo não mudam. = Support symbol rotated; restraints and analysis results are unchanged.
Grelha: +w em Z; θx/θy e torção pela mão direita. Reações: Rz, Mx, My. Diagramas amostrados. = Grillage: +w along Z; θx/θy and torsion follow the right-hand rule. Reactions: Rz, Mx, My. Diagrams use sampled values.
Sinais: = Sign convention:
N+ tração = N+ tension
V+ força local esquerda = V+ on the local left face
M+ sagente, fibra inferior = M+ sagging, bottom fibre in tension
momentos anti-horários. Diagramas: escala comum por esforço; leitura interpolada entre amostras. = counterclockwise moments. Each force component uses a common diagram scale; hover values are interpolated between samples.
Deformada ampliada × = Deflection magnification ×
deslocamentos em = displacements in
x desde o início da barra = x measured from the member start
w fora do plano representado esquematicamente na vertical. = Out-of-plane w is shown schematically in the vertical direction.
δx/δy globais; θ em rad. Passe o mouse sobre a curva. = Global δx/δy; θ in rad. Hover over the curve to read values.
δx/δy globais. = Global δx/δy.
livre = released
Verifique o modelo = Check the model
Modelo alterado. Calcule novamente. Unidades internas: kN, m, rad; EA em kN; EI em kN·m². = Model changed. Run the analysis again. Internal units: kN, m, rad; EA in kN; EI in kN·m².
Crie uma barra antes de atribuir um perfil. = Create a member before assigning a cross-section.
Crie uma barra antes de atribuir um material. = Create a member before assigning a material.
Aplicar perfil a barras = Assign section to members
Números das barras separados por vírgula, ou * para todas: = Enter member numbers separated by commas, or * for all members:
Informe números de barras existentes. = Enter valid member numbers.
Informe barras existentes. = Enter valid member numbers.
Aplicar material = Assign material
Salvar relatório de análise = Save analysis report
Abrir projeto = Open project
Salvar projeto = Save project
Liberação de momento = Member end moment release
Escolha a extremidade. Uma rótula existente será removida. = Choose an end. An existing moment release will be removed.
Início — nó = Start — node
Fim — nó = End — node
Calcule o modelo antes de exportar resultados. = Analyze the model before exporting results.
Não foi possível gravar a imagem. = The image could not be saved.
Imagem = Image
Resultados = Results
Deslocamentos = Displacements
Relatório = Report
Projeto = Project
Resíduos de equilíbrio: = Equilibrium residuals:
Relatório PDF salvo com tabelas e diagramas: = PDF report saved with tables and diagrams:
Clique sobre uma barra para aplicar = Click a member to apply
Estas ferramentas de carga e liberação são para vigas, pórticos e arcos. Treliças já são biarticuladas; grelhas mantêm as limitações descritas na documentação. = These load and release tools apply to beams, plane frames and arches. Truss members are already pin-ended; grillage limitations are described in the documentation.
Selecione Viga, Pórtico plano ou Arco antes de inserir esta geometria. = Select Beam, Plane frame or Arch before inserting this geometry.
Propriedades do nó = Node properties
Propriedades da barra = Member properties
Coordenada x (m) = x coordinate (m)
Coordenada y (m) = y coordinate (m)
Momento (kN·m) = Moment (kN·m)
Restringir = Restrain
Direção restringida do móvel (° de +X) = Roller restraint direction (° from +X)
Ângulo da normal ao plano de rolamento. Padrão 90° = restrição vertical. Esta direção influencia o cálculo. = Angle of the normal to the rolling plane. Default: 90° for vertical restraint. This direction affects the analysis.
Girar 90° = Rotate 90°
Apoio móvel: o ângulo define a direção física da restrição (normal à rampa), usado no cálculo. = Roller support: the angle defines the physical restraint direction (normal to the rolling plane) used in the analysis.
Engaste e apoio fixo: a orientação é somente visual. As restrições globais em X/Y e, no engaste, rotação, não mudam ao girar. = Fixed and pinned supports: rotation changes only the symbol orientation. Global X/Y restraints and the rotational restraint at fixed supports remain unchanged.
Grelha: os graus de liberdade são w, θx e θy. A orientação do símbolo é apenas visual; w atua fora do plano. = Grillage degrees of freedom are w, θx and θy. Symbol orientation is visual only; w acts out of plane.
Rigidez axial EA (kN) = Axial stiffness EA (kN)
Rigidez à flexão EI (kN·m²) = Flexural stiffness EI (kN·m²)
Carga uniforme local q (kN/m) = Uniform load in local y, q (kN/m)
Rótula no início = Start-end moment release
Rótula no fim = Finish-end moment release
Selecionar / editar perfil da seção = Select / edit cross-section
Cargas distribuídas adicionais (somadas à carga uniforme acima): = Additional distributed loads (added to the uniform load above):
Fórmula avançada = Advanced expression
Remover carga selecionada = Remove selected load
Entrada de coordenadas — Ctrl+E = Coordinate entry — Ctrl+E
Absolutas X, Y = Absolute X, Y
Relativas Δx, Δy ao último nó = Relative Δx, Δy from the last node
Polares: comprimento, ângulo (graus) = Polar: length, angle (degrees)
Entrada exata, independente do snap. Edite X/Y na tabela abaixo. = Enter exact coordinates independently of grid snapping. Edit X/Y in the table below.
Y / Δy (m) / ângulo (°) = Y / Δy (m) / angle (°)
Inserir nó (Enter) = Add node (Enter)
Criar barra entre nós = Create member between nodes
Nó inicial = Start node
Nó final = End node
Insira um nó absoluto antes de usar coordenadas relativas. = Add an absolute node before using relative coordinates.
Comprimento polar deve ser positivo. = Polar length must be positive.
Coordenada inválida. = Invalid coordinate.
Coordenadas devem ser finitas. = Coordinates must be finite.
Barra criada. = Member created.
Coordenadas atualizadas. = Coordinates updated.
Já existe nó nessa posição; edição cancelada. = A node already exists at this position; edit cancelled.
Formato = Load shape
Uniforme = Uniform
Triangular crescente = Triangular — increasing
Triangular decrescente = Triangular — decreasing
Parabólica = Parabolic
Senoidal = Sinusoidal
Por pontos = Tabulated points
Posições em = Position units
Metros = Metres
% do comprimento = % of member length
Início do trecho = Start of loaded interval
Fim do trecho = End of loaded interval
q inicial (kN/m) = Start intensity q (kN/m)
q final (kN/m) = End intensity q (kN/m)
Acréscimo no centro (kN/m) = Additional intensity at mid-interval (kN/m)
Direção = Direction
Vertical global Y = Global Y
Transversal local y = Local transverse y
Adicionar ponto = Add point
Remover ponto = Remove point
Fórmula (avançado) = Expression (advanced)
Avançado = Advanced
x em metros desde o nó inicial; L = comprimento total. Use x^2, sin(pi*x/L), etc. = x in metres from the start node; L is the total member length. Use x^2, sin(pi*x/L), etc.
Valores negativos atuam em −Y ou −y, por metro real de barra (não por projeção). Na parábola/senoide, o acréscimo é somado à reta entre q inicial e final. Pontos são unidos por segmentos lineares. = Negative values act along −Y or −y, per unit of actual member length (not projected length). For parabolic/sinusoidal loads, the additional intensity is superimposed on the line between the end intensities. Tabulated points are joined by straight segments.
Aplicar carga = Apply load
Cancelar = Cancel
Verifique a carga = Check the load
Preencha os campos para visualizar a carga. = Enter the parameters to preview the load.
Preencha x e q em todas as linhas. = Enter x and q in every row.
Informe pelo menos dois pontos. = Enter at least two points.
Informe uma expressão matemática. = Enter a mathematical expression.
O trecho deve satisfazer 0 ≤ início < fim ≤ comprimento da barra. = The loaded interval must satisfy 0 ≤ start < end ≤ member length.
Resultante nula: posição da resultante não definida. = The resultant is zero; its position is undefined.
Resultante = Resultant
Posição = Position
Função personalizada = Custom load
Exemplo: parábola −10·(x/L)² = Example: parabola −10·(x/L)²
Desenhar arco = Draw arch
Forma do arco = Arch shape
Parabólico = Parabolic
Circular = Circular
X inicial (m) = Start X (m)
Y inicial (m) = Start Y (m)
X final (m) = End X (m)
Y final (m) = End Y (m)
Flecha normal à corda (m) = Rise normal to the chord (m)
Número de segmentos = Number of segments
O arco será acrescentado ao desenho. Extremos coincidentes com nós existentes serão unidos. = The arch will be added to the model. Endpoints coincident with existing nodes will be merged.
A geometria é aproximada por barras retas; apoios, seção, material e cargas são definidos após inserir. = Geometry is approximated by straight members. Define supports, sections, materials and loads after insertion.
Inserir arco = Insert arch
Ajuste os parâmetros para visualizar o arco. = Set the parameters to preview the arch.
Verifique o arco = Check the arch
A flecha deve ser positiva. = The arch rise must be positive.
Para arco circular use 0 < flecha ≤ metade da distância entre extremos. = A circular arch requires 0 < rise ≤ half the distance between endpoints.
Perfil e propriedades geométricas = Cross-section and geometric properties
Família = Section shape
Unidade das dimensões = Dimension units
Inércia de flexão usada = Second moment of area used for bending
Sobrescrever = Override
Restaurar valores calculados = Restore calculated values
Como foi calculado = Calculation details
Aplicar perfil = Apply section
Verifique o perfil = Check the section
Verifique: = Check:
Valor definido pelo material da barra. Use o botão Material para alterar. = Value defined by the member material. Use Material to change it.
Genérico — personalizar = Generic — customize
Quadrado = Square
Circular maciço = Solid circular
Tubo circular = Circular hollow
Caixão = Rectangular hollow
Arbitrário = General properties
Personalizado = Custom
dimensões nominais = nominal dimensions
Concreto — 20 × 40 cm = Concrete — 20 × 40 cm
Madeira serrada — 6 × 12 cm = Sawn timber — 6 × 12 cm
Perfis nominais IPE/UPE: dimensões ArcelorMittal; cálculo com cantos vivos, sem raios. = Nominal IPE/UPE sections: ArcelorMittal dimensions; sharp-corner geometry without fillets.
Propriedades geométricas aproximadas, diferentes das tabelas de laminação. E e G são dados do material. = Geometric properties are approximate and differ from rolled-section tables. E and G are material properties.
VALORES SOBRESCRITOS: = OVERRIDDEN VALUES:
A, Ix, Iy e J arbitrários devem ser positivos. = General properties A, Ix, Iy and J must be positive.
Sobrescritas exigem A/Ix/Iy/J positivos e finitos. = Overrides require positive, finite A/Ix/Iy/J values.
Família de seção desconhecida. = Unknown cross-section shape.
b e h devem ser positivos. = b and h must be positive.
Dimensões devem ser finitas. = Dimensions must be finite.
t deve ser positivo e menor que b/2 e h/2. = t must be positive and less than b/2 and h/2.
Exige d > 0 e, no tubo, 0 < t < d/2. = Requires d > 0 and, for hollow sections, 0 < t < d/2.
Exige 0 < tw < b e 0 < tf < h/2. = Requires 0 < tw < b and 0 < tf < h/2.
J aproximado por Bredt para parede fina fechada; cantos vivos. = J approximated using Bredt’s formula for thin-walled closed sections; sharp corners.
J aproximado Σ(l·t³/3), parede fina aberta; sem raios de concordância ou empenamento. = J approximated as Σ(l·t³/3) for thin-walled open sections; fillets and warping are excluded.
Valores arbitrários informados pelo usuário. Centroide e W exigem geometria e não são inferidos. = General properties supplied by the user. The centroid and elastic section modulus W require geometry and are not inferred.
Cantoneira: Ix/Iy geométricos não são eixos principais; o motor plano não inclui flexão acoplada. = Angle section: the geometric x/y axes are not principal axes; the plane-frame solver does not include coupled bending.
W=I/cmáx; r=√(I/A). = W=I/c_max; r=√(I/A).
n ímpar (100 termos) = odd n (100 terms)
Material e propriedades físicas = Material and physical properties
Nome do material = Material name
Módulo de elasticidade E (MPa) = Young’s modulus E (MPa)
Módulo de cisalhamento G (MPa) = Shear modulus G (MPa)
Coeficiente de Poisson ν = Poisson’s ratio ν
Peso específico γ (kN/m³) = Unit weight γ (kN/m³)
Dilatação térmica α (1/°C) = Thermal expansion coefficient α (1/°C)
Aço — referência didática = Steel — educational reference
Concreto — referência didática = Concrete — educational reference
Madeira — equivalente isotrópico = Timber — isotropic equivalent
Alumínio — referência didática = Aluminium — educational reference
E e G, junto da seção, definem EA, EI e GJ. α é usado na temperatura uniforme. = E and G, together with the cross-section, define EA, EI and GJ. α is used for uniform temperature changes.
γ é armazenado; o programa não aplica peso próprio automaticamente. = γ is stored; self-weight is not applied automatically.
Presets são referências didáticas editáveis, não valores normativos por classe. = Presets are editable educational references, not code-specified design values.
Madeira: modelo isotrópico equivalente; ortotropia não é considerada. = Timber uses an equivalent isotropic model; orthotropy is not considered.
Unidades internas: E/G × 1000 → kN/m². Sem seção atribuída, EA/EI/GJ existentes são mantidos. = Internal units: E/G × 1000 → kN/m². Existing EA/EI/GJ are retained when no cross-section is assigned.
Verifique o material = Check the material
Informe o nome do material. = Enter the material name.
As propriedades do material devem ser finitas. = Material properties must be finite.
E e G devem ser positivos e finitos. = E and G must be positive and finite.
E e G devem ser positivos. = E and G must be positive.
Coeficiente de Poisson deve estar entre −1 e 0,5 (exclusivos). = Poisson’s ratio must be strictly between −1 and 0.5.
Peso específico não pode ser negativo. = Unit weight cannot be negative.
Nome do projeto = Project name
Forças e momentos nos resultados = Result force and moment units
Deslocamentos nos resultados = Result displacement units
Casas decimais = Decimal places
Zero de esforços/reação (kN, kN·m) = Force/reaction zero threshold (kN, kN·m)
Zero relativo dos deslocamentos = Relative displacement zero threshold
Exibir grade = Show grid
Capturar pontos na grade (snap) = Snap points to grid
Passo da grade (m) = Grid spacing (m)
Amplificação da deformada (×) = Deflection magnification (×)
Mostrar valores nos diagramas = Show diagram values
Geometria e entrada de coordenadas permanecem em metros. As unidades acima são de apresentação; não alteram o modelo ou a precisão do cálculo. = Geometry and coordinate input remain in metres. These are display units; they do not change the model or analysis precision.
Editor de dados para diagnóstico. Use somente se necessário. = Data editor for diagnostics. Use only when necessary.
Abrir editor JSON do projeto = Open project JSON editor
Aplicar preferências = Apply settings
Sem título = Untitled
Modelo: índices i/j começam em zero; q local positivo em +y = Model: i/j indices start at zero; positive local q acts along +y
Reações de apoio = Support reactions
Resumo de máximos e mínimos = Maximum and minimum results
Esforço normal = Axial force
Esforço cortante = Shear force
Momento fletor = Bending moment
Momento torçor = Torsional moment
Mínimo = Minimum
Máximo = Maximum
Mín. = Min.
Máx. = Max.
x mín. (m) = x at min. (m)
x máx. (m) = x at max. (m)
Resultado = Result
■  RELATÓRIO DE RESULTADOS // ESTRUTURAL = ■  ANALYSIS RESULTS // ESTRUTURAL
ESTRUTURAL // RESULTADOS = ESTRUTURAL // RESULTS
Estrutural // resultados = Estrutural // results
PÁG. = PAGE
FIG. 01 // Modelo, apoios e cargas. Geometria em m. = FIG. 01 // Model, supports and loads. Geometry in m.
N+ tração · V+ face esquerda · M+ sagente · T pela mão direita. = N+ tension · V+ on the left face · M+ sagging · T follows the right-hand rule.
Módulo |δ| em = Displacement magnitude |δ| in
deformada ampliada para leitura. = deflected shape magnified for clarity.
Extremos da discretização/interpolação. x medido desde o início de cada barra. = Extrema from discretization/interpolation. x is measured from the start of each member.
Amplificação × = Magnification ×
Calcule um modelo antes de emitir o relatório. = Analyze a model before generating a report.
O relatório PDF não foi gravado. = The PDF report could not be saved.
EXEMPLOS POR TIPOLOGIA = EXAMPLES BY STRUCTURE TYPE
Escolha um exemplo para carregar e calcular. Esc fecha esta janela. = Select an example to load and analyze. Press Esc to close.
Biapoiada — carga uniforme = Simply supported beam — uniform load
Balanço — força na ponta = Cantilever — tip force
Contínua — dois vãos = Continuous beam — two spans
Portal biengastado = Fixed-base portal frame
Portal — duas águas = Gable frame
Pórtico — dois pavimentos = Two-storey frame
Triangular simples = Simple triangular truss
Parabólico triarticulado = Three-hinged parabolic arch
Circular biarticulado = Two-hinged circular arch
Arco — carga no centro = Arch — crown load
Grelha em L = L-shaped grillage
Grelha — viga transversal = Grillage — transverse beams
Malha 2×2 = 2×2 grillage
Vão 6 m, q=10 kN/m. = Span 6 m, q=10 kN/m.
Ry=30 kN em cada apoio; Mmáx=qL²/8=45 kN·m. = Ry=30 kN at each support; M_max=qL²/8=45 kN·m.
Balanço de 3 m, P=10 kN. = 3 m cantilever, P=10 kN.
Dois vãos de 6 m e q=10 kN/m. = Two 6 m spans carrying q=10 kN/m.
Reações 22,5 / 75 / 22,5 kN; momento no apoio central −45 kN·m. = Reactions 22.5 / 75 / 22.5 kN; bending moment at the intermediate support −45 kN·m.
Portal de 4×3 m com força horizontal de 10 kN. = 4×3 m portal frame with a 10 kN lateral force.
ΣRx=-10 kN; ΣRy=0; equilíbrio de momento externo 30 kN·m. = ΣRx=-10 kN; ΣRy=0; external moment equilibrium: 30 kN·m.
Cobertura simétrica com força vertical na cumeeira. = Symmetric pitched frame with a vertical force at the ridge.
Por simetria: Ry=10 kN em cada base; deslocamento horizontal da cumeeira nulo. = By symmetry: Ry=10 kN at each base; zero horizontal displacement at the ridge.
Dois pavimentos de 3 m; forças horizontais e verticais. = Two 3 m storeys; lateral and vertical forces.
ΣRx=-15 kN; ΣRy=40 kN; verificar equilíbrio e reciprocidade. = ΣRx=-15 kN; ΣRy=40 kN; check equilibrium and reciprocity.
Triângulo isostático, P=10 kN no vértice. = Statically determinate triangular truss with P=10 kN at the apex.
Banzo inferior +5 kN; diagonais −5√2 kN; reações +5 kN. = Bottom chord +5 kN; diagonals −5√2 kN; reactions +5 kN.
Quatro painéis de 2 m; altura 2 m; 10 kN por nó superior. = Four 2 m panels; height 2 m; 10 kN at each top chord node.
Ry=20 kN por apoio; esforços conferidos por equilíbrio de cada nó. = Ry=20 kN per support; member forces checked using joint equilibrium.
Triângulos alternados com cargas de 10 kN nos nós superiores. = Alternating triangles with 10 kN loads at the top chord nodes.
Ry=15 kN por apoio; esforços conferidos por equilíbrio de cada nó (isostática). = Ry=15 kN per support; member forces checked using joint equilibrium (statically determinate).
Vão 6 m, flecha 2 m; 16 segmentos retos. Carga uniforme por projeção horizontal. = Span 6 m, rise 2 m; 16 straight segments. Uniform load per unit of horizontal projection.
Uniforme: Ry=30 kN por apoio; triarticulado H=qL²/8f=22,5 kN. = Uniform load: Ry=30 kN per support; three-hinged arch H=qL²/8f=22.5 kN.
Ry=30 kN por apoio; simetria, equilíbrio e convergência de discretização. = Ry=30 kN per support; symmetry, equilibrium and mesh convergence.
Viga principal biengastada e dois balanços transversais. = Main beam fixed at both ends with two transverse cantilevers.
Rz=10 kN por base; simetria; ΣRz=20 kN. = Rz=10 kN per support; symmetry; ΣRz=20 kN.
Balanço em L; Fz=-10 kN na ponta. = L-shaped cantilever; Fz=-10 kN at the free end.
Rz=10 kN; Mx=20 kN·m; My=-30 kN·m; w ponta=−0,01783333 m (energia). = Rz=10 kN; Mx=20 kN·m; My=-30 kN·m; tip w=−0.01783333 m (energy method).
Quatro células de 2×2 m, qz=-2 kN/m em todas as barras. = Four 2×2 m cells with qz=-2 kN/m on every member.
Comprimento total 24 m; ΣRz=48 kN; simetria entre quatro cantos. = Total member length 24 m; ΣRz=48 kN; symmetry at the four corners.
Ry=10 kN; M=30 kN·m; v=-PL³/3EI=-0,0045 m. = Ry=10 kN; M=30 kN·m; v=-PL³/3EI=-0.0045 m.
Estrutura instável: grau de liberdade sem rigidez. = Unstable structure: a degree of freedom has no stiffness.
Matriz singular: verifique apoios e mecanismos internos. = Singular stiffness matrix: check supports and internal mechanisms.
Análise de segunda ordem ainda não validada e indisponível. = Second-order analysis has not yet been validated and is unavailable.
Insira ao menos dois nós e uma barra. = Add at least two nodes and one member.
Rigidez de mola deve ser não negativa. = Spring stiffness must be non-negative.
Barra referencia nó inexistente. = A member references a node that does not exist.
Barra de comprimento zero: separe seus nós extremos. = Zero-length member: separate its end nodes.
Barra de comprimento zero. = Zero-length member.
EA e EI devem ser positivos, em kN e kN·m². = EA and EI must be positive, in kN and kN·m².
Treliça aceita cargas pontuais nos nós; barras já são biarticuladas. = Trusses accept nodal point loads; members are already pin-ended.
Trecho de carga fora da barra. = The loaded interval lies outside the member.
Carga pontual fora da barra. = The point load lies outside the member.
Tipologia inválida. = Invalid structure type.
Há nós duplicados. Ajuste as coordenadas antes de continuar. = Duplicate nodes found. Adjust their coordinates before continuing.
Índice de nó inválido. = Invalid node index.
Ângulo de apoio deve ser finito. = Support angle must be finite.
Cancelar = Cancel
Fechar = Close
Sim = Yes
Não = No
Inserir = Insert
Não foi possível = Could not
deve ser numérico e finito. = must be numeric and finite.
inserido: = inserted:
desde o início da barra. = from the member start.
na barra (m) = along member (m)
''')

CATALOGO['Calcular G = E / [2(1 + ν)]']='Calculate G = E / [2(1 + ν)]'
CATALOGO['A, Ix, Iy e J\ninformados diretamente']='A, Ix, Iy and J\nspecified directly'
CATALOGO['θext']='θend'
_pares('''
Eixo de carga aceita local_y ou global_y; cargas projetadas não estão implementadas. = Load axes must be local_y or global_y; projected loads are not implemented.
Grelha exige comprimento, EI e GJ positivos. = Grillage members require positive length, EI and GJ.
Grelha sem nós ou barras. = The grillage has no nodes or members.
Grelha: esta versão aceita apenas cargas pontuais nos nós e uniformes locais. = Grillage analysis currently supports only nodal point loads and uniform local member loads.
Barra de comprimento nulo. = Zero-length member.
Constante inválida. = Invalid constant.
Dimensões devem ser positivas. = Dimensions must be positive.
Diâmetro deve ser positivo. = Diameter must be positive.
Expoente deve ser constante entre 0 e 12. = The exponent must be a constant between 0 and 12.
Extremos do arco devem ser distintos. = Arch endpoints must be distinct.
Função muito complexa. = The load expression is too complex.
Função muito longa (máximo 200 caracteres). = The load expression is too long (maximum 200 characters).
Função não permitida. = Function not allowed.
Integração da carga não convergiu. Simplifique a função ou divida o trecho. = Load integration did not converge. Simplify the expression or split the loaded interval.
Já existe barra entre esses nós. = A member already connects these nodes.
Momento aplicado em rotação totalmente liberada. = A moment is applied to a fully released rotational degree of freedom.
Nome desconhecido na função: = Unknown name in the load expression:
Nó inexistente. = Node does not exist.
Os nós extremos devem ser diferentes. = Member end nodes must be distinct.
Resultado não finito. = The result is not finite.
Use apenas números, x, L, pi, operadores e funções permitidas. = Use only numbers, x, L, pi, and supported operators and functions.
Use entre 2 e 1000 segmentos. = Use between 2 and 1000 segments.
Use pelo menos dois pontos finitos com x crescente e distinto. = Use at least two finite points with distinct x coordinates in ascending order.
Função de carga inválida em = Invalid load expression at
Já existe um nó nessa posição: nó = A node already exists at this position: node
Propriedade de barra desconhecida ou não implementada. = Unknown or unsupported member property.
Propriedade de projeto desconhecida. Consulte docs/VERSAO_02.md. = Unknown project property. See docs/VERSAO_02.md.
Propriedade nodal desconhecida. = Unknown nodal property.
pórticos exigem três componentes. = plane frames require three components.
use dois ou três valores numéricos finitos. = use two or three finite numeric values.
Rigidez direta = Direct stiffness values
Verifique as dimensões = Check the dimensions
Sinais: N+ tração · M+ sagente (fibra inferior) · V+ força local esquerda · forças +X/+Y · momento anti-horário. = Sign convention: N+ tension · M+ sagging (bottom fibre in tension) · V+ on the local left face · forces +X/+Y · counterclockwise moment.
Português (Brasil) = Portuguese (Brazil)
momentos anti-horários. = counterclockwise moments.
Diagramas: escala comum por esforço; leitura interpolada entre amostras. = Diagrams share a scale for each force component; hover values are interpolated between samples.
''')
_pares('''
Criado por Matheus Schardosim = Created by Matheus Schardosim
Arraste para selecionar ou mover. Ctrl/Shift combina seleções; duplo clique edita. Esc cancela. = Drag to select or move. Ctrl/Shift adds to or removes from the selection; double-click to edit. Esc cancels.
Mostrar ou ocultar entrada por coordenadas X/Y. = Show or hide X/Y coordinate entry.
Inserir (Enter) = Insert (Enter)
Novo trecho = New chain
Coordenadas inseridas. Para barras, informe o próximo ponto ou use Novo trecho. = Coordinates entered. For members, enter the next point or choose New chain.
O movimento deixaria uma carga fora da barra. = This move would leave a load outside its member.
Movimento cancelado: = Move cancelled:
''')
_pares('''
Criado por = Created by
Abrir GitHub ou LinkedIn de Matheus Schardosim. = Open Matheus Schardosim’s GitHub or LinkedIn profile.
Pórtico inclinado — referência = Inclined frame — reference
Referência da imagem: painéis de 2 m, níveis de 3 m e rótula em G. 1 tf equivale a 9,80665 kN. Carga de 1 tf/m por projeção horizontal em C–G–H; forças de 2 tf em F/I e 4 tf em D. Hipótese: 6 tf·m anti-horário no lado horizontal de G. = Image reference: 2 m panels, 3 m storeys and a hinge at G. 1 tf = 9.80665 kN. UDL of 1 tf/m per horizontal metre along C–G–H; 2 tf forces at F/I and 4 tf at D. Assumption: 6 tf·m counterclockwise on the horizontal side of G.
Hipótese M_G=+6 tf·m: A=(+2,5; +6,75) tf; B=(−2,5; +9,25) tf. Rótula no fim de FG. = Assumed M_G=+6 tf·m: A=(+2.5; +6.75) tf; B=(−2.5; +9.25) tf. Moment release at the G end of FG.
''')
_pares('''
Abrir GitHub, LinkedIn ou e-mail de Matheus Schardosim. = Open Matheus Schardosim’s GitHub, LinkedIn or email.
Pórtico inclinado = Inclined frame
Painéis de 2 m, níveis de 3 m e rótula em G. Carga de 10 kN/m por projeção horizontal em C–G–H; forças de 20 kN em F/I e 40 kN em D. Momento de 60 kN·m anti-horário no lado horizontal de G. = 2 m panels, 3 m storeys and a hinge at G. UDL of 10 kN/m per horizontal metre along C–G–H; 20 kN forces at F/I and 40 kN at D. A 60 kN·m counterclockwise moment acts on the horizontal side of G.
A: Rx=+25 kN, Ry=+67,5 kN. B: Rx=−25 kN, Ry=+92,5 kN. Momento nulo no fim de FG. = A: Rx=+25 kN, Ry=+67.5 kN. B: Rx=−25 kN, Ry=+92.5 kN. Zero bending moment at the G end of FG.
Vão 6 m, flecha 2 m; 16 segmentos retos. = Span 6 m, rise 2 m; 16 straight segments.
Força vertical de 20 kN no centro. = A 20 kN vertical force at the crown.
Carga uniforme de 10 kN/m por projeção horizontal. = UDL of 10 kN/m per horizontal metre.
projeção X = horizontal projection
Substituir arquivo? = Replace file?
Já existe um arquivo com este nome: = A file with this name already exists:
Deseja substituí-lo? = Do you want to replace it?
''')
CATALOGO['Alternar entre português, inglês e francês.'] = 'Switch between Portuguese, English and French.'
_CATALOGOS = {'en_US': CATALOGO, 'fr_FR': CATALOGO_FR}
CATALOGO['todas as barras']='all members'
CATALOGO_FR['todas as barras']='toutes les barres'
CATALOGO['w em Z, fora do plano XY; geometria original sem amplificação.'] = 'w along Z, out of the XY plane; original geometry without magnification.'
CATALOGO_FR['w em Z, fora do plano XY; geometria original sem amplificação.'] = 'w suivant Z, hors du plan XY ; géométrie initiale sans amplification.'
CATALOGO.update({
    'Dados do modelo devem ser finitos.':'Model data must be finite.',
    'Tipo de estrutura desconhecido.':'Unknown structure type.',
    'Coordenadas dos nós devem ser numéricas.':'Node coordinates must be numeric.',
    'Vetor nodal inválido:':'Invalid nodal vector:',
    'Rigidez ou carregamento fora da faixa numérica do cálculo.':'Stiffness or loading exceeds the numerical range of the analysis.',
})
CATALOGO_FR.update({
    'Dados do modelo devem ser finitos.':'Les données du modèle doivent être finies.',
    'Tipo de estrutura desconhecido.':'Type de structure inconnu.',
    'Coordenadas dos nós devem ser numéricas.':'Les coordonnées des nœuds doivent être numériques.',
    'Vetor nodal inválido:':'Vecteur nodal non valide :',
    'Rigidez ou carregamento fora da faixa numérica do cálculo.':'La rigidité ou le chargement dépasse la plage numérique du calcul.',
})
_PADROES = {idioma: re.compile('|'.join(re.escape(k) for k in sorted(catalogo, key=len, reverse=True)))
            for idioma, catalogo in _CATALOGOS.items()}


def traduzir(texto, idioma='pt_BR'):
    if idioma not in _CATALOGOS or not texto:
        return texto
    catalogo = _CATALOGOS[idioma]
    if texto in catalogo:
        return catalogo[texto]
    # Composed strings retain numeric values, markup, units and user formulae.
    # Never replace pieces inside another word or a HTML/CSS attribute.
    def replace(m):
        a, b = m.span()
        if a and texto[a-1].isalpha() or b < len(texto) and texto[b].isalpha():
            return m.group()
        return catalogo[m.group()]
    resultado=_PADROES[idioma].sub(replace, texto)
    return re.sub(r'(?<=\d) a (?=[−+\-\d])', ' à ' if idioma == 'fr_FR' else ' to ', resultado)
