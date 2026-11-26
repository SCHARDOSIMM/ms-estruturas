# MS Estruturas 1.0.5

- Corrige os máximos e mínimos dos esforços entre os pontos de desenho, incluindo limites dos saltos de forças e momentos.
- Adiciona carga distribuída na direção horizontal global X.
- Melhora a leitura dos arcos com muitas barras e inicia novos arcos com 96 segmentos.
- Mantém a consulta e as tabelas completas por barra, com pontos críticos compartilhados entre tela, CSV e PDF.

Validação dos fontes: 109 testes aprovados, 134 modelos com referência estática independente e 150 modelos calculados/exportados pela interface. O executável também passa pelo diagnóstico de instalação antes da publicação.

Baixe **MS-Estruturas-Setup.exe** para instalar ou atualizar. Projetos e preferências são preservados. O instalador e o aplicativo ainda não possuem assinatura digital.

Os três guias gerais são os da versão 1.0.4. As novidades e os limites desta versão estão no arquivo **EXTREMOS_E_ARCOS.md**. Arcos continuam sendo aproximações por barras retas e exigem comparação de malhas; funções de carga arbitrárias usam busca numérica de extremos.
