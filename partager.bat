@echo off
REM Partager l'agent sur Internet (lien jetable Cloudflare, sans compte ni cle API).
REM Fermer cette fenetre = le lien public s'arrete.
cd /d "%~dp0"
python -u partager.py %*
echo.
pause
