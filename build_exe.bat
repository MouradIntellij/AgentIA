@echo off
REM Build .exe atelier - CSS/MathJax inclus, AUCUN internet requis (sauf ollama.com pour installer Ollama)
pip install pyinstaller
REM --onedir (dossier) et non --onefile : garde cours\, static\, banque, cache chemins relatifs
python -m PyInstaller --noconfirm --clean --onedir --name AgentReact ^
  --add-data "cours;cours" ^
  --add-data "static;static" ^
  --add-data "banque_react.py;." ^
  --add-data "etape10_ressources.py;." ^
  --add-data "GUIDE_REPRISE.txt;." ^
  --exclude-module torch --exclude-module transformers --exclude-module sklearn ^
  app_final.py
echo.
echo EXE pret : dist\AgentReact\AgentReact.exe
echo Copiez dist\AgentReact + installer.bat + lien ollama.com/download sur la cle USB.
echo L'exe embarque Python+appli+docs. Ollama + llama3.2 s'installent a part (installer.bat).
pause
