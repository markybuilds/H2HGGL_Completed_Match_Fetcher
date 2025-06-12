#!/usr/bin/env python3
"""
H2H GG League - Match Statistics Fetcher

This script fetches detailed match statistics from the H2H GG League API
for completed matches and saves them to JSON files for analysis.

Usage:
    python fetch_match_stats.py --match-id NB125120625
    python fetch_match_stats.py --matches-file completed_matches.json
    python fetch_match_stats.py --match-id NB125120625 --output stats.json

Requires:
    - requests library for HTTP requests
    - Valid API authentication (automatically refreshed)
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


class H2HMatchStatsFetcher:
    """Fetches detailed match statistics from H2H GG League API."""
    
    def __init__(self, base_url: str = "https://api-sis-stats.hudstats.com/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Set default headers based on the example in match_stats_information.txt
        self.session.headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://h2hggl.com',
            'priority': 'u=1, i',
            'referer': 'https://h2hggl.com/',
            'sec-ch-ua': '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        })
    
    def set_auth_token(self, token: str) -> None:
        """Set authentication token."""
        self.session.headers.update({'authorization': f'Bearer {token}'})
    
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
    
    def fetch_match_stats(self, match_id: str, verbose: bool = False, retry_on_auth_fail: bool = True) -> Optional[Dict]:
        """Fetch detailed statistics for a specific match."""
        
        # Build the API endpoint URL
        url = f"{self.base_url}/match/{match_id}/stats"
        
        try:
            if verbose:
                print(f"Fetching statistics for match {match_id}...")
            
            response = self.session.get(url, timeout=30)
            
            # Check for authentication errors
            if response.status_code == 401:
                error_text = response.text.lower()
                auth_error_detected = (
                    'unauthenticated' in error_text or 
                    'authentication' in error_text or
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
                        return self.fetch_match_stats(match_id, verbose, retry_on_auth_fail=False)
                    else:
                        print("Failed to obtain new authentication token.")
                        print("Error: Authentication required. The API returned 'Unauthenticated'.")
                        return None
                else:
                    print("Error: Authentication required. The API returned 'Unauthenticated'.")
                    return None
            
            # Check for other HTTP errors
            if response.status_code == 404:
                print(f"Match {match_id} not found or statistics not available.")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching statistics for match {match_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for match {match_id}: {e}")
            return None
    
    def fetch_stats_from_matches_file(self, matches_file: str, verbose: bool = False) -> Dict[str, Dict]:
        """Fetch statistics for all matches from a completed matches file."""
        
        try:
            with open(matches_file, 'r', encoding='utf-8') as f:
                matches_data = json.load(f)
            
            matches = matches_data.get('matches', [])
            if not matches:
                print(f"No matches found in {matches_file}")
                return {}
            
            print(f"Found {len(matches)} matches in {matches_file}")
            
            all_stats = {}
            successful_fetches = 0
            failed_fetches = 0
            
            for i, match in enumerate(matches, 1):
                match_id = match.get('matchId')
                if not match_id:
                    print(f"Match {i}: No match ID found, skipping...")
                    failed_fetches += 1
                    continue
                
                # Convert match_id to string if it's a number
                match_id_str = str(match_id)
                
                if verbose:
                    home_team = match.get('homeTeamName', 'Unknown')
                    away_team = match.get('awayTeamName', 'Unknown')
                    print(f"Match {i}/{len(matches)}: {home_team} vs {away_team} (ID: {match_id_str})")
                else:
                    print(f"Fetching stats for match {i}/{len(matches)} (ID: {match_id_str})")
                
                stats = self.fetch_match_stats(match_id_str, verbose=verbose)
                
                if stats:
                    all_stats[match_id_str] = {
                        'match_info': {
                            'matchId': match_id_str,
                            'homeTeamName': match.get('homeTeamName'),
                            'awayTeamName': match.get('awayTeamName'),
                            'homeScore': match.get('homeScore'),
                            'awayScore': match.get('awayScore'),
                            'startDate': match.get('startDate'),
                            'tournamentName': match.get('tournamentName')
                        },
                        'statistics': stats
                    }
                    successful_fetches += 1
                else:
                    failed_fetches += 1
            
            print(f"\nStatistics fetching completed:")
            print(f"  Successful: {successful_fetches}")
            print(f"  Failed: {failed_fetches}")
            print(f"  Total: {len(matches)}")
            
            return all_stats
            
        except FileNotFoundError:
            print(f"Error: Matches file '{matches_file}' not found.")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing matches file '{matches_file}': {e}")
            return {}
        except Exception as e:
            print(f"Error processing matches file '{matches_file}': {e}")
            return {}
    
    def save_stats_to_file(self, stats_data: Dict, output_file: str, match_id: str = None) -> None:
        """Save match statistics to a JSON file."""
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Prepare the data structure
        if match_id:
            # Single match statistics
            output_data = {
                'metadata': {
                    'match_id': match_id,
                    'fetched_at': datetime.now().isoformat(),
                    'api_endpoint': f"{self.base_url}/match/{match_id}/stats"
                },
                'statistics': stats_data
            }
        else:
            # Multiple matches statistics
            output_data = {
                'metadata': {
                    'total_matches': len(stats_data),
                    'fetched_at': datetime.now().isoformat(),
                    'api_endpoint': f"{self.base_url}/match/[match_id]/stats"
                },
                'matches_statistics': stats_data
            }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            if match_id:
                print(f"Successfully saved statistics for match {match_id} to {output_file}")
            else:
                print(f"Successfully saved statistics for {len(stats_data)} matches to {output_file}")
            
        except IOError as e:
            print(f"Error saving file: {e}")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    
    parser = argparse.ArgumentParser(
        description='Fetch match statistics from H2H GG League API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_match_stats.py --match-id NB125120625
  python fetch_match_stats.py --matches-file h2hggl_data/completed_matches.json
  python fetch_match_stats.py --match-id NB125120625 --output custom_stats.json
  python fetch_match_stats.py --matches-file matches.json --output all_stats.json
        """
    )
    
    # Match identification arguments (mutually exclusive)
    match_group = parser.add_mutually_exclusive_group(required=True)
    match_group.add_argument(
        '--match-id',
        help='Specific match ID to fetch statistics for'
    )
    
    match_group.add_argument(
        '--matches-file',
        help='JSON file containing completed matches (from fetch_completed_matches.py)'
    )
    
    # Output arguments
    parser.add_argument(
        '--output',
        help='Output file path (default: auto-generated based on input)'
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
    """Main function to execute the match statistics fetching process."""
    
    args = parse_arguments()
    
    # Determine output file if not specified
    if not args.output:
        if args.match_id:
            args.output = f'h2hggl_data/match_stats_{args.match_id}.json'
        else:
            # Extract base name from matches file
            base_name = os.path.splitext(os.path.basename(args.matches_file))[0]
            args.output = f'h2hggl_data/{base_name}_statistics.json'
    
    if args.verbose:
        if args.match_id:
            print(f"Fetching statistics for match: {args.match_id}")
        else:
            print(f"Fetching statistics from matches file: {args.matches_file}")
        print(f"Output file: {args.output}")
    
    # Initialize the fetcher
    fetcher = H2HMatchStatsFetcher()
    
    # Set authentication token
    fetcher.set_auth_token(args.auth_token)
    if args.verbose:
        print("Authentication token set")
    
    try:
        if args.match_id:
            # Fetch statistics for a single match
            stats = fetcher.fetch_match_stats(args.match_id, verbose=args.verbose)
            
            if not stats:
                print("No statistics found or error occurred during fetching.")
                return
            
            # Save to file
            fetcher.save_stats_to_file(stats, args.output, args.match_id)
            
            # Print summary
            print(f"\nSummary:")
            print(f"  Match ID: {args.match_id}")
            print(f"  Output file: {args.output}")
            
            if args.verbose and stats:
                # Show available periods
                periods = [key for key in stats.keys() if key != 'metadata']
                print(f"  Available periods: {', '.join(periods)}")
                
                # Show sample data from endMatch if available
                if 'endMatch' in stats:
                    end_match = stats['endMatch']
                    print(f"  Final Score: {end_match.get('homePoints', 'N/A')} - {end_match.get('awayPoints', 'N/A')}")
                    print(f"  Teams: {end_match.get('homeTeamName', 'N/A')} vs {end_match.get('awayTeamName', 'N/A')}")
        
        else:
            # Fetch statistics for all matches in the file
            all_stats = fetcher.fetch_stats_from_matches_file(args.matches_file, verbose=args.verbose)
            
            if not all_stats:
                print("No statistics found or error occurred during fetching.")
                return
            
            # Save to file
            fetcher.save_stats_to_file(all_stats, args.output)
            
            # Print summary
            print(f"\nSummary:")
            print(f"  Total matches with statistics: {len(all_stats)}")
            print(f"  Source file: {args.matches_file}")
            print(f"  Output file: {args.output}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()