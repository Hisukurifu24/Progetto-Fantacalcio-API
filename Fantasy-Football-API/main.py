from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Any, Optional
from enum import Enum
import pandas as pd
import uvicorn
import os
import subprocess
import shutil
import time
import json
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
import sys
import math

# Read base directory from environment so paths are configurable in Docker/hosts
BASE_DIR = os.getenv("BASE_DIR", "..")

# Pydantic Models
class CompetitionType(str, Enum):
    POINTS = "POINTS"
    CHAMPIONSHIP = "CHAMPIONSHIP"
    GROUP_TOURNAMENT = "GROUP_TOURNAMENT"
    KNOCKOUT_TOURNAMENT = "KNOCKOUT_TOURNAMENT"
    FORMULA1 = "FORMULA1"

class Player(BaseModel):
    """Player model - basic structure for now, can be extended"""
    id: Optional[str] = None
    name: str = ""
    role: Optional[str] = None

    class Config:
        extra = "allow"

class Match(BaseModel):
    """Match model for competitions"""
    day: int
    home_team: str
    away_team: str
    home_score: Optional[float] = None
    away_score: Optional[float] = None
    played: bool = False

class StandingEntry(BaseModel):
    """Standings entry for a team"""
    team_name: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: float = 0.0
    goals_against: float = 0.0
    goal_difference: float = 0.0
    points: int = 0

class Competition(BaseModel):
    """Competition model based on Godot structure"""
    name: str = ""
    type: CompetitionType = CompetitionType.POINTS
    participants: List[Player] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=lambda: {
        "start_day": 1,
        "end_day": 38,
    })
    calendar: List[Match] = Field(default_factory=list)
    standings: List[StandingEntry] = Field(default_factory=list)

class Fantateam(BaseModel):
    """Fantateam model based on Godot structure"""
    name: str = ""
    owner: str = ""
    owner_id: Optional[str] = None  # Added to store original user ID
    roster: List[Player] = Field(default_factory=list)

class League(BaseModel):
    """League model based on Godot structure"""
    id: Optional[str] = Field(default=None, description="Unique league ID (auto-generated)")
    name: str = Field(..., description="League name")
    created_by: Optional[str] = Field(default=None, description="User ID of the league creator")
    is_public: bool = Field(default=False, description="Whether the league is public")
    invite_code: Optional[str] = Field(default=None, description="Invite code for private leagues")
    teams: List[Fantateam] = Field(default_factory=list)
    competitions: List[Competition] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=lambda: {
        "start_day": 1,
        "max_budget": 500,
        "max_players_per_role": {
            "P": 3,
            "D": 8,
            "C": 8,
            "A": 6
        }
    })

class LeagueCreate(BaseModel):
    """Model for league creation (without ID)"""
    name: str = Field(..., description="League name")
    created_by: Optional[str] = Field(default=None, description="User ID of the league creator")
    is_public: bool = Field(default=False, description="Whether the league is public")
    teams: List[Fantateam] = Field(default_factory=list)
    competitions: List[Competition] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=lambda: {
        "start_day": 1,
        "max_budget": 500,
        "max_players_per_role": {
            "P": 3,
            "D": 8,
            "C": 8,
            "A": 6
        }
    })

