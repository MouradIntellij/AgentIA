@echo off
REM Installateur atelier - 1 fois avec wifi
python --version || (echo Installez Python (cocher Add to PATH) : python.org/downloads & pause & exit)
pip install -r requirements.txt
where ollama >nul 2>nul || (echo Installez Ollama : ollama.com/download puis relancez ce fichier & pause & exit)
ollama pull llama3.2:latest
echo.
echo OK - double-cliquez demarrer-agent.bat
pause
