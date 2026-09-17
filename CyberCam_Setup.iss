#define MyAppName "CyberCam"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Ivan Roliuk"
#define MyAppExeName "CyberCam.exe"

[Setup]
AppId={{8F33B779-FF24-4C74-93A8-43D46F5C9F67}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\CyberCam
DefaultGroupName=CyberCam

OutputDir=installer
OutputBaseFilename=CyberCam_Setup_v{#MyAppVersion}

SetupIconFile=assets\icons\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

Compression=lzma2
SolidCompression=yes

WizardStyle=modern
PrivilegesRequired=admin

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "dist\CyberCam\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\CyberCam"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\CyberCam"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch CyberCam"; Flags: nowait postinstall skipifsilent