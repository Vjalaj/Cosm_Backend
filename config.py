"""
Configuration module for the Cosmic Explorer application.
Contains settings, constants, and configuration parameters.
"""

import os
from typing import Dict, List, Tuple

class Config:
    """Application configuration class."""
    
    # Application settings
    APP_NAME = "Cosmic Explorer Pro"
    APP_VERSION = "2.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Web scraping settings
    REQUEST_TIMEOUT = 10
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    # User agents for web scraping
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    # Space information sources
    SPACE_SOURCES = {
        'nasa': {
            'name': 'NASA',
            'base_url': 'https://www.nasa.gov',
            'news_url': 'https://www.nasa.gov/news/',
            'enabled': True,
            'priority': 1
        },
        'spacex': {
            'name': 'SpaceX',
            'base_url': 'https://www.spacex.com',
            'news_url': 'https://www.spacex.com/',
            'enabled': True,
            'priority': 2
        },
        'space_com': {
            'name': 'Space.com',
            'base_url': 'https://www.space.com',
            'search_url': 'https://www.space.com/search?q={}',
            'enabled': True,
            'priority': 3
        },
        'esa': {
            'name': 'ESA',
            'base_url': 'https://www.esa.int',
            'news_url': 'https://www.esa.int/Newsroom',
            'enabled': True,
            'priority': 4
        },
        'wikipedia': {
            'name': 'Wikipedia',
            'base_url': 'https://en.wikipedia.org',
            'search_url': 'https://en.wikipedia.org/wiki/Special:Search?search={}&go=Go',
            'enabled': True,
            'priority': 5
        }
    }
    
    # NLP configuration
    NLP_CONFIG = {
        'max_keywords': 10,
        'min_word_length': 3,
        'stopwords_language': 'english',
        'lemmatize': True,
        'remove_punctuation': True
    }
    
    # Space-related keywords and categories
    SPACE_KEYWORDS = {
        'nasa': ['nasa', 'space', 'mission', 'rocket', 'astronaut', 'administration'],
        'mars': ['mars', 'red', 'planet', 'rover', 'perseverance', 'curiosity', 'martian'],
        'moon': ['moon', 'lunar', 'apollo', 'artemis', 'selenian'],
        'iss': ['iss', 'international', 'space', 'station', 'orbit'],
        'spacex': ['spacex', 'falcon', 'dragon', 'elon', 'musk', 'starship'],
        'satellite': ['satellite', 'orbit', 'gps', 'communication'],
        'solar': ['solar', 'sun', 'system', 'planet', 'heliocentric'],
        'asteroid': ['asteroid', 'meteor', 'comet', 'meteorite', 'celestial'],
        'hubble': ['hubble', 'telescope', 'image', 'observation'],
        'launch': ['launch', 'rocket', 'mission', 'liftoff', 'countdown'],
        'galaxy': ['galaxy', 'milky', 'way', 'star', 'galactic'],
        'universe': ['universe', 'cosmos', 'big', 'bang', 'cosmic'],
        'exploration': ['exploration', 'probe', 'discovery', 'research'],
        'technology': ['technology', 'spacecraft', 'engine', 'propulsion'],
        'crew': ['crew', 'astronaut', 'cosmonaut', 'spacewalk', 'eva']
    }
    
    # Search intent categories
    INTENT_CATEGORIES = {
        'exploration': ['mars', 'moon', 'planet', 'rover', 'mission', 'exploration', 'probe'],
        'technology': ['rocket', 'satellite', 'spacecraft', 'technology', 'engine', 'propulsion'],
        'discovery': ['telescope', 'hubble', 'james webb', 'discovery', 'observation', 'image'],
        'commercial': ['spacex', 'blue origin', 'commercial', 'private', 'company'],
        'research': ['research', 'study', 'experiment', 'science', 'analysis', 'data'],
        'international': ['iss', 'international', 'cooperation', 'station', 'crew', 'multinational'],
        'military': ['space force', 'defense', 'security', 'military', 'surveillance'],
        'scientific': ['physics', 'astronomy', 'astrophysics', 'cosmology', 'science']
    }
    
    # UI configuration
    UI_CONFIG = {
        'max_results_default': 10,
        'max_results_limit': 50,
        'results_per_page': 10,
        'show_relevance_scores': True,
        'show_source_logos': True,
        'enable_dark_theme': True,
        'animation_speed': 300  # milliseconds
    }
    
    # Color schemes
    COLOR_SCHEMES = {
        'cosmic': {
            'primary': '#00d4ff',
            'secondary': '#ff0080',
            'accent': '#ffed4a',
            'background': '#0f0f23',
            'surface': 'rgba(255,255,255,0.1)',
            'text': '#ffffff',
            'text_secondary': '#a0a0a0'
        },
        'nebula': {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'accent': '#f093fb',
            'background': '#1a1a2e',
            'surface': 'rgba(102,126,234,0.1)',
            'text': '#ffffff',
            'text_secondary': '#d0d0d0'
        }
    }
    
    # Caching configuration
    CACHE_CONFIG = {
        'enable_caching': True,
        'cache_duration': 3600,  # 1 hour in seconds
        'max_cache_size': 100,   # maximum number of cached queries
        'cache_file': 'cache/space_cache.json'
    }
    
    # Rate limiting
    RATE_LIMIT_CONFIG = {
        'enable_rate_limiting': True,
        'requests_per_minute': 30,
        'requests_per_hour': 500,
        'cooldown_period': 60  # seconds
    }
    
    # Error handling
    ERROR_CONFIG = {
        'max_error_retries': 3,
        'error_timeout': 5,
        'fallback_enabled': True,
        'error_logging': True
    }

