# Extremos dos esforços e discretização dos arcos

O máximo exibido anteriormente era o maior dos valores amostrados em 41 posições por barra. Um extremo entre essas posições podia ser subestimado. Agora a malha visual é complementada com as raízes de `V(x)=0` para os extremos de momento e com os zeros das componentes da carga distribuída para os extremos de cortante e normal.

Para cargas uniformes, trapezoidais e tabelas lineares por trechos, essas raízes são calculadas analiticamente em cada trecho contínuo. Limites de cargas, pontos da tabela e forças ou momentos concentrados delimitam os trechos. Os dois lados dos saltos continuam representados; uma troca de sinal causada por uma força concentrada não é tratada como uma raiz contínua do cortante.

Funções de carga arbitrárias usam subdivisão e bisseção numérica. Oscilações mais rápidas que a busca não têm garantia de serem todas identificadas: divida o trecho ou compare os resultados com uma referência independente nesses casos.

Os pontos críticos fazem parte de `resultado['barras'][i]['pontos']`. Portanto a tela, o CSV e os resumos do PDF usam os mesmos extremos refinados. Código que consome esse vetor deve consultar `x`, sem assumir comprimento fixo ou índice fixo para o meio da barra.

Em uma força ou momento concentrado, os limites esquerdo e direito aparecem na mesma coordenada `x`, nessa ordem, com o campo `lado` no resultado. Assim o máximo junto a um salto não é avaliado em uma seção artificialmente afastada por epsilon. O CSV conserva as duas linhas na mesma posição.

## Verificações analíticas

| Caso | Máximo com 41 posições | Máximo refinado |
| --- | ---: | ---: |
| Trecho com `V(x)=50-10x²` | 14,531250 kN·m | 14,535599 kN·m, em x=√5 m |
| Pequeno momento positivo junto à rótula do pórtico | 0,038438 kN·m | 0,050281 kN·m |

As regressões em `tests/test_extremos.py` também cobrem grelha, cargas parciais, tabelas, funções, saltos, grandezas pequenas e deslocamentos sob carga horizontal em barra inclinada.

## Carga horizontal e projeções

`distribuidas[].eixo` aceita `global_x`, `global_y` ou `local_y`. A direção global X também está disponível no formulário, no desenho e no PDF. A intensidade é sempre por metro real da barra. Para uma intensidade uniforme `qh` por projeção vertical e `qv` por projeção horizontal, em uma barra de comprimento `L`:

```python
barra['distribuidas'] = [
    {'qa': qh * abs(dy) / L, 'eixo': 'global_x'},
    {'qa': qv * abs(dx) / L, 'eixo': 'global_y'},
]
```

Isso permite representar as duas cargas continuamente em cada segmento, em vez de substituí-las por uma força pontual no meio. Projetos anteriores são conservados: cargas pontuais existentes não são transformadas automaticamente em cargas distribuídas.

## Arcos continuam sendo barras retas

A busca correta do extremo de um segmento não transforma um polígono em um elemento curvo exato. Compare malhas sucessivas. O formulário agora inicia com 96 segmentos e permite até 200; o número escolhido continua explícito e os projetos existentes não são remalhados silenciosamente.

Na regressão do quarto de círculo com raio 4 m, carga horizontal de 30 kN/m por projeção vertical e vertical de -20 kN/m por projeção horizontal, o máximo da curva contínua é 20 kN·m. Cargas contínuas e refinamento reduzem a diferença; `tests/test_arcos_extremos.py` exige erro absoluto menor que 0,01 kN·m com 96 segmentos e verifica as reações analíticas. Isso demonstra convergência desse caso, sem estabelecer uma tolerância universal para qualquer arco.

## Leitura do desenho

Em arcos com mais de 12 barras, os rótulos numéricos do diagrama se limitam aos extremos globais. Nós de apoio, extremidades, rótulas e o nó selecionado continuam identificados. A seleção e a consulta com o mouse abrangem todas as barras; tabelas e CSV mantêm todos os resultados. Cargas realmente uniformes por projeção recebem um rótulo comum, recalculado a cada edição da geometria ou da carga. Os rótulos que não cabem sem sobreposição são omitidos do desenho.

O objetivo é melhorar a leitura da tela e do PDF sem alterar a análise nem remover dados das exportações tabulares. Os testes de desenho verificam a preservação dos apoios/rótulas, da consulta de cada barra, da identificação dos extremos e da direção das duas cargas globais.
