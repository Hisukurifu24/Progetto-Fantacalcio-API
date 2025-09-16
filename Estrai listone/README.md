# SCRAPER QUOTAZIONI FANTACALCIO

Questo progetto estrae automaticamente le quotazioni e i FVM (Fantacalcio Market Value) dei giocatori dal sito Fantacalcio.it.

## 🚀 Funzionalità principali

- **Download automatico**: Scarica direttamente da https://www.fantacalcio.it/quotazioni-fantacalcio
- **Backup automatico**: Salva una copia HTML per uso offline
- **Fallback intelligente**: Se la connessione fallisce, usa il file di backup
- **Estrazione completa**: Tutti i giocatori di Serie A con quotazioni e FVM
- **Debug avanzato**: Salva file di debug in caso di problemi

## 📁 Struttura del progetto

```
Estrai listone/
├── src/
│   └── quotazioni_scraper.py       # Script principale con download automatico
├── data/
│   ├── quotazioni.html             # Backup automatico della pagina
│   ├── quotazioni_fantacalcio.csv  # File di output con le quotazioni
│   └── debug_*.txt/html            # File di debug (se necessari)
├── esegui_quotazioni.bat           # Launcher Windows (consigliato) ⭐
└── README.md                       # Questo file
```

## 🎯 Come utilizzarlo

### Metodo 1: File Batch (.bat) - SUPER FACILE ⭐
1. Fai doppio clic su `esegui_quotazioni.bat`
2. Lo script scarica automaticamente le quotazioni da Fantacalcio.it
3. Il file CSV viene creato automaticamente in `data/quotazioni_fantacalcio.csv`
4. **Nessun file da salvare manualmente!**

### Metodo 2: Manuale - PER SVILUPPATORI
1. Apri il terminale/prompt
2. Naviga nella cartella del progetto
3. Esegui: `..\.venv\Scripts\python.exe src\quotazioni_scraper.py`

## 🔧 Cosa fa lo script

- **Scarica automaticamente** la pagina delle quotazioni da Fantacalcio.it
- **Salva un backup** HTML in `data/quotazioni.html` per uso offline
- **Estrae i dati** di tutti i giocatori di Serie A con quotazioni
- **Crea il CSV** in `data/quotazioni_fantacalcio.csv` con colonne:
  - Nome giocatore
  - Squadra
  - Ruolo (p/d/c/a)
  - Quotazione (prezzo d'asta)
  - FVM (Fantacalcio Market Value)
  - Raw data (per debug)

## 📋 Note importanti

- **Connessione automatica**: Lo script si connette automaticamente a Fantacalcio.it
- **Fallback offline**: Se la connessione fallisce, usa il file di backup esistente
- **Debug avanzato**: In caso di problemi, genera file di debug per l'analisi
- **Parsing intelligente**: Prova diversi selettori per trovare i dati
- **Sempre aggiornato**: Ogni esecuzione scarica le quotazioni più recenti

## ⚙️ Caratteristiche tecniche

- **Gestione errori**: Robusto handling delle connessioni e parsing
- **Timeout intelligente**: 30 secondi per evitare blocchi
- **Encoding UTF-8**: Supporto completo per caratteri speciali
- **Path assoluti**: Funziona da qualsiasi directory
- **Multiple selectors**: Prova diversi selettori CSS per trovare le tabelle
- **Auto-installazione**: Installa automaticamente le dipendenze mancanti

## 🔗 Dipendenze

Usa l'ambiente virtuale del progetto principale che include:
- `requests` - Per il download delle pagine web
- `beautifulsoup4` - Per il parsing HTML
- `csv` - Per la creazione dei file CSV (incluso in Python)

Buone quotazioni! 🚀💰⚽