# User Models
class UserSignup(BaseModel):
    """Model for user signup"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password")

class UserLogin(BaseModel):
    """Model for user login"""
    username_or_email: str = Field(..., description="Username or email address")
    password: str = Field(..., description="Password")

class User(BaseModel):
    """User model"""
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    created_at: str = Field(..., description="Creation timestamp")

class UserResponse(BaseModel):
    """Response model for user operations"""
    user: User
    token: str = Field(..., description="Authentication token")

app = FastAPI(
    title="Fantasy Football API",
    description="Simple API for fantasy football data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Fantasy Football API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Authentication endpoints
@app.post("/api/auth/signup", response_model=UserResponse)
async def signup(user_data: UserSignup):
    """Register a new user"""
    try:
        return _create_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@app.post("/api/auth/login", response_model=UserResponse)
async def login(login_data: UserLogin):
    """Login user and return token"""
    try:
        return _authenticate_user(login_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error authenticating user: {str(e)}")

def _run_python_scraper(script_rel_path: str, timeout: int = 180):
    """Run a Python scraper script reliably.

    script_rel_path: path relative to BASE_DIR pointing to the .py script to execute.
    Returns (stdout, elapsed_seconds)
    Raises HTTPException on failure.
    """
    script_abs = os.path.join(BASE_DIR, script_rel_path)
    if not os.path.exists(script_abs):
        raise HTTPException(status_code=500, detail=f"Scraper script missing: {script_rel_path}")
    start = time.time()
    # Use the same Python interpreter that's running this server
    proc = subprocess.run([
        sys.executable, script_abs
    ], capture_output=True, text=True, timeout=timeout)
    elapsed = time.time() - start
    if proc.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Scraper failed ({script_rel_path}): {proc.stderr[:500]}")
    return proc.stdout, elapsed

def _read_csv(csv_path: str):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)
    return pd.read_csv(csv_path)

# Storage files
LEAGUES_FILE = os.path.join("data", "leagues.json")
SCRAPER_TIMESTAMPS_FILE = os.path.join("data", "scraper_timestamps.json")
USERS_FILE = os.path.join("data", "users.json")
TOKENS_FILE = os.path.join("data", "tokens.json")

# Security setup
security = HTTPBearer()

def _ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs("data", exist_ok=True)

def _load_leagues() -> Dict[str, Dict]:
    """Load all leagues from storage"""
    _ensure_data_dir()
    if not os.path.exists(LEAGUES_FILE):
        return {}
    try:
        with open(LEAGUES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def _save_leagues(leagues: Dict[str, Dict]):
    """Save all leagues to storage"""
    _ensure_data_dir()
    with open(LEAGUES_FILE, 'w', encoding='utf-8') as f:
        json.dump(leagues, f, indent=2, ensure_ascii=False)

def _generate_league_id() -> str:
    """Generate a unique league ID"""
    return str(uuid.uuid4())

def _generate_invite_code() -> str:
    """Generate a unique 6-character invite code"""
    return secrets.token_urlsafe(4).upper()[:6]

def _create_league(league_data: LeagueCreate) -> League:
    """Create a new league with unique ID and save it"""
    leagues = _load_leagues()
    
    # Generate unique ID
    league_id = _generate_league_id()
    while league_id in leagues:
        league_id = _generate_league_id()
    
    # Generate unique invite code
    invite_code = _generate_invite_code()
    existing_codes = {league.get('invite_code') for league in leagues.values() if league.get('invite_code')}
    while invite_code in existing_codes:
        invite_code = _generate_invite_code()
    
    # Create league object
    league = League(
        id=league_id,
        name=league_data.name,
        created_by=league_data.created_by,
        is_public=league_data.is_public,
        invite_code=invite_code,
        teams=league_data.teams,
        competitions=league_data.competitions,
        settings=league_data.settings
    )
    
    # Save to storage
    leagues[league_id] = league.model_dump()
    _save_leagues(leagues)
    
    return league

def _enrich_league_with_usernames(league_data: Dict) -> Dict:
    """Enrich league data by adding username to team owner field"""
    users = _load_users()
    if "teams" in league_data:
        for team in league_data["teams"]:
            owner_id = team.get("owner", "")
            if owner_id in users:
                # Store original owner ID in a separate field and replace owner with username
                team["owner_id"] = owner_id
                team["owner"] = users[owner_id].get("username", owner_id)
    return league_data

def _get_all_players_from_csv():
    """Reads all players from the quotazioni CSV and returns them as a dict keyed by name."""
    csv_path = os.path.join(BASE_DIR, "Estrai listone", "data", "quotazioni_fantacalcio.csv")
    if not os.path.exists(csv_path):
        return {}
    try:
        df = pd.read_csv(csv_path)
        # Use a case-insensitive key for robustness
        return {player['nome'].lower(): player for player in df.to_dict('records')}
    except Exception:
        return {}

def _enrich_rosters_with_player_data(league_data: Dict) -> Dict:
    """Enrich rosters in a league with full player data from the CSV."""
    all_players_map = _get_all_players_from_csv()
    if not all_players_map:
        return league_data

    if "teams" in league_data:
        for team in league_data["teams"]:
            if "roster" in team:
                enriched_roster = []
                for player in team["roster"]:
                    player_name_lower = player.get("name", "").lower()
                    full_player_data = all_players_map.get(player_name_lower)
                    
                    if full_player_data:
                        # Create a new enriched player object
                        enriched_player = {
                            **player,  # Keep original data like id
                            **full_player_data,  # Add full data from CSV
                        }

                        # Normalize naming and roles (CSV roles are lowercase)
                        name_from_csv = full_player_data.get('nome')
                        if name_from_csv:
                            enriched_player['name'] = name_from_csv
                        enriched_player.pop('nome', None)

                        role_from_source = player.get('role') or full_player_data.get('ruolo')
                        if role_from_source:
                            enriched_player['role'] = str(role_from_source).upper()
                        enriched_player.pop('ruolo', None)

                        # Expose team name consistently for the app
                        team_from_source = player.get('team') or full_player_data.get('squadra')
                        if team_from_source:
                            enriched_player['team'] = team_from_source
                        enriched_player.pop('squadra', None)
                        
                        enriched_roster.append(enriched_player)
                    else:
                        # Keep original player if not found in CSV
                        enriched_roster.append(player)
                
                team["roster"] = enriched_roster
                
    return league_data

def _get_league_by_id(league_id: str) -> Optional[League]:
    """Get a league by its ID"""
    leagues = _load_leagues()
    if league_id in leagues:
        league_data = leagues[league_id].copy()
        league_data = _enrich_league_with_usernames(league_data)
        league_data = _enrich_rosters_with_player_data(league_data)
        return League(**league_data)
    return None

def _get_all_leagues() -> List[League]:
    """Get all leagues"""
    leagues = _load_leagues()
    return [League(**_enrich_league_with_usernames(league_data.copy())) for league_data in leagues.values()]

def _delete_league_by_id(league_id: str) -> bool:
    """Delete a league by its ID. Returns True if deleted, False if not found."""
    leagues = _load_leagues()
    if league_id in leagues:
        del leagues[league_id]
        _save_leagues(leagues)
        return True
    return False

def _update_league_by_id(league_id: str, league_data: LeagueCreate) -> Optional[League]:
    """Update an existing league by its ID. Returns updated league or None if not found."""
    leagues = _load_leagues()
    if league_id not in leagues:
        return None
    
    # Get existing league to preserve created_by and invite_code
    existing_league = leagues[league_id]
    
    # Process competitions: generate calendar for new competitions
    processed_competitions = []
    existing_competitions = existing_league.get('competitions', [])
    
    for idx, comp_data in enumerate(league_data.competitions):
        competition = Competition(**comp_data.model_dump() if hasattr(comp_data, 'model_dump') else comp_data)
        
        # Check if this is a new competition or if it doesn't have a calendar yet
        # Also regenerate if calendar is empty (for previously created cups)
        is_new = idx >= len(existing_competitions)
        has_no_calendar = not existing_competitions[idx].get('calendar') if not is_new else True
        has_empty_calendar = len(existing_competitions[idx].get('calendar', [])) == 0 if not is_new else True
        
        should_generate = is_new or has_no_calendar or has_empty_calendar
        
        if should_generate:
            # Generate calendar and standings for new competition or empty calendar
            competition = _generate_competition_calendar(competition)
        else:
            # Keep existing calendar and standings if they exist
            if existing_competitions[idx].get('calendar'):
                competition.calendar = [Match(**m) for m in existing_competitions[idx]['calendar']]
            if existing_competitions[idx].get('standings'):
                competition.standings = [StandingEntry(**s) for s in existing_competitions[idx]['standings']]
        
        processed_competitions.append(competition)
    
    # Create updated league object with existing ID, created_by, and invite_code
    updated_league = League(
        id=league_id,
        name=league_data.name,
        created_by=existing_league.get('created_by', league_data.created_by),
        is_public=league_data.is_public,
        invite_code=existing_league.get('invite_code'),
        teams=league_data.teams,
        competitions=processed_competitions,
        settings=league_data.settings
    )
    
    # Save to storage
    leagues[league_id] = updated_league.model_dump()
    _save_leagues(leagues)
    
    return updated_league

# Calendar generation functions
def _generate_round_robin_calendar(
    participants: List[str],
    start_day: int,
    end_day: int,
    calendar_type: str = "standard",
    total_days: int = None,
    day_slots: List[int] = None
) -> List[Match]:
    """Generate a round-robin calendar and optionally force it to span a given number of days.
    
    When total_days is provided, the calendar will contain exactly that many matchdays
    (useful when every Serie A giornata must be played). If total_days is greater than
    the base round-robin cycle, the cycle is repeated swapping home/away every other loop.
    When day_slots is provided, those exact giornate are used (in order).
    """
    import random
    
    n = len(participants)
    if n < 2:
        return []
    
    # If explicit day slots are provided, they win over start/end in terms of spacing
    if day_slots:
        day_slots = sorted(day_slots)
        target_days = len(day_slots)
        available_days = len(day_slots)
        start_day = min(day_slots)
        end_day = max(day_slots)
    else:
        available_days = end_day - start_day + 1
        target_days = total_days if total_days is not None else None
    
    # If odd number of teams, add a dummy team (bye)
    teams = participants.copy()
    if n % 2 != 0:
        teams.append("BYE")
        n += 1
    
    # Generate first half of the season using round-robin algorithm (pairings only)
    rounds = []
    num_rounds = n - 1
    matches_per_round = n // 2
    
    # Fixed team at position 0, rotate others
    for round_num in range(num_rounds):
        round_matches = []
        for match_num in range(matches_per_round):
            home_idx = match_num
            away_idx = n - 1 - match_num
            
            if round_num % 2 == 1:
                # Swap home/away for alternating rounds
                home_idx, away_idx = away_idx, home_idx
            
            home_team = teams[home_idx]
            away_team = teams[away_idx]
            
            # Skip matches with BYE team
            if home_team != "BYE" and away_team != "BYE":
                round_matches.append((home_team, away_team))
        
        rounds.append(round_matches)
        
        # Rotate teams (except first one)
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]
    
    # Build full cycle based on calendar type
    base_cycle = rounds.copy()
    if calendar_type == "standard":
        # Standard: second half with inverted home/away
        base_cycle += [[(away, home) for home, away in rnd] for rnd in rounds]
    elif calendar_type == "asymmetric":
        # Asymmetric: shuffled second half with random home/away
        all_pairings = [pair for rnd in rounds for pair in rnd]
        random.shuffle(all_pairings)
        asymmetric_rounds = []
        for i in range(0, len(all_pairings), matches_per_round):
            chunk = all_pairings[i:i+matches_per_round]
            adjusted = []
            for home, away in chunk:
                if random.random() < 0.5:
                    home, away = away, home
                adjusted.append((home, away))
            asymmetric_rounds.append(adjusted)
        base_cycle += asymmetric_rounds
    elif calendar_type == "mirror":
        # Mirror: identical order as first half
        base_cycle += [rnd.copy() for rnd in rounds]
    elif calendar_type == "single":
        # Only first half
        pass
    else:
        # Fallback to single round-robin if unknown type
        pass
    
    min_rounds_needed = len(base_cycle)
    
    # Decide how many matchdays we need to schedule
    if target_days is None:
        target_days = min_rounds_needed
    if target_days < min_rounds_needed:
        raise HTTPException(
            status_code=400,
            detail=f"Intervallo giornate troppo corto: servono almeno {min_rounds_needed} giornate. Aumenta il range di giornate o riduci le altre impostazioni."
        )
    if target_days > available_days:
        raise HTTPException(
            status_code=400,
            detail=f"Intervallo giornate insufficiente: servono {target_days} giornate, ma il range impostato ne ha {available_days}. Aumenta il range di giornate o riduci le altre impostazioni."
        )
    
    # Repeat cycles if we need to cover more matchdays than a single cycle provides
    full_rounds = []
    cycle_idx = 0
    while len(full_rounds) < target_days:
        for rnd in base_cycle:
            if len(full_rounds) >= target_days:
                break
            # Alternate home/away every other cycle to balance repeats
            if cycle_idx % 2 == 1:
                full_rounds.append([(away, home) for home, away in rnd])
            else:
                full_rounds.append(rnd.copy())
        cycle_idx += 1
    
    # Assign days consecutively to match Serie A giornate
    calendar = []
    for offset, round_matches in enumerate(full_rounds):
        day = day_slots[offset] if day_slots else (start_day + offset)
        for home, away in round_matches:
            calendar.append(Match(
                day=day,
                home_team=home,
                away_team=away
            ))
    
    return calendar

def _initialize_standings(participants: List[str]) -> List[StandingEntry]:
    """Initialize standings for a competition"""
    return [
        StandingEntry(team_name=participant)
        for participant in participants
    ]

def _generate_knockout_calendar(team_names: List[str], start_day: int, end_day: int, 
                                home_away: bool = True, final_home_away: bool = False,
                                random_seed: bool = True,
                                total_days: int = None) -> List[Match]:
    """Generate a knockout tournament calendar"""
    import random
    
    num_teams = len(team_names)
    
    # Check if it's a power of 2
    if num_teams & (num_teams - 1) != 0:
        raise ValueError("Number of teams must be a power of 2 for knockout tournament")
    
    available_days = end_day - start_day + 1
    
    # Determine how many distinct matchdays we need (each leg gets its own giornata)
    num_rounds = int(math.log2(num_teams))
    leg_days_needed = []
    for round_idx in range(num_rounds):
        is_final = (round_idx == num_rounds - 1)
        use_home_away = home_away if not is_final else final_home_away
        leg_days_needed.append(2 if use_home_away else 1)
    
    required_days = sum(leg_days_needed)
    target_days = total_days if total_days is not None else required_days
    
    if target_days < required_days:
        raise HTTPException(
            status_code=400,
            detail=f"Intervallo giornate troppo corto per i playoff: servono almeno {required_days} giornate. Aumenta il range di giornate o riduci le altre impostazioni."
        )
    if target_days > available_days:
        raise HTTPException(
            status_code=400,
            detail=f"Intervallo giornate insufficiente per i playoff: servono {target_days} giornate, ma il range impostato ne ha {available_days}. Aumenta il range di giornate o riduci le altre impostazioni."
        )
    
    # Shuffle teams if randomization is enabled
    teams = team_names.copy()
    if random_seed:
        random.shuffle(teams)
    
    calendar = []
    day_slots = _spread_days(start_day, end_day, target_days)
    day_pointer = 0
    current_teams = teams
    
    for round_idx in range(num_rounds):
        round_matches = []
        is_final = (round_idx == num_rounds - 1)
        use_home_away = home_away if not is_final else final_home_away
        
        # First leg day
        first_leg_day = day_slots[day_pointer]
        day_pointer += 1
        
        # Pair teams for this round
        for i in range(0, len(current_teams), 2):
            if i + 1 < len(current_teams):
                home_team = current_teams[i]
                away_team = current_teams[i + 1]
                
                # Add first leg
                round_matches.append(Match(
                    day=first_leg_day,
                    home_team=home_team,
                    away_team=away_team
                ))
        
        # Add return leg if needed
        if use_home_away:
            second_leg_day = day_slots[day_pointer]
            day_pointer += 1
            if second_leg_day <= first_leg_day:
                # Ensure legs are not on the same or previous day
                second_leg_day = first_leg_day + 1
            for match in round_matches.copy():
                round_matches.append(Match(
                    day=second_leg_day,
                    home_team=match.away_team,
                    away_team=match.home_team
                ))
        
        calendar.extend(round_matches)
        
        # Prepare for next round (winners will be determined later)
        current_teams = [f"Winner_{i//2}" for i in range(0, len(current_teams), 2)]
    
    return calendar

def _generate_group_tournament_calendar(team_names: List[str], start_day: int, end_day: int,
                                       num_groups: int = 2, teams_per_group: int = None,
                                       matches_per_team: int = 2,
                                       calendar_type: str = "standard",
                                       knockout_home_away: bool = True,
                                       final_home_away: bool = False,
                                       random_groups: bool = True) -> tuple:
    """Generate a group stage tournament calendar with knockout phase
    Returns: (calendar, groups_structure)
    """
    import random
    
    num_teams = len(team_names)
    available_days = end_day - start_day + 1
    
    # Calculate teams per group if not provided
    if teams_per_group is None:
        teams_per_group = num_teams // num_groups
    
    # Shuffle teams if randomization is enabled
    teams = team_names.copy()
    if random_groups:
        random.shuffle(teams)
    
    # Divide teams into groups
    groups = []
    for i in range(num_groups):
        start_idx = i * teams_per_group
        end_idx = start_idx + teams_per_group
        # Handle remaining teams for last group if division is not exact
        if i == num_groups - 1:
            end_idx = num_teams
        group_teams = teams[start_idx:end_idx]
        
        # Skip groups with less than 2 teams
        if len(group_teams) < 2:
            continue
            
        groups.append({
            'name': f'Girone {chr(65 + i)}',  # A, B, C, ...
            'teams': group_teams,
            'standings': [s.model_dump() for s in _initialize_standings(group_teams)]
        })
    
    calendar = []
    
    # Determine how many matchdays are required to complete the group stage
    # Each "round" corresponds to a giornata; groups can play in parallel
    required_days = 0
    rounds_per_group = []
    for group in groups:
        n = len(group['teams'])
        if n < 2:
            rounds_per_group.append(0)
            continue
        
        # (n - 1) rounds for single; double if matches_per_team == 2
        group_rounds = (n - 1) * max(1, matches_per_team)
        rounds_per_group.append(group_rounds)
        required_days = max(required_days, group_rounds)
    
    if required_days == 0:
        return [], groups
    
    if required_days > available_days:
        raise HTTPException(
            status_code=400,
            detail=f"Intervallo giornate insufficiente per completare i gironi: servono almeno {required_days} giornate, ma il range impostato ne ha {available_days}. Aumenta il range di giornate o riduci le altre impostazioni."
        )
    
    # Spread required giornate across the provided range so the user-specified window is respected
    shared_day_slots = _spread_days(start_day, end_day, required_days)
    
    # Generate group calendars; each group uses the same giornata numbering so round 1 di ogni girone ricade nella stessa giornata di Serie A
    for idx, group in enumerate(groups):
        group_teams = group['teams']
        group_rounds_needed = rounds_per_group[idx]
        
        if matches_per_team == 1:
            group_calendar_type = "single"
        else:
            group_calendar_type = calendar_type
        
        group_calendar = _generate_round_robin_calendar(
            group_teams,
            start_day,
            end_day,
            group_calendar_type,
            total_days=group_rounds_needed,
            day_slots=shared_day_slots[:group_rounds_needed]
        )
        
        calendar.extend(group_calendar)
    
    # Placeholder for knockout phase (will be populated after group stage)
    return calendar, groups

def _spread_days(start_day: int, end_day: int, needed_slots: int) -> List[int]:
    """Return a list of giornate evenly spread between start_day and end_day (inclusive)."""
    if needed_slots <= 0:
        return []
    if needed_slots == 1:
        return [start_day]
    
    total_span = end_day - start_day
    step = total_span / (needed_slots - 1)
    slots = [start_day]
    for i in range(1, needed_slots - 1):
        # Round to nearest int but guarantee strictly increasing
        proposed = int(round(start_day + step * i))
        proposed = max(proposed, slots[-1] + 1)
        slots.append(proposed)
    slots.append(end_day)
    return slots

def _generate_competition_calendar(competition: Competition) -> Competition:
    """Generate calendar and initialize standings for a competition based on its type"""
    team_names = [p.name for p in competition.participants]
    
    if competition.type == CompetitionType.CHAMPIONSHIP:
        # Generate round-robin calendar
        calendar_type = competition.settings.get("calendar_type", "standard")
        start_day = competition.settings.get("start_day", 1)
        end_day = competition.settings.get("end_day", 38)
        available_days = end_day - start_day + 1
        day_slots = list(range(start_day, end_day + 1))
        
        competition.calendar = _generate_round_robin_calendar(
            team_names, start_day, end_day, calendar_type, total_days=available_days, day_slots=day_slots
        )
        competition.standings = _initialize_standings(team_names)
    
    elif competition.type == CompetitionType.KNOCKOUT_TOURNAMENT:
        # Generate knockout tournament calendar
        start_day = competition.settings.get("start_day", 1)
        end_day = competition.settings.get("end_day", 38)
        home_away = competition.settings.get("rounds_home_away", True)
        final_home_away = competition.settings.get("final_home_away", False)
        random_brackets = competition.settings.get("random_brackets", True)
        
        try:
            # Each leg consumes one giornata; ensure the range is enough
            num_teams = len(team_names)
            required_rounds = int(math.log2(num_teams)) if num_teams > 0 else 0
            legs_per_round = []
            for idx in range(required_rounds):
                is_final = (idx == required_rounds - 1)
                legs_per_round.append(2 if (home_away if not is_final else final_home_away) else 1)
            total_leg_days = sum(legs_per_round)
            leg_day_slots = _spread_days(start_day, end_day, total_leg_days) if total_leg_days > 0 else []
            
            competition.calendar = _generate_knockout_calendar(
                team_names,
                start_day,
                end_day,
                home_away,
                final_home_away,
                random_brackets,
                total_days=total_leg_days
            )
            competition.standings = _initialize_standings(team_names)
        except ValueError as e:
            # If teams count is not power of 2, just initialize empty
            competition.calendar = []
            competition.standings = _initialize_standings(team_names)
    
    elif competition.type == CompetitionType.GROUP_TOURNAMENT:
        # Generate group tournament calendar
        start_day = competition.settings.get("start_day", 1)
        end_day = competition.settings.get("end_day", 38)
        num_groups = competition.settings.get("num_groups", 2)
        teams_per_group = competition.settings.get("teams_per_group", None)
        matches_per_team = competition.settings.get("matches_per_team", 2)
        calendar_type = competition.settings.get("calendar_type", "standard")
        knockout_home_away = competition.settings.get("knockout_home_away", True)
        final_home_away = competition.settings.get("final_home_away", False)
        random_groups = competition.settings.get("random_groups", True)
        
        calendar, groups = _generate_group_tournament_calendar(
            team_names, start_day, end_day, num_groups, teams_per_group, 
            matches_per_team, calendar_type, knockout_home_away, final_home_away, 
            random_groups
        )
        
        competition.calendar = calendar
        # Store groups structure in settings for later reference
        # Need to create new dict to trigger Pydantic update
        new_settings = competition.settings.copy()
        new_settings['groups'] = groups
        competition.settings = new_settings
        competition.standings = _initialize_standings(team_names)
    
    elif competition.type in [CompetitionType.POINTS, CompetitionType.FORMULA1]:
        # These don't need match calendars, just standings
        competition.calendar = []
        start_day = competition.settings.get("start_day", 1)
        end_day = competition.settings.get("end_day", 38)
        new_settings = competition.settings.copy()
        new_settings['match_days'] = list(range(start_day, end_day + 1))
        competition.settings = new_settings
        competition.standings = _initialize_standings(team_names)
    
    return competition

# User management functions
def _hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def _verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed_password

def _generate_token() -> str:
    """Generate a random token"""
    return secrets.token_urlsafe(32)

def _load_users() -> Dict[str, Dict]:
    """Load all users from storage"""
    _ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def _save_users(users: Dict[str, Dict]):
    """Save all users to storage"""
    _ensure_data_dir()
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def _load_tokens() -> Dict[str, str]:
    """Load all tokens from storage"""
    _ensure_data_dir()
    if not os.path.exists(TOKENS_FILE):
        return {}
    try:
        with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def _save_tokens(tokens: Dict[str, str]):
    """Save all tokens to storage"""
    _ensure_data_dir()
    with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tokens, f, indent=2, ensure_ascii=False)

def _create_user(user_data: UserSignup) -> UserResponse:
    """Create a new user"""
    users = _load_users()
    
    # Check if username already exists
    for user_info in users.values():
        if user_info['username'] == user_data.username:
            raise HTTPException(status_code=400, detail="Username already exists")
        if user_info['email'] == user_data.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Generate user ID and token
    user_id = str(uuid.uuid4())
    token = _generate_token()
    
    # Create user object
    user_dict = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": _hash_password(user_data.password),
        "created_at": datetime.now().isoformat()
    }
    
    # Save user
    users[user_id] = user_dict
    _save_users(users)
    
    # Save token
    tokens = _load_tokens()
    tokens[token] = user_id
    _save_tokens(tokens)
    
    # Return user response
    user = User(
        id=user_id,
        username=user_data.username,
        email=user_data.email,
        created_at=user_dict["created_at"]
    )
    
    return UserResponse(user=user, token=token)

def _authenticate_user(login_data: UserLogin) -> UserResponse:
    """Authenticate a user and return token"""
    users = _load_users()
    
    # Find user by username or email
    user_dict = None
    for user_info in users.values():
        if (user_info['username'] == login_data.username_or_email or 
            user_info['email'] == login_data.username_or_email):
            user_dict = user_info
            break
    
    if not user_dict:
        raise HTTPException(status_code=401, detail="Invalid username/email or password")
    
    # Verify password
    if not _verify_password(login_data.password, user_dict['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid username/email or password")
    
    # Generate new token
    token = _generate_token()
    tokens = _load_tokens()
    tokens[token] = user_dict['id']
    _save_tokens(tokens)
    
    # Return user response
    user = User(
        id=user_dict['id'],
        username=user_dict['username'],
        email=user_dict['email'],
        created_at=user_dict['created_at']
    )
    
    return UserResponse(user=user, token=token)

def _get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from token"""
    token = credentials.credentials
    tokens = _load_tokens()
    
    if token not in tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = tokens[token]
    users = _load_users()
    
    if user_id not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_dict = users[user_id]
    return User(
        id=user_dict['id'],
        username=user_dict['username'],
        email=user_dict['email'],
        created_at=user_dict['created_at']
    )

