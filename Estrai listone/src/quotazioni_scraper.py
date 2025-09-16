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

if missing_modules:
    print(f"Librerie mancanti: {', '.join(missing_modules)}. Tentativo di installazione...")
    import subprocess
    import sys
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_modules)
        print("Librerie installate con successo!")
        # Re-import dopo l'installazione
        import requests
        from bs4 import BeautifulSoup
    except Exception as e:
        print(f"Errore nell'installazione: {e}")
        print(f"Installa manualmente con: pip install {' '.join(missing_modules)}")
        exit(1)
else:
    import requests
    from bs4 import BeautifulSoup

import csv
import os
import re

# Ottieni il percorso della directory principale del progetto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
data_dir = os.path.join(project_dir, 'data')

# URL della pagina da scaricare
URL = "https://www.fantacalcio.it/quotazioni-fantacalcio"
OUTPUT_CSV = os.path.join(data_dir, "quotazioni_fantacalcio.csv")
HTML_BACKUP = os.path.join(data_dir, "quotazioni.html")

def download_page():
    """Scarica la pagina web e salva l'HTML come backup, o usa il file locale se disponibile"""
    
    # Se esiste un file locale nella cartella data, usalo prima
    local_file = os.path.join(data_dir, "listone.html")
    if os.path.exists(local_file):
        print(f"Usando il file HTML locale: {local_file}")
        with open(local_file, 'r', encoding='utf-8') as file:
            return file.read()
    
    print("Scaricando le quotazioni da Fantacalcio.it...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Salva l'HTML come backup
        with open(HTML_BACKUP, 'w', encoding='utf-8') as file:
            file.write(response.text)
        
        print(f"Pagina scaricata e salvata in {HTML_BACKUP}")
        return response.text
        
    except requests.RequestException as e:
        print(f"Errore durante il download: {e}")
        # Prova a usare il file di backup se esiste
        if os.path.exists(HTML_BACKUP):
            print(f"Uso il file di backup: {HTML_BACKUP}")
            with open(HTML_BACKUP, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            print("Nessun file di backup disponibile!")
            return None

def extract_number(text):
    """Estrae un numero da una stringa, gestendo i decimali con virgola"""
    if not text:
        return 0
    # Cerca numeri con virgola o punto come separatore decimale
    match = re.search(r'(\d+)[,.]?(\d*)', str(text).strip())
    if match:
        integer_part = match.group(1)
        decimal_part = match.group(2) if match.group(2) else '0'
        return float(f"{integer_part}.{decimal_part}")
    return 0

def clean_name(name):
    """Pulisce il nome del giocatore rimuovendo caratteri speciali e spazi extra"""
    if not name:
        return ""
    # Rimuovi spazi extra, newline, tab e normalizza
    cleaned = ' '.join(name.strip().replace('\n', '').replace('\t', '').split())
    return cleaned

def main():
    # Scarica la pagina web
    html_content = download_page()
    if not html_content:
        print("Impossibile ottenere il contenuto HTML!")
        return

    # Analizza l'HTML con BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Cerca le righe dei giocatori
    player_rows = soup.find_all('tr', class_='player-row')
    
    if not player_rows:
        print("Nessuna riga giocatore trovata! Provo con altri selettori...")
        
        # Fallback: cerca altri pattern
        player_rows = soup.find_all('tr', class_=lambda x: x and 'player' in x)
        
        if not player_rows:
            print("Nessun dato trovato! Salvo l'HTML per debug...")
            with open(os.path.join(data_dir, "debug_quotazioni.html"), 'w', encoding='utf-8') as f:
                f.write(html_content)
            return

    print(f"Trovate {len(player_rows)} righe di giocatori")

    # Lista per raccogliere tutti i dati
    all_players = []
    
    for i, row in enumerate(player_rows, 1):
        try:            
            # Estrai nome giocatore - cerca prima nel link
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

            # Estrai ruolo classico
            role_element = row.find('th', class_='player-role-classic')
            role = ""
            if role_element:
                role_span = role_element.find('span', class_='role')
                if role_span and role_span.get('data-value'):
                    role = role_span.get('data-value')

            # Estrai quotazione iniziale classica
            initial_price_element = row.find('td', class_='player-classic-initial-price')
            initial_price = extract_number(initial_price_element.get_text(strip=True)) if initial_price_element else 0

            # Estrai quotazione attuale classica
            current_price_element = row.find('td', class_='player-classic-current-price')
            current_price = extract_number(current_price_element.get_text(strip=True)) if current_price_element else 0

            # Estrai FVM classico
            fvm_element = row.find('td', class_='player-classic-fvm')
            fvm = extract_number(fvm_element.get_text(strip=True)) if fvm_element else 0

            # Estrai quotazione iniziale mantra
            initial_price_mantra_element = row.find('td', class_='player-mantra-initial-price')
            initial_price_mantra = extract_number(initial_price_mantra_element.get_text(strip=True)) if initial_price_mantra_element else 0

            # Estrai quotazione attuale mantra
            current_price_mantra_element = row.find('td', class_='player-mantra-current-price')
            current_price_mantra = extract_number(current_price_mantra_element.get_text(strip=True)) if current_price_mantra_element else 0

            # Estrai FVM mantra
            fvm_mantra_element = row.find('td', class_='player-mantra-fvm')
            fvm_mantra = extract_number(fvm_mantra_element.get_text(strip=True)) if fvm_mantra_element else 0

            player_info = {
                'nome': name,
                'squadra': team,
                'ruolo': role,
                'quotazione_iniziale_classico': initial_price,
                'quotazione_attuale_classico': current_price,
                'fvm_classico': fvm,
                'quotazione_iniziale_mantra': initial_price_mantra,
                'quotazione_attuale_mantra': current_price_mantra,
                'fvm_mantra': fvm_mantra
            }
            
            all_players.append(player_info)
            
            if i <= 10:  # Mostra i primi 10
                print(f"  {name} ({team}) - Ruolo: {role} - Q.Class: {current_price} - FVM.Class: {fvm}")
                
        except Exception as e:
            print(f"Errore nell'elaborazione della riga {i}: {e}")
            continue

    if not all_players:
        print("Nessun giocatore estratto! Controlla i selettori CSS.")
        return

    # Salva i dati in CSV
    print(f"\nSalvataggio di {len(all_players)} giocatori nel file CSV...")
    
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'nome', 'squadra', 'ruolo', 
            'quotazione_iniziale_classico', 'quotazione_attuale_classico', 'fvm_classico',
            'quotazione_iniziale_mantra', 'quotazione_attuale_mantra', 'fvm_mantra'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for player in all_players:
            writer.writerow(player)

    print(f"Salvati {len(all_players)} giocatori in {OUTPUT_CSV}")
    
    # Mostra alcuni esempi
    print("\nPrimi 5 esempi:")
    for i, player in enumerate(all_players[:5]):
        print(f"  {player['nome']} ({player['squadra']}) - Ruolo: {player['ruolo']}")
        print(f"    Classico: Q.Att: {player['quotazione_attuale_classico']}, FVM: {player['fvm_classico']}")
        print(f"    Mantra: Q.Att: {player['quotazione_attuale_mantra']}, FVM: {player['fvm_mantra']}")

    print(f"\n===============================================")
    print(f"COMPLETATO! Estratti {len(all_players)} giocatori")
    print(f"File CSV: {OUTPUT_CSV}")
    print(f"===============================================")

if __name__ == "__main__":
    main()
