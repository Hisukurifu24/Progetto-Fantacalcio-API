@echo off
echo ===============================================
echo       SCRAPER VOTI FANTACALCIO
echo ===============================================
echo.

REM Cambia directory al progetto
cd /d "%~dp0"

REM Controlla se esiste l'ambiente virtuale
if not exist ".venv\Scripts\python.exe" (
    echo ERRORE: Ambiente virtuale non trovato!
    echo Assicurati che la cartella .venv esista.
    pause
    exit /b 1
)

REM Controlla se esiste il file HTML
if not exist "data\fantacalcio.html" (
    echo ERRORE: File data\fantacalcio.html non trovato!
    echo Salva prima la pagina web come data\fantacalcio.html
    pause
    exit /b 1
)

REM Esegue lo script
echo Eseguendo lo scraper...
echo.
".venv\Scripts\python.exe" "src\voti_scraper.py"

echo.
echo ===============================================
if exist "data\voti_fantacalcio.csv" (
    echo COMPLETATO! File CSV creato con successo.
    echo Puoi trovare i voti in: data\voti_fantacalcio.csv
) else (
    echo ERRORE: Il file CSV non è stato creato.
)
echo ===============================================
echo.
echo Premi un tasto per chiudere...
pause >nul
