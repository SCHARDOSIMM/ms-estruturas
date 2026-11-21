$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
$workspace = (Get-Location).Path
$qaPath = [IO.Path]::GetFullPath((Join-Path $workspace 'tmp\instalacao-qa'))
if (-not $qaPath.StartsWith(($workspace + '\tmp\'),[StringComparison]::OrdinalIgnoreCase)) { throw 'Destino de teste fora da pasta autorizada.' }
if (Test-Path -LiteralPath $qaPath) { throw 'A pasta de instalacao de teste ja existe. Verifique-a antes de repetir.' }
$registryPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{57F94E5A-F04F-4AA4-933F-D8BD4D995DE2}_is1'
if (Test-Path -LiteralPath $registryPath) { throw 'Ja existe uma instalacao registrada. O teste nao deve remove-la.' }
$before = & .\.venv\Scripts\python empacotamento\hash_preferencias.py
$setup = (Resolve-Path -LiteralPath 'entrega\MS-Estruturas-1.0.4-Setup.exe').Path
$setupLog = Join-Path $workspace 'build\teste-instalar.log'
$argsInstall = @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/sematalho=1',('/DIR="'+$qaPath+'"'),('/LOG="'+$setupLog+'"'))
$installed = Start-Process -FilePath $setup -ArgumentList $argsInstall -WindowStyle Hidden -Wait -PassThru
if ($installed.ExitCode -ne 0) { throw ('Instalador retornou '+$installed.ExitCode) }
$exe = Join-Path $qaPath 'MS Estruturas.exe'
if (-not (Test-Path -LiteralPath $exe)) { throw 'Executavel instalado ausente.' }
$out = Join-Path $workspace 'tmp\instalado-verificacao'
$originalPath = $env:PATH
$originalPythonPath = $env:PYTHONPATH
$originalPythonHome = $env:PYTHONHOME
try {
    $env:PYTHONPATH='';$env:PYTHONHOME='';$env:PATH="$env:SystemRoot\System32;$env:SystemRoot"
    $checked = Start-Process -FilePath $exe -ArgumentList @('--verificar-instalacao',('"'+$out+'"')) -WorkingDirectory $env:TEMP -WindowStyle Hidden -Wait -PassThru
    if ($checked.ExitCode -ne 0) { throw ('Verificacao retornou '+$checked.ExitCode) }
} finally {
    $env:PATH=$originalPath;$env:PYTHONPATH=$originalPythonPath;$env:PYTHONHOME=$originalPythonHome
}
$result = Get-Content -LiteralPath (Join-Path $out 'verificacao.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $result.ok -or $result.exemplos.Count -ne 17 -or $result.verificacoes.Count -lt 50) { throw 'Falha nos testes do aplicativo instalado.' }
$uninstaller = Join-Path $qaPath 'unins000.exe'
$removed = Start-Process -FilePath $uninstaller -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -WindowStyle Hidden -Wait -PassThru
if ($removed.ExitCode -ne 0) { throw ('Desinstalador retornou '+$removed.ExitCode) }
for ($i=0;$i -lt 50 -and (Test-Path -LiteralPath $exe);$i++) { Start-Sleep -Milliseconds 200 }
if (Test-Path -LiteralPath $exe) { throw 'Executavel nao foi removido.' }
if (Test-Path -LiteralPath $registryPath) { throw 'Registro de desinstalacao nao foi removido.' }
$after = & .\.venv\Scripts\python empacotamento\hash_preferencias.py
if ($before -ne $after) { throw 'As preferencias reais do usuario foram alteradas.' }
$summary = [pscustomobject]@{Instalacao=$true;ExecutavelIndependente=$true;Exemplos=$result.exemplos.Count;Verificacoes=$result.verificacoes.Count;Desinstalacao=$true;PreferenciasPreservadas=$true;PastaDeTesteRemovida=(-not (Test-Path -LiteralPath $qaPath))}
$summary | ConvertTo-Json | Set-Content -LiteralPath 'build\validacao-instalador.json' -Encoding UTF8
$summary | Format-List
