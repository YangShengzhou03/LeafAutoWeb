; 脚本由 Inno Setup 脚本向导 生成！
; 有关创建 Inno Setup 脚本文件的详细资料请查阅帮助文档！

#define MyAppName "LeafAuto Web"
#define MyAppVersion "1.0.0.0"
#define MyAppPublisher "Yangshengzhou"
#define MyAppURL "https://blog.csdn.net/Yang_shengzhou"
#define AppSupportURL "https://blog.csdn.net/Yang_shengzhou/article/details/143782041"
#define MyAppExeName "LeafAutoWeb.exe"

[Setup]
; 注: AppId的值为单独标识该应用程序。
; 不要为其他安装程序使用相同的AppId值。
; (若要生成新的 GUID，可在菜单中点击 "工具|生成 GUID"。)
AppId={{444BC871-89CE-48D5-8AE9-7188BB9708A2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#AppSupportURL}
AppUpdatesURL={#MyAppURL}
VersionInfoVersion=1.0.0.0
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=license.txt
; 以下行取消注释，以在非管理安装模式下运行（仅为当前用户安装）。
;PrivilegesRequired=lowest
; 以管理员身份运行
PrivilegesRequired=admin
OutputDir=C:\Users\YangShengzhou\Desktop
OutputBaseFilename=LeafAuto Web {#MyAppVersion}
SetupIconFile=resources\setup.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
AppCopyright=© 2025 LeafAutoWeb by YangShengzhou.版权所有
UninstallDisplayIcon={app}\backend\_internal\resources\icon.ico


[UninstallDelete]
Type: files; Name: "{app}\*.*"
Type: dirifempty; Name: "{app}"

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkablealone

[Files]
Source: "D:\LeafAutoWeb\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\LeafAutoWeb\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 注意: 不要在任何共享系统文件上使用“Flags: ignoreversion”

[Icons]
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; 安装完成后运行
Filename: "{app}\{#MyAppExeName}"; Description: "立即运行“{#MyAppName}”"; Flags: nowait postinstall skipifsilent runascurrentuser
; 安装完成后运行 Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchWebgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

