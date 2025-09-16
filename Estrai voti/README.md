# SCRAPER VOTI FANTACALCIO

Questo progetto permette di estrarre automaticamente i voti del fantacalcio dal sito Fantacalcio.it e salvarli in un file CSV.

## 🚀 Funzionalità principali

- **Download automatico**: Scarica direttamente dalla pagina web di Fantacalcio.it
- **Backup automatico**: Salva una copia HTML per uso offline
- **Fallback intelligente**: Se la connessione fallisce, usa il file di backup
- **Estrazione completa**: Tutti i 315+ giocatori di Serie A
- **Bonus dettagliati**: Calcolo preciso di tutti i bonus/malus

## Struttura del progetto

```
progetto fantacalcio/
├── src/                          # Codice sorgente
│   ├── voti_scraper.py          # Script principale (con download automatico)
│   └── voti_scraper_local.py    # Versione locale (backup)
├── data/                         # File di dati
│   ├── fantacalcio.html         # Backup automatico della pagina
│   └── voti_fantacalcio.csv     # File di output con i voti
├── .venv/                        # Ambiente virtuale Python
├── esegui_scraper.bat           # Launcher Windows (consigliato)
├── esegui_scraper.ps1           # Launcher PowerShell
└── README.md                    # Questo file
```

## 🎯 Come utilizzarlo

### Metodo 1: File Batch (.bat) - SUPER FACILE ⭐
1. Fai doppio clic su `esegui_scraper.bat`
2. Lo script scarica automaticamente i voti da Fantacalcio.it
3. Il file CSV viene creato automaticamente in `data/voti_fantacalcio.csv`
4. **Nessun file da salvare manualmente!**

### Metodo 2: PowerShell (.ps1) - ALTERNATIVO
1. Fai doppio clic su `esegui_scraper.ps1`
2. Se richiesto, autorizza l'esecuzione dello script
3. Lo script gestisce tutto automaticamente

### Metodo 3: Manuale - PER SVILUPPATORI
1. Apri il terminale/prompt
2. Naviga nella cartella del progetto
3. Esegui: `.venv\Scripts\python.exe src\voti_scraper.py`

## 🔧 Cosa fa lo script

- **Scarica automaticamente** la pagina da https://www.fantacalcio.it/voti-fantacalcio-serie-a
- **Salva un backup** HTML in `data/fantacalcio.html` per uso offline
- **Estrae i dati** di tutti i 315+ giocatori di Serie A (20 squadre)
- **Calcola bonus/malus** secondo le regole ufficiali del fantacalcio
- **Crea il CSV** in `data/voti_fantacalcio.csv` con 14 colonne complete:
  - Nome giocatore
  - Squadra
  - Ruolo (p/d/c/a)
  - Voto in pagella
  - Fantavoto
  - Gol segnati
  - Assist
  - Rigori segnati
  - Rigori sbagliati
  - Rigori parati
  - Gol subiti
  - Autoreti
  - Player of the Match
  - Bonus/malus totali

## 📋 Note importanti

- **Connessione automatica**: Lo script si connette automaticamente a Fantacalcio.it
- **Fallback offline**: Se la connessione fallisce, usa il file di backup esistente
- **Voti "55"**: Indicano giocatori subentrati troppo tardi per ricevere voto
- **Bonus automatici**: Calcolati secondo le regole standard del fantacalcio
- **Sempre aggiornato**: Ogni esecuzione scarica i voti più recenti
- **User-Agent**: Utilizza un browser header per evitare blocchi

## ⚙️ Caratteristiche tecniche

- **Gestione errori**: Robusto handling delle connessioni e parsing
- **Timeout intelligente**: 30 secondi per evitare blocchi
- **Encoding UTF-8**: Supporto completo per caratteri speciali
- **Path assoluti**: Funziona da qualsiasi directory
- **Auto-installazione**: Installa automaticamente le dipendenze mancanti

## 📁 File del progetto

- `src/voti_scraper.py` - Script principale con download automatico
- `src/voti_scraper_local.py` - Versione locale (backup/legacy)
- `esegui_scraper.bat` - Launcher Windows (raccomandato) ⭐
- `esegui_scraper.ps1` - Launcher PowerShell alternativo
- `data/fantacalcio.html` - Backup automatico della pagina
- `data/voti_fantacalcio.csv` - File di output con tutti i voti

Buon fantacalcio! 🚀⚽️🏆
