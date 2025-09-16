@echo off
echo ===============================================
echo       SCRAPER QUOTAZIONI FANTACALCIO
echo ===============================================
echo.

REM Controlla se esiste l'ambiente virtuale locale
set VENV_PATH=.venv\Scripts\python.exe

if exist "%VENV_PATH%" (
    echo Usando l'ambiente virtuale locale...
    echo.
    echo Eseguendo lo scraper delle quotazioni...
    echo.
    
    "%VENV_PATH%" "src\quotazioni_scraper.py"
    set SCRIPT_RESULT=%ERRORLEVEL%
) else (
    echo Ambiente virtuale non trovato, usando Python di sistema...
    echo.
    echo Eseguendo lo scraper delle quotazioni...
    echo.
    
    python "src\quotazioni_scraper.py"
    set SCRIPT_RESULT=%ERRORLEVEL%
)

if %SCRIPT_RESULT% EQU 0 (
    echo.
    echo ===============================================
    echo COMPLETATO! File CSV creato con successo.
    echo Puoi trovare le quotazioni in: data\quotazioni_fantacalcio.csv
    echo ===============================================
) else (
    echo.
    echo ===============================================
    echo ERRORE durante l'esecuzione dello script!
    echo Controlla i messaggi sopra per maggiori dettagli.
    echo ===============================================
    echo.
    echo Se Python non e' installato o non e' nel PATH,
    echo puoi configurare un ambiente virtuale:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install beautifulsoup4 requests
)

@REM echo.
@REM echo Premi un tasto per chiudere...
@REM pause >nul
