# Verifica e installa requests se necessario
try:
    import requests
except ImportError:
    print("Libreria 'requests' non trovata. Tentativo di installazione...")
    import subprocess
    import sys
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
        import requests
        print("Libreria 'requests' installata con successo!")
    except Exception as e:
        print(f"Errore nell'installazione di requests: {e}")
        print("Installa manualmente con: pip install requests")
        exit(1)

from bs4 import BeautifulSoup
import csv
import os
import re
import sys

# Import Live API
try:
    from live_api import FantacalcioLiveAPI
except ImportError:
    # try relative import if running as script
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from live_api import FantacalcioLiveAPI

# Ottieni il percorso della directory principale del progetto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
data_dir = os.path.join(project_dir, 'data')

# Assicurati che la directory data esista
os.makedirs(data_dir, exist_ok=True)

# URL della pagina da scaricare
URL = "https://www.fantacalcio.it/voti-fantacalcio-serie-a"
CALENDAR_URL = "https://www.fantacalcio.it/serie-a/calendario"

OUTPUT_CSV = os.path.join(data_dir, "voti_fantacalcio.csv")
HTML_BACKUP = os.path.join(data_dir, "fantacalcio.html")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def download_page(url, backup_path=None):
    """Scarica la pagina web"""
    print(f"Scaricando: {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        if backup_path:
            with open(backup_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
        
        return response.text
    except requests.RequestException as e:
        print(f"Errore durante il download di {url}: {e}")
        return None

def parse_votes_main_page(html_content, giornata):
    """Parsing della pagina voti classica (tabulare)"""
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table', class_='grades-table')
    print(f"Trovate {len(tables)} tabelle dei voti nel sito principale")

    voti_data = []
    
    for table in tables:
        team_name = "Sconosciuta"
        caption = table.find('caption')
        if caption:
            team_name = caption.get_text().strip()
        
        rows = table.find_all('tr')[1:] # Salta header
        for row in rows:
            cols = row.find_all('td')
            if not cols: continue
            
            try:
                # Struttura attesa: Ruolo, Nome, Voto, Fantavoto, Gol, Amm, Esp, ...
                # Verificare indici reali se possibile, ma per ora usiamo euristica simile al vecchio codice o standard
                # Standard Fantacalcio.it:
                # 0: Ruolo, 1: Nome, 2: Voto, 3: Fantavoto
                
                ruolo = cols[0].get_text().strip()
                nome = cols[1].get_text().strip()
                voto_text = cols[2].get_text().strip()
                fantavoto_text = cols[3].get_text().strip()
                
                current_row = create_vote_row(giornata, nome, team_name, ruolo, voto_text, fantavoto_text)
                
                # Parsing Bonus/Malus se le colonne sono note
                # Se i dati non sono puliti, current_row ha default 0
                
                voti_data.append(current_row)
            except Exception as e:
                pass
                
    return voti_data

def scrape_live_matches(giornata):
    """Scraping partite live dal calendario"""
    print(f"Avvio scansione partite LIVE per la giornata {giornata}...")
    html = download_page(CALENDAR_URL)
    if not html: return []
    
    soup = BeautifulSoup(html, 'html.parser')
    votes_list = []
    
    # Cerca link: /serie-a/calendario/{giornata}/...
    pattern = re.compile(f"/serie-a/calendario/{giornata}/")
    links = soup.find_all('a', href=pattern)
    
    match_urls = set()
    for link in links:
        href = link['href']
        # Validazione link partita
        if href.count('/') >= 6:
            full_url = "https://www.fantacalcio.it" + href if href.startswith('/') else href
            # Rimuovi query string
            full_url = full_url.split('?')[0]
            match_urls.add(full_url)
            
    print(f"Trovate {len(match_urls)} partite per la giornata {giornata}")
    
    for url in match_urls:
        # Aggiungi /voti se manca
        if not url.endswith('/voti'):
            url_voti = url + '/voti'
        else:
            url_voti = url
            
        print(f"Scraping voti da: {url_voti}")
        votes_list.extend(scrape_single_live_match(url_voti, giornata))
        
    return votes_list

def scrape_single_live_match(url, giornata):
    print(f"Analisi match: {url}")
    
    # 1. Tentativo API LIVE (Protobuf)
    try:
        api = FantacalcioLiveAPI()
        match_data = api.get_live_votes(url)
        
        if match_data:
            print(f"[API] Dati trovati per ID {match_data['match_id']}")
            votes = []
            
            # Home Team
            for p in match_data.get('home', []):
                # Usa create_vote_row definita globalmente
                # Nota: create_vote_row accetta (giornata, nome, squadra, ruolo, voto, fantavoto)
                # Qui usiamo voto=fantavoto temporaneamente
                row = create_vote_row(giornata, p['name'], "Home", p['role'], str(p['vote']), str(p['vote']))
                votes.append(row)
                
            for p in match_data.get('away', []):
                row = create_vote_row(giornata, p['name'], "Away", p['role'], str(p['vote']), str(p['vote']))
                votes.append(row)
                
            return votes
            
    except Exception as e:
        print(f"[API] Errore API: {e}. Fallback to HTML...")

    # 2. Fallback HTML Scraping (Legacy)
    html = download_page(url)
    if not html: return []
    
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    
    # Euristica per trovare le squadre e i giocatori
    # Iteriamo su tutti gli elementi rilevanti
    # Cerchiamo Header Squadra -> Lista Giocatori
    
    # Troviamo tutti i link alle squadre per capire i nomi dei team in gioco
    # Solitamente h1 o h2 o div con classe team-name
    # Usiamo un approccio di scansione lineare dei nodi
    
    current_team = "Sconosciuta"
    
    # Cerchiamo container principali
    # Spesso la pagina ha due colonne per le squadre.
    # Ma flat è più semplice da parsare se sequenziale
    
    all_elements = soup.find_all(['h3', 'h4', 'div', 'li', 'td'])
    
    for el in all_elements:
        text = el.get_text(" ", strip=True)
        
        # Check se è un header di squadra (molto euristico)
        # Se il testo è breve e non contiene numeri o "Voti"
        if el.name in ['h3', 'h4'] and len(text) < 30 and "Voti" not in text and "Pagelle" not in text:
            # Potrebbe essere il nome della squadra
            # Ignoriamo label comuni
            if text not in ["Tabellino", "Statistiche", "Notizie", "Redazione"]:
                current_team = text
        
        # Check se è una riga giocatore
        # Regex: Nome Ruolo Voto (es: Falcone P 6)
        # O: Nome Ruolo Voto Gol ...
        
        # Pattern base: Nome (spazi o ' o .) + Ruolo (P,D,C,A) + Voto (numero)
        # Escludiamo righe header (es: Nome Voto)
        match = re.search(r'^([A-Za-zÀ-ÿ\s\'.]+?)\s+([PDCA])\s+(\d+[.,]?\d*)', text)
        if match:
            nome = match.group(1).strip()
            ruolo = match.group(2)
            voto = match.group(3).replace(',', '.')
            
            # Filtri anti-falso positivo
            if nome.lower() in ["nome", "panchina", "titolari", "allenatore"]:
                continue
            
            # Parsing Bonus dal testo se possibile (es: Falcone P 6 -1)
            # Ma spesso sono icone.
            # Proviamo a creare la riga
            
            vote_obj = create_vote_row(giornata, nome, current_team, ruolo, voto, voto)
            
            # Evita duplicati nella stessa scansione (es: tabellino vs voti)
            # Qui si assume che stiamo parsando la sezione voti
            data.append(vote_obj)

    return data

def create_vote_row(giornata, nome, squadra, ruolo, voto, fantavoto):
    def parse_float(v):
        try:
            val = float(v)
            if val > 20: return 0 # Sanity check
            return val
        except: return 0
        
    return {
        'giornata': giornata,
        'nome': nome,
        'squadra': squadra,
        'ruolo': ruolo,
        'voto': parse_float(voto),
        'fantavoto': parse_float(fantavoto), # Default a voto se non c'è
        'gol': 0, 'assist': 0, 'rigori_segnati': 0, 'rigori_sbagliati': 0,
        'rigori_parati': 0, 'gol_subiti': 0, 'autoreti': 0, 'motm': 0, 'bonus_totali': 0
    }

def save_to_csv(data):
    if not data:
        print("Nessun dato da salvare.")
        return
        
    fieldnames = ['giornata', 'nome', 'squadra', 'ruolo', 'voto', 'fantavoto', 
                  'gol', 'assist', 'rigori_segnati', 'rigori_sbagliati', 
                  'rigori_parati', 'gol_subiti', 'autoreti', 'motm', 'bonus_totali']
    
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Dati salvati in {OUTPUT_CSV}. Totale righe: {len(data)}")

def detect_giornata(soup):
    title_tag = soup.find('h1')
    if title_tag:
        text = title_tag.get_text().lower()
        match = re.search(r'(\d+)[°\s]+giornata', text) or re.search(r'giornata\s+(\d+)', text)
        if match:
            return int(match.group(1))
            
    page_title = soup.find('title')
    if page_title:
        text = page_title.get_text().lower()
        match = re.search(r'(\d+)[°\s]+giornata', text) or re.search(r'giornata\s+(\d+)', text)
        if match:
            return int(match.group(1))
            
    return 0

def main():
    # 1. Scarica pagina principale per determinare giornata e vedere se ci sono voti definitivi
    html_main = download_page(URL, HTML_BACKUP)
    if not html_main: return
    
    soup_main = BeautifulSoup(html_main, 'html.parser')
    giornata = detect_giornata(soup_main)
    print(f"Giornata rilevata: {giornata}")
    
    if giornata == 0:
        print("Impossibile determinare giornata. Stop.")
        return

    # 2. Parsing voti definitivi
    all_votes = parse_votes_main_page(html_main, giornata)
    
    # 3. Parsing voti LIVE (opzionale o integrazione)
    # Se abbiamo pochi voti definitivi (es < 200) o se vogliamo aggiornare i live
    # Eseguiamo sempre il live check per sicurezza in questa fase di dev
    live_votes = scrape_live_matches(giornata)
    
    # 4. Merge (Priorità ai live se mancano nel main? O viceversa?)
    # Solitamente: Main > Live per voti "ufficiali", ma Live > Main per tempestività.
    # Creiamo un dict per merge chiave (nome, squadra)
    
    merged_votes = {}
    
    # Prima inseriamo i main (ufficiali)
    for v in all_votes:
        key = (v['nome'].lower(), v['squadra'].lower())
        merged_votes[key] = v
        
    # Poi aggiorniamo/inseriamo i live
    # Nota: se il main è vuoto o parziale, il live riempie.
    # Se il live è più recente... difficile dirlo.
    # Facciamo che il Live ha priorità se il main NON ha quel giocatore.
    # Se il main HA il giocatore, teniamo il main (spesso più accurato con bonus finali).
    
    for v in live_votes:
        key = (v['nome'].lower(), v['squadra'].lower())
        if key not in merged_votes:
            merged_votes[key] = v
            # print(f"Aggiunto voto LIVE per {v['nome']}")
        else:
            # Opzionale: update se il voto main è nullo?
            pass
            
    final_list = list(merged_votes.values())
    print(f"Totale voti unici: {len(final_list)}")
    
    save_to_csv(final_list)

if __name__ == "__main__":
    main()