class SpaceAgencies:
    """Space agency information and endpoints."""
    
    AGENCIES = {
        'NASA': {
            'full_name': 'National Aeronautics and Space Administration',
            'country': 'USA',
            'founded': 1958,
            'website': 'https://www.nasa.gov',
            'logo': 'https://www.nasa.gov/sites/all/themes/custom/nasatwo/images/nasa-logo.svg'
        },
        'ESA': {
            'full_name': 'European Space Agency',
            'country': 'Europe',
            'founded': 1975,
            'website': 'https://www.esa.int',
            'logo': 'https://www.esa.int/var/esa/storage/images/esa_multimedia/images/2002/06/esa_logo_deep_blue_square_2002_06_26/9142877-3-eng-GB/ESA_logo_deep_blue_square_2002_06_26.jpg'
        },
        'SpaceX': {
            'full_name': 'Space Exploration Technologies Corp.',
            'country': 'USA',
            'founded': 2002,
            'website': 'https://www.spacex.com',
            'logo': 'https://www.spacex.com/static/images/share.jpg'
        },
        'ROSCOSMOS': {
            'full_name': 'Russian Federal Space Agency',
            'country': 'Russia',
            'founded': 1992,
            'website': 'https://www.roscosmos.ru',
            'logo': None
        },
        'CNSA': {
            'full_name': 'China National Space Administration',
            'country': 'China',
            'founded': 1993,
            'website': 'http://www.cnsa.gov.cn',
            'logo': None
        },
        'ISRO': {
            'full_name': 'Indian Space Research Organisation',
            'country': 'India',
            'founded': 1969,
            'website': 'https://www.isro.gov.in',
            'logo': None
        }
    }

class SpaceMissions:
    """Information about major space missions."""
    
    ACTIVE_MISSIONS = {
        'perseverance': {
            'name': 'Mars 2020 Perseverance Rover',
            'agency': 'NASA',
            'destination': 'Mars',
            'launch_date': '2020-07-30',
            'status': 'Active',
            'objective': 'Search for signs of ancient microbial life on Mars'
        },
        'curiosity': {
            'name': 'Mars Science Laboratory Curiosity',
            'agency': 'NASA',
            'destination': 'Mars',
            'launch_date': '2011-11-26',
            'status': 'Active',
            'objective': 'Assess Mars\' past habitability'
        },
        'jwst': {
            'name': 'James Webb Space Telescope',
            'agency': 'NASA/ESA/CSA',
            'destination': 'L2 Lagrange Point',
            'launch_date': '2021-12-25',
            'status': 'Active',
            'objective': 'Infrared astronomy and cosmology'
        },
        'artemis': {
            'name': 'Artemis Program',
            'agency': 'NASA',
            'destination': 'Moon',
            'launch_date': 'TBD',
            'status': 'In Development',
            'objective': 'Return humans to the Moon'
        }
    }

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    CACHE_CONFIG = {**Config.CACHE_CONFIG, 'enable_caching': False}
    
class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    RATE_LIMIT_CONFIG = {**Config.RATE_LIMIT_CONFIG, 'requests_per_minute': 60}

class TestingConfig(Config):
    """Testing environment configuration."""
    DEBUG = True
    REQUEST_TIMEOUT = 5
    CACHE_CONFIG = {**Config.CACHE_CONFIG, 'enable_caching': False}

# Configuration factory
def get_config(env: str = 'development') -> Config:
    """Get configuration based on environment."""
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return configs.get(env, DevelopmentConfig)()
