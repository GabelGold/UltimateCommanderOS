; Ultimate Commander OS — Inno Setup
; Christian Schmitt, Solingen — 13. August 2026

#define MyAppName "Ultimate Commander OS"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Christian Schmitt, Solingen"
#define MyAppURL "https://github.com/GabelGold/UltimateCommanderOS"
#define MyAppExeName "UltimateCommanderOS.exe"

[Setup]
AppId={{8F3C2A11-9B44-4D6A-9E21-C0FFEE202601}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\Ultimate Commander OS
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=no
OutputDir=Output
OutputBaseFilename=UltimateCommanderOS-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupLogging=yes

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\UltimateCommanderOS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Live Check"; Filename: "{app}\{#MyAppExeName}"; Parameters: ""
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
