@echo off
echo Starting LeafAuto Web application...

:: Start backend service
echo Starting backend service...
start "LeafAuto Backend" cmd /k "cd /d %~dp0LeafAutoBackend && LeafAutoBackend.exe"

:: Wait for backend service to start
timeout /t 3 /nobreak >nul

:: Start frontend service
echo Starting frontend service...
start "LeafAuto Frontend" cmd /k "cd /d %~dp0LeafAutoFrontend && LeafAutoFrontend.exe"

:: Wait for frontend service to start
echo Waiting for frontend service to start...
timeout /t 5 /nobreak >nul

:: Open browser with frontend URL
echo Opening browser...
start http://localhost:8080

echo Application is starting...
echo Backend service running at: http://localhost:5000
echo Frontend service running at: http://localhost:8080
echo Browser should open automatically with the application

:: Wait for user to press any key to exit
pause