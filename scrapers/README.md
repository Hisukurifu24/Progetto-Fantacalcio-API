# Scrapers Fantacalcio

Questo folder contiene gli scraper per estrarre i dati dei giocatori da Fantacalcio.it e salvarli nel database.

## Setup

### 1. Installa le dipendenze Python

```bash
cd Progetto-Fantacalcio-API/scrapers
pip install -r requirements.txt
```

### 2. Configura le variabili d'ambiente

Crea un file `.env` nella directory `scrapers`:

```bash
cp .env.example .env
```

Modifica il file `.env` con i tuoi parametri del database:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=app_fantacalcio
DB_USER=postgres
DB_PASSWORD=postgres
```

### 3. Assicurati che il database sia attivo

Il database PostgreSQL deve essere in esecuzione. Se stai usando Docker:

```bash
cd ../backend
docker-compose up -d
```

## Utilizzo

### Scraper Database (Raccomandato)

Lo scraper `db_scraper.py` estrae i dati da Fantacalcio.it e li salva direttamente nel database PostgreSQL:

```bash
python db_scraper.py
```

Questo script:
- Scarica le quotazioni da https://www.fantacalcio.it/quotazioni-fantacalcio
- Estrae nome, ruolo, squadra, quotazioni (iniziali e attuali) e FVM per entrambe le modalità (classico e mantra)
- Salva i dati nel database usando UPSERT (inserisce nuovi giocatori o aggiorna quelli esistenti)
- Genera ID deterministici basati su nome e squadra per evitare duplicati

### Scraper legacy (CSV)

Gli scraper originali in `Estrai listone` e `Estrai voti` salvano i dati in file CSV:

**Quotazioni:**
```bash
cd "Estrai listone/src"
python quotazioni_scraper.py
```

**Voti:**
```bash
cd "Estrai voti/src"
python voti_scraper.py
```

## Struttura dati

Lo scraper estrae i seguenti campi per ogni giocatore:

- `id` (UUID): Generato deterministicamente da nome + squadra
- `name`: Nome completo del giocatore
- `role`: Ruolo (P, D, C, A)
- `real_team`: Squadra Serie A (sigla a 3 lettere)
- `quotazione_iniziale_classico`: Quotazione iniziale modalità classico
- `quotazione_attuale_classico`: Quotazione attuale modalità classico
- `quotazione_iniziale_mantra`: Quotazione iniziale modalità mantra
- `quotazione_attuale_mantra`: Quotazione attuale modalità mantra
- `fvm_classico`: Fanta Valore Mercato classico
- `fvm_mantra`: Fanta Valore Mercato mantra

## Troubleshooting

### Errore di connessione al database

Verifica che:
1. PostgreSQL sia in esecuzione
2. Le credenziali nel file `.env` siano corrette
3. Il database `app_fantacalcio` esista

### Nessun giocatore estratto

- Il sito di Fantacalcio.it potrebbe aver cambiato la struttura HTML
- Verifica la connessione internet
- Controlla che l'URL sia ancora valido

### Errore UUID

Se ricevi errori relativi agli UUID, potrebbe essere necessario abilitare l'estensione PostgreSQL:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

## Scheduling automatico

Per eseguire lo scraper automaticamente a intervalli regolari, puoi usare:

### Linux/macOS (cron)

```bash
# Ogni giorno alle 3:00 AM
0 3 * * * cd /path/to/scrapers && /usr/bin/python3 db_scraper.py >> /var/log/scraper.log 2>&1
```

### Windows (Task Scheduler)

Crea un task schedulato che esegua:
```
python C:\path\to\scrapers\db_scraper.py
```

## Note

- Gli ID dei giocatori sono generati in modo deterministico usando UUID5 basato su nome + squadra
- Questo garantisce che lo stesso giocatore abbia sempre lo stesso ID tra esecuzioni diverse
- L'operazione di UPSERT aggiorna i giocatori esistenti invece di creare duplicati