# Scraper timestamp functions
def _load_scraper_timestamps() -> Dict[str, str]:
    """Load scraper timestamps from storage"""
    _ensure_data_dir()
    if not os.path.exists(SCRAPER_TIMESTAMPS_FILE):
        return {}
    try:
        with open(SCRAPER_TIMESTAMPS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def _save_scraper_timestamps(timestamps: Dict[str, str]):
    """Save scraper timestamps to storage"""
    _ensure_data_dir()
    with open(SCRAPER_TIMESTAMPS_FILE, 'w', encoding='utf-8') as f:
        json.dump(timestamps, f, indent=2, ensure_ascii=False)

def _update_scraper_timestamp(scraper_name: str):
    """Update the timestamp for a specific scraper"""
    timestamps = _load_scraper_timestamps()
    timestamps[scraper_name] = datetime.now().isoformat()
    _save_scraper_timestamps(timestamps)

def _should_run_scraper(scraper_name: str, cache_hours: int = 24) -> bool:
    """Check if scraper should run based on last run time (default: once per day)"""
    timestamps = _load_scraper_timestamps()
    
    if scraper_name not in timestamps:
        return True  # Never run before, should run
    
    try:
        last_run = datetime.fromisoformat(timestamps[scraper_name])
        time_since_run = datetime.now() - last_run
        return time_since_run > timedelta(hours=cache_hours)
    except (ValueError, TypeError):
        return True  # Invalid timestamp, should run

@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(_get_current_user)):
    """Get current user information"""
    return current_user

