# Script PowerShell per eseguire lo scraper voti fantacalcio
# Uso: doppio clic o .\esegui_scraper.ps1

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "       SCRAPER VOTI FANTACALCIO" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Cambia directory al percorso dello script
Set-Location $PSScriptRoot

# Controlla se esiste l'ambiente virtuale
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "ERRORE: Ambiente virtuale non trovato!" -ForegroundColor Red
    Write-Host "Assicurati che la cartella .venv esista." -ForegroundColor Red
    Read-Host "Premi INVIO per chiudere"
    exit 1
}

# Controlla se esiste il file HTML
if (-not (Test-Path "data\fantacalcio.html")) {
    Write-Host "ERRORE: File data\fantacalcio.html non trovato!" -ForegroundColor Red
    Write-Host "Salva prima la pagina web come data\fantacalcio.html" -ForegroundColor Red
    Read-Host "Premi INVIO per chiudere"
    exit 1
}

# Esegue lo script
Write-Host "Eseguendo lo scraper..." -ForegroundColor Green
Write-Host ""

try {
    & ".venv\Scripts\python.exe" "src\voti_scraper.py"
    
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Cyan
    
    if (Test-Path "data\voti_fantacalcio.csv") {
        Write-Host "COMPLETATO! File CSV creato con successo." -ForegroundColor Green
        Write-Host "Puoi trovare i voti in: data\voti_fantacalcio.csv" -ForegroundColor Green
        
        # Mostra statistiche del file
        $csvContent = Get-Content "data\voti_fantacalcio.csv"
        $numRighe = $csvContent.Count - 1  # -1 per escludere l'header
        Write-Host "Numero di giocatori estratti: $numRighe" -ForegroundColor Yellow
    } else {
        Write-Host "ERRORE: Il file CSV non è stato creato." -ForegroundColor Red
    }
} catch {
    Write-Host "ERRORE durante l'esecuzione: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Premi INVIO per chiudere"
