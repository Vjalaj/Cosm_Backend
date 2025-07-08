import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import time
import random
from urllib.parse import quote_plus
import logging

# Set up logging
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/space_scraper.log", encoding='utf-8'),
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
    
logger = logging.getLogger("space_scraper")

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Define a simple tokenizer function that doesn't rely on punkt_tab
def simple_tokenize(text):
    # First try NLTK's word_tokenize
    try:
        from nltk.tokenize import word_tokenize
        return word_tokenize(text)
    except:
        # Fall back to simple splitting on spaces and punctuation
        import re
        return re.findall(r'\w+', text.lower())

class SpaceInfoScraper:
    def __init__(self):
        # Use a more modern and complete set of headers to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        logger.info("SpaceInfoScraper initialized")
    
    def get_headers(self, site=None):
        """Get headers with a random user agent and site-specific customizations"""
        headers = self.headers.copy()
        headers['User-Agent'] = random.choice(self.user_agents)
        
        # Add site-specific modifications
        if site == 'google':
            headers['Referer'] = 'https://www.google.com/'
        elif site == 'nasa':
            headers['Referer'] = 'https://www.nasa.gov/'
        elif site == 'wikipedia':
            headers['Referer'] = 'https://www.wikipedia.org/'
        
        return headers
        
    def get_with_retry(self, url, site=None, max_retries=3):
        """Make a GET request with retries and random delays to avoid being blocked"""
        headers = self.get_headers(site)
        retries = 0
        
        while retries < max_retries:
            try:
                # Add a random delay between requests
                if retries > 0:
                    delay = 1 + random.random() * 2  # 1-3 seconds
                    logger.info(f"Retry {retries}/{max_retries}, waiting {delay:.1f} seconds")
                    time.sleep(delay)
                
                # Make the request
                response = requests.get(url, headers=headers, timeout=15)
                
                # Check if we might be blocked (CAPTCHA or empty response)
                if "captcha" in response.text.lower() or (response.status_code == 200 and len(response.text) < 1000):
                    logger.warning(f"Possible blocking detected for {url}")
                    retries += 1
                    continue
                
                return response
            except Exception as e:
                logger.error(f"Error during request to {url}: {str(e)}")
                retries += 1
        
        logger.error(f"Failed to get {url} after {max_retries} retries")
        return None
    
    def process_nlp(self, query):
        """Process user query using NLP to extract keywords and intent"""
        # Use our simple tokenizer that has a fallback mechanism
        tokens = simple_tokenize(query.lower())
        
        # Remove stopwords and non-alphabetic tokens
        filtered_tokens = [word for word in tokens if word.isalpha() and word not in self.stop_words]
        
        # Lemmatize
        lemmatized = [self.lemmatizer.lemmatize(word) for word in filtered_tokens]
        
        # Space-related keywords mapping
        space_keywords = {
            'nasa': ['nasa', 'space', 'mission', 'rocket', 'astronaut'],
            'mars': ['mars', 'red', 'planet', 'rover', 'perseverance', 'curiosity'],
            'moon': ['moon', 'lunar', 'apollo', 'artemis'],
            'iss': ['iss', 'international', 'space', 'station'],
            'spacex': ['spacex', 'falcon', 'dragon', 'elon', 'musk'],
            'satellite': ['satellite', 'orbit', 'gps'],
            'solar': ['solar', 'sun', 'system', 'planet'],
            'asteroid': ['asteroid', 'meteor', 'comet'],
            'hubble': ['hubble', 'telescope', 'image', 'webb', 'james'],
            'launch': ['launch', 'rocket', 'mission'],
            'galaxy': ['galaxy', 'milky', 'way', 'star'],
            'universe': ['universe', 'cosmos', 'big', 'bang', 'black', 'hole', 'quasar']
        }
        
        # Determine search intent
        intent = 'general'
        for category, keywords in space_keywords.items():
            if any(keyword in lemmatized for keyword in keywords):
                intent = category
                break
        
        logger.info(f"NLP processing: Query '{query}' → Intent: {intent}, Keywords: {lemmatized}")
        
        return {
            'processed_query': ' '.join(lemmatized),
            'original_query': query,
            'intent': intent,
            'keywords': lemmatized
        }
    
    def scrape_nasa_news(self, query_info):
        """Scrape NASA news and information with robust element detection"""
        try:
            # Use NASA's newer search URL format
            search_query = quote_plus(query_info['original_query'])
            # Try multiple possible NASA search URLs
            urls = [
                f"https://www.nasa.gov/search/{search_query}/",  # New format
                f"https://www.nasa.gov/search/?q={search_query}",  # Alternative format
                f"https://www.nasa.gov/?s={search_query}",  # WordPress format
                "https://www.nasa.gov/"  # Fallback to homepage if search fails
            ]
            
            response = None
            for url in urls:
                logger.info(f"Trying NASA URL: {url}")
                try:
                    response = self.get_with_retry(url, site='nasa')
                    if response and response.status_code == 200:
                        logger.info(f"Successfully connected to NASA at {url}")
                        break
                except Exception as e:
                    logger.error(f"Error with NASA URL {url}: {str(e)}")
            
            if not response or response.status_code != 200:
                logger.error(f"All NASA URLs failed, no valid response")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # Try multiple possible article selectors (NASA changes their HTML structure frequently)
            selectors = [
                ('article', {}),
                ('div', {'class': ['search-result', 'search-item', 'news-item', 'article-card']}),
                ('.news-content'),  # CSS selector approach
                ('.search-results .item'),
                ('.list-items .item'),  # Another common pattern
                ('.articles-listing article'),
                ('.grid-item')  # Common for grid layouts
            ]
            
            # Try each selector until we find content
            news_items = []
            for selector in selectors:
                if isinstance(selector, tuple):
                    tag, attrs = selector
                    # Handle tag + attrs format
                    news_items = soup.find_all(tag, attrs)
                else:
                    # Handle CSS selector format
                    news_items = soup.select(selector)
                
                if news_items and len(news_items) > 0:
                    logger.info(f"Found NASA content using selector: {selector}")
                    break
                    
            # If we still didn't find any specific news items, look for any content blocks
            if not news_items:
                # Look for any content blocks with headings and links - common pattern for all websites
                content_blocks = []
                for heading in ['h1', 'h2', 'h3', 'h4']:
                    for h in soup.find_all(heading):
                        # Find the nearest container that might be an article
                        parent = h.parent
                        for _ in range(3):  # Look up to 3 levels up
                            if parent and parent.name in ['div', 'article', 'section']:
                                # Check if this container has a link
                                if parent.find('a'):
                                    content_blocks.append(parent)
                                    break
                            if parent:
                                parent = parent.parent
                
                if content_blocks:
                    news_items = content_blocks[:5]
                    logger.info(f"Found NASA content using content block approach, found {len(content_blocks)} blocks")
                
            # Limit to first 5 results if we have many
            news_items = news_items[:5]
            
            # Process each news item
            for item in news_items:
                # Try various heading tags for the title
                title_elem = None
                for heading in ['h1', 'h2', 'h3', 'h4']:
                    title_elem = item.find(heading)
                    if title_elem:
                        break
                
                # Try to find a link - look for the most relevant link
                link_elem = None
                links = item.find_all('a')
                for link in links:
                    if link.get('href'):
                        link_elem = link
                        if link.find('h1') or link.find('h2') or link.find('h3'):
                            # This link contains a heading - likely the main link
                            break
                
                # Try to find description in paragraph or div with class containing 'desc'
                desc_elem = item.find('p')
                if not desc_elem:
                    # Try to find divs with description-like class names
                    for div in item.find_all('div'):
                        div_class = div.get('class', [])
                        if isinstance(div_class, list):
                            div_class = ' '.join(div_class)
                        if 'desc' in str(div_class).lower() or 'summary' in str(div_class).lower() or 'content' in str(div_class).lower():
                            desc_elem = div
                            break
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    link = link_elem.get('href', '')
                    
                    # Fix relative URLs
                    if link.startswith('/'):
                        link = 'https://www.nasa.gov' + link
                    elif not link.startswith('http'):
                        link = 'https://www.nasa.gov/' + link
                    
                    description = desc_elem.get_text().strip() if desc_elem else "View this NASA article for more information."
                    
                    # Check if article is relevant to query
                    relevance_score = self.calculate_relevance(title + " " + description, query_info['keywords'])
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'description': description,
                        'source': 'NASA',
                        'relevance': relevance_score
                    })
            
            logger.info(f"Found {len(articles)} NASA articles")
            return sorted(articles, key=lambda x: x['relevance'], reverse=True)
        except Exception as e:
            logger.error(f"Error scraping NASA: {str(e)}")
            return []
    
    def scrape_space_com(self, query_info):
        """Scrape Space.com for news and information"""
        try:
            # Space.com search URL
            search_query = quote_plus(query_info['original_query'])
            url = f"https://www.space.com/search?q={search_query}"
            logger.info(f"Scraping Space.com search results from {url}")
            
            response = self.get_with_retry(url, site='space.com')
            logger.info(f"Space.com response status: {response.status_code if response else 'No response'}")
            
            if not response or response.status_code != 200:
                logger.error(f"Space.com returned status code {response.status_code if response else 'No response'}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Try to find articles
            article_elements = soup.find_all('article')
            logger.info(f"Found {len(article_elements)} article elements on Space.com")
            
            if not article_elements:
                # If no article elements found, try other common selectors
                for selector in ['.search-result', '.result-item', '.listingResult']:
                    elements = soup.select(selector)
                    if elements:
                        logger.info(f"Found {len(elements)} elements using selector '{selector}'")
                        article_elements = elements
                        break
            
            # Process each article
            for article in article_elements[:5]:  # Limit to first 5
                # Try to find title
                title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
                if not title_elem:
                    # If no heading tags, look for elements with title-like class names
                    for elem in article.find_all(['div', 'span']):
                        elem_class = ' '.join(elem.get('class', []))
                        if any(title_term in elem_class.lower() for title_term in ['title', 'heading', 'header']):
                            title_elem = elem
                            break
                
                # Try to find link
                link_elem = article.find('a')
                
                # Try to find description
                desc_elem = article.find('p')
                if not desc_elem:
                    # Try to find divs with description-like class names
                    for elem in article.find_all(['div', 'span']):
                        elem_class = ' '.join(elem.get('class', []))
                        if any(desc_term in elem_class.lower() for desc_term in ['desc', 'summary', 'content', 'excerpt']):
                            desc_elem = elem
                            break
                
                # Only add if we have at least a title and link
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    
                    # Skip "Search" titles
                    if title.lower() == "search":
                        continue
                        
                    link = link_elem.get('href', '')
                    
                    # Fix relative URLs
                    if link.startswith('/'):
                        link = 'https://www.space.com' + link
                    elif not link.startswith('http'):
                        link = 'https://www.space.com/' + link
                    
                    # Get description
                    description = desc_elem.get_text().strip() if desc_elem else "Visit Space.com for more information on this space-related topic."
                    
                    # Skip generic search descriptions
                    if "enter your search term" in description.lower():
                        description = "Visit Space.com for more information on this space-related topic."
                    
                    # Calculate relevance based on keyword matching
                    relevance_score = self.calculate_relevance(title + " " + description, query_info['keywords'])
                    
                    # Only add relevant results
                    if relevance_score > 0 or len(articles) == 0:
                        articles.append({
                            'title': title,
                            'link': link,
                            'description': description,
                            'source': 'Space.com',
                            'relevance': relevance_score
                        })
            
            # If we didn't find good articles from the search, try the homepage for general space news
            if len(articles) == 0:
                logger.info("No relevant articles found on Space.com search, trying homepage")
                
                # Try Space.com homepage
                homepage_url = "https://www.space.com/"
                homepage_response = requests.get(homepage_url, headers=self.headers, timeout=10)
                
                if homepage_response.status_code == 200:
                    homepage_soup = BeautifulSoup(homepage_response.content, 'html.parser')
                    featured_articles = homepage_soup.find_all('article')[:3]  # Get top 3 featured articles
                    
                    for article in featured_articles:
                        title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
                        link_elem = article.find('a')
                        desc_elem = article.find('p')
                        
                        if title_elem and link_elem:
                            title = title_elem.get_text().strip()
                            link = link_elem.get('href', '')
                            
                            # Fix relative URLs
                            if link.startswith('/'):
                                link = 'https://www.space.com' + link
                            elif not link.startswith('http'):
                                link = 'https://www.space.com/' + link
                            
                            description = desc_elem.get_text().strip() if desc_elem else "Latest space news from Space.com"
                            
                            articles.append({
                                'title': title,
                                'link': link,
                                'description': description,
                                'source': 'Space.com',
                                'relevance': 1  # Low relevance for homepage articles
                            })
                    
                    logger.info(f"Added {len(articles)} general articles from Space.com homepage")
            
            logger.info(f"Found total of {len(articles)} Space.com articles")
            return sorted(articles, key=lambda x: x['relevance'], reverse=True)
        except Exception as e:
            logger.error(f"Error scraping Space.com: {str(e)}")
            return []
    
    def scrape_wikipedia(self, query_info):
        """Scrape Wikipedia for space-related information with improved handling of astronomical objects"""
        try:
            # Construct search query for Wikipedia
            original_query = query_info['original_query']
            
            # Special handling for specific astronomical objects
            if 'black hole' in original_query.lower():
                search_terms = "black hole astronomy"
            elif 'mars rover' in original_query.lower():
                search_terms = "mars rover perseverance curiosity opportunity"
            elif 'quasar' in original_query.lower():
                search_terms = "quasar astronomy"
            elif any(term in original_query.lower() for term in ['galaxy', 'universe', 'star', 'nebula']):
                # Add astronomy context for celestial objects
                search_terms = original_query + " astronomy astrophysics"
            else:
                # Standard handling
                search_terms = original_query
                if 'space' not in search_terms.lower():
                    # Add space context if not present in the query
                    if any(term in query_info['intent'] for term in ['solar', 'galaxy', 'universe', 'nasa', 'mars']):
                        # Already has space context
                        pass
                    else:
                        # Add space context
                        search_terms = search_terms + " space astronomy"
            
            search_query = quote_plus(search_terms)
            url = f"https://en.wikipedia.org/w/index.php?search={search_query}"
            logger.info(f"Scraping Wikipedia with query: {search_terms}")
            
            response = self.get_with_retry(url, site='wikipedia')
            if not response or response.status_code != 200:
                logger.error(f"Wikipedia search failed with status code {response.status_code if response else 'No response'}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # Check if we were redirected directly to an article
            if '/wiki/' in response.url and 'search' not in response.url:
                logger.info(f"Direct Wikipedia article found: {response.url}")
                # Direct article - get title and first few paragraphs
                title_elem = soup.find('h1', {'id': 'firstHeading'})
                content_div = soup.find('div', {'id': 'mw-content-text'})
                
                if title_elem and content_div:
                    title = title_elem.get_text().strip()
                    
                    # Get the first few paragraphs
                    paragraphs = content_div.find_all('p', limit=3)
                    description = ""
                    for p in paragraphs:
                        text = p.get_text().strip()
                        if len(text) > 50:  # Only include substantial paragraphs
                            description += text + " "
                    
                    description = description.strip()
                    if description:
                        articles.append({
                            'title': title,
                            'link': response.url,
                            'description': description[:500] + "..." if len(description) > 500 else description,
                            'source': 'Wikipedia',
                            'relevance': 9  # High relevance for direct article
                        })
            else:
                # Search results page - get the search results
                search_results = soup.find_all('div', {'class': 'mw-search-result-heading'})
                logger.info(f"Found {len(search_results)} Wikipedia search results")
                
                for i, result in enumerate(search_results[:3]):  # Take top 3 results
                    link_elem = result.find('a')
                    if link_elem:
                        title = link_elem.get_text().strip()
                        link = 'https://en.wikipedia.org' + link_elem.get('href', '')
                        
                        # Now get the description by fetching the article
                        try:
                            article_response = requests.get(link, headers=self.headers, timeout=10)
                            article_soup = BeautifulSoup(article_response.content, 'html.parser')
                            
                            # Get the first substantial paragraph
                            content_div = article_soup.find('div', {'id': 'mw-content-text'})
                            description = ""
                            
                            if content_div:
                                # First try to find the lead paragraph
                                lead_paras = content_div.select('.mw-parser-output > p')
                                if lead_paras:
                                    for p in lead_paras:
                                        text = p.get_text().strip()
                                        if len(text) > 50:  # Only include substantial paragraphs
                                            description += text + " "
                                            if len(description) > 200:
                                                break
                            
                            if not description:
                                description = "Visit Wikipedia for detailed information on this topic."
                            
                            relevance_score = self.calculate_relevance(title + " " + description, query_info['keywords'])
                            # Boost relevance for astronomical object queries
                            if any(term in title.lower() for term in ['black hole', 'mars rover', 'quasar', 'galaxy']):
                                relevance_score += 3
                            
                            articles.append({
                                'title': title,
                                'link': link,
                                'description': description[:500] + "..." if len(description) > 500 else description,
                                'source': 'Wikipedia',
                                'relevance': relevance_score
                            })
                        except Exception as e:
                            logger.error(f"Error fetching Wikipedia article {link}: {str(e)}")
                            # Still add the result with a generic description
                            articles.append({
                                'title': title,
                                'link': link,
                                'description': "Visit Wikipedia for detailed information on this topic.",
                                'source': 'Wikipedia',
                                'relevance': 5
                            })
            
            logger.info(f"Found {len(articles)} Wikipedia articles")
            return sorted(articles, key=lambda x: x['relevance'], reverse=True)
        except Exception as e:
            logger.error(f"Error scraping Wikipedia: {str(e)}")
            return []
            
    def scrape_universe_today(self, query_info):
        """Scrape Universe Today for space-related information"""
        try:
            # Construct search query
            search_query = quote_plus(query_info['original_query'])
            url = f"https://www.universetoday.com/?s={search_query}"
            logger.info(f"Scraping Universe Today with query: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            logger.info(f"Universe Today response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Universe Today returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Try to find articles - Universe Today typically uses 'article' elements
            article_elements = soup.find_all('article', class_='post')
            logger.info(f"Found {len(article_elements)} article elements on Universe Today")
            
            if not article_elements:
                # If no specific article class found, try generic article elements
                article_elements = soup.find_all('article')
                logger.info(f"Found {len(article_elements)} generic article elements")
            
            # Process each article
            for article in article_elements[:5]:  # Limit to first 5
                # Try to find title
                title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
                
                # Try to find link
                link_elem = article.find('a')
                
                # Try to find description
                desc_elem = article.find('p', class_='excerpt') or article.find('p')
                
                # Only add if we have at least a title and link
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    link = link_elem.get('href', '')
                    
                    # Ensure link is absolute
                    if not link.startswith('http'):
                        link = 'https://www.universetoday.com' + link
                    
                    # Get description
                    description = desc_elem.get_text().strip() if desc_elem else "Visit Universe Today for more information on this space-related topic."
                    
                    # Calculate relevance based on keyword matching
                    relevance_score = self.calculate_relevance(title + " " + description, query_info['keywords'])
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'description': description,
                        'source': 'Universe Today',
                        'relevance': relevance_score
                    })
            
            logger.info(f"Found {len(articles)} Universe Today articles")
            return sorted(articles, key=lambda x: x['relevance'], reverse=True)
        except Exception as e:
            logger.error(f"Error scraping Universe Today: {str(e)}")
            return []
    
    def scrape_spacex_info(self, query_info):
        """Scrape SpaceX information"""
        try:
            url = "https://www.spacex.com/"
            logger.info(f"Scraping SpaceX from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            info = []
            # Look for mission information
            mission_sections = soup.find_all('section')[:3]
            
            for section in mission_sections:
                title_elem = section.find('h1') or section.find('h2') or section.find('h3')
                desc_elem = section.find('p')
                
                if title_elem:
                    title = title_elem.get_text().strip()
                    description = desc_elem.get_text().strip() if desc_elem else ""
                    
                    if title and len(title) > 5:  # Filter out very short titles
                        relevance_score = self.calculate_relevance(title + " " + description, query_info['keywords'])
                        
                        info.append({
                            'title': title,
                            'link': url,
                            'description': description,
                            'source': 'SpaceX',
                            'relevance': relevance_score
                        })
            
            logger.info(f"Found {len(info)} SpaceX information items")
            return sorted(info, key=lambda x: x['relevance'], reverse=True)
        except Exception as e:
            logger.error(f"Error scraping SpaceX: {str(e)}")
            return []
            
    def scrape_nasa_homepage(self, query_info):
        """Scrape NASA homepage for latest space news"""
        try:
            url = "https://www.nasa.gov/"
            logger.info(f"Scraping NASA homepage: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            logger.info(f"NASA homepage response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"NASA homepage returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Try to find featured content blocks
            content_blocks = soup.find_all('article') or soup.select('.ubernode') or soup.select('.grid-item')
            logger.info(f"Found {len(content_blocks)} content blocks on NASA homepage")
            
            # Process up to 3 content blocks
            for block in content_blocks[:3]:
                # Try to find title
                title_elem = block.find(['h1', 'h2', 'h3', 'h4'])
                
                # Try to find link
                link_elem = block.find('a')
                
                # Try to find description
                desc_elem = block.find('p')
                
                if title_elem:
                    title = title_elem.get_text().strip()
                    
                    # Get link
                    link = link_elem.get('href', '') if link_elem else url
                    
                    # Fix relative URLs
                    if link.startswith('/'):
                        link = 'https://www.nasa.gov' + link
                    elif not link.startswith('http'):
                        link = 'https://www.nasa.gov/' + link
                    
                    # Get description
                    description = desc_elem.get_text().strip() if desc_elem else "Visit NASA for the latest space news and information."
                    
                    # Calculate relevance based on keyword matching
                    relevance_score = self.calculate_relevance(title + " " + description, query_info['keywords'])
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'description': description,
                        'source': 'NASA',
                        'relevance': relevance_score
                    })
            
            logger.info(f"Found {len(articles)} NASA articles")
            return sorted(articles, key=lambda x: x['relevance'], reverse=True)
        except Exception as e:
            logger.error(f"Error scraping NASA homepage: {str(e)}")
            return []
    
    def scrape_google(self, query_info):
        """Scrape Google for space-related information"""
        try:
            # Build a more specific search query to target space-related results
            search_terms = query_info['original_query']
            # Add space context if not already present
            if not any(term in search_terms.lower() for term in ['space', 'nasa', 'astronomy', 'cosmos', 'universe']):
                search_terms += " space astronomy"
                
            search_query = quote_plus(search_terms)
            url = f"https://www.google.com/search?q={search_query}"
            logger.info(f"Scraping Google with query: {search_terms}")
            
            response = self.get_with_retry(url, site='google')
            if not response or response.status_code != 200:
                logger.error(f"Google search failed with status code {response.status_code if response else 'No response'}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Google search results are typically in divs with class 'g'
            search_results = soup.find_all('div', {'class': 'g'})
            if not search_results:
                # Try alternative selectors as Google's HTML structure can change
                search_results = soup.select('.rc') or soup.select('.yuRUbf') or soup.select('.jtfYYd')
                
            logger.info(f"Found {len(search_results)} Google search results")
            
            for result in search_results[:5]:  # Limit to first 5 results
                # Try to find title and link
                title_elem = result.find('h3')
                link_elem = result.find('a')
                
                # Try to find description (Google calls it a "snippet")
                desc_elem = result.select_one('.VwiC3b') or result.select_one('.st') or result.select_one('.aCOpRe')
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    link = link_elem.get('href', '')
                    
                    # Clean up Google redirect links
                    if link.startswith('/url?'):
                        import urllib.parse
                        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
                        if 'q' in query_params:
                            link = query_params['q'][0]
                    
                    # Skip Google's own services links like Google Maps, etc.
                    if 'google.com' in link and not any(term in link for term in ['scholar', 'books']):
                        continue
                        
                    description = desc_elem.get_text().strip() if desc_elem else "Find more information on Google."
                    
                    # Get the domain name for source attribution
                    domain = ""
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(link).netloc
                        if domain.startswith('www.'):
                            domain = domain[4:]
                    except:
                        domain = "website"
                    
                    # Calculate relevance
                    relevance_score = self.calculate_relevance(title + " " + description, query_info['keywords'])
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'description': description,
                        'source': f"Google ({domain})",
                        'relevance': relevance_score
                    })
            
            logger.info(f"Found {len(articles)} relevant Google results")
            return sorted(articles, key=lambda x: x['relevance'], reverse=True)
        except Exception as e:
            logger.error(f"Error scraping Google: {str(e)}")
            return []
    
    def scrape_nasa_science(self, query_info):
        """Scrape NASA Science website for space information"""
        try:
            search_query = quote_plus(query_info['original_query'])
            url = f"https://science.nasa.gov/search/{search_query}/"
            logger.info(f"Scraping NASA Science with query: {url}")
            
            response = self.get_with_retry(url, site='nasa')
            logger.info(f"NASA Science response status: {response.status_code if response else 'No response'}")
            
            if not response or response.status_code != 200:
                # Try alternative URL format
                alt_url = f"https://science.nasa.gov/?s={search_query}"
                logger.info(f"Trying alternative NASA Science URL: {alt_url}")
                try:
                    response = self.get_with_retry(alt_url, site='nasa')
                except Exception as e:
                    logger.error(f"Error with alternative NASA Science URL: {str(e)}")
                    return []
                    
            if not response or response.status_code != 200:
                logger.error(f"NASA Science returned status code {response.status_code if response else 'No response'}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Try to find articles
            article_elements = soup.find_all('article') or soup.select('.search-result') or soup.select('.result-item')
            logger.info(f"Found {len(article_elements)} article elements on NASA Science")
            
            # Process each article
            for article in article_elements[:5]:  # Limit to first 5
                # Try to find title
                title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
                
                # Try to find link
                link_elem = article.find('a')
                
                # Try to find description
                desc_elem = article.find('p')
                
                # Only add if we have at least a title and link
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    link = link_elem.get('href', '')
                    
                    # Fix relative URLs
                    if link.startswith('/'):
                        link = 'https://science.nasa.gov' + link
                    elif not link.startswith('http'):
                        link = 'https://science.nasa.gov/' + link
                    
                    # Get description
                    description = desc_elem.get_text().strip() if desc_elem else "Visit NASA Science for more information on this space-related topic."
                    
                    # Calculate relevance
                    relevance_score = self.calculate_relevance(title + " " + description, query_info['keywords'])
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'description': description,
                        'source': 'NASA Science',
                        'relevance': relevance_score
                    })
            
            # If we didn't find results, try the homepage for featured content
            if not articles:
                logger.info("No search results found, trying NASA Science homepage")
                try:
                    homepage_url = "https://science.nasa.gov/"
                    homepage_response = requests.get(homepage_url, headers=self.headers, timeout=10)
                    
                    if homepage_response.status_code == 200:
                        homepage_soup = BeautifulSoup(homepage_response.content, 'html.parser')
                        featured_content = homepage_soup.select('.featured-content') or homepage_soup.select('.nasa-card')
                        
                        for item in featured_content[:3]:
                            title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
                            link_elem = item.find('a')
                            desc_elem = item.find('p')
                            
                            if title_elem and link_elem:
                                title = title_elem.get_text().strip()
                                link = link_elem.get('href', '')
                                
                                # Fix relative URLs
                                if link.startswith('/'):
                                    link = 'https://science.nasa.gov' + link
                                elif not link.startswith('http'):
                                    link = 'https://science.nasa.gov/' + link
                                
                                description = desc_elem.get_text().strip() if desc_elem else "Latest featured content from NASA Science."
                                
                                articles.append({
                                    'title': title,
                                    'link': link,
                                    'description': description,
                                    'source': 'NASA Science',
                                    'relevance': 2  # Lower relevance for homepage content
                                })
                except Exception as e:
                    logger.error(f"Error scraping NASA Science homepage: {str(e)}")
            
            logger.info(f"Found {len(articles)} NASA Science articles")
            return sorted(articles, key=lambda x: x['relevance'], reverse=True)
        except Exception as e:
            logger.error(f"Error scraping NASA Science: {str(e)}")
            return []
    
    def scrape_space_facts(self, query_info):
        """Scrape Space Facts website for planetary and space facts"""
        try:
            # Space Facts doesn't have a search function, so we'll map certain queries to their pages
            base_url = "https://space-facts.com/"
            
            # Map of topics to URLs on the site
            topic_urls = {
                'mars': 'mars/',
                'earth': 'earth/',
                'moon': 'moon/',
                'sun': 'sun/',
                'mercury': 'mercury/',
                'venus': 'venus/',
                'jupiter': 'jupiter/',
                'saturn': 'saturn/',
                'uranus': 'uranus/',
                'neptune': 'neptune/',
                'pluto': 'pluto/',
                'planet': 'planets/',
                'solar system': 'solar-system/',
                'space': ''
            }
            
            # Determine the most relevant page based on query keywords
            page_url = base_url
            max_matches = 0
            chosen_topic = 'space'
            
            for topic, path in topic_urls.items():
                matches = sum(1 for keyword in query_info['keywords'] if keyword in topic.split())
                if matches > max_matches:
                    max_matches = matches
                    page_url = base_url + path
                    chosen_topic = topic
            
            logger.info(f"Scraping Space Facts for topic: {chosen_topic} at {page_url}")
            
            response = self.get_with_retry(page_url, site='space-facts')
            if not response or response.status_code != 200:
                logger.error(f"Space Facts returned status code {response.status_code if response else 'No response'}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            facts = []
            
            # Get the page title
            page_title = soup.find('h1').get_text().strip() if soup.find('h1') else chosen_topic.title()
            
            # Find fact tables - Space Facts typically has tables with facts
            fact_tables = soup.find_all('table')
            logger.info(f"Found {len(fact_tables)} fact tables on Space Facts")
            
            facts_list = []
            
            # Extract facts from tables
            for table in fact_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 2:
                        fact_name = cells[0].get_text().strip()
                        fact_value = cells[1].get_text().strip()
                        facts_list.append(f"{fact_name}: {fact_value}")
            
            # Also look for list items which often contain facts
            fact_lists = soup.find_all('ul')
            for list_el in fact_lists:
                items = list_el.find_all('li')
                for item in items:
                    fact_text = item.get_text().strip()
                    if len(fact_text) > 10:  # Skip very short items
                        facts_list.append(fact_text)
            
            # Combine facts into a description
            if facts_list:
                # Take first 5 facts
                facts_subset = facts_list[:5]
                description = "Facts: " + " | ".join(facts_subset)
                
                # Calculate relevance
                relevance_score = self.calculate_relevance(page_title + " " + description, query_info['keywords'])
                
                facts.append({
                    'title': f"{page_title} Facts",
                    'link': page_url,
                    'description': description,
                    'source': 'Space Facts',
                    'relevance': relevance_score
                })
            
            # Also look for individual sections/articles
            sections = soup.find_all(['section', 'article', 'div'], class_=['post', 'entry', 'content'])
            
            for section in sections[:2]:  # Limit to first 2 sections
                title_elem = section.find(['h2', 'h3', 'h4'])
                desc_elem = section.find('p')
                
                if title_elem and desc_elem:
                    title = title_elem.get_text().strip()
                    description = desc_elem.get_text().strip()
                    
                    # Calculate relevance
                    relevance_score = self.calculate_relevance(title + " " + description, query_info['keywords'])
                    
                    facts.append({
                        'title': title,
                        'link': page_url + "#" + title.lower().replace(' ', '-'),
                        'description': description,
                        'source': 'Space Facts',
                        'relevance': relevance_score
                    })
            
            logger.info(f"Found {len(facts)} Space Facts entries")
            return sorted(facts, key=lambda x: x['relevance'], reverse=True)
        except Exception as e:
            logger.error(f"Error scraping Space Facts: {str(e)}")
            return []
    
    def scrape_astrogeology(self, query_info):
        """Scrape USGS Astrogeology Science Center for planetary geology information"""
        try:
            search_query = quote_plus(query_info['original_query'])
            url = f"https://astrogeology.usgs.gov/search/results?q={search_query}"
            logger.info(f"Scraping USGS Astrogeology with query: {url}")
            
            response = self.get_with_retry(url, site='usgs')
            if not response or response.status_code != 200:
                logger.error(f"USGS Astrogeology returned status code {response.status_code if response else 'No response'}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Find result items - typically in item or product-item classes
            result_items = soup.select('.item') or soup.select('.product-item') or soup.select('.result-item')
            logger.info(f"Found {len(result_items)} result items on USGS Astrogeology")
            
            for item in result_items[:5]:  # Limit to first 5
                title_elem = item.find(['h2', 'h3', 'h4', 'h5']) or item.select_one('.title')
                link_elem = item.find('a')
                desc_elem = item.find('p') or item.select_one('.description')
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    link = link_elem.get('href', '')
                    
                    # Fix relative URLs
                    if link.startswith('/'):
                        link = 'https://astrogeology.usgs.gov' + link
                    elif not link.startswith('http'):
                        link = 'https://astrogeology.usgs.gov/' + link
                    
                    # Get description
                    description = desc_elem.get_text().strip() if desc_elem else "Planetary geology resource from USGS Astrogeology Science Center."
                    
                    # Calculate relevance
                    relevance_score = self.calculate_relevance(title + " " + description, query_info['keywords'])
                    
                    results.append({
                        'title': title,
                        'link': link,
                        'description': description,
                        'source': 'USGS Astrogeology',
                        'relevance': relevance_score
                    })
            
            # If no search results, look for featured content on the homepage
            if not results:
                logger.info("No search results found, trying USGS Astrogeology homepage")
                try:
                    homepage_url = "https://astrogeology.usgs.gov/"
                    homepage_response = requests.get(homepage_url, headers=self.headers, timeout=10)
                    
                    if homepage_response.status_code == 200:
                        homepage_soup = BeautifulSoup(homepage_response.content, 'html.parser')
                        featured_items = homepage_soup.select('.featured') or homepage_soup.select('.highlight') or homepage_soup.select('.carousel-item')
                        
                        for item in featured_items[:3]:
                            title_elem = item.find(['h2', 'h3', 'h4']) or item.select_one('.title')
                            link_elem = item.find('a')
                            desc_elem = item.find('p') or item.select_one('.description')
                            
                            if title_elem and link_elem:
                                title = title_elem.get_text().strip()
                                link = link_elem.get('href', '')
                                
                                # Fix relative URLs
                                if link.startswith('/'):
                                    link = 'https://astrogeology.usgs.gov' + link
                                elif not link.startswith('http'):
                                    link = 'https://astrogeology.usgs.gov/' + link
                                
                                # Get description
                                description = desc_elem.get_text().strip() if desc_elem else "Featured content from USGS Astrogeology Science Center."
                                
                                results.append({
                                    'title': title,
                                    'link': link,
                                    'description': description,
                                    'source': 'USGS Astrogeology',
                                    'relevance': 2  # Lower relevance for homepage content
                                })
                except Exception as e:
                    logger.error(f"Error scraping USGS Astrogeology homepage: {str(e)}")
            
            logger.info(f"Found {len(results)} USGS Astrogeology results")
            return sorted(results, key=lambda x: x['relevance'], reverse=True)
        except Exception as e:
            logger.error(f"Error scraping USGS Astrogeology: {str(e)}")
            return []
    
    def calculate_relevance(self, text, keywords):
        """Calculate relevance score based on keyword matching"""
        text_lower = text.lower()
        score = 0
        for keyword in keywords:
            if keyword in text_lower:
                score += 1
        return score
    
    def get_space_info(self, query):
        """Main method to get space information based on user query"""
        logger.info(f"Processing query: {query}")
        
        try:
            # Process query using NLP
            query_info = self.process_nlp(query)
            
            all_results = []
            source_results = {}  # Track results by source
            
            # Create a list of all scrapers to try
            scrapers = [
                # Primary sources - always try these
                {"name": "Wikipedia", "func": self.scrape_wikipedia, "condition": True},
                {"name": "Google", "func": self.scrape_google, "condition": True},
                {"name": "NASA", "func": self.scrape_nasa_news, "condition": True},
                {"name": "Space.com", "func": self.scrape_space_com, "condition": True},
                
                # Specialized sources - based on query context
                {"name": "NASA Science", "func": self.scrape_nasa_science, 
                 "condition": query_info['intent'] in ['solar', 'galaxy', 'universe', 'asteroid']},
                {"name": "Space Facts", "func": self.scrape_space_facts,
                 "condition": query_info['intent'] in ['solar', 'mars', 'moon', 'asteroid']},
                {"name": "USGS Astrogeology", "func": self.scrape_astrogeology,
                 "condition": query_info['intent'] in ['mars', 'moon', 'asteroid']},
                {"name": "SpaceX", "func": self.scrape_spacex_info,
                 "condition": query_info['intent'] in ['spacex', 'launch', 'rocket']},
                
                # Fallback sources - only try if needed
                {"name": "NASA Homepage", "func": self.scrape_nasa_homepage, 
                 "condition": len(all_results) < 3},
                {"name": "Universe Today", "func": self.scrape_universe_today,
                 "condition": len(all_results) < 5}
            ]
            
            # Add Wikipedia as a priority source for scientific objects
            if any(term in query.lower() for term in ['black hole', 'quasar', 'galaxy', 'star', 'universe', 'mars rover']):
                logger.info("Scientific object query detected, prioritizing scientific sources")
            
            # Execute each scraper based on conditions
            for scraper in scrapers:
                if scraper["condition"]:
                    source_name = scraper["name"]
                    logger.info(f"Attempting to scrape {source_name}...")
                    
                    try:
                        results = scraper["func"](query_info)
                        logger.info(f"{source_name} scraping returned {len(results)} results")
                        
                        # Store results by source
                        source_results[source_name] = results
                        all_results.extend(results)
                    except Exception as e:
                        logger.error(f"{source_name} scraping failed: {str(e)}")
            
            # If still no results, use fallback data
            if not all_results:
                logger.warning(f"No results found for query: {query}, using fallback data")
                fallback_results = self.get_fallback_results(query_info)
                all_results.extend(fallback_results)
                
                # Add fallback results to source tracking
                if fallback_results:
                    source_results['Static Knowledge'] = fallback_results
            
            # Sort by relevance and remove duplicates
            unique_results = []
            seen_titles = set()
            
            for result in sorted(all_results, key=lambda x: x['relevance'], reverse=True):
                if result['title'] not in seen_titles:
                    unique_results.append(result)
                    seen_titles.add(result['title'])
            
            # Append source attribution information
            sources_used = []
            for source, results in source_results.items():
                if results:
                    sources_used.append(f"{source} ({len(results)} results)")
            
            sources_info = {
                'sources_queried': list(source_results.keys()),
                'sources_with_results': [source for source, results in source_results.items() if results],
                'result_counts': {source: len(results) for source, results in source_results.items() if results}
            }
            
            logger.info(f"Returning {len(unique_results)} unique results from {len(sources_info['sources_with_results'])} sources for query: {query}")
            
            return {
                'query_info': query_info,
                'results': unique_results[:10],  # Return top 10 results
                'total_found': len(unique_results),
                'sources_info': sources_info  # Include information about which sources were used
            }
        except Exception as e:
            logger.error(f"Error processing query '{query}': {str(e)}")
            # Return a minimal response with error info but don't raise exception
            return {
                'query_info': {
                    'original_query': query,
                    'processed_query': query,
                    'intent': 'general',
                    'keywords': query.lower().split()
                },
                'results': [{
                    'title': 'Cosmic Explorer Information',
                    'description': f"We're having trouble processing your query. Our team is working on it. In the meantime, try one of our example queries!",
                    'source': 'System',
                    'link': '#',
                    'relevance': 1
                }],
                'total_found': 1
            }
    
    def get_fallback_results(self, query_info):
        """Provide fallback results when web scraping fails"""
        query = query_info['original_query'].lower()
        intent = query_info['intent']
        
        # Static knowledge base for when scraping fails
        fallback_data = {
            'mars': {
                'title': 'Mars - The Red Planet',
                'description': 'Mars is the fourth planet from the Sun and is known as the Red Planet due to iron oxide on its surface. NASA has sent multiple rovers including Perseverance and Curiosity to explore Mars.',
                'link': 'https://mars.nasa.gov/',
                'source': 'Static Knowledge'
            },
            'moon': {
                'title': 'Earth\'s Moon',
                'description': 'The Moon is Earth\'s only natural satellite. NASA\'s Apollo missions landed humans on the Moon, and the Artemis program aims to return astronauts to the lunar surface.',
                'link': 'https://moon.nasa.gov/',
                'source': 'Static Knowledge'
            },
            'black hole': {
                'title': 'Black Holes',
                'description': 'Black holes are regions of spacetime where gravity is so strong that nothing can escape. The Event Horizon Telescope captured the first image of a black hole in 2019.',
                'link': 'https://www.nasa.gov/audience/forstudents/k-4/stories/nasa-knows/what-is-a-black-hole-k4.html',
                'source': 'Static Knowledge'
            },
            'spacex': {
                'title': 'SpaceX',
                'description': 'SpaceX is a private aerospace company founded by Elon Musk. They develop reusable rockets and spacecraft, including the Falcon 9 rocket and Dragon capsule.',
                'link': 'https://www.spacex.com/',
                'source': 'Static Knowledge'
            },
            'iss': {
                'title': 'International Space Station',
                'description': 'The ISS is a space station in low Earth orbit where astronauts conduct scientific research. It has been continuously occupied since 2000.',
                'link': 'https://www.nasa.gov/mission_pages/station/main/index.html',
                'source': 'Static Knowledge'
            },
            'hubble': {
                'title': 'Hubble Space Telescope',
                'description': 'The Hubble Space Telescope has been observing the universe since 1990, providing stunning images and scientific discoveries about distant galaxies, nebulae, and planets.',
                'link': 'https://hubblesite.org/',
                'source': 'Static Knowledge'
            },
            'james webb': {
                'title': 'James Webb Space Telescope',
                'description': 'The James Webb Space Telescope is the most powerful space telescope ever built, designed to observe the universe in infrared light and study the formation of the first galaxies.',
                'link': 'https://webb.nasa.gov/',
                'source': 'Static Knowledge'
            }
        }
        
        results = []
        
        # Find relevant fallback data
        for key, data in fallback_data.items():
            if key in query or intent in key or any(word in key for word in query_info['keywords']):
                results.append({
                    'title': data['title'],
                    'link': data['link'],
                    'description': data['description'],
                    'source': data['source'],
                    'relevance': 3  # Medium relevance for fallback data
                })
        
        # If no specific matches, provide general space information
        if not results:
            results.append({
                'title': 'Space Exploration',
                'description': 'Space exploration involves the discovery and exploration of celestial structures in outer space by means of continuously evolving space technology. NASA, ESA, and other space agencies lead missions to study planets, moons, asteroids, and distant galaxies.',
                'link': 'https://www.nasa.gov/',
                'source': 'Static Knowledge',
                'relevance': 2
            })
        
        return results
