"""
Utility functions for the Cosmic Explorer application.
Contains helper functions for data processing, formatting, and common operations.
"""

import re
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, urljoin
import random

def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]', '', text)
    
    # Remove multiple consecutive punctuation
    text = re.sub(r'[\.]{2,}', '...', text)
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    
    return text

def truncate_text(text: str, max_length: int = 300, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length of text
        suffix: Suffix to add if text is truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    # Find the last space before max_length to avoid cutting words
    truncate_pos = text.rfind(' ', 0, max_length - len(suffix))
    if truncate_pos == -1:
        truncate_pos = max_length - len(suffix)
    
    return text[:truncate_pos] + suffix

def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text.
    
    Args:
        text: Text to extract keywords from
        min_length: Minimum length of keywords
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Convert to lowercase and split
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter by length and remove common words
    common_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
        'those', 'all', 'any', 'each', 'few', 'more', 'most', 'other', 'some',
        'such', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can',
        'will', 'just', 'should', 'now', 'get', 'has', 'had', 'have', 'been',
        'being', 'was', 'were', 'are', 'is', 'am', 'be', 'do', 'does', 'did',
        'would', 'could', 'should', 'may', 'might', 'must'
    }
    
    keywords = [word for word in words 
                if len(word) >= min_length and word not in common_words]
    
    # Count frequency and return most common
    keyword_freq = {}
    for keyword in keywords:
        keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
    return [keyword for keyword, _ in sorted_keywords[:max_keywords]]

def normalize_url(url: str, base_url: str = "") -> str:
    """
    Normalize and validate URL.
    
    Args:
        url: URL to normalize
        base_url: Base URL for relative URLs
        
    Returns:
        Normalized URL
    """
    if not url:
        return ""
    
    # Handle relative URLs
    if url.startswith('/') and base_url:
        url = urljoin(base_url, url)
    
    # Ensure protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url

def calculate_relevance_score(content: str, keywords: List[str], 
                            title_weight: float = 2.0) -> float:
    """
    Calculate relevance score for content based on keywords.
    
    Args:
        content: Content to score
        keywords: List of keywords to match
        title_weight: Weight multiplier for title matches
        
    Returns:
        Relevance score (0-10)
    """
    if not content or not keywords:
        return 0.0
    
    content_lower = content.lower()
    score = 0.0
    total_keywords = len(keywords)
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # Count occurrences
        occurrences = content_lower.count(keyword_lower)
        if occurrences > 0:
            # Base score for presence
            score += 1.0
            
            # Bonus for multiple occurrences (diminishing returns)
            if occurrences > 1:
                score += min(0.5, (occurrences - 1) * 0.1)
    
    # Normalize to 0-10 scale
    max_possible_score = total_keywords * 1.5  # Max with bonuses
    normalized_score = min(10.0, (score / max_possible_score) * 10.0)
    
    return round(normalized_score, 1)

def format_datetime(dt: datetime, format_type: str = 'relative') -> str:
    """
    Format datetime for display.
    
    Args:
        dt: Datetime to format
        format_type: Type of formatting ('relative', 'absolute', 'short')
        
    Returns:
        Formatted datetime string
    """
    if not dt:
        return "Unknown"
    
    now = datetime.now()
    
    if format_type == 'relative':
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    elif format_type == 'short':
        return dt.strftime('%m/%d/%Y')
    
    else:  # absolute
        return dt.strftime('%Y-%m-%d %H:%M UTC')

def generate_cache_key(query: str, source: str = "", additional_params: Dict = None) -> str:
    """
    Generate cache key for query results.
    
    Args:
        query: Search query
        source: Data source
        additional_params: Additional parameters
        
    Returns:
        Cache key string
    """
    # Create a string representation of all parameters
    cache_data = {
        'query': query.lower().strip(),
        'source': source,
        'params': additional_params or {}
    }
    
    # Create hash
    cache_string = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(cache_string.encode()).hexdigest()