@app.post("/api/leagues", response_model=League)
async def create_league(league_data: LeagueCreate, current_user: User = Depends(_get_current_user)):
    """Create a new fantasy league"""
    try:
        # Set the creator automatically from authenticated user
        league_data.created_by = current_user.id
        league = _create_league(league_data)
        return league
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating league: {str(e)}")

@app.get("/api/leagues", response_model=List[League])
async def get_all_leagues(current_user: User = Depends(_get_current_user)):
    """Get all fantasy leagues where the current user has a team"""
    try:
        all_leagues = _get_all_leagues()
        # Filter leagues where user has a team
        user_leagues = []
        for league in all_leagues:
            # Use owner_id if available (enriched leagues), otherwise fallback to owner
            has_team = any(
                (team.owner_id if team.owner_id else team.owner) == current_user.id 
                for team in league.teams
            )
            if has_team:
                user_leagues.append(league)
        return user_leagues
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving leagues: {str(e)}")

@app.get("/api/leagues/public", response_model=List[League])
async def get_public_leagues(current_user: User = Depends(_get_current_user)):
    """Get all public fantasy leagues where the user doesn't have a team yet"""
    try:
        all_leagues = _get_all_leagues()
        # Filter leagues that are public AND where user doesn't have a team
        public_leagues = []
        for league in all_leagues:
            if league.is_public:
                # Check if user already has a team in this league
                # Use owner_id if available (enriched leagues), otherwise fallback to owner
                has_team = any(
                    (team.owner_id if team.owner_id else team.owner) == current_user.id 
                    for team in league.teams
                )
                if not has_team:
                    public_leagues.append(league)
        return public_leagues
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving public leagues: {str(e)}")

