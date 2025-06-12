#!/usr/bin/env python3
"""
H2H GG League - Authentication Token Fetcher

This script navigates to the H2HGGL website and extracts the authentication token
from local storage to save it for use with the API.

Usage:
    python fetch_auth_token.py
    python fetch_auth_token.py --headless
    python fetch_auth_token.py --output custom_token.json

Requires:
    - selenium library for browser automation
    - Chrome/Chromium browser
"""

import argparse
import json
import time
from pathlib import Path
from typing import Optional

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
except ImportError:
    print("Error: selenium library not found. Install with: pip install selenium")
    print("Also ensure Chrome/Chromium browser is installed")
    exit(1)


class H2HTokenFetcher:
    """Fetches authentication token from H2HGGL website using Playwright."""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.target_url = "https://h2hggl.com/en/match/NB122120625"
        self.token_key = "sis-hudstats-token"
    
    def fetch_token(self) -> Optional[str]:
        """Navigate to H2HGGL website and extract auth token from local storage."""
        driver = None
        try:
            # Setup Chrome options
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Initialize the Chrome driver
            print("Starting Chrome browser...")
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(self.timeout // 1000)  # Convert to seconds
            
            print(f"Navigating to {self.target_url}...")
            
            # Navigate to the target URL
            driver.get(self.target_url)
            
            print("Page loaded successfully. Waiting for token to be set...")
            
            # Wait a moment for the page to fully load and set the token
            time.sleep(3)
            
            # Extract token from local storage using JavaScript
            token = driver.execute_script(f"""
                return localStorage.getItem('{self.token_key}');
            """)
            
            if token:
                print(f"Successfully extracted token: {token[:50]}...")
                return token
            else:
                print(f"No token found in local storage with key '{self.token_key}'")
                return None
                
        except TimeoutException:
            print(f"Timeout: Page failed to load within {self.timeout // 1000} seconds")
            return None
        except WebDriverException as e:
            print(f"WebDriver error: {e}")
            return None
        except Exception as e:
            print(f"Error fetching token: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def save_token_to_file(self, token: str, output_file: str = "auth_token.json") -> bool:
        """Save the extracted token to a JSON file."""
        
        try:
            token_data = {
                "token": token,
                "extracted_at": self._get_current_timestamp(),
                "source": self.target_url,
                "key": self.token_key
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, indent=2, ensure_ascii=False)
            
            print(f"Token saved to {output_file}")
            return True
            
        except IOError as e:
            print(f"Error saving token to file: {e}")
            return False
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()





def main():
    """Main function to handle command line arguments and fetch token."""
    parser = argparse.ArgumentParser(
        description="Fetch authentication token from H2HGGL website"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (default: False)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds for page operations (default: 30)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="auth_token.json",
        help="Output file for the token (default: auth_token.json)"
    )
    
    args = parser.parse_args()
    
    # Create fetcher and get token
    fetcher = H2HTokenFetcher(headless=args.headless, timeout=args.timeout * 1000)
    token = fetcher.fetch_token()
    
    if token:
        if fetcher.save_token_to_file(token, args.output):
            print(f"Token successfully saved to {args.output}")
            return 0
        else:
            print("Failed to save token to file")
            return 1
    else:
        print("Failed to fetch authentication token")
        return 1


if __name__ == '__main__':
    exit(main())