from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from space_scraper import SpaceInfoScraper

# Set up API logging
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/api.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
except Exception as e:
    # Fallback to basic configuration if file handler fails
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    print(f"Warning: Could not set up file logging: {str(e)}")

logger = logging.getLogger("api")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the space scraper
scraper = SpaceInfoScraper()
logger.info("API initialized with SpaceInfoScraper")

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    
    if not query.strip():
        logger.warning("Empty query received")
        return jsonify({'error': 'Please provide a query'}), 400
    
    logger.info(f"Received search request for query: '{query}'")
    
    try:
        logger.info(f"Processing query with scraper: '{query}'")
        results = scraper.get_space_info(query)
        logger.info(f"Query processed. Found {len(results.get('results', []))} results")
        return jsonify(results)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"ERROR processing query '{query}': {str(e)}\n{error_traceback}")
        return jsonify({'error': str(e), 'details': error_traceback}), 500

@app.route('/api/examples', methods=['GET'])
def get_examples():
    examples = [
        "Latest NASA missions to Mars",
        "SpaceX rocket launches this year",
        "International Space Station updates",
        "Hubble telescope discoveries",
        "Solar system exploration",
        "Moon landing missions",
        "Asteroid and comet news",
        "Galaxy and universe studies"
    ]
    logger.info("Examples requested")
    return jsonify({'examples': examples})

@app.route('/health', methods=['GET'])
def health_check():
    logger.info("Health check requested")
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