@app.get("/api/leagues/{league_id}", response_model=League)
async def get_league(league_id: str):
    """Get a specific fantasy league by ID"""
    try:
        league = _get_league_by_id(league_id)
        if league is None:
            raise HTTPException(status_code=404, detail="League not found")
        return league
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving league: {str(e)}")

@app.delete("/api/leagues/{league_id}")
async def delete_league(league_id: str):
    """Delete a specific fantasy league by ID"""
    try:
        deleted = _delete_league_by_id(league_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="League not found")
        return {"message": f"League {league_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting league: {str(e)}")

@app.put("/api/leagues/{league_id}", response_model=League)
async def update_league(league_id: str, league_data: LeagueCreate, current_user: User = Depends(_get_current_user)):
    """Update/save an existing fantasy league by ID"""
    try:
        # Get existing league to check permissions
        existing_league = _get_league_by_id(league_id)
        if existing_league is None:
            raise HTTPException(status_code=404, detail="League not found")
        
        # Check if user is the league creator or owns a team in the league
        is_creator = existing_league.created_by == current_user.id
        is_team_owner = any(team.owner == current_user.id for team in existing_league.teams)
        
        if not (is_creator or is_team_owner):
            raise HTTPException(status_code=403, detail="You don't have permission to update this league")
        
        updated_league = _update_league_by_id(league_id, league_data)
        return updated_league
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating league: {str(e)}")

class LeaguePartialUpdate(BaseModel):
    """Model for partial league updates"""
    name: Optional[str] = None
    is_public: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None

