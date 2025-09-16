from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import uvicorn
import os
import subprocess
import shutil
import time

# Read base directory from environment so paths are configurable in Docker/hosts
BASE_DIR = os.getenv("BASE_DIR", "..")

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

@app.get("/api/get_listone")
async def get_listone():
    """Always refresh and return player quotes (listone)."""
    try:
        stdout, elapsed = _run_python_scraper(os.path.join("Estrai listone", "src", "quotazioni_scraper.py"))
        csv_path = os.path.join(BASE_DIR, "Estrai listone", "data", "quotazioni_fantacalcio.csv")
        df = _read_csv(csv_path)
        players = df.to_dict('records')
        return {
            "status": "success",
            "count": len(players),
            "scraper_seconds": round(elapsed, 2),
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
    """Always refresh and return player votes (voti)."""
    try:
        stdout, elapsed = _run_python_scraper(os.path.join("Estrai voti", "src", "voti_scraper.py"), timeout=300)
        csv_path = os.path.join(BASE_DIR, "Estrai voti", "data", "voti_fantacalcio.csv")
        df = _read_csv(csv_path)
        votes = df.to_dict('records')
        return {
            "status": "success",
            "count": len(votes),
            "scraper_seconds": round(elapsed, 2),
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
