# Fantasy Football API

A comprehensive REST API for managing fantasy football data, including player quotes and match ratings.

## Features

- 📊 **Player Management**: Get player information, quotes, and statistics
- ⚽ **Match Ratings**: Access detailed match performance data
- 🔄 **Data Scraping**: Automated data collection from external sources
- 📈 **Statistics**: Advanced analytics and performance metrics
- 🎯 **Filtering**: Powerful search and filtering capabilities
- 📄 **Documentation**: Auto-generated OpenAPI/Swagger documentation

## Quick Start

### Installation

1. **Clone the repository**
```bash
cd Fantasy-Football-API
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the API server**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Players
- `GET /api/v1/players/` - Get all players with pagination
- `GET /api/v1/players/search` - Search players with filters
- `GET /api/v1/players/{name}` - Get single player by name  
- `GET /api/v1/players/{name}/ratings` - Get player with match ratings
- `GET /api/v1/players/team/{team}` - Get players by team
- `GET /api/v1/players/role/{role}` - Get players by position
- `GET /api/v1/players/teams/list` - Get all teams
- `POST /api/v1/players/refresh` - Refresh player data

### Match Ratings  
- `GET /api/v1/matches/` - Get match ratings with filters
- `GET /api/v1/matches/player/{name}` - Get ratings for specific player
- `GET /api/v1/matches/team/{team}` - Get team match ratings
- `GET /api/v1/matches/matchday/{number}` - Get matchday ratings
- `GET /api/v1/matches/top-performers` - Get top performing players

### Data Scraping
- `POST /api/v1/scrapers/quotazioni` - Run player quotes scraper
- `POST /api/v1/scrapers/voti` - Run match ratings scraper  
- `POST /api/v1/scrapers/all` - Run all scrapers
- `GET /api/v1/scrapers/status/{task_id}` - Get scraper task status
- `GET /api/v1/scrapers/status` - Get all scraper tasks
- `POST /api/v1/scrapers/refresh-data` - Refresh API data from files
- `POST /api/v1/scrapers/scrape-and-refresh` - Scrape and refresh in one operation

## Data Sources

The API integrates with existing Python scrapers that collect data from:
- **Fantacalcio.it** - Player quotes and market values
- **Match data** - Performance ratings, goals, assists, and bonus points

## Project Structure

```
Fantasy-Football-API/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py     # Pydantic data models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── players.py     # Player endpoints
│   │   ├── matches.py     # Match rating endpoints  
│   │   └── scrapers.py    # Scraper control endpoints
│   └── services/
│       ├── __init__.py
│       ├── data_manager.py    # Data loading and management
│       └── scraper_service.py # Scraper execution service
└── data/                  # Local data storage (created automatically)
```

## Usage Examples

### Get all players
```bash
curl "http://localhost:8000/api/v1/players/"
```

### Search players by team and position
```bash
curl "http://localhost:8000/api/v1/players/search?squadra=Inter&ruolo=A"
```

### Get player with match ratings
```bash  
curl "http://localhost:8000/api/v1/players/Lautaro Martinez/ratings"
```

### Get top scorers
```bash
curl "http://localhost:8000/api/v1/matches/top-performers?metric=gol&limit=10"
```

### Run scrapers to update data
```bash
# Run all scrapers
curl -X POST "http://localhost:8000/api/v1/scrapers/all"

# Check scraper status  
curl "http://localhost:8000/api/v1/scrapers/status"

# Refresh API data after scraping
curl -X POST "http://localhost:8000/api/v1/scrapers/refresh-data"
```

## Configuration

The API automatically detects and uses data from the existing scraper projects:
- `../Estrai listone/data/quotazioni_fantacalcio.csv` - Player quotes
- `../Estrai voti/data/voti_fantacalcio.csv` - Match ratings

## Development

### Running in Development Mode
```bash
# With auto-reload
uvicorn main:app --reload --port 8000

# Or using the main.py file
python main.py
```

### API Response Format
All endpoints return a consistent response format:
```json
{
    "success": true,
    "message": "Description of the operation",
    "data": { /* Response data */ },
    "count": 42  /* Optional: number of items returned */
}
```

## Error Handling

The API provides detailed error messages and appropriate HTTP status codes:
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource doesn't exist)  
- `500` - Internal Server Error (server issues)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Progetto-Fantacalcio ecosystem.