@app.patch("/api/leagues/{league_id}", response_model=League)
async def partial_update_league(
    league_id: str, 
    update_data: LeaguePartialUpdate, 
    current_user: User = Depends(_get_current_user)
):
    """Partially update a league (e.g., only settings)"""
    try:
        # Get existing league to check permissions
        existing_league = _get_league_by_id(league_id)
        if existing_league is None:
            raise HTTPException(status_code=404, detail="League not found")
        
        # Check if user is the league creator
        if existing_league.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="Only the league creator can update settings")
        
        # Load leagues data
        leagues = _load_leagues()
        league_dict = leagues[league_id]
        
        # Update only provided fields
        if update_data.name is not None:
            league_dict['name'] = update_data.name
        if update_data.is_public is not None:
            league_dict['is_public'] = update_data.is_public
        if update_data.settings is not None:
            # Merge settings (keep existing keys, update provided ones)
            if 'settings' not in league_dict:
                league_dict['settings'] = {}
            league_dict['settings'].update(update_data.settings)
        
        # Save updated league
        leagues[league_id] = league_dict
        _save_leagues(leagues)
        
        # Return updated league
        return League(**league_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating league: {str(e)}")

class JoinLeagueRequest(BaseModel):
    """Model for joining a league"""
    team_name: str = Field(..., description="Name of the team joining the league")
    manager_name: str = Field(..., description="Name of the manager")

class AdminAddPlayerRequest(BaseModel):
    """Model for admin adding a player to a team"""
    team_name: str = Field(..., description="Name of the team")
    player_name: str = Field(..., description="Name of the player to add")
    player_role: Optional[str] = Field(None, description="Role of the player (P, D, C, A)")

class AdminRemovePlayerRequest(BaseModel):
    """Model for admin removing a player from a team"""
    team_name: str = Field(..., description="Name of the team")
    player_name: str = Field(..., description="Name of the player to remove")

@app.post("/api/leagues/{league_id}/join", response_model=League)
async def join_league(
    league_id: str,
    join_request: JoinLeagueRequest,
    current_user: User = Depends(_get_current_user)
):
    """Join a league by league ID"""
    try:
        league = _get_league_by_id(league_id)
        if league is None:
            raise HTTPException(status_code=404, detail="League not found")
        
        # Check if user already has a team in this league
        for team in league.teams:
            if team.owner == current_user.id:
                raise HTTPException(status_code=400, detail="You already have a team in this league")
        
        # Create new team
        new_team = Fantateam(
            name=join_request.team_name,
            owner=current_user.id,
            roster=[]
        )
        
        # Add team to league
        league.teams.append(new_team)
        
        # Update league
        league_data = LeagueCreate(
            name=league.name,
            created_by=league.created_by,
            is_public=league.is_public,
            teams=league.teams,
            competitions=league.competitions,
            settings=league.settings
        )
        
        updated_league = _update_league_by_id(league_id, league_data)
        return updated_league
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error joining league: {str(e)}")

@app.delete("/api/leagues/{league_id}/competitions/{competition_index}")
async def delete_competition(
    league_id: str,
    competition_index: int,
    current_user: User = Depends(_get_current_user)
):
    """Delete a competition from a league"""
    try:
        # Get existing league
        league = _get_league_by_id(league_id)
        if league is None:
            raise HTTPException(status_code=404, detail="League not found")
        
        # Check if user is the league creator
        if league.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="Only the league creator can delete competitions")
        
        # Check if competition index is valid
        if competition_index < 0 or competition_index >= len(league.competitions):
            raise HTTPException(status_code=404, detail="Competition not found")
        
        # Remove competition
        league.competitions.pop(competition_index)
        
        # Update league
        league_data = LeagueCreate(
            name=league.name,
            created_by=league.created_by,
            is_public=league.is_public,
            teams=league.teams,
            competitions=league.competitions,
            settings=league.settings
        )
        
        updated_league = _update_league_by_id(league_id, league_data)
        return {"message": "Competition deleted successfully", "league": updated_league}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting competition: {str(e)}")

@app.post("/api/leagues/join-with-code", response_model=League)
async def join_league_with_code(
    invite_code: str,
    join_request: JoinLeagueRequest,
    current_user: User = Depends(_get_current_user)
):
    """Join a league using an invite code"""
    try:
        leagues = _load_leagues()
        
        # Find league with matching invite code
        league_id = None
        for lid, league_data in leagues.items():
            if league_data.get('invite_code', '').upper() == invite_code.upper():
                league_id = lid
                break
        
        if league_id is None:
            raise HTTPException(status_code=404, detail="Invalid invite code")
        
        league = _get_league_by_id(league_id)
        if league is None:
            raise HTTPException(status_code=404, detail="League not found")
        
        # Check if user already has a team in this league
        for team in league.teams:
            if team.owner == current_user.id:
                raise HTTPException(status_code=400, detail="You already have a team in this league")
        
        # Create new team
        new_team = Fantateam(
            name=join_request.team_name,
            owner=current_user.id,
            roster=[]
        )
        
        # Add team to league
        league.teams.append(new_team)
        
        # Update league
        league_data = LeagueCreate(
            name=league.name,
            created_by=league.created_by,
            is_public=league.is_public,
            teams=league.teams,
            competitions=league.competitions,
            settings=league.settings
        )
        
        updated_league = _update_league_by_id(league_id, league_data)
        return updated_league
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error joining league with code: {str(e)}")

@app.delete("/api/leagues/{league_id}/leave", response_model=League)
async def leave_league(
    league_id: str,
    current_user: User = Depends(_get_current_user)
):
    """Leave a league by removing the user's team"""
    try:
        league = _get_league_by_id(league_id)
        if league is None:
            raise HTTPException(status_code=404, detail="League not found")
        
        # Find user's team in the league (check both ID and username for compatibility)
        user_team_index = None
        for i, team in enumerate(league.teams):
            if team.owner == current_user.id or team.owner == current_user.username:
                user_team_index = i
                break
        
        if user_team_index is None:
            raise HTTPException(status_code=404, detail="You don't have a team in this league")
        
        # Prevent league creator from leaving if there are other teams
        if league.created_by == current_user.id and len(league.teams) > 1:
            raise HTTPException(
                status_code=400, 
                detail="League creator cannot leave while other teams are in the league. Delete the league or transfer ownership first."
            )
        
        # Remove user's team
        league.teams.pop(user_team_index)
        
        # Update league
        league_data = LeagueCreate(
            name=league.name,
            created_by=league.created_by,
            is_public=league.is_public,
            teams=league.teams,
            competitions=league.competitions,
            settings=league.settings
        )
        
        updated_league = _update_league_by_id(league_id, league_data)
        return updated_league
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leaving league: {str(e)}")

