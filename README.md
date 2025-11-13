# Fantasy Football API 🏆

A comprehensive REST API for managing fantasy football leagues and automatically scraping Italian Serie A player data from Fantacalcio.it.

## ✨ Features

- 🏆 **League Management**: Create and manage fantasy football leagues
- 📊 **Player Quotes**: Auto-scrape real-time player market values
- ⚽ **Match Ratings**: Auto-scrape player performance and match votes
- 🔄 **Real-time Data**: Fresh data pulled directly from Fantacalcio.it
- 📱 **REST API**: Modern FastAPI with automatic documentation
- 🐳 **Docker Ready**: Containerized for easy deployment

## 🚀 Quick Start

### Local Development (Python)

#### 🪟 Windows - One-Click Start (Easiest!)

1. **Clone the repository**
```bash
git clone https://github.com/Hisukurifu24/Progetto-Fantacalcio-API.git
cd Progetto-Fantacalcio-API
```

2. **Double-click `start_local.bat`** or run in terminal:
```bash
start_local.bat
```

This script will automatically:
- ✅ Create a virtual environment (if needed)
- ✅ Install all dependencies
- ✅ Start the server on http://localhost:8000

#### 🐧 Manual Setup (All Platforms)

1. **Clone & Navigate**
```bash
git clone https://github.com/Hisukurifu24/Progetto-Fantacalcio-API.git
cd Progetto-Fantacalcio-API
```

2. **Create Virtual Environment** (Recommended)
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. **Navigate to API Directory**
```bash
cd Fantasy-Football-API
```

4. **Install Dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the Server**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

**✅ Server is running when you see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

**🛑 To stop:** Press `CTRL+C` in the terminal

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in detached mode (background)
docker-compose up -d

# Stop containers
docker-compose down
```

### 📚 Documentation & Testing

Once the server is running, access:

- **🌐 Main API**: http://localhost:8000
- **📖 Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **📋 Alternative Docs (ReDoc)**: http://localhost:8000/redoc

The interactive docs allow you to test all endpoints directly from your browser!

## 📋 API Endpoints

### Core Endpoints
- `GET /` - API information and status

### League Management
- `POST /api/leagues` - Create a new fantasy league
- `GET /api/leagues` - Get all leagues
- `GET /api/leagues/{league_id}` - Get specific league by ID

### Data Scraping
- `GET /api/get_listone` - Scrape and return player quotes (market values)
- `GET /api/get_voti` - Scrape and return match ratings/votes

## 🏗️ Project Structure

```
Progetto-Fantacalcio-API/
├── Fantasy-Football-API/           # Main API application
│   ├── main.py                    # FastAPI server
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Container configuration
│   └── data/                     # API data storage
├── Estrai listone/               # Player quotes scraper
│   ├── src/quotazioni_scraper.py # Scraping logic
│   └── data/                     # Scraped quotes data
├── Estrai voti/                  # Match ratings scraper
│   ├── src/voti_scraper.py       # Scraping logic
│   └── data/                     # Scraped votes data
├── docker-compose.yml            # Multi-container setup
└── Dockerfile                    # Main container config
```

## 🎯 Usage Examples

### Using the Interactive Docs (Easiest)
Visit http://localhost:8000/docs and use the "Try it out" buttons to test endpoints directly in your browser!

### Using curl

#### Create a League
```bash
# Windows (PowerShell) - use backtick for line continuation
curl -X POST "http://localhost:8000/api/leagues" `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Champions League 2025\",\"teams\":[{\"name\":\"Team Alpha\",\"owner\":\"Player1\",\"roster\":[]}]}'

# Linux/Mac
curl -X POST "http://localhost:8000/api/leagues" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Champions League 2025",
    "teams": [
      {
        "name": "Team Alpha",
        "owner": "Player1",
        "roster": []
      }
    ]
  }'
```

#### Get Player Quotes
```bash
curl "http://localhost:8000/api/get_listone"
```

#### Get Match Ratings
```bash
curl "http://localhost:8000/api/get_voti"
```

#### Get All Leagues
```bash
curl "http://localhost:8000/api/leagues"
```

### Using PowerShell's Invoke-RestMethod
```powershell
# Create a League
$body = @{
    name = "Champions League 2025"
    teams = @(
        @{
            name = "Team Alpha"
            owner = "Player1"
            roster = @()
        }
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/leagues" -Method Post -Body $body -ContentType "application/json"

# Get all leagues
Invoke-RestMethod -Uri "http://localhost:8000/api/leagues" -Method Get

# Get player quotes
Invoke-RestMethod -Uri "http://localhost:8000/api/get_listone" -Method Get
```

## 🔧 Data Models

### League Structure
```json
{
  "id": "unique-league-id",
  "name": "League Name",
  "teams": [
    {
      "name": "Team Name",
      "owner": "Owner Name", 
      "roster": [
        {
          "name": "Player Name",
          "role": "A"
        }
      ]
    }
  ],
  "competitions": [],
  "settings": {
    "start_day": 1,
    "max_budget": 500,
    "max_players_per_role": {
      "P": 3, "D": 8, "C": 8, "A": 6
    }
  }
}
```

## 🔄 Data Sources

The API integrates with automated scrapers that collect real-time data from:

- **Fantacalcio.it** - Official Italian fantasy football platform
- **Player Quotes** - Market values and player pricing
- **Match Ratings** - Weekly performance scores, goals, assists, bonus points

## 🐳 Docker Configuration

The project includes multiple deployment options:

- **Development**: Run locally with Python
- **Production**: Docker container with optimized settings
- **Multi-service**: Docker Compose for full stack deployment

## 🛠️ Development

### Requirements
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Dependencies
- FastAPI - Modern web framework
- Uvicorn - ASGI server
- Pydantic - Data validation
- Pandas - Data manipulation
- Requests - HTTP client
- BeautifulSoup4 - Web scraping

### Environment Variables
- `BASE_DIR`: Base directory for data files (default: "..")
- `PORT`: Server port (default: 8000)

### Project Commands

#### Windows PowerShell
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Deactivate virtual environment
deactivate

# Run server with auto-reload
cd Fantasy-Football-API
python main.py

# Install new package
pip install package-name
pip freeze > requirements.txt
```

#### Linux/Mac
```bash
# Activate virtual environment
source .venv/bin/activate

# Deactivate virtual environment
deactivate

# Run server with auto-reload
cd Fantasy-Football-API
python main.py

# Install new package
pip install package-name
pip freeze > requirements.txt
```

### Troubleshooting

**Server won't start?**
- Ensure you're in the `Fantasy-Football-API` directory
- Check if port 8000 is already in use
- Verify Python version: `python --version` (need 3.8+)
- Reinstall dependencies: `pip install -r requirements.txt`

**Import errors?**
- Make sure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

**Can't access http://localhost:8000?**
- Check if server is running in terminal
- Try http://127.0.0.1:8000 instead
- Check firewall settings

## 📈 Roadmap

- [ ] Enhanced league statistics and analytics
- [ ] Player performance predictions
- [ ] Automated tournament scheduling
- [ ] Mobile app integration
- [ ] Real-time notifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

---

**Made with ⚽ for Italian Fantasy Football enthusiasts**