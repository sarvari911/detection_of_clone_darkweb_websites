"""
Configuration Module for Dark Web Clone Detection
Windows-Compatible Settings
=============================================
This module handles all project configurations,
directory management, and environment settings.
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


class Config:
    """
    Central configuration class for the project.
    All settings are loaded from environment variables
    with sensible defaults for Windows.
    """
    
    # ============================================
    # PROJECT PATHS
    # ============================================
    
    # Base directory (where config.py is located)
    BASE_DIR = Path(__file__).parent.absolute()
    
    # Data directories
    DATA_DIR = BASE_DIR / 'data'
    RAW_DATA_DIR = DATA_DIR / 'raw'
    PROCESSED_DATA_DIR = DATA_DIR / 'processed'
    METADATA_DIR = DATA_DIR / 'metadata'
    FEATURES_DIR = DATA_DIR / 'features'
    DATASET_DIR = DATA_DIR / 'dataset'
    
    # Model and output directories
    MODELS_DIR = BASE_DIR / 'models'
    OUTPUT_DIR = BASE_DIR / 'output'
    LOGS_DIR = BASE_DIR / 'logs'
    SCRIPTS_DIR = BASE_DIR / 'scripts'
    
    # ============================================
    # TOR CONFIGURATION
    # ============================================
    
    # Tor proxy settings (SOCKS5)
    TOR_PROXY_HOST = os.getenv('TOR_PROXY_HOST', '127.0.0.1')
    TOR_PROXY_PORT = int(os.getenv('TOR_PROXY_PORT', '9150'))
    TOR_CONTROL_PORT = int(os.getenv('TOR_CONTROL_PORT', '9051'))
    TOR_PASSWORD = os.getenv('TOR_PASSWORD', None)
    
    # Tor connection string for requests library
    TOR_PROXY_URL = f'socks5h://{TOR_PROXY_HOST}:{TOR_PROXY_PORT}'
    
    # ============================================
    # CRAWLER SETTINGS
    # ============================================
    
    # Request timeouts and delays (in seconds)
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '60'))
    REQUEST_DELAY = int(os.getenv('REQUEST_DELAY', '10'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    
    # Maximum page size to download (10MB default)
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', str(10 * 1024 * 1024)))
    
    # User agent string (mimics Firefox on Windows)
    USER_AGENT = os.getenv(
        'USER_AGENT',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
    )
    
    # ============================================
    # CLONE DETECTION SETTINGS
    # ============================================
    
    # Similarity threshold for clone detection (0.0 to 1.0)
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.85'))
    
    # Features to extract for comparison
    FEATURE_TYPES = [
        'html_structure',
        'text_content',
        'css_classes',
        'script_patterns',
        'meta_tags',
        'link_patterns',
        'form_structures',
        'image_hashes'
    ]
    
    # ============================================
    # SAFETY AND COMPLIANCE
    # ============================================
    
    # Domain whitelist (empty = allow all)
    ALLOWED_DOMAINS = [
        domain.strip() 
        for domain in os.getenv('ALLOWED_DOMAINS', '').split(',') 
        if domain.strip()
    ]
    
    # Maximum number of pages per crawl session
    MAX_PAGES_PER_SESSION = int(os.getenv('MAX_PAGES_PER_SESSION', '10'))
    
    # Respect robots.txt (even on dark web, be ethical)
    RESPECT_ROBOTS_TXT = os.getenv('RESPECT_ROBOTS_TXT', 'True').lower() == 'true'
    
    # ============================================
    # FILE NAMING CONVENTIONS
    # ============================================
    
    @staticmethod
    def generate_filename(url, prefix='page'):
        """
        Generate a safe filename from URL
        
        Args:
            url: The URL to generate filename from
            prefix: Prefix for the filename
            
        Returns:
            str: Safe filename with timestamp
        """
        # Create a hash from URL
        url_hash = abs(hash(url)) % 1000000
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create safe filename
        filename = f"{prefix}_{url_hash}_{timestamp}"
        
        # Remove any unsafe characters
        safe_filename = "".join(
            c for c in filename 
            if c.isalnum() or c in ('_', '-')
        )
        
        return safe_filename
    
    @staticmethod
    def get_timestamp():
        """Get current timestamp string"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # ============================================
    # DIRECTORY MANAGEMENT
    # ============================================
    
    @classmethod
    def create_directories(cls):
        """
        Create all necessary project directories.
        Safe to call multiple times - won't error if directories exist.
        """
        directories = [
            cls.DATA_DIR,
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.METADATA_DIR,
            cls.FEATURES_DIR,
            cls.DATASET_DIR,
            cls.MODELS_DIR,
            cls.OUTPUT_DIR,
            cls.LOGS_DIR,
            cls.SCRIPTS_DIR
        ]
        
        created_count = 0
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                
                # Create .gitkeep to track empty directories in git
                gitkeep_file = directory / '.gitkeep'
                if not gitkeep_file.exists():
                    gitkeep_file.touch()
                    created_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                raise
        
        logger.info(f"Directories initialized ({len(directories)} total, {created_count} new)")
        
        return True
    
    @classmethod
    def validate(cls):
        """
        Validate configuration settings
        
        Returns:
            bool: True if configuration is valid
        """
        errors = []
        
        # Check Tor proxy port
        if not (1024 <= cls.TOR_PROXY_PORT <= 65535):
            errors.append(f"Invalid TOR_PROXY_PORT: {cls.TOR_PROXY_PORT}")
        
        # Check request timeout
        if cls.REQUEST_TIMEOUT < 10:
            errors.append("REQUEST_TIMEOUT should be at least 10 seconds")
        
        # Check similarity threshold
        if not (0.0 <= cls.SIMILARITY_THRESHOLD <= 1.0):
            errors.append("SIMILARITY_THRESHOLD must be between 0.0 and 1.0")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False
        
        logger.info("Configuration validated successfully")
        return True
    
    @classmethod
    def display(cls):
        """Display current configuration settings"""
        print("\n" + "="*50)
        print("CURRENT CONFIGURATION")
        print("="*50)
        print(f"Base Directory: {cls.BASE_DIR}")
        print(f"Tor Proxy: {cls.TOR_PROXY_URL}")
        print(f"Request Timeout: {cls.REQUEST_TIMEOUT}s")
        print(f"Request Delay: {cls.REQUEST_DELAY}s")
        print(f"Max Retries: {cls.MAX_RETRIES}")
        print(f"Similarity Threshold: {cls.SIMILARITY_THRESHOLD}")
        print(f"Max Pages/Session: {cls.MAX_PAGES_PER_SESSION}")
        print("="*50 + "\n")