@app.post("/api/leagues/{league_id}/admin/add-player", response_model=League)
async def admin_add_player_to_team(
    league_id: str,
    player_request: AdminAddPlayerRequest,
    current_user: User = Depends(_get_current_user)
):
    """Admin endpoint: Add a player to any team in the league"""
    try:
        league = _get_league_by_id(league_id)
        if league is None:
            raise HTTPException(status_code=404, detail="League not found")
        
        # Check if user is the league creator (admin)
        if league.created_by != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Only the league creator can add players to teams"
            )
        
        team_name = player_request.team_name
        
        # Find the team
        team_index = None
        for i, team in enumerate(league.teams):
            if team.name == team_name:
                team_index = i
                break
        
        if team_index is None:
            raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found in this league")
        
        # Get team and league settings
        team = league.teams[team_index]
        max_players_per_role = league.settings.get("max_players_per_role", {
            "P": 3,
            "D": 8,
            "C": 8,
            "A": 6
        })
        
        # Calculate total max players (25 by default: 3P + 8D + 8C + 6A)
        max_total_players = sum(max_players_per_role.values())
        
        # Check total roster limit
        if len(team.roster) >= max_total_players:
            raise HTTPException(
                status_code=400,
                detail=f"Team '{team_name}' has reached the maximum roster size ({max_total_players} players)"
            )
        
        # Check role-specific limit if role is specified
        if player_request.player_role:
            role = player_request.player_role.upper()
            if role in max_players_per_role:
                current_count = sum(1 for p in team.roster if p.role and p.role.upper() == role)
                max_for_role = max_players_per_role[role]
                
                if current_count >= max_for_role:
                    role_names = {
                        "P": "portieri",
                        "D": "difensori",
                        "C": "centrocampisti",
                        "A": "attaccanti"
                    }
                    raise HTTPException(
                        status_code=400,
                        detail=f"Team '{team_name}' has reached the maximum number of {role_names.get(role, role)} ({max_for_role})"
                    )
        
        # Check if player already exists in this team
        for player in team.roster:
            if player.name.lower() == player_request.player_name.lower():
                raise HTTPException(
                    status_code=400, 
                    detail=f"Player '{player_request.player_name}' already exists in team '{team_name}'"
                )
        
        # Create new player
        new_player = Player(
            id=str(uuid.uuid4()),
            name=player_request.player_name,
            role=player_request.player_role
        )
        
        # Add player to team roster
        league.teams[team_index].roster.append(new_player)
        
        # Update league
        league_data = LeagueCreate(
            name=league.name,
            created_by=league.created_by,
            is_public=league.is_public,
            teams=league.teams,
            competitions=league.competitions,
            settings=league.settings
        )
        
        updated_league = _update_league_by_id(league_id, league_data)
        return updated_league
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding player to team: {str(e)}")

@app.post("/api/leagues/{league_id}/admin/remove-player", response_model=League)
async def admin_remove_player_from_team(
    league_id: str,
    remove_request: AdminRemovePlayerRequest,
    current_user: User = Depends(_get_current_user)
):
    """Admin endpoint: Remove a player from any team in the league"""
    try:
        league = _get_league_by_id(league_id)
        if league is None:
            raise HTTPException(status_code=404, detail="League not found")
        
        # Check if user is the league creator (admin)
        if league.created_by != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Only the league creator can remove players from teams"
            )
        
        team_name = remove_request.team_name
        player_name = remove_request.player_name
        
        # Find the team
        team_index = None
        for i, team in enumerate(league.teams):
            if team.name == team_name:
                team_index = i
                break
        
        if team_index is None:
            raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found in this league")
        
        # Find and remove the player
        team = league.teams[team_index]
        player_index = None
        for i, player in enumerate(team.roster):
            if player.name.lower() == player_name.lower():
                player_index = i
                break
        
        if player_index is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Player '{player_name}' not found in team '{team_name}'"
            )
        
        # Remove player from roster
        league.teams[team_index].roster.pop(player_index)
        
        # Update league
        league_data = LeagueCreate(
            name=league.name,
            created_by=league.created_by,
            is_public=league.is_public,
            teams=league.teams,
            competitions=league.competitions,
            settings=league.settings
        )
        
        updated_league = _update_league_by_id(league_id, league_data)
        return updated_league
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing player from team: {str(e)}")

@app.get("/api/players")
async def get_players(
    league_id: Optional[str] = None,
    free_agents_only: bool = False,
    role: Optional[str] = None,
    search: Optional[str] = None,
    team: Optional[str] = None,
    min_quotazione: Optional[float] = None,
    max_quotazione: Optional[float] = None,
    min_fvm: Optional[float] = None,
    max_fvm: Optional[float] = None,
    sort_by: Optional[str] = None
):
    """
    Get all players with optional filtering and sorting.
    
    Parameters:
    - league_id: Filter players by league (if provided, shows only players in this league)
    - free_agents_only: If True, returns only players not assigned to any team
    - role: Filter by role (P, D, C, A)
    - search: Search players by name
    - team: Filter by Serie A team (e.g., INT, MIL, JUV)
    - min_quotazione: Minimum quotazione_attuale_classico
    - max_quotazione: Maximum quotazione_attuale_classico
    - min_fvm: Minimum fvm_classico
    - max_fvm: Maximum fvm_classico
    - sort_by: Sort results (quotazione_asc, quotazione_desc, fvm_asc, fvm_desc)
    """
    csv_path = os.path.join(BASE_DIR, "Estrai listone", "data", "quotazioni_fantacalcio.csv")
    scraper_name = "listone"
    
    try:
        # Check if we should run the scraper (once per day)
        should_scrape = _should_run_scraper(scraper_name, cache_hours=24)
        elapsed = 0
        
        if should_scrape or not os.path.exists(csv_path):
            try:
                stdout, elapsed = _run_python_scraper(os.path.join("Estrai listone", "src", "quotazioni_scraper.py"))
                _update_scraper_timestamp(scraper_name)
            except Exception as scraper_error:
                # If scraper fails but we have cached data, use it
                if not os.path.exists(csv_path):
                    raise HTTPException(status_code=500, detail=f"Player data not available and scraper failed: {str(scraper_error)}")
        
        # Read CSV
        df = pd.read_csv(csv_path)
        players = df.to_dict('records')
        
        # Get assigned players if filtering by league or free agents
        assigned_players = set()
        if league_id or free_agents_only:
            leagues = _load_leagues()
            
            if league_id:
                # Get players from specific league
                if league_id in leagues:
                    league_data = leagues[league_id]
                    for fantateam in league_data.get('teams', []):
                        for player in fantateam.get('roster', []):
                            if 'name' in player:
                                assigned_players.add(player['name'].lower())
            else:
                # Get all assigned players from all leagues
                for league_data in leagues.values():
                    for fantateam in league_data.get('teams', []):
                        for player in fantateam.get('roster', []):
                            if 'name' in player:
                                assigned_players.add(player['name'].lower())
        
        # Filter players
        filtered_players = []
        for player in players:
            # Free agents filter
            if free_agents_only and player.get('nome', '').lower() in assigned_players:
                continue
            
            # Role filter
            if role and player.get('ruolo', '').upper() != role.upper():
                continue
            
            # Search filter
            if search and search.lower() not in player.get('nome', '').lower():
                continue
            
            # Team filter
            if team:
                player_team = player.get('squadra', '')
                if isinstance(player_team, str) and player_team.upper() != team.upper():
                    continue
            
            # Quotazione filters
            quotazione = player.get('quotazione_attuale_classico')
            if quotazione is not None and not isinstance(quotazione, str):
                if min_quotazione is not None and quotazione < min_quotazione:
                    continue
                if max_quotazione is not None and quotazione > max_quotazione:
                    continue
            
            # FVM filters
            fvm = player.get('fvm_classico')
            if fvm is not None and not isinstance(fvm, str):
                if min_fvm is not None and fvm < min_fvm:
                    continue
                if max_fvm is not None and fvm > max_fvm:
                    continue
            
            filtered_players.append(player)
        
        # Sort players if requested
        if sort_by:
            if sort_by == 'quotazione_asc':
                filtered_players.sort(key=lambda p: p.get('quotazione_attuale_classico', 0) if isinstance(p.get('quotazione_attuale_classico'), (int, float)) else 0)
            elif sort_by == 'quotazione_desc':
                filtered_players.sort(key=lambda p: p.get('quotazione_attuale_classico', 0) if isinstance(p.get('quotazione_attuale_classico'), (int, float)) else 0, reverse=True)
            elif sort_by == 'fvm_asc':
                filtered_players.sort(key=lambda p: p.get('fvm_classico', 0) if isinstance(p.get('fvm_classico'), (int, float)) else 0)
            elif sort_by == 'fvm_desc':
                filtered_players.sort(key=lambda p: p.get('fvm_classico', 0) if isinstance(p.get('fvm_classico'), (int, float)) else 0, reverse=True)
        
        return {
            "status": "success",
            "count": len(filtered_players),
            "total": len(players),
            "scraper_seconds": round(elapsed, 2),
            "cached": not should_scrape and os.path.exists(csv_path),
            "data": filtered_players
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Player scraper timeout")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading players: {str(e)}")

