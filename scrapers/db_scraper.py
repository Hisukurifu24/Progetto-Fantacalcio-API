#!/usr/bin/env python3
"""
Scraper che estrae le quotazioni dei giocatori da Fantacalcio.it
e le salva direttamente nel database PostgreSQL
"""

import os
import sys
import uuid
import re
from datetime import datetime

# Verifica e installa le dipendenze necessarie
missing_modules = []

try:
    import requests
except ImportError:
    missing_modules.append('requests')

try:
    from bs4 import BeautifulSoup
except ImportError:
    missing_modules.append('beautifulsoup4')

try:
    import psycopg2
    from psycopg2.extras import execute_batch
except ImportError:
    missing_modules.append('psycopg2-binary')

try:
    from dotenv import load_dotenv
except ImportError:
    missing_modules.append('python-dotenv')

if missing_modules:
    print(f"Librerie mancanti: {', '.join(missing_modules)}")
    print(f"Installa con: pip install {' '.join(missing_modules)}")
    sys.exit(1)

# Carica variabili d'ambiente
load_dotenv()

# Configurazione database
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'app_fantacalcio'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# URL della pagina da scaricare
URL = "https://www.fantacalcio.it/quotazioni-fantacalcio"

# Mapping ruoli
ROLE_MAPPING = {
    'P': 'P',
    'D': 'D',
    'C': 'C',
    'A': 'A',
    'Por': 'P',
    'Dif': 'D',
    'Cen': 'C',
    'Att': 'A'
}

def connect_db():
    """Connette al database PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print(f"✓ Connesso al database {DB_CONFIG['database']} su {DB_CONFIG['host']}")
        return conn
    except Exception as e:
        print(f"✗ Errore di connessione al database: {e}")
        sys.exit(1)

def download_page():
    """Scarica la pagina web delle quotazioni"""
    print("Scaricando le quotazioni da Fantacalcio.it...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=30)
        response.raise_for_status()
        print("✓ Pagina scaricata con successo")
        return response.text
    except requests.RequestException as e:
        print(f"✗ Errore durante il download: {e}")
        return None

def extract_number(text):
    """Estrae un numero da una stringa, gestendo i decimali con virgola"""
    if not text:
        return None
    match = re.search(r'(\d+)[,.]?(\d*)', str(text).strip())
    if match:
        integer_part = match.group(1)
        decimal_part = match.group(2) if match.group(2) else '0'
        return int(float(f"{integer_part}.{decimal_part}"))
    return None

def clean_name(name):
    """Pulisce il nome del giocatore"""
    if not name:
        return ""
    return ' '.join(name.strip().replace('\n', '').replace('\t', '').split())

def normalize_role(role):
    """Normalizza il ruolo del giocatore"""
    if not role:
        return None
    role = role.strip().upper()
    return ROLE_MAPPING.get(role, role)

def generate_player_id(name, team):
    """Genera un UUID deterministico per il giocatore basato su nome e squadra"""
    unique_string = f"{name.lower()}_{team.lower()}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))

def parse_quotazioni(html_content):
    """Estrae i dati dei giocatori dall'HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Cerca le righe dei giocatori
    player_rows = soup.find_all('tr', class_='player-row')
    
    if not player_rows:
        print("✗ Nessuna riga giocatore trovata!")
        return []
    
    print(f"✓ Trovate {len(player_rows)} righe di giocatori")
    
    players = []
    
    for row in player_rows:
        try:
            # Estrai nome
            name_link = row.find('a', class_='player-name')
            if name_link:
                name_span = name_link.find('span')
                name = clean_name(name_span.get_text(strip=True)) if name_span else ""
            else:
                name_element = row.find('span')
                name = clean_name(name_element.get_text(strip=True)) if name_element else ""
            
            if not name or name.lower() in ['nome', 'giocatore', 'player']:
                continue
            
            # Estrai squadra
            team_element = row.find('td', class_='player-team')
            team = clean_name(team_element.get_text(strip=True)) if team_element else ""
            
            # Estrai ruolo (dal data attribute o dal tag th)
            role_element = row.find('th', class_='player-role-classic')
            role = ""
            if role_element:
                role_span = role_element.find('span', class_='role')
                if role_span:
                    role = normalize_role(role_span.get('data-value', ''))
            
            # Se non trovato, prova con data-filter-role-classic
            if not role:
                role = row.get('data-filter-role-classic', '')
                role = normalize_role(role)
            
            # Estrai quotazioni dalle celle specifiche
            # Classico
            q_iniziale_classico_elem = row.find('td', class_='player-classic-initial-price')
            q_iniziale_classico = extract_number(q_iniziale_classico_elem.get_text(strip=True)) if q_iniziale_classico_elem else None
            
            q_attuale_classico_elem = row.find('td', class_='player-classic-current-price')
            q_attuale_classico = extract_number(q_attuale_classico_elem.get_text(strip=True)) if q_attuale_classico_elem else None
            
            fvm_classico_elem = row.find('td', class_='player-classic-fvm')
            fvm_classico = extract_number(fvm_classico_elem.get_text(strip=True)) if fvm_classico_elem else None
            
            # Mantra
            q_iniziale_mantra_elem = row.find('td', class_='player-mantra-initial-price')
            q_iniziale_mantra = extract_number(q_iniziale_mantra_elem.get_text(strip=True)) if q_iniziale_mantra_elem else None
            
            q_attuale_mantra_elem = row.find('td', class_='player-mantra-current-price')
            q_attuale_mantra = extract_number(q_attuale_mantra_elem.get_text(strip=True)) if q_attuale_mantra_elem else None
            
            fvm_mantra_elem = row.find('td', class_='player-mantra-fvm')
            fvm_mantra = extract_number(fvm_mantra_elem.get_text(strip=True)) if fvm_mantra_elem else None
            
            # Genera ID deterministico
            player_id = generate_player_id(name, team)
            
            player = {
                'id': player_id,
                'name': name,
                'role': role,
                'real_team': team,
                'quotazione_iniziale_classico': q_iniziale_classico,
                'quotazione_attuale_classico': q_attuale_classico,
                'quotazione_iniziale_mantra': q_iniziale_mantra,
                'quotazione_attuale_mantra': q_attuale_mantra,
                'fvm_classico': fvm_classico,
                'fvm_mantra': fvm_mantra
            }
            
            players.append(player)
            
        except Exception as e:
            print(f"✗ Errore nel parsing della riga: {e}")
            continue
    
    return players

