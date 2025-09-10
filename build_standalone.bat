@echo off
setlocal enabledelayedexpansion
echo Starting to build LeafAuto Web standalone application...

:: Create output directory
if not exist "output" mkdir output

:: Build frontend Vue project
echo Building frontend Vue project...
cd frontend
call npm install
call npm run build
cd ..

:: Check if frontend dist directory exists
if not exist "frontend\dist" (
    echo Error: Frontend dist directory not found!
    echo Directory listing of frontend folder:
    dir frontend
    pause
    exit /b 1
)

:: Ensure dist folder is included in packaging
echo Frontend dist directory found, proceeding with packaging...

:: Package backend
echo Packaging backend...
pyinstaller --clean backend_standalone.spec

:: Package main entry
echo Packaging main entry...
pyinstaller --clean start_production.spec
if %errorlevel% neq 0 (
    echo Error: Failed to package main entry!
    echo PyInstaller error code: %errorlevel%
    pause
    exit /b 1
)

:: Verify main entry was generated
set "main_exe_path=dist\LeafAutoWeb\LeafAutoWeb.exe"
if not exist "%main_exe_path%" (
    echo Error: Main entry file not generated at expected location:
    echo Expected path: %main_exe_path%
    echo Directory listing of dist folder:
    dir dist
    pause
    exit /b 1
)

:: Package frontend
echo Packaging frontend...
pyinstaller --clean frontend.spec
if %errorlevel% neq 0 (
    echo Error: Failed to package frontend!
    echo PyInstaller error code: %errorlevel%
    pause
    exit /b 1
)

:: Create final output directory
if not exist "output\LeafAutoWeb" mkdir output\LeafAutoWeb

:: Copy backend files
echo Copying backend files...
xcopy /E /I /Y "dist\LeafAutoBackend" "output\LeafAutoWeb\backend"

:: Copy main entry files
echo Copying main entry files...
if exist "%main_exe_path%" (
    echo Found main entry at: %main_exe_path%
    copy "%main_exe_path%" "output\LeafAutoWeb\LeafAutoWeb.exe" >nul 2>&1
    if not exist "output\LeafAutoWeb\LeafAutoWeb.exe" (
        echo Error: Failed to copy main entry file to output directory!
        echo Source: %main_exe_path%
        echo Destination: output\LeafAutoWeb\LeafAutoWeb.exe
        pause
        exit /b 1
    )
    echo Main entry file copied successfully.
) else (
    echo Error: Main entry file not found at: %main_exe_path%
    pause
    exit /b 1
)

:: Copy frontend files
echo Copying frontend files...
if exist "dist\LeafAutoFrontend" (
    if not exist "output\LeafAutoWeb\frontend" mkdir "output\LeafAutoWeb\frontend"
    xcopy /E /I /Y "dist\LeafAutoFrontend\*" "output\LeafAutoWeb\frontend"
    if %errorlevel% gtr 1 (
        echo Error: Failed to copy frontend files!
        echo XCopy error code: %errorlevel%
        pause
        exit /b 1
    )
    echo Frontend files copied successfully.
) else (
    echo Error: Frontend dist directory not found!
    echo Directory listing of dist folder:
    dir dist
    pause
    exit /b 1
)

:: Remove old startup script
del "output\LeafAutoWeb\start_both.bat" >nul 2>&1

:: Copy documentation
echo Copying documentation...
copy "README.md" "output\LeafAutoWeb\" >nul 2>&1

:: Create shortcut
echo Creating shortcut...
set VBS_FILE=%temp%\create_shortcut.vbs
echo Set oWS = WScript.CreateObject("WScript.Shell") > %VBS_FILE%
echo sLinkFile = "%~dp0output\LeafAutoWeb\LeafAuto Web.lnk" >> %VBS_FILE%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %VBS_FILE%
echo oLink.TargetPath = "%~dp0output\LeafAutoWeb\LeafAutoWeb.exe" >> %VBS_FILE%
echo oLink.WorkingDirectory = "%~dp0output\LeafAutoWeb" >> %VBS_FILE%
echo oLink.IconLocation = "\LeafAutoBackend\_internal\resources\icon.ico" >> %VBS_FILE%
echo oLink.Save >> %VBS_FILE%
cscript %VBS_FILE%
del %VBS_FILE%

echo Build completed!
echo Output directory: output\LeafAutoWeb
echo Please double-click "LeafAuto Web.lnk" or "start_both.bat" to start the application

:: Open output directory
explorer "output\LeafAutoWeb"

pause