@echo off
cd /d "%~dp0"
echo === Instalando el sistema de gestion de obras ===
if not exist .venv (
    python -m venv .venv || goto error
)
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt || goto error
if not exist .env copy .env.example .env
.venv\Scripts\python.exe manage.py migrate || goto error
echo.
echo Listo. Para cargar datos de ejemplo:  .venv\Scripts\python.exe manage.py cargar_demo
echo Para crear el primer usuario de Gerencia: .venv\Scripts\python.exe manage.py createsuperuser
echo Despues abri run.bat
pause
exit /b 0
:error
echo Hubo un error durante la instalacion.
pause
exit /b 1
