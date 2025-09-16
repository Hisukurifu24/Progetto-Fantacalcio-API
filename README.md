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

### Local Development

1. **Clone & Navigate**
```bash
git clone https://github.com/Hisukurifu24/Progetto-Fantacalcio-API.git
cd Progetto-Fantacalcio-API/Fantasy-Football-API
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the Server**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Documentation

- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

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

### Create a League
```bash
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

### Get Player Quotes
```bash
curl "http://localhost:8000/api/get_listone"
```

### Get Match Ratings
```bash
curl "http://localhost:8000/api/get_voti"
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
- FastAPI
- Pandas
- Requests
- BeautifulSoup4 (for scraping)

### Environment Variables
- `BASE_DIR`: Base directory for data files (default: "..")
- `PORT`: Server port (default: 8000)

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