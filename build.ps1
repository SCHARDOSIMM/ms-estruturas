# Development/build entry point; the installed app needs none of these tools.
param([switch]$SomenteAplicativo)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& .\.venv\Scripts\python -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw 'Falha ao preparar empacotador.' }
& .\.venv\Scripts\python empacotamento\preparar_avisos.py
if ($LASTEXITCODE -ne 0) { throw 'Falha ao preparar avisos de dependencias.' }
& .\.venv\Scripts\python -m PyInstaller --noconfirm 'empacotamento\MS Estruturas.spec'
if ($LASTEXITCODE -ne 0) { throw 'Falha ao empacotar aplicativo.' }
if ($SomenteAplicativo) { exit 0 }
$compilerPath = Join-Path $PSScriptRoot '.build-tools\inno\ISCC.exe'
if (-not (Test-Path -LiteralPath $compilerPath)) {
    $compilerCommand = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($compilerCommand) { $compilerPath = $compilerCommand.Source }
    else { throw 'Compilador Inno Setup ausente. Consulte docs/INSTALADOR.md.' }
}
& $compilerPath instalador.iss
if ($LASTEXITCODE -ne 0) { throw 'Falha ao compilar instalador.' }
Copy-Item -LiteralPath 'empacotamento\INSTALACAO.txt' -Destination 'entrega\LEIA-ME.txt'
$installer = Get-Item -LiteralPath 'entrega\MS-Estruturas-1.0.5-Setup.exe'
$hash = (Get-FileHash -LiteralPath $installer.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
Set-Content -LiteralPath 'entrega\SHA256SUMS.txt' -Value "$hash  $($installer.Name)" -Encoding ascii
Write-Host 'Instalador pronto em entrega\MS-Estruturas-1.0.5-Setup.exe'
