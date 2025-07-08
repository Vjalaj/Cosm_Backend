# 🌌 Cosmic Explorer Backend API 🚀

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13.5-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.2.3-green?style=for-the-badge&logo=flask&logoColor=white)
![Heroku](https://img.shields.io/badge/Heroku-Ready-purple?style=for-the-badge&logo=heroku&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A sophisticated space information API that uses Natural Language Processing to understand queries and provides real-time space data through intelligent web scraping.**

[🚀 Live Demo](#) • [📖 API Docs](#api-endpoints) • [🐛 Report Bug](../../issues) • [✨ Request Feature](../../issues)

</div>

---

## ✨ What Makes This Special

🧠 **Advanced NLP Engine** - NLTK-powered natural language understanding for space queries  
🌐 **Multi-Source Intelligence** - Scrapes NASA, SpaceX, Space.com, Wikipedia, and more  
🎯 **Smart Intent Recognition** - Understands Mars missions, ISS updates, rocket launches, etc.  
⚡ **Real-Time Data** - Fresh space news and mission updates  
🔄 **RESTful API** - Clean, documented endpoints for easy integration  
📊 **Relevance Scoring** - Smart ranking algorithm for search results  
🐳 **Production Ready** - Heroku-optimized with gunicorn and proper logging  
🛡️ **Robust Error Handling** - Comprehensive exception management and logging  

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │───▶│  Flask API       │───▶│  Space Scraper  │
│   (Frontend)    │    │  (api.py)        │    │  (NLP Engine)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
                       ┌──────────────┐         ┌─────────────────┐
                       │   Logging    │         │  Web Sources    │
                       │   System     │         │  NASA, SpaceX   │
                       └──────────────┘         │  Wikipedia, etc │
                                               └─────────────────┘
```

### 🔧 Core Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **`api.py`** | Main Flask application & REST endpoints | Flask, CORS |
| **`space_scraper.py`** | NLP processing & web scraping engine | NLTK, BeautifulSoup, Requests |
| **`utils.py`** | Data processing utilities | Python |
| **`config.py`** | Application configuration | Python |

## ⚡ Quick Start

### 🐳 Deploy to Heroku (Recommended)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

```bash
# Clone the repository
git clone https://github.com/Vjalaj/Cosm_Backend.git
cd cosmic-explorer-backend

# Deploy to Heroku
heroku create your-app-name
git push heroku main
```

### 🖥️ Local Development

```bash
# 1. Clone and setup
git clone https://github.com/Vjalaj/Cosm_Backend.git
cd cosmic-explorer-backend

# 2. Create virtual environment (REQUIRED)
python -m venv venv

# 3. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the API server
python api.py
```

🎉 **API will be running at** `http://localhost:5000`

### 🔗 Connect Your Frontend

This backend is designed to work with any frontend framework. Set your API base URL to:
- **Local Development**: `http://localhost:5000`
- **Production**: `https://your-heroku-app.herokuapp.com`

## 🤔 Common Issues & Solutions

### If the app fails to start:

1. **Virtual Environment Issues**:
   ```powershell
   # Recreate the virtual environment
   python -m venv venv --clear
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Flask/Werkzeug Compatibility**:
   ```powershell
   pip uninstall -y flask werkzeug
   pip install flask==2.0.1 werkzeug==2.0.1
   ```

3. **Frontend Dependencies**:
   ```powershell
   cd frontend
   npm ci  # Clean install of dependencies
   ```

4. **Network Connectivity**:
   - The app needs internet access to scrape space information
   - Check your firewall settings if web scraping fails

### Common Backend Issues

If you encounter this error when starting the Flask backend:
```
ImportError: cannot import name 'url_quote' from 'werkzeug.urls'
```
Use the `cosm.bat` script which will automatically set up the correct environment. Alternatively, try reinstalling Flask and Werkzeug manually:
```powershell
pip uninstall -y flask werkzeug
pip install -r requirements.txt
```

### Common Frontend Issues

If you encounter this error when starting the React frontend:
```
'react-scripts' is not recognized as an internal or external command
```
Use the `cosm.bat` script which automatically checks and fixes frontend dependencies. For manual fixing:
```powershell
cd frontend
# Update the react-scripts version in package.json to "5.0.1"
npm install
```

## 🧠 How the NLP Engine Works

```python
# Example of how queries are processed
query = "What are the latest SpaceX Starship updates?"

# 1. Tokenization & Cleaning
tokens = ["latest", "spacex", "starship", "updates"]

# 2. Intent Detection
intents = ["spacex", "starship", "news"]

# 3. Source Selection
sources = ["spacex.com", "space.com", "nasa.gov"]

# 4. Web Scraping & Content Extraction
results = scrape_multiple_sources(query, sources)

# 5. Relevance Scoring & Ranking
ranked_results = rank_by_relevance(results, query)
```

### 🎯 Supported Query Types

| Intent | Examples | Sources Used |
|--------|----------|-------------|
| **Mars Missions** | "Mars rover updates", "Perseverance news" | NASA, Space.com, Wikipedia |
| **SpaceX** | "Falcon Heavy launch", "Starship test" | SpaceX.com, Space.com |
| **ISS** | "Space station crew", "ISS experiments" | NASA, Space Facts |
| **Astronomy** | "Hubble discoveries", "James Webb telescope" | NASA Science, Universe Today |
| **General Space** | "Space news", "astronomical events" | Multiple sources |

## 🌐 Data Sources

<div align="center">

| Source | Type | Use Case |
|--------|------|----------|
| 🚀 **NASA** | Official | Mission updates, scientific discoveries |
| 🛸 **SpaceX** | Official | Rocket launches, Starship development |
| 📰 **Space.com** | News | Breaking space news, analysis |
| 📚 **Wikipedia** | Encyclopedia | Comprehensive space topics |
| 🔍 **Google** | Search | Real-time web results |
| 🌌 **Universe Today** | News | Astronomy and space exploration |
| 🪐 **Space Facts** | Educational | Planetary and space facts |

</div>

## ⚙️ Configuration

### Environment Variables

```bash
# Required for production
PORT=5000                    # Server port (Heroku sets this automatically)

# Optional
DEBUG=False                  # Enable debug mode (default: True in development)
LOG_LEVEL=INFO              # Logging level
CACHE_TIMEOUT=3600          # Cache timeout in seconds
```

### Logging

The application uses structured logging:
- **Console**: Real-time logs during development
- **File**: `logs/api.log` for persistent logging
- **Levels**: INFO, WARNING, ERROR with timestamps

## 🚨 Error Handling

The API includes comprehensive error handling:

```json
// Example error response
{
  "error": "Failed to process query",
  "details": "Network timeout while scraping NASA.gov",
  "timestamp": "2025-07-08T10:30:00Z",
  "request_id": "req_123456789"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (empty query)
- `500` - Internal Server Error
- `503` - Service Unavailable (scraping failed)

## 📡 API Endpoints

### 🔍 Search Space Information
```http
POST /api/search
Content-Type: application/json

{
  "query": "Latest NASA Mars missions"
}
```

**Response:**
```json
{
  "query_info": {
    "original_query": "Latest NASA Mars missions",
    "processed_tokens": ["latest", "nasa", "mars", "mission"],
    "detected_intents": ["mars", "nasa", "mission"],
    "space_keywords": ["nasa", "mars", "mission"]
  },
  "results": [
    {
      "title": "NASA's Perseverance Rover Discovers...",
      "content": "NASA's Mars rover has made a groundbreaking discovery...",
      "url": "https://www.nasa.gov/news/...",
      "source": "NASA",
      "relevance_score": 0.95,
      "scraped_at": "2025-07-08T10:30:00Z"
    }
  ],
  "total_results": 15,
  "sources_used": ["NASA", "Space.com", "Wikipedia"],
  "processing_time": "2.3s"
}
```

### 💡 Get Example Queries
```http
GET /api/examples
```

**Response:**
```json
{
  "examples": [
    "Latest NASA missions to Mars",
    "SpaceX rocket launches this year",
    "International Space Station updates",
    "Hubble telescope discoveries",
    "Solar system exploration"
  ]
}
```

### ❤️ Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "ok"
}
```

## 🤔 Troubleshooting

<details>
<summary><strong>❌ Common Issues & Solutions</strong></summary>

### Virtual Environment Issues
```bash
# Recreate virtual environment
python -m venv venv --clear
# Windows
.\venv\Scripts\activate
# macOS/Linux  
source venv/bin/activate
pip install -r requirements.txt
```

### Flask/Werkzeug Compatibility
```bash
pip uninstall -y flask werkzeug
pip install flask==2.2.3 werkzeug==2.2.3
```

### Network/Scraping Issues
- Ensure internet connectivity
- Check firewall settings
- Some sources may have rate limiting

### Import Errors
```bash
# If you see "ImportError: cannot import name 'url_quote'"
pip install --upgrade flask werkzeug
```

</details>

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_space_scraper.py -v

# Test the API endpoints
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Mars rover news"}'
```

## 🚀 Performance

- **Response Time**: ~2-5 seconds per query
- **Concurrent Requests**: Handles multiple simultaneous requests
- **Caching**: Smart caching for repeated queries
- **Scalability**: Heroku-ready with gunicorn workers

## 📊 Monitoring

Track your API usage:
- Check `logs/api.log` for detailed request logs
- Monitor response times and error rates
- Use Heroku metrics for production monitoring

## 🛡️ Security

- **Input Validation**: All queries are sanitized
- **Rate Limiting**: Prevents abuse (implement as needed)
- **CORS**: Configured for cross-origin requests
- **Environment Variables**: Sensitive data in config vars

## 🤝 Contributing

We love contributions! Here's how you can help:

### 🐛 Found a Bug?
1. Check if it's already reported in [Issues](../../issues)
2. Create a new issue with detailed steps to reproduce
3. Include logs and system information

### ✨ Want to Add a Feature?
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

### 📝 Contribution Guidelines
- Follow PEP 8 for Python code
- Add docstrings to new functions
- Update tests for new features
- Update this README if needed

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## � Acknowledgments

- **NLTK Team** - For natural language processing tools
- **Flask Community** - For the amazing web framework
- **Space Agencies** - NASA, SpaceX, ESA for providing public data
- **Contributors** - Everyone who helps improve this project

## 📞 Support

Need help? We've got you covered:

- 📖 **Documentation**: You're reading it!
- 🐛 **Bug Reports**: [GitHub Issues](../../issues)
- 💬 **Discussions**: [GitHub Discussions](../../discussions)
- 📧 **Contact**: Open an issue for any questions

---

<div align="center">

**Built with ❤️ for space enthusiasts everywhere**

⭐ **Star this repo if you found it helpful!** ⭐

[🚀 Deploy Now](https://heroku.com/deploy) • [📖 API Docs](#-api-endpoints) • [🤝 Contribute](#-contributing)

</div>
