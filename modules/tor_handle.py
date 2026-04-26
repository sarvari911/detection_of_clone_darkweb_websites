"""
Tor Handler Module
Works with Tor Browser (Option 1 - No tor.exe needed)
"""

import socket
import logging

logger = logging.getLogger(__name__)


class TorHandler:
    """Handles Tor connection via Tor Browser"""

    def __init__(self, proxy_port=9150):
        """
        Initialize Tor Handler
        
        Args:
            proxy_port: Tor proxy port (9150 for Tor Browser, 9050 for Expert Bundle)
        """
        self.proxy_port = proxy_port
        self.control_port = 9151

    def is_tor_running(self):
        """
        Check if Tor Browser's Tor is running
        
        Returns:
            bool: True if Tor is accessible
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('127.0.0.1', self.proxy_port))
            sock.close()
            
            if result == 0:
                logger.info(f"Tor is running on port {self.proxy_port}")
                return True
            else:
                logger.warning(f"Tor not found on port {self.proxy_port}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking Tor: {e}")
            return False

    def check_connection(self):
        """
        Check Tor connectivity status
        
        Returns:
            dict: Status information
        """
        is_running = self.is_tor_running()
        
        status = {
            'tor_running': is_running,
            'proxy_port': self.proxy_port,
            'method': 'Tor Browser'
        }

        print("\n" + "=" * 40)
        print("TOR CONNECTION STATUS")
        print("=" * 40)
        
        if is_running:
            print(f"✓ Tor is running on port {self.proxy_port}")
            print(f"✓ Using: Tor Browser")
            print("\nYou can now crawl .onion sites!")
        else:
            print(f"✗ Tor is NOT running on port {self.proxy_port}")
            print("\nPlease open Tor Browser first!")
            print("Keep Tor Browser open while crawling.")
        
        print("=" * 40 + "\n")

        return status


def test_tor():
    """Test Tor handler"""
    print("\nTesting Tor Connection...\n")
    
    # Try port 9150 first (Tor Browser)
    tor = TorHandler(proxy_port=9150)
    
    if tor.is_tor_running():
        tor.check_connection()
        return True
    
    # If 9150 fails, try 9050
    print("Port 9150 not available, trying port 9050...\n")
    tor = TorHandler(proxy_port=9050)
    
    if tor.is_tor_running():
        tor.check_connection()
        return True
    
    print("\n❌ Tor is not running on either port.")
    print("\nTo fix this:")
    print("1. Open Tor Browser (keep it open)")
    print("2. Wait for it to connect")
    print("3. Run this test again")
    return False


if __name__ == "__main__":
    test_tor()