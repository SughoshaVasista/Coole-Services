@echo off
set PROJECT_DIR=c:\Users\sugho\Downloads\app\app\Safe_project-main\Safe_project-main\Safe_project-main\edunet-main\edunet_pro
set ENV_ACTIVATE=c:\Users\sugho\Downloads\app\env\Scripts\activate

echo.
echo ======================================================
echo    COOL-E PLATFORM PRESENTATION LAUNCHER
echo ======================================================
echo.

echo [1/2] Launching Customer Portal on Port 8000...
start "Cool-E CUSTOMER (8000)" cmd /k "call \"%ENV_ACTIVATE%\" && cd /d \"%PROJECT_DIR%\" && python manage.py runserver 8000"

timeout /t 2 /nobreak > nul

echo [2/2] Launching Partner Portal on Port 8001...
start "Cool-E PARTNER (8001)" cmd /k "call \"%ENV_ACTIVATE%\" && cd /d \"%PROJECT_DIR%\" && python manage.py runserver 8001"

echo.
echo ------------------------------------------------------
echo  SUCCESS: Both environments are starting!
echo.
echo  CUSTOMER ACCESS: http://127.0.0.1:8000
echo  PARTNER ACCESS:  http://127.0.0.1:8001
echo ------------------------------------------------------
echo.
echo  DONT CLOSE THIS WINDOW UNTIL FINISHED
echo.
pause
