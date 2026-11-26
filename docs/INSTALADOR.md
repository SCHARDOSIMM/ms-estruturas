# Instalador MS Estruturas 1.0.5

## Para usar e distribuir

O produto para o usuário é **entrega/MS-Estruturas-1.0.5-Setup.exe**.
Instale e abra **MS Estruturas** pelo menu Iniciar.
O assistente oferece opções para criar um atalho na área de trabalho e abrir
o programa ao concluir. Em uma instalação nova, ambas começam desmarcadas.
Nenhuma instalação de Python é necessária.
A pasta `entrega` também contém instruções curtas e o SHA-256 do instalador.

A instalação final foi concluída neste computador em:
`%LOCALAPPDATA%\Programs\MS Estruturas`.
Esse é um local próprio para programas instalados por usuário, sem exigir
elevação administrativa. A versão instalada ocupa aproximadamente 62,34 MiB,
incluindo o desinstalador. Os componentes ficam na subpasta `_internal`.

O diretório do programa contém o executável, uma pasta interna de componentes
e o desinstalador. Não leva `.venv`, código de testes, imagens de revisão,
relatórios de exemplo, compiladores ou ferramentas de desenvolvimento.

O primeiro salvamento sugere **Documentos\MS Estruturas**. A pasta só é criada
ao usar o diálogo de salvamento. Os diálogos lembram o último local escolhido.
Projetos e relatórios continuam podendo ser salvos em qualquer pasta escolhida.

Para desinstalar, use Configurações do Windows → Aplicativos → MS Estruturas.
Projetos, relatórios e preferências do usuário são preservados. A pasta original
deste projeto fica exclusivamente como ambiente de desenvolvimento/manutenção.

## O que foi empacotado

Python 3.13 x64, PyQt5/QtCore/QtGui/QtWidgets/QtSvg, ReportLab e suas dependências
necessárias. Permanecem os recursos de ícones, a tradução de interface do Qt
para português e as fontes livres de fallback do ReportLab. Avisos e textos
de licença acompanham o aplicativo em `_internal\Licencas`.

Foram excluídos Qt Quick/QML, WebEngine, multimídia, módulos de testes,
ferramentas científicas não usadas, idiomas adicionais, suporte AVIF do Pillow
e renderizadores OpenGL/ANGLE que não participam do canvas raster.
O pacote executável caiu de 78,30 para 57,88 MiB antes de adicionar o desinstalador.
Os testes foram repetidos depois dessa redução.

Foi escolhido um pacote instalado em pasta, comprimido num instalador único.
Isso mantém a abertura direta e evita extrair bibliotecas novamente a cada
execução, como ocorre no modo one-file. Referência: [documentação do PyInstaller](https://www.pyinstaller.org/en/stable/operating-mode.html).
O instalador usa o [Inno Setup](https://jrsoftware.org/inno-setup/downloads),
com instalação por usuário, interface em português, inglês e francês e
desinstalação registrada.

## Validação realizada

- Executável iniciado fora do projeto, com PYTHONHOME/PYTHONPATH vazios e
  PATH restrito ao Windows: nenhuma dependência do Python de desenvolvimento.
- 17 exemplos calculados, com verificação de equilíbrio e deslocamentos finitos.
- 53 verificações no pacote instalado: recursos gráficos, modos de resultado,
  PNG, PDF, CSV, projeto JSON e restauração de preferências.
- PDF do aplicativo instalado reaberto com um parser: cinco páginas com texto
  legível para o exemplo de pórtico inclinado.
- Instalação e desinstalação em pasta de teste: diretório e registro removidos.
- Hash das preferências reais idêntico antes/depois do teste de instalação.
- Instalação final: executável conferido por SHA-256 e atalho apontando para
  a pasta instalada, com diretório de trabalho correto.
- 75 testes automatizados da aplicação passaram antes da montagem final;
  teste adicional cobre a organização das pastas de projetos/relatórios.

Auditoria em `build/validacao-instalador.json`; diagnóstico do executável
instalado em `tmp/instalado-verificacao/verificacao.json`.

## Reproduzir a compilação

O ambiente de desenvolvimento deve conter os requisitos de `requirements.txt`.
As ferramentas de build estão em `requirements-build.txt` e não são distribuídas
como dependências do usuário. `build.ps1` instala essas ferramentas, prepara os
avisos, executa a especificação PyInstaller e compila o Inno Setup.

O compilador oficial Inno Setup 6.7.4 foi baixado da distribuição oficial e sua
assinatura foi validada (Pyrsys B.V.). A cópia de desenvolvimento foi preparada
em modo portátil dentro de `.build-tools/inno`, sem atalhos próprios.
O compilador não é incluído no aplicativo instalado.

```powershell
.\build.ps1
```

Para apenas gerar o pacote, use `-SomenteAplicativo`. A especificação está em
`empacotamento/MS Estruturas.spec`; o instalador é definido em `instalador.iss`.
`empacotamento/testar_instalador.ps1` faz instalação, verificação e desinstalação
em pasta temporária sem criar atalho de teste. Ele se recusa a executar se já
existe uma instalação registrada, para não removê-la acidentalmente.

O instalador e o executável do produto ainda não possuem assinatura digital.
Os arquivos de fonte e as instruções de build permanecem neste projeto para
manutenção; as licenças dos componentes de terceiros são incluídas no pacote.
