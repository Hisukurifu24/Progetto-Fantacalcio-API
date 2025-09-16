from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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
from datetime import datetime, timedelta

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

class Competition(BaseModel):
    """Competition model based on Godot structure"""
    name: str = ""
    type: CompetitionType = CompetitionType.POINTS
    participants: List[Player] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=lambda: {
        "start_day": 1,
        "end_day": 38,
    })

class Fantateam(BaseModel):
    """Fantateam model based on Godot structure"""
    name: str = ""
    owner: str = ""
    roster: List[Player] = Field(default_factory=list)

class League(BaseModel):
    """League model based on Godot structure"""
    id: Optional[str] = Field(default=None, description="Unique league ID (auto-generated)")
    name: str = Field(..., description="League name")
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
    # Use current Python interpreter available in container
    proc = subprocess.run([
        "python", script_abs
    ], capture_output=True, text=True, timeout=timeout)
    elapsed = time.time() - start
    if proc.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Scraper failed ({script_rel_path}): {proc.stderr[:500]}")
    return proc.stdout, elapsed

def _read_csv(csv_path: str):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)
    return pd.read_csv(csv_path)

# League storage functions
LEAGUES_FILE = os.path.join("data", "leagues.json")
SCRAPER_TIMESTAMPS_FILE = os.path.join("data", "scraper_timestamps.json")

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

def _create_league(league_data: LeagueCreate) -> League:
    """Create a new league with unique ID and save it"""
    leagues = _load_leagues()
    
    # Generate unique ID
    league_id = _generate_league_id()
    while league_id in leagues:
        league_id = _generate_league_id()
    
    # Create league object
    league = League(
        id=league_id,
        name=league_data.name,
        teams=league_data.teams,
        competitions=league_data.competitions,
        settings=league_data.settings
    )
    
    # Save to storage
    leagues[league_id] = league.model_dump()
    _save_leagues(leagues)
    
    return league

def _get_league_by_id(league_id: str) -> Optional[League]:
    """Get a league by its ID"""
    leagues = _load_leagues()
    if league_id in leagues:
        return League(**leagues[league_id])
    return None

def _get_all_leagues() -> List[League]:
    """Get all leagues"""
    leagues = _load_leagues()
    return [League(**league_data) for league_data in leagues.values()]

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

def _should_run_scraper(scraper_name: str, cache_hours: int = 8) -> bool:
    """Check if scraper should run based on last run time"""
    timestamps = _load_scraper_timestamps()
    
    if scraper_name not in timestamps:
        return True  # Never run before, should run
    
    try:
        last_run = datetime.fromisoformat(timestamps[scraper_name])
        time_since_run = datetime.now() - last_run
        return time_since_run > timedelta(hours=cache_hours)
    except (ValueError, TypeError):
        return True  # Invalid timestamp, should run

@app.post("/api/leagues", response_model=League)
async def create_league(league_data: LeagueCreate):
    """Create a new fantasy league"""
    try:
        league = _create_league(league_data)
        return league
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating league: {str(e)}")

@app.get("/api/leagues", response_model=List[League])
async def get_all_leagues():
    """Get all fantasy leagues"""
    try:
        leagues = _get_all_leagues()
        return leagues
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving leagues: {str(e)}")

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

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
