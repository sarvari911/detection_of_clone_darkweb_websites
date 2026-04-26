"""
Dark Web Crawler Module
Crawls .onion websites through Tor Browser
"""

import requests
import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Disable SSL warnings (some .onion sites have SSL issues)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DarkWebCrawler:
    """Crawler for .onion dark web sites via Tor Browser"""

    def __init__(self, proxy_host="127.0.0.1", proxy_port=9150):
        """
        Initialize the dark web crawler
        
        Args:
            proxy_host: Tor proxy host (default: 127.0.0.1)
            proxy_port: Tor proxy port (9150 for Tor Browser, 9050 for Expert Bundle)
        """
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_url = f"socks5h://{proxy_host}:{proxy_port}"
        self.request_delay = 10  # seconds between requests
        self.max_retries = 3
        
        # Create a session
        self.session = self._create_session()
        
        logger.info(f"Crawler initialized with proxy: {self.proxy_url}")

    def _create_session(self):
        """Create a requests session configured for Tor"""
        session = requests.Session()
        
        # Set SOCKS5 proxy
        session.proxies = {
            'http': self.proxy_url,
            'https': self.proxy_url
        }
        
        # Browser-like headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        
        return session

    def verify_connection(self):
        """
        Check if we can connect through Tor
        
        Returns:
            bool: True if connected through Tor
        """
        print("\n🔍 Verifying Tor connection...")
        
        try:
            response = self.session.get(
                'https://check.torproject.org/api/ip',
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('IsTor'):
                    print(f"✅ Connected through Tor!")
                    print(f"   Exit IP: {data.get('IP', 'Unknown')}")
                    return True
                else:
                    print("❌ NOT using Tor! Check your proxy settings.")
                    return False
            else:
                print(f"⚠️ Got status code: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Tor. Is Tor Browser open?")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def fetch_page(self, url):
        """
        Fetch a single .onion page
        
        Args:
            url: The .onion URL to fetch
            
        Returns:
            dict: Page data or None if failed
        """
        print(f"\n📡 Fetching: {url}")
        
        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()
                
                response = self.session.get(
                    url,
                    timeout=60,
                    allow_redirects=True,
                    verify=False
                )
                
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    print(f"   ✅ Success ({elapsed:.1f}s)")
                    
                    # Parse HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract data
                    page_data = {
                        'url': url,
                        'status_code': response.status_code,
                        'response_time': round(elapsed, 2),
                        'html': response.text,
                        'html_length': len(response.text),
                        'title': soup.title.string.strip() if soup.title else 'No Title',
                        'text_preview': soup.get_text()[:500],
                        'timestamp': datetime.now().isoformat(),
                    }
                    
                    return page_data
                    
                elif response.status_code == 404:
                    print(f"   ❌ Page not found (404)")
                    return None
                elif response.status_code == 403:
                    print(f"   ❌ Access forbidden (403)")
                    return None
                else:
                    print(f"   ⚠️ Attempt {attempt}: Status {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"   ⏱️ Timeout on attempt {attempt}")
            except requests.exceptions.ConnectionError:
                print(f"   🔌 Connection error on attempt {attempt}")
            except Exception as e:
                print(f"   ❌ Error on attempt {attempt}: {e}")
            
            # Wait before retry
            if attempt < self.max_retries:
                wait = self.request_delay * attempt
                print(f"   Waiting {wait}s before retry...")
                time.sleep(wait)
        
        print(f"   ❌ Failed after {self.max_retries} attempts")
        return None

    def save_page(self, page_data, folder="data/raw"):
        """
        Save crawled page to disk
        
        Args:
            page_data: Dictionary with page data
            folder: Folder to save in
            
        Returns:
            str: Path to saved file
        """
        # Create folder if needed
        Path(folder).mkdir(parents=True, exist_ok=True)
        
        # Generate safe filename
        url_hash = abs(hash(page_data['url'])) % 100000
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"page_{url_hash}_{timestamp}.json"
        filepath = os.path.join(folder, filename)
        
        # Save as JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Saved: {filename}")
        return filepath

    def crawl_original_and_suspect(self, original_url, suspect_url):
        """
        Crawl both original and suspected clone sites
        
        Args:
            original_url: Original .onion site
            suspect_url: Suspected clone .onion site
            
        Returns:
            tuple: (original_data, suspect_data) or (None, None)
        """
        print("\n" + "=" * 50)
        print("CRAWLING FOR CLONE DETECTION")
        print("=" * 50)
        
        print(f"\n📌 Original site: {original_url}")
        print(f"📌 Suspect site:  {suspect_url}")
        
        # Crawl original
        original_data = self.fetch_page(original_url)
        
        if not original_data:
            print("\n❌ Failed to crawl original site. Stopping.")
            return None, None
        
        # Respectful delay between requests
        print(f"\n⏳ Waiting {self.request_delay}s before next request...")
        time.sleep(self.request_delay)
        
        # Crawl suspect
        suspect_data = self.fetch_page(suspect_url)
        
        if not suspect_data:
            print("\n❌ Failed to crawl suspect site. Stopping.")
            return None, None
        
        # Save both
        print("\n💾 Saving data...")
        self.save_page(original_data)
        self.save_page(suspect_data)
        
        # Quick summary
        print("\n" + "=" * 50)
        print("CRAWL SUMMARY")
        print("=" * 50)
        print(f"Original: {original_data['title'][:80]}")
        print(f"  Size: {original_data['html_length']} chars")
        print(f"Suspect:  {suspect_data['title'][:80]}")
        print(f"  Size: {suspect_data['html_length']} chars")
        print("=" * 50)
        
        return original_data, suspect_data


# ============================================
# QUICK TEST
# ============================================

def quick_test():
    """Test the crawler with a known .onion site"""
    print("\n🧪 Dark Web Crawler Quick Test")
    print("-" * 40)
    
    crawler = DarkWebCrawler()
    
    # Step 1: Verify Tor connection
    if not crawler.verify_connection():
        print("\n❌ Tor verification failed.")
        print("Make sure Tor Browser is open!")
        return
    
    # Step 2: Try fetching a known .onion site
    # DuckDuckGo's .onion address (safe to test)
    test_url = "https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/"
    
    print(f"\n📡 Testing with: DuckDuckGo .onion")
    page = crawler.fetch_page(test_url)
    
    if page:
        print(f"\n✅ Test successful!")
        print(f"   Title: {page['title']}")
        print(f"   Size: {page['html_length']} characters")
        print(f"   Time: {page['response_time']}s")
        
        # Save test result
        crawler.save_page(page)
    else:
        print("\n❌ Test failed. The .onion site might be down.")


if __name__ == "__main__":
    quick_test()