#!/usr/bin/env python3
"""
H2H GG League - Completed Matches Fetcher

This script fetches completed match results from the H2H GG League API
and saves them to a JSON file for analysis.

Usage:
    python fetch_completed_matches.py
    python fetch_completed_matches.py --from "2025-04-29 04:00" --to "2025-04-30 03:59"
    python fetch_completed_matches.py --tournament-id 1 --output matches.json

Requires:
    - requests library for HTTP requests
    - Valid API authentication (if required)
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


class H2HMatchFetcher:
    """Fetches completed match data from H2H GG League API."""
    
    def __init__(self, base_url: str = "https://api-sis-stats.hudstats.com/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'H2H-GG-League-Fetcher/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def set_auth_token(self, token: str) -> None:
        """Set authentication token if required."""
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def refresh_auth_token(self, verbose: bool = False) -> Optional[str]:
        """Fetch a new authentication token using the token fetcher script."""
        try:
            if verbose:
                print("Attempting to fetch new authentication token...")
            
            # Run the token fetcher script
            result = subprocess.run(
                [sys.executable, 'fetch_auth_token.py', '--headless'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Load the token from the output file
                try:
                    with open('auth_token.json', 'r', encoding='utf-8') as f:
                        token_data = json.load(f)
                    
                    new_token = token_data.get('token')
                    if new_token:
                        if verbose:
                            print("Successfully fetched new token")
                        return new_token
                    else:
                        if verbose:
                            print("Token file exists but no token found")
                        return None
                        
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    if verbose:
                        print(f"Error reading token file: {e}")
                    return None
            else:
                if verbose:
                    print(f"Token fetcher script failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            if verbose:
                print("Token fetcher script timed out")
            return None
        except Exception as e:
            if verbose:
                print(f"Error running token fetcher: {e}")
            return None
    
    def format_datetime(self, dt_str: str) -> str:
        """Format datetime string for API."""
        # Parse the datetime string and format it properly
        # Let requests handle URL encoding automatically
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            formatted = dt.strftime("%Y-%m-%d %H:%M")
            return formatted
        except ValueError as e:
            raise ValueError(f"Invalid datetime format. Use 'YYYY-MM-DD HH:MM': {e}")
    
    def fetch_matches_page(self, 
                          from_date: str, 
                          to_date: str, 
                          tournament_id: int = 1,
                          page: int = 1,
                          page_size: int = 100,
                          verbose: bool = False,
                          retry_on_auth_fail: bool = True) -> Dict:
        """Fetch a single page of completed matches."""
        
        # Format dates for URL encoding
        from_encoded = self.format_datetime(from_date)
        to_encoded = self.format_datetime(to_date)
        
        # Build the API endpoint URL
        url = f"{self.base_url}/schedule"
        params = {
            'schedule-type': 'match',
            'from': from_encoded,
            'to': to_encoded,
            'order': 'desc',
            'tournament-id': tournament_id,
            'page': page,
            'page-size': page_size
        }
        
        try:
            if verbose:
                print(f"Fetching page {page} from {from_date} to {to_date}...")
            else:
                print(f"Fetching page {page} from {from_date} to {to_date}...")
            
            response = self.session.get(url, params=params, timeout=30)
            
            # Check for authentication errors
            if response.status_code == 401:
                error_text = response.text.lower()
                auth_error_detected = (
                    'unauthenticated' in error_text or 
                    'authentication' in error_text or
                    'api key' in error_text or
                    'authentication token' in error_text
                )
                
                if auth_error_detected and retry_on_auth_fail:
                    print("Authentication failed. Attempting to fetch new token...")
                    
                    # Try to get a new token
                    new_token = self.refresh_auth_token(verbose=verbose)
                    
                    if new_token:
                        # Update the session with the new token
                        self.set_auth_token(new_token)
                        print("Retrying request with new token...")
                        
                        # Retry the request with the new token (no retry to avoid infinite loop)
                        return self.fetch_matches_page(
                            from_date, to_date, tournament_id, page, page_size, 
                            verbose, retry_on_auth_fail=False
                        )
                    else:
                        print("Failed to obtain new authentication token.")
                        print("Error: Authentication required. The API returned 'Unauthenticated'.")
                        print("Please check if you need to provide an API key or authentication token.")
                        return None
                else:
                    print("Error: Authentication required. The API returned 'Unauthenticated'.")
                    print("Please check if you need to provide an API key or authentication token.")
                    return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
    
    def fetch_all_matches(self, 
                         from_date: str, 
                         to_date: str, 
                         tournament_id: int = 1,
                         verbose: bool = False) -> List[Dict]:
        """Fetch all completed matches within the date range."""
        
        all_matches = []
        page = 1
        
        while True:
            data = self.fetch_matches_page(from_date, to_date, tournament_id, page, verbose=verbose)
            
            if not data or 'data' not in data:
                break
            
            matches = data['data']
            if not matches:
                break
            
            all_matches.extend(matches)
            
            # Check if we have more pages
            last_page = data.get('lastPage', 1)
            current_page = data.get('currentPage', page)
            total = data.get('total', 0)
            
            print(f"Fetched {len(matches)} matches from page {current_page}/{last_page} (total: {total})")
            
            if current_page >= last_page:
                break
            
            page += 1
        
        return all_matches
    
    def save_matches_to_file(self, matches: List[Dict], output_file: str) -> None:
        """Save matches data to a JSON file."""
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Prepare the data structure
        output_data = {
            'metadata': {
                'total_matches': len(matches),
                'fetched_at': datetime.now().isoformat(),
                'api_endpoint': f"{self.base_url}/schedule"
            },
            'matches': matches
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"Successfully saved {len(matches)} matches to {output_file}")
            
        except IOError as e:
            print(f"Error saving file: {e}")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    
    parser = argparse.ArgumentParser(
        description='Fetch completed matches from H2H GG League API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_completed_matches.py
  python fetch_completed_matches.py --from "2025-04-29 04:00" --to "2025-04-30 03:59"
  python fetch_completed_matches.py --tournament-id 2 --output custom_matches.json
  python fetch_completed_matches.py --auth-token "your-api-token"
        """
    )
    
    # Date range arguments
    parser.add_argument(
        '--from', 
        dest='from_date',
        default=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M"),
        help='Start date and time (format: "YYYY-MM-DD HH:MM", default: 30 days ago)'
    )
    
    parser.add_argument(
        '--to', 
        dest='to_date',
        default=datetime.now().strftime("%Y-%m-%d %H:%M"),
        help='End date and time (format: "YYYY-MM-DD HH:MM", default: current date/time)'
    )
    
    # Tournament and output arguments
    parser.add_argument(
        '--tournament-id', 
        type=int, 
        default=1,
        help='Tournament ID (default: 1)'
    )
    
    parser.add_argument(
        '--output', 
        default='h2hggl_data/completed_matches.json',
        help='Output file path (default: h2hggl_data/completed_matches.json)'
    )
    
    # Authentication
    parser.add_argument(
        '--auth-token',
        default='test',
        help='API authentication token (default: test token to trigger auth refresh)'
    )
    
    # Verbose output
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def main():
    """Main function to execute the match fetching process."""
    
    args = parse_arguments()
    
    if args.verbose:
        print(f"Fetching matches from {args.from_date} to {args.to_date}")
        print(f"Tournament ID: {args.tournament_id}")
        print(f"Output file: {args.output}")
    
    # Initialize the fetcher
    fetcher = H2HMatchFetcher()
    
    # Set authentication token (now has default value)
    fetcher.set_auth_token(args.auth_token)
    if args.verbose:
        print("Authentication token set")
    
    # Fetch all matches
    try:
        matches = fetcher.fetch_all_matches(
            from_date=args.from_date,
            to_date=args.to_date,
            tournament_id=args.tournament_id,
            verbose=args.verbose
        )
        
        if not matches:
            print("No matches found or error occurred during fetching.")
            return
        
        # Save to file
        fetcher.save_matches_to_file(matches, args.output)
        
        # Print summary
        print(f"\nSummary:")
        print(f"  Total matches fetched: {len(matches)}")
        print(f"  Date range: {args.from_date} to {args.to_date}")
        print(f"  Tournament ID: {args.tournament_id}")
        print(f"  Output file: {args.output}")
        
        if args.verbose and matches:
            print(f"\nSample match data:")
            sample_match = matches[0]
            print(f"  Match ID: {sample_match.get('matchId')}")
            print(f"  Teams: {sample_match.get('homeTeamName')} vs {sample_match.get('awayTeamName')}")
            print(f"  Score: {sample_match.get('homeScore')} - {sample_match.get('awayScore')}")
            print(f"  Date: {sample_match.get('startDate')}")
            print(f"  Tournament: {sample_match.get('tournamentName')}")
            print(f"  Result: {sample_match.get('result')}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()