@app.get("/api/get_listone")
async def get_listone():
    """Return player quotes (listone), only refresh if not updated in last 8 hours."""
    csv_path = os.path.join(BASE_DIR, "Estrai listone", "data", "quotazioni_fantacalcio.csv")
    scraper_name = "listone"
    
    try:
        # Check if we should run the scraper
        should_scrape = _should_run_scraper(scraper_name)
        elapsed = 0
        
        if should_scrape:
            # Run the scraper
            stdout, elapsed = _run_python_scraper(os.path.join("Estrai listone", "src", "quotazioni_scraper.py"))
            _update_scraper_timestamp(scraper_name)
        
        # Read the data (either freshly scraped or cached)
        if not os.path.exists(csv_path):
            # If no cached data exists, force run the scraper
            stdout, elapsed = _run_python_scraper(os.path.join("Estrai listone", "src", "quotazioni_scraper.py"))
            _update_scraper_timestamp(scraper_name)
        
        df = _read_csv(csv_path)
        players = df.to_dict('records')
        
        return {
            "status": "success",
            "count": len(players),
            "scraper_seconds": round(elapsed, 2),
            "cached": not should_scrape and os.path.exists(csv_path),
            "data": players
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Listone data not found after scraping")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Listone scraper timeout")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading listone: {str(e)}")

@app.get("/api/get_voti")
async def get_voti():
    """Return player votes (voti), only refresh if not updated in last 8 hours."""
    csv_path = os.path.join(BASE_DIR, "Estrai voti", "data", "voti_fantacalcio.csv")
    scraper_name = "voti"
    
    try:
        # Check if we should run the scraper
        should_scrape = _should_run_scraper(scraper_name)
        elapsed = 0
        
        if should_scrape:
            # Run the scraper
            stdout, elapsed = _run_python_scraper(os.path.join("Estrai voti", "src", "voti_scraper.py"), timeout=300)
            _update_scraper_timestamp(scraper_name)
        
        # Read the data (either freshly scraped or cached)
        if not os.path.exists(csv_path):
            # If no cached data exists, force run the scraper
            stdout, elapsed = _run_python_scraper(os.path.join("Estrai voti", "src", "voti_scraper.py"), timeout=300)
            _update_scraper_timestamp(scraper_name)
        
        df = _read_csv(csv_path)
        votes = df.to_dict('records')
        
        return {
            "status": "success",
            "count": len(votes),
            "scraper_seconds": round(elapsed, 2),
            "cached": not should_scrape and os.path.exists(csv_path),
            "data": votes
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Voti data not found after scraping")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Voti scraper timeout")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# DEBUG ENDPOINT - Simulate matches for testing
class SimulateMatchesRequest(BaseModel):
    """Model for simulating matches"""
    day: Optional[int] = Field(None, description="Specific day to simulate (if None, simulates next unplayed day)")
    num_days: int = Field(1, description="Number of days to simulate")

@app.post("/api/leagues/{league_id}/competitions/{competition_index}/simulate")
async def simulate_matches(
    league_id: str,
    competition_index: int,
    request: SimulateMatchesRequest,
    current_user: User = Depends(_get_current_user)
):
    """DEBUG: Simulate matches for a competition with random scores"""
    import random
    
    try:
        # Get existing league
        league = _get_league_by_id(league_id)
        if league is None:
            raise HTTPException(status_code=404, detail="League not found")
        
        # Check if user is the league creator
        if league.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="Only the league creator can simulate matches")
        
        # Check if competition index is valid
        if competition_index < 0 or competition_index >= len(league.competitions):
            raise HTTPException(status_code=404, detail="Competition not found")
        
        competition = league.competitions[competition_index]
        
        # Get matches to simulate
        if request.day is not None:
            # Simulate specific day(s)
            days_to_simulate = list(range(request.day, request.day + request.num_days))
        else:
            # Find next unplayed day
            played_days = set()
            unplayed_days = set()
            for match in competition.calendar:
                if match.played:
                    played_days.add(match.day)
                else:
                    unplayed_days.add(match.day)
            
            if not unplayed_days:
                raise HTTPException(status_code=400, detail="No unplayed matches found")
            
            next_day = min(unplayed_days)
            days_to_simulate = list(range(next_day, next_day + request.num_days))
        
        # Simulate matches for specified days
        simulated_matches = []
        for day in days_to_simulate:
            day_matches = [m for m in competition.calendar if m.day == day and not m.played]
            
            for match in day_matches:
                # Generate random scores (50-90 range typical for fantasy football)
                match.home_score = round(random.uniform(50.0, 90.0), 2)
                match.away_score = round(random.uniform(50.0, 90.0), 2)
                match.played = True
                
                simulated_matches.append({
                    "day": match.day,
                    "home_team": match.home_team,
                    "away_team": match.away_team,
                    "home_score": match.home_score,
                    "away_score": match.away_score
                })
                
                # Update standings if it's a championship
                if competition.type == CompetitionType.CHAMPIONSHIP:
                    _update_standings_for_match(competition.standings, match)
        
        # Save updated league
        leagues = _load_leagues()
        leagues[league_id] = league.model_dump()
        _save_leagues(leagues)
        
        return {
            "message": f"Simulated {len(simulated_matches)} matches across {len(days_to_simulate)} day(s)",
            "simulated_matches": simulated_matches,
            "days_simulated": days_to_simulate
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating matches: {str(e)}")

def _update_standings_for_match(standings: List[StandingEntry], match: Match):
    """Update standings based on match result"""
    if match.home_score is None or match.away_score is None:
        return
    
    # Find teams in standings
    home_standing = next((s for s in standings if s.team_name == match.home_team), None)
    away_standing = next((s for s in standings if s.team_name == match.away_team), None)
    
    if not home_standing or not away_standing:
        return
    
    # Update stats
    home_standing.played += 1
    away_standing.played += 1
    
    home_standing.goals_for += match.home_score
    home_standing.goals_against += match.away_score
    away_standing.goals_for += match.away_score
    away_standing.goals_against += match.home_score
    
    # Determine result
    if match.home_score > match.away_score:
        home_standing.won += 1
        home_standing.points += 3
        away_standing.lost += 1
    elif match.home_score < match.away_score:
        away_standing.won += 1
        away_standing.points += 3
        home_standing.lost += 1
    else:
        home_standing.drawn += 1
        home_standing.points += 1
        away_standing.drawn += 1
        away_standing.points += 1
    
    # Update goal difference
    home_standing.goal_difference = home_standing.goals_for - home_standing.goals_against
    away_standing.goal_difference = away_standing.goals_for - away_standing.goals_against

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