def save_to_database(conn, players):
    """Salva i giocatori nel database usando UPSERT"""
    if not players:
        print("Nessun giocatore da salvare")
        return
    
    cursor = conn.cursor()
    
    # Query UPSERT: inserisce o aggiorna se esiste già
    query = """
        INSERT INTO player (
            id, name, role, real_team,
            quotazione_iniziale_classico, quotazione_attuale_classico,
            quotazione_iniziale_mantra, quotazione_attuale_mantra,
            fvm_classico, fvm_mantra
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            role = EXCLUDED.role,
            real_team = EXCLUDED.real_team,
            quotazione_iniziale_classico = EXCLUDED.quotazione_iniziale_classico,
            quotazione_attuale_classico = EXCLUDED.quotazione_attuale_classico,
            quotazione_iniziale_mantra = EXCLUDED.quotazione_iniziale_mantra,
            quotazione_attuale_mantra = EXCLUDED.quotazione_attuale_mantra,
            fvm_classico = EXCLUDED.fvm_classico,
            fvm_mantra = EXCLUDED.fvm_mantra
    """
    
    # Prepara i dati per il batch insert
    data = [
        (
            p['id'],
            p['name'],
            p['role'],
            p['real_team'],
            p['quotazione_iniziale_classico'],
            p['quotazione_attuale_classico'],
            p['quotazione_iniziale_mantra'],
            p['quotazione_attuale_mantra'],
            p['fvm_classico'],
            p['fvm_mantra']
        )
        for p in players
    ]
    
    try:
        execute_batch(cursor, query, data, page_size=100)
        conn.commit()
        print(f"✓ Salvati/aggiornati {len(players)} giocatori nel database")
    except Exception as e:
        conn.rollback()
        print(f"✗ Errore nel salvataggio: {e}")
        raise
    finally:
        cursor.close()

def main():
    print("=" * 60)
    print("SCRAPER FANTACALCIO -> DATABASE")
    print("=" * 60)
    print()
    
    # Scarica la pagina
    html_content = download_page()
    if not html_content:
        print("✗ Impossibile ottenere il contenuto HTML")
        sys.exit(1)
    
    print()
    
    # Estrai i dati
    players = parse_quotazioni(html_content)
    print(f"\n✓ Estratti {len(players)} giocatori")
    
    if not players:
        print("✗ Nessun giocatore estratto")
        sys.exit(1)
    
    # Mostra alcuni esempi
    print("\nEsempi di giocatori estratti:")
    for player in players[:5]:
        print(f"  - {player['name']} ({player['role']}) - {player['real_team']} - Q: {player['quotazione_attuale_classico']} - FVM: {player['fvm_classico']}")
    
    print()
    
    # Connetti al database
    conn = connect_db()
    
    try:
        # Salva nel database
        save_to_database(conn, players)
        print("\n✓ Operazione completata con successo!")
    except Exception as e:
        print(f"\n✗ Errore: {e}")
        sys.exit(1)
    finally:
        conn.close()
        print("✓ Connessione al database chiusa")

if __name__ == "__main__":
    main()
