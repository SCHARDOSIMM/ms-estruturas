# Francês na aplicação

O idioma `fr_FR` está disponível nos fontes, seguindo o mesmo sistema de tradução de apresentação de PT-BR e EN. As configurações oferecem **Français**; o botão rápido percorre PT-BR → EN → FR → PT-BR e indica o próximo idioma. A escolha é salva nas preferências do usuário.

O catálogo francês cobre todas as entradas do catálogo inglês, incluindo mensagens, dicas, exemplos e relatórios. Cabeçalhos textuais de CSV e janelas padrão do Qt também são localizados. Identificadores dos projetos JSON, fórmulas, unidades, precisão numérica e dados editáveis do usuário são preservados. Os números mantêm o formatador de resultados existente; a adição de francês não altera o formato numérico dos CSVs.

## Critérios de terminologia

As traduções usam o vocabulário francês de resistência dos materiais e análise de estruturas. Os textos explicativos foram adaptados ao contexto, sem reproduzir classificações brasileiras de vínculos que não são usuais na França.

| Português | Francês adotado | Observação |
| --- | --- | --- |
| Apoio fixo | Appui articulé | Bloqueia duas translações no modelo plano; rotação livre. Não confundir com encastrement. |
| Apoio móvel | Appui simple | Uma direção de translação bloqueada; direção definida pela normal ao plano de rolamento. |
| Engaste | Encastrement | Translações e rotação bloqueadas. |
| Esforço normal / cortante | Effort normal / tranchant | Esforços internos nas barras. |
| Momento fletor / torçor | Moment fléchissant / de torsion | Preservam-se os símbolos N, V, M e T do aplicativo. |
| Momento sagente positivo | Moment positif avec fibre inférieure tendue | Explicita a convenção física em vez de traduzir literalmente “sagente”. |
| Grelha | Gril de poutres | Rede de barras solicitada fora do plano; não confundir com a grille de desenho. |
| Deformada / balanço / vão | Déformée / console / travée ou portée | Travée para o trecho entre apoios; portée para sua extensão. |
| Alma / mesa | Âme / semelle | Terminologia de perfis metálicos. |
| Inércia de seção | Moment quadratique | Propriedade geométrica de área, distinta de inércia de massa. |
| Peso específico | Poids volumique | γ em kN/m³, distinto de masse volumique. |

## Fontes consultadas

- [Code_Aster — validação de estruturas lineares](https://code-aster.org/doc/v15/V3.html): poutres, portiques plans, treillis, arcs, appuis articulés e encastrements.
- [Code_Aster — carregamentos mecânicos](https://code-aster.org/doc/v15/man_u/u4/u4.44.01.pdf): esforços, repères locaux/globaux e cargas nas barras.
- [Université d’Aix-Marseille — Équation de flexion d’une poutre](https://sebastien-brisard.pedaweb.univ-amu.fr/extranet/R3.08/equation_de_flexion.html): effort tranchant, moment fléchissant e flèche.
- [Code_Aster — características elásticas](https://codeaster.gitlab.io/doc/docaster/manuals/man_r/r4/r4.01.02/Utilisation_dans_Code_Aster.html): module de Young, module de cisaillement, coefficient de Poisson e dilatation thermique.
- [ArcelorMittal — concepção e cálculo de portiques](https://sections.arcelormittal.com/repo/Sections/FR/5_49_SSB04_Conception%2520et%2520calcul%2520des%2520portiques.pdf): âme e semelles dos perfis.
- [Lexique de construction métallique et de résistance des matériaux](https://www.btscm.fr/dicocm/V/vocabulaire/private/protected/LCM-RdM.pdf): gril de poutres e poutres croisées.
- [Autodesk — condições de apoio em francês](https://help.autodesk.com/cloudhelp/2027/FRA/Revit-StructEng/files/GUID-81666153-CD1E-4BC2-8F7D-4CF9C060A467.htm): distinção entre encastré, articulé e appui simple.

## Verificação

`tests/test_idioma_fr.py` verifica cobertura do catálogo, termos técnicos, persistência, escolha nas configurações, alternância com janelas abertas, invariância do modelo e resultados, filtros, cabeçalhos CSV e emissão de relatório francês. O empacotamento inclui `qt_fr.qm` e `qtbase_fr.qm` para manter as janelas padrão em francês na distribuição.

Os guias PDF em português, inglês e francês acompanham a release.
