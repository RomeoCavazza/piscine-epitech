@echo off
setlocal

echo ======================================
echo     Installation de Bookworm
echo ======================================

REM Detecte un interpreteur Python 3.11-3.14 qui s'execute reellement.
REM "where python" peut renvoyer le stub Microsoft Store (non executable) :
REM on teste donc chaque candidat en l'executant, puis on bascule sur "py -3".
set "PYTHON="
call :pick_python python
if not defined PYTHON call :pick_python "py -3"
if not defined PYTHON (
    echo.
    echo ERREUR: aucun Python 3.11 a 3.14 executable n'a ete trouve.
    echo Installez Python 3.11-3.14 depuis https://www.python.org/downloads/
    echo  ^(evitez le raccourci Microsoft Store^), puis relancez install.bat.
    exit /b 1
)
echo Interpreteur Python detecte : %PYTHON%

echo.
echo [1/4] Creation de l'environnement virtuel (venv)...
%PYTHON% -m venv venv
if errorlevel 1 goto error
call venv\Scripts\activate.bat
if errorlevel 1 goto error

echo.
echo [2/4] Installation des dependances Python...
python -m pip install --upgrade pip
if errorlevel 1 goto error
python -m pip install -e ".[web,dev]"
if errorlevel 1 goto error

echo.
echo [3/4] Initialisation des ressources locales...
python core\utils.py
if errorlevel 1 goto error

echo.
echo [4/4] Telechargement du modele linguistique spaCy (version figee)...
python -m pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
if errorlevel 1 goto error

echo.
echo ======================================
echo  Installation terminee avec succes !
echo ======================================
echo.
echo Pour utiliser Bookworm, activez l'environnement avec :
echo   venv\Scripts\activate.bat
echo Puis lancez :
echo   python bookworm.py --help
pause
exit /b 0

:pick_python
%~1 -c "import sys; raise SystemExit(0 if sys.version_info[:2] in [(3,11),(3,12),(3,13),(3,14)] else 1)" >nul 2>nul
if not errorlevel 1 set "PYTHON=%~1"
goto :eof

:error
echo.
echo Installation interrompue. Corrigez l'erreur ci-dessus puis relancez install.bat.
pause
exit /b 1
