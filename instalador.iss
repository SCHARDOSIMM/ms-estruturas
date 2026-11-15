#define AppVersion "1.0.3"
#ifndef AppDistDir
  #define AppDistDir "dist\MS Estruturas"
#endif
[Setup]
AppId={{57F94E5A-F04F-4AA4-933F-D8BD4D995DE2}
AppName=MS Estruturas
AppVersion={#AppVersion}
AppPublisher=Matheus Schardosim
AppPublisherURL=https://github.com/SCHARDOSIMM
AppSupportURL=https://github.com/SCHARDOSIMM
SetupIconFile=estrutural\ui\assets\ms-estruturas.ico
UninstallDisplayIcon={app}\MS Estruturas.exe
DefaultDirName={localappdata}\Programs\MS Estruturas
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=entrega
OutputBaseFilename=MS-Estruturas-{#AppVersion}-Setup
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
WizardStyle=modern
DisableDirPage=yes
DisableProgramGroupPage=yes
DisableReadyPage=yes
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
VersionInfoVersion={#AppVersion}.0
VersionInfoDescription=Instalador do MS Estruturas
VersionInfoCompany=Matheus Schardosim

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#AppDistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userdesktop}\MS Estruturas"; Filename: "{app}\MS Estruturas.exe"; WorkingDir: "{app}"; IconFilename: "{app}\MS Estruturas.exe"; AppUserModelID: "MS.Estruturas"; Check: CriarAtalho

[Run]
Filename: "{app}\MS Estruturas.exe"; Description: "{cm:LaunchProgram,MS Estruturas}"; Flags: nowait postinstall skipifsilent

[Code]
function CriarAtalho: Boolean;
begin
  Result := ExpandConstant('{param:sematalho|0}') <> '1';
end;