def validate_space_query(query: str) -> Tuple[bool, str]:
    """
    Validate if query is space-related.
    
    Args:
        query: Query to validate
        
    Returns:
        Tuple of (is_valid, suggestion)
    """
    if not query or len(query.strip()) < 3:
        return False, "Please enter a query with at least 3 characters"
    
    space_indicators = {
        'space', 'nasa', 'mars', 'moon', 'rocket', 'satellite', 'astronaut',
        'spacecraft', 'mission', 'launch', 'orbit', 'planet', 'galaxy',
        'universe', 'cosmos', 'telescope', 'hubble', 'iss', 'station',
        'spacex', 'exploration', 'solar', 'asteroid', 'comet', 'meteor'
    }
    
    query_lower = query.lower()
    query_words = set(re.findall(r'\b[a-zA-Z]+\b', query_lower))
    
    # Check for space-related keywords
    if any(indicator in query_lower for indicator in space_indicators):
        return True, ""
    
    # Check for common space words in query
    space_word_count = len(query_words.intersection(space_indicators))
    if space_word_count > 0:
        return True, ""
    
    # Suggest making query more space-specific
    suggestions = [
        "Try adding space-related keywords like 'NASA', 'Mars', 'rocket', or 'satellite'",
        "Consider searching for specific missions like 'Mars rover' or 'ISS'",
        "Add terms like 'space exploration' or 'astronomical discovery'"
    ]
    
    return False, random.choice(suggestions)

def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain string
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    except:
        return "unknown"

def format_number(number: int, suffix: str = "") -> str:
    """
    Format large numbers with appropriate suffixes.
    
    Args:
        number: Number to format
        suffix: Optional suffix to add
        
    Returns:
        Formatted number string
    """
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M{suffix}"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K{suffix}"
    else:
        return f"{number}{suffix}"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename

def parse_space_date(date_string: str) -> Optional[datetime]:
    """
    Parse various date formats commonly found in space news.
    
    Args:
        date_string: Date string to parse
        
    Returns:
        Parsed datetime or None
    """
    if not date_string:
        return None
    
    # Common date formats in space news
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%m/%d/%Y',
        '%B %d, %Y',
        '%d %B %Y',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ'
    ]
    
    # Clean the date string
    date_string = date_string.strip()
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return None

def get_color_by_source(source: str) -> str:
    """
    Get color associated with a data source.
    
    Args:
        source: Source name
        
    Returns:
        Color hex code
    """
    source_colors = {
        'nasa': '#0B3D91',      # NASA Blue
        'spacex': '#005288',    # SpaceX Blue
        'esa': '#003247',       # ESA Dark Blue
        'space.com': '#1e3d59', # Space.com Blue
        'wikipedia': '#000000',  # Wikipedia Black
        'space force': '#1C4B96', # Space Force Blue
        'default': '#667eea'     # Default Purple
    }
    
    return source_colors.get(source.lower(), source_colors['default'])

def create_search_summary(results: List[Dict], query: str) -> Dict[str, Any]:
    """
    Create a summary of search results.
    
    Args:
        results: List of search results
        query: Original search query
        
    Returns:
        Summary dictionary
    """
    if not results:
        return {
            'total_results': 0,
            'sources': [],
            'avg_relevance': 0,
            'keywords_found': [],
            'search_time': datetime.now().isoformat()
        }
    
    # Calculate statistics
    sources = list(set(result.get('source', 'Unknown') for result in results))
    relevance_scores = [result.get('relevance', 0) for result in results]
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
    
    # Extract common keywords from results
    all_text = ' '.join([
        result.get('title', '') + ' ' + result.get('description', '')
        for result in results
    ])
    keywords_found = extract_keywords(all_text, max_keywords=5)
    
    return {
        'total_results': len(results),
        'sources': sources,
        'avg_relevance': round(avg_relevance, 1),
        'keywords_found': keywords_found,
        'search_time': datetime.now().isoformat(),
        'query': query
    }
