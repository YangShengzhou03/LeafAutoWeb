@echo off
echo Starting to build LeafAuto Web standalone application...

:: Create output directory
if not exist "output" mkdir output

:: Build frontend Vue project
echo Building frontend Vue project...
cd frontend
call npm install
call npm run build
cd ..

:: Copy frontend dist files to packaging directory
echo Copying frontend dist files...
if not exist "frontend\dist" (
    echo Error: Frontend dist directory not found!
    pause
    exit /b 1
)
:: 确保dist文件夹被包含在打包中
xcopy /E /I /Y "frontend\dist" "frontend" >nul 2>&1

:: Package backend
echo Packaging backend...
pyinstaller --clean backend_standalone.spec

:: Package frontend
echo Packaging frontend...
pyinstaller --clean frontend.spec

:: Create final output directory
if not exist "output\LeafAutoWeb" mkdir output\LeafAutoWeb

:: Copy backend files
echo Copying backend files...
xcopy /E /I /Y "dist\LeafAutoBackend" "output\LeafAutoWeb\LeafAutoBackend"

:: Copy frontend files
echo Copying frontend files...
xcopy /E /I /Y "dist\LeafAutoFrontend" "output\LeafAutoWeb\LeafAutoFrontend"

:: Copy startup script
echo Copying startup script...
copy "start_both.bat" "output\LeafAutoWeb\"

:: Copy documentation
echo Copying documentation...
copy "README.md" "output\LeafAutoWeb\" >nul 2>&1
if exist "\u6253\u5305\u4f7f\u7528\u8bf4\u660e.md" copy "\u6253\u5305\u4f7f\u7528\u8bf4\u660e.md" "output\LeafAutoWeb\" >nul 2>&1

:: Create shortcut
echo Creating shortcut...
set VBS_FILE=%temp%\create_shortcut.vbs
echo Set oWS = WScript.CreateObject("WScript.Shell") > %VBS_FILE%
echo sLinkFile = "%~dp0output\LeafAutoWeb\LeafAuto Web.lnk" >> %VBS_FILE%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %VBS_FILE%
echo oLink.TargetPath = "%~dp0output\LeafAutoWeb\start_both.bat" >> %VBS_FILE%
echo oLink.WorkingDirectory = "%~dp0output\LeafAutoWeb" >> %VBS_FILE%
echo oLink.IconLocation = "%~dp0output\LeafAutoWeb\LeafAutoBackend\_internal\resources\icon.ico" >> %VBS_FILE%
echo oLink.Save >> %VBS_FILE%
cscript %VBS_FILE%
del %VBS_FILE%

echo Build completed!
echo Output directory: output\LeafAutoWeb
echo Please double-click "LeafAuto Web.lnk" or "start_both.bat" to start the application

:: Open output directory
explorer "output\LeafAutoWeb"

pause