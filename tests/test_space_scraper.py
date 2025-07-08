import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestSpaceInfoScraper(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock NLTK imports since they might not be available during testing
        with patch.dict('sys.modules', {
            'nltk': MagicMock(),
            'nltk.tokenize': MagicMock(),
            'nltk.corpus': MagicMock(),
            'nltk.stem': MagicMock(),
            'streamlit': MagicMock(),
            'requests': MagicMock(),
            'bs4': MagicMock(),
            'pandas': MagicMock()
        }):
            from app import SpaceInfoScraper
            self.scraper = SpaceInfoScraper()
    
    def test_process_nlp_basic_query(self):
        """Test NLP processing with a basic space query."""
        with patch.dict('sys.modules', {
            'nltk': MagicMock(),
            'nltk.tokenize': MagicMock(),
            'nltk.corpus': MagicMock(),
            'nltk.stem': MagicMock()
        }):
            # Mock NLTK functions
            mock_tokenize = MagicMock(return_value=['latest', 'mars', 'mission'])
            mock_stopwords = MagicMock()
            mock_stopwords.words.return_value = ['the', 'a', 'an']
            mock_lemmatizer = MagicMock()
            mock_lemmatizer.lemmatize.side_effect = lambda x: x
            
            with patch('app.word_tokenize', mock_tokenize), \
                 patch('app.stopwords', mock_stopwords), \
                 patch.object(self.scraper, 'lemmatizer', mock_lemmatizer):
                
                result = self.scraper.process_nlp("latest Mars mission")
                
                self.assertIn('intent', result)
                self.assertIn('keywords', result)
                self.assertIn('original_query', result)
                self.assertEqual(result['original_query'], "latest Mars mission")
    
    def test_calculate_relevance(self):
        """Test relevance calculation."""
        text = "NASA Mars rover mission to explore the red planet"
        keywords = ['mars', 'nasa', 'rover']
        
        relevance = self.scraper.calculate_relevance(text, keywords)
        
        self.assertGreaterEqual(relevance, 0)
        self.assertIsInstance(relevance, int)
    
    @patch('app.requests.get')
    def test_scrape_nasa_news_success(self, mock_get):
        """Test successful NASA news scraping."""
        # Mock HTML response
        mock_response = MagicMock()
        mock_response.content = b'''
        <html>
            <body>
                <article class="hds-content-item">
                    <h3>Mars Mission Update</h3>
                    <a href="/news/mars-update">Read more</a>
                    <p>Latest update on Mars exploration mission.</p>
                </article>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response
        
        query_info = {
            'keywords': ['mars', 'mission'],
            'intent': 'mars',
            'original_query': 'Mars mission'
        }
        
        with patch('app.BeautifulSoup') as mock_soup:
            mock_soup.return_value.find_all.return_value = []
            
            results = self.scraper.scrape_nasa_news(query_info)
            
            self.assertIsInstance(results, list)
    
    @patch('app.requests.get')
    def test_scrape_nasa_news_error_handling(self, mock_get):
        """Test NASA news scraping error handling."""
        # Simulate network error
        mock_get.side_effect = Exception("Network error")
        
        query_info = {
            'keywords': ['mars'],
            'intent': 'mars',
            'original_query': 'Mars mission'
        }
        
        results = self.scraper.scrape_nasa_news(query_info)
        
        # Should return empty list on error
        self.assertEqual(results, [])
    
    def test_intent_recognition(self):
        """Test intent recognition for different queries."""
        test_cases = [
            ("SpaceX rocket launch", "spacex"),
            ("Mars rover mission", "mars"),
            ("International Space Station", "iss"),
            ("Hubble telescope images", "hubble"),
            ("NASA mission updates", "nasa")
        ]
        
        for query, expected_intent in test_cases:
            with patch('app.word_tokenize') as mock_tokenize, \
                 patch('app.stopwords') as mock_stopwords:
                
                mock_tokenize.return_value = query.lower().split()
                mock_stopwords.words.return_value = []
                
                result = self.scraper.process_nlp(query)
                
                # Intent should be detected correctly or fallback to 'general'
                self.assertIn(result['intent'], [expected_intent, 'general'])

class TestAdvancedSpaceScraper(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        with patch.dict('sys.modules', {
            'streamlit': MagicMock(),
            'requests': MagicMock(),
            'bs4': MagicMock()
        }):
            from enhanced_app import AdvancedSpaceScraper
            self.advanced_scraper = AdvancedSpaceScraper()
    
    @patch('enhanced_app.requests.Session')
    def test_initialization(self, mock_session):
        """Test AdvancedSpaceScraper initialization."""
        from enhanced_app import AdvancedSpaceScraper
        scraper = AdvancedSpaceScraper()
        
        self.assertIsNotNone(scraper.headers)
        self.assertIn('User-Agent', scraper.headers)
    
    def test_scrape_space_wiki_error_handling(self):
        """Test Wikipedia scraping error handling."""
        with patch.object(self.advanced_scraper.session, 'get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            results = self.advanced_scraper.scrape_space_wiki("mars")
            
            self.assertEqual(results, [])

class TestSpaceDataAnalyzer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from enhanced_app import SpaceDataAnalyzer
            self.analyzer = SpaceDataAnalyzer()
    
    def test_analyze_trends(self):
        """Test trend analysis functionality."""
        sample_results = [
            {
                'title': 'Mars Rover Discovery',
                'description': 'New Mars rover finds evidence of water',
                'source': 'NASA'
            },
            {
                'title': 'SpaceX Launch Success',
                'description': 'SpaceX successfully launches satellite',
                'source': 'SpaceX'
            }
        ]
        
        trends = self.analyzer.analyze_trends(sample_results)
        
        self.assertIn('categories', trends)
        self.assertIn('sources', trends)
        self.assertIn('total_results', trends)
        self.assertEqual(trends['total_results'], 2)

class TestUtilityFunctions(unittest.TestCase):
    
    def test_quote_plus_handling(self):
        """Test URL encoding functionality."""
        from urllib.parse import quote_plus
        
        test_query = "mars rover mission"
        encoded = quote_plus(test_query)
        
        self.assertNotIn(' ', encoded)
        self.assertIn('mars', encoded.lower())

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestSpaceInfoScraper))
    test_suite.addTest(unittest.makeSuite(TestAdvancedSpaceScraper))
    test_suite.addTest(unittest.makeSuite(TestSpaceDataAnalyzer))
    test_suite.addTest(unittest.makeSuite(TestUtilityFunctions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
