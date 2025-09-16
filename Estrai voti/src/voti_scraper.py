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

# Ottieni il percorso della directory principale del progetto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
data_dir = os.path.join(project_dir, 'data')

# URL della pagina da scaricare
URL = "https://www.fantacalcio.it/voti-fantacalcio-serie-a"
OUTPUT_CSV = os.path.join(data_dir, "voti_fantacalcio.csv")
HTML_BACKUP = os.path.join(data_dir, "fantacalcio.html")

def download_page():
    """Scarica la pagina web e salva l'HTML come backup"""
    print("Scaricando la pagina da Fantacalcio.it...")
    
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

def main():
    # Scarica la pagina web
    html_content = download_page()
    if not html_content:
        print("Impossibile ottenere il contenuto HTML!")
        return

    # Analizza l'HTML con BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Trova TUTTE le tabelle con i voti
    tables = soup.find_all('table', class_='grades-table')
    print(f"Trovate {len(tables)} tabelle dei voti")

    voti_data = []

    for table_num, table in enumerate(tables, 1):
        print(f"Analizzando tabella {table_num}...")
        
        # Trova il nome della squadra dalla div team-info
        team_info = table.find('div', class_='team-info')
        squadra = "N/A"
        if team_info:
            team_link = team_info.find('a', class_='team-name')
            if team_link:
                squadra = team_link.get_text(strip=True)
        
        # Trova tutte le righe della tabella (escludendo l'header)
        rows = table.find('tbody').find_all('tr') if table.find('tbody') else table.find_all('tr')[1:]
        
        for row in rows:
            # Trova il nome del giocatore
            player_link = row.find('a', class_='player-link')
            if player_link:
                nome_span = player_link.find('span')
                nome = nome_span.get_text(strip=True) if nome_span else ''
                
                # Trova il ruolo
                role_span = row.find('span', class_='role')
                ruolo = role_span.get('data-value', '') if role_span else ''
                
                # Trova i voti (primo voto disponibile)
                grade_span = row.find('span', class_='player-grade')
                voto = grade_span.get('data-value', '') if grade_span else ''
                
                # Trova il fantavoto (primo fantavoto disponibile)
                fanta_grade_span = row.find('span', class_='player-fanta-grade')
                fantavoto = fanta_grade_span.get('data-value', '') if fanta_grade_span else ''
                
                # Estrai bonus e malus
                bonus_spans = row.find_all('span', class_='player-bonus')
                gol = assist = rigori_segnati = rigori_sbagliati = rigori_parati = gol_subiti = autoreti = motm = 0
                
                for bonus_span in bonus_spans:
                    title = bonus_span.get('title', '').lower()
                    value = int(bonus_span.get('data-value', '0') or '0')
                    
                    if 'gol segnati' in title:
                        gol = value
                    elif 'assist' in title:
                        assist = value
                    elif 'rigori segnati' in title:
                        rigori_segnati = value
                    elif 'rigori sbagliati' in title:
                        rigori_sbagliati = -value  # Malus
                    elif 'rigori parati' in title:
                        rigori_parati = value
                    elif 'gol subiti' in title:
                        gol_subiti = -value  # Malus per portieri
                    elif 'autoret' in title:
                        autoreti = -value  # Malus
                    elif 'player of the match' in title or 'motm' in title:
                        motm = value
                
                # Calcola bonus/malus totali
                bonus_totali = gol*3 + assist*1 + rigori_segnati*3 + rigori_parati*3 + rigori_sbagliati*3 + gol_subiti*1 + autoreti*2 + motm*1
                
                # Aggiungi i dati solo se abbiamo almeno il nome
                if nome:
                    voti_data.append([nome, squadra, ruolo, voto, fantavoto, gol, assist, rigori_segnati, rigori_sbagliati, rigori_parati, gol_subiti, autoreti, motm, bonus_totali])
                    print(f"  {nome} ({squadra}) - Ruolo: {ruolo} - Voto: {voto} - Fantavoto: {fantavoto} - Bonus: {bonus_totali}")

    # Scrivi i dati nel file CSV
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Nome', 'Squadra', 'Ruolo', 'Voto', 'Fantavoto', 'Gol', 'Assist', 'Rigori_Segnati', 'Rigori_Sbagliati', 'Rigori_Parati', 'Gol_Subiti', 'Autoreti', 'MOTM', 'Bonus_Totali'])
        writer.writerows(voti_data)
    
    print(f"Salvati {len(voti_data)} voti in {OUTPUT_CSV}")
    if voti_data:
        print("Primi 5 esempi:")
        for i, row in enumerate(voti_data[:5]):
            print(f"  {row[0]} ({row[1]}) - Ruolo: {row[2]} - Voto: {row[3]}, Fantavoto: {row[4]}, Bonus: {row[13]}")

if __name__ == "__main__":
    main()
