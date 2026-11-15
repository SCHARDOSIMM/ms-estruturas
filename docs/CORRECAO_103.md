# MS Estruturas 1.0.3 — cotas dos perfis

Os esquemas de todas as famílias de seção passam a usar a mesma prancha vetorial,
centralizada e escalada uniformemente ao redimensionar a janela.

- Largura b e altura h com linhas de extensão, setas e letras centralizadas.
- Diâmetro d dos perfis circulares e espessura radial t dos tubos.
- Espessura de parede t no caixão, com contorno fechado e vazio interno.
- Espessuras tw da alma e tf das mesas em I/H, U, T e L. Na cantoneira L,
  a cota tf aponta para a aba inferior. Setas externas identificam espessuras
  pequenas sem exagerar a geometria.
- Contornos únicos sem linhas internas de montagem. O caixão usa dois contornos
  com preenchimento par/ímpar; os perfis abertos usam polígonos explícitos,
  evitando falhas de união numérica entre retângulos adjacentes.
- Legendas de símbolos em português e inglês e contraste nos dois temas.

Mantidos os tokens de cor e tipografia da identidade visual. As cotas técnicas,
não especificadas no arquivo de identidade, seguem o desenho usual com setas e
linhas auxiliares finas. O desenho preserva as proporções das dimensões informadas.
Nenhuma propriedade de seção, material ou cálculo foi alterada.

## Conferência

Abrir Perfil e percorrer Retangular, Quadrado, Circular maciço, Tubo circular,
Caixão, I/H, U, T, L e Arbitrário. Alterar as dimensões e a unidade; verificar
as letras, as faces apontadas e o preenchimento. Repetir nos dois temas/idiomas.

Capturas nativas com configurações isoladas:
`docs/verificar_perfis_103.py` → `tmp/perfis-103/`.
O roteiro não altera as preferências reais do usuário.

O instalador 1.0.3 atualiza a instalação existente e preserva as preferências.
O guia de uso anterior permanece identificado como documentação da versão 1.0.2.

Validação: **76 testes existentes passaram**. Revisão visual das dez famílias,
em português/inglês e claro/escuro, com capturas nativas do Qt. O motor de cálculo
e as fórmulas geométricas não foram alterados.

Durante a compilação havia uma cópia 1.0.2 executando diretamente de `dist`.
A distribuição final foi gerada em `tmp/perfis-103/distribuicao-final`, sem fechar
a janela aberta. O parâmetro opcional `AppDistDir` do Inno Setup permite compilar
o instalador dessa pasta; o caminho padrão do build continua sendo `dist`.

O instalador foi aplicado com sucesso à instalação do usuário (versão 1.0.3),
com fechamento automático de aplicativos desativado. A cópia antiga aberta foi
preservada; reabrir pelo atalho carrega a atualização. Dependências ausentes na
distribuição de desenvolvimento foram repostas sem substituir arquivos em uso.
A instalação passou pelo diagnóstico: 17 exemplos e 53 verificações aprovadas.
