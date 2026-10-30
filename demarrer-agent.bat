@echo off
set PYTHONIOENCODING=utf-8
ollama list | findstr llama3.2 >nul 2>nul || (echo Moteur absent : lancez installer.bat une fois avec wifi & pause & exit)
start http://127.0.0.1:3000
python app_final.py
pause