# ============================================
# INITIALIZATION FUNCTION
# ============================================

def initialize_project():
    """
    Initialize the entire project.
    Call this once at the start of your application.
    
    Returns:
        bool: True if initialization successful
    """
    try:
        logger.info("Initializing Dark Web Clone Detection System...")
        
        # Create all directories
        Config.create_directories()
        
        # Validate configuration
        if not Config.validate():
            logger.error("Configuration validation failed")
            return False
        
        # Display configuration (optional)
        # Config.display()
        
        logger.info("Project initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Project initialization failed: {e}")
        return False


# ============================================
# MAIN GUARD FOR TESTING
# ============================================

if __name__ == "__main__":
    """
    Test the configuration module directly.
    Run: python config.py
    """
    print("\n" + "🔧 Testing Configuration Module 🔧")
    
    # Initialize project
    if initialize_project():
        print("\n✅ Configuration is valid and directories are ready!")
        Config.display()
    else:
        print("\n❌ Configuration has errors. Check the logs above.")
    
    # Show all directory paths
    print("\n📁 Project Directory Structure:")
    print(f"   Raw Data: {Config.RAW_DATA_DIR}")
    print(f"   Processed Data: {Config.PROCESSED_DATA_DIR}")
    print(f"   Features: {Config.FEATURES_DIR}")
    print(f"   Models: {Config.MODELS_DIR}")
    print(f"   Output: {Config.OUTPUT_DIR}")
    print(f"   Logs: {Config.LOGS_DIR}")