@echo off
REM Reconstruit static\app.css apres avoir ajoute des classes Tailwind dans app_*.py
REM Necessite internet UNE fois (npx telecharge tailwindcss). Le CSS produit est autonome.
cd /d "%~dp0"
call npx --yes tailwindcss@3.4.17 -c tailwind.config.js -i entree.css -o ..\static\app.css --minify
if errorlevel 1 (
  echo ECHEC : verifiez que Node.js est installe ^(node --version^).
  pause
  exit /b 1
)
cd ..
python outils_tailwind\verif_css.py
echo.
echo CSS reconstruit : static\app.css
pause
