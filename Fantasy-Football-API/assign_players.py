#!/usr/bin/env python3
"""
Script per assegnare giocatori alle squadre della lega FANTAStico
"""
import json
import csv
import uuid
import random
from collections import defaultdict

def load_leagues():
    """Carica le leghe dal file JSON"""
    with open('data/leagues.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_leagues(leagues):
    """Salva le leghe nel file JSON"""
    with open('data/leagues.json', 'w', encoding='utf-8') as f:
        json.dump(leagues, f, indent=2, ensure_ascii=False)

def load_players():
    """Carica i giocatori dal CSV"""
    csv_path = '../Estrai listone/data/quotazioni_fantacalcio.csv'
    
    players = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Determina il ruolo in base alla colonna 'ruolo'
            role = row['ruolo'].upper()
            
            player = {
                'id': str(uuid.uuid4()),
                'name': row['nome'],
                'role': role,
                'team': row['squadra'],
                'quotazione': float(row['quotazione_attuale_classico'])
            }
            players.append(player)
    
    return players

def distribute_players(teams, players, players_per_team=25):
    """
    Distribuisce i giocatori tra le squadre in modo bilanciato
    """
    # Dividi i giocatori per ruolo
    players_by_role = defaultdict(list)
    for player in players:
        players_by_role[player['role']].append(player)
    
    # Mescola i giocatori di ogni ruolo per distribuzione casuale
    for role in players_by_role:
        random.shuffle(players_by_role[role])
    
    # Per ogni squadra, assegna giocatori bilanciati per ruolo
    # Distribuzione tipica: 3 portieri, 8 difensori, 8 centrocampisti, 6 attaccanti
    role_distribution = {
        'P': 3,
        'D': 8,
        'C': 8,
        'A': 6
    }
    
    for team_idx, team in enumerate(teams):
        if team['roster']:  # Salta la squadra FC++ che ha già giocatori
            print(f"⏭️  Salto '{team['name']}' che ha già {len(team['roster'])} giocatori")
            continue
            
        team_roster = []
        
        for role, count in role_distribution.items():
            available = players_by_role[role]
            
            # Prendi i primi 'count' giocatori disponibili per questo ruolo
            for i in range(min(count, len(available))):
                if available:
                    player = available.pop(0)
                    team_roster.append({
                        'id': player['id'],
                        'name': player['name'],
                        'role': player['role']
                    })
        
        team['roster'] = team_roster
        print(f"✅ Assegnati {len(team_roster)} giocatori a '{team['name']}'")

def main():
    print("🏆 Assegnazione giocatori alla lega FANTAStico")
    print("=" * 60)
    
    # Carica dati
    print("\n📂 Caricamento dati...")
    leagues = load_leagues()
    players = load_players()
    print(f"   Trovati {len(players)} giocatori disponibili")
    
    # Trova la lega FANTAStico
    fantastico_league = None
    for league_id, league in leagues.items():
        if league['name'] == 'FANTAStico':
            fantastico_league = league
            break
    
    if not fantastico_league:
        print("❌ Lega 'FANTAStico' non trovata!")
        return
    
    print(f"   Trovata lega '{fantastico_league['name']}' con {len(fantastico_league['teams'])} squadre")
    
    # Distribuisci i giocatori
    print("\n⚽ Distribuzione giocatori...")
    distribute_players(fantastico_league['teams'], players)
    
    # Salva i dati aggiornati
    print("\n💾 Salvataggio dati...")
    save_leagues(leagues)
    
    print("\n✨ Operazione completata con successo!")
    print(f"   Controlla il file data/leagues.json per vedere i cambiamenti")
    
    # Stampa riepilogo
    print("\n📊 Riepilogo squadre:")
    for team in fantastico_league['teams']:
        roles_count = defaultdict(int)
        for player in team['roster']:
            roles_count[player['role']] += 1
        
        roles_str = ", ".join([f"{role}: {count}" for role, count in sorted(roles_count.items())])
        print(f"   {team['name']}: {len(team['roster'])} giocatori ({roles_str})")

if __name__ == '__main__':
    main()
