#!/usr/bin/env python3
"""
H2H GG League - Match Statistics Demo

This script demonstrates fetching match statistics for a small subset of matches
from the completed matches file for testing and demonstration purposes.

Usage:
    python demo_match_stats.py
    python demo_match_stats.py --count 10
"""

import argparse
import json
import sys
from fetch_match_stats import H2HMatchStatsFetcher


def main():
    """Demo function to fetch statistics for a few matches."""
    
    parser = argparse.ArgumentParser(
        description='Demo: Fetch match statistics for a subset of matches'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='Number of matches to process (default: 5)'
    )
    
    parser.add_argument(
        '--matches-file',
        default='h2hggl_data/completed_matches.json',
        help='Completed matches file (default: h2hggl_data/completed_matches.json)'
    )
    
    parser.add_argument(
        '--output',
        default='h2hggl_data/demo_match_statistics.json',
        help='Output file (default: h2hggl_data/demo_match_statistics.json)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        # Load the completed matches file
        with open(args.matches_file, 'r', encoding='utf-8') as f:
            matches_data = json.load(f)
        
        matches = matches_data.get('matches', [])
        if not matches:
            print(f"No matches found in {args.matches_file}")
            return
        
        # Take only the first N matches
        subset_matches = matches[:args.count]
        
        print(f"Processing {len(subset_matches)} matches from {args.matches_file}")
        
        # Initialize the fetcher
        fetcher = H2HMatchStatsFetcher()
        fetcher.set_auth_token('test')  # Will trigger auto-refresh
        
        all_stats = {}
        successful_fetches = 0
        failed_fetches = 0
        
        for i, match in enumerate(subset_matches, 1):
            match_id = match.get('matchId')
            if not match_id:
                print(f"Match {i}: No match ID found, skipping...")
                failed_fetches += 1
                continue
            
            match_id_str = str(match_id)
            home_team = match.get('homeTeamName', 'Unknown')
            away_team = match.get('awayTeamName', 'Unknown')
            home_score = match.get('homeScore', 'N/A')
            away_score = match.get('awayScore', 'N/A')
            
            print(f"Match {i}/{len(subset_matches)}: {home_team} vs {away_team} ({home_score}-{away_score}) [ID: {match_id_str}]")
            
            stats = fetcher.fetch_match_stats(match_id_str, verbose=args.verbose)
            
            if stats:
                all_stats[match_id_str] = {
                    'match_info': {
                        'matchId': match_id_str,
                        'homeTeamName': home_team,
                        'awayTeamName': away_team,
                        'homeScore': home_score,
                        'awayScore': away_score,
                        'startDate': match.get('startDate'),
                        'tournamentName': match.get('tournamentName'),
                        'result': match.get('result')
                    },
                    'statistics': stats
                }
                successful_fetches += 1
                
                # Show some key stats
                if 'endMatch' in stats:
                    end_stats = stats['endMatch']
                    home_fg_pct = end_stats.get('homeFieldGoalsPercent', 'N/A')
                    away_fg_pct = end_stats.get('awayFieldGoalsPercent', 'N/A')
                    home_assists = end_stats.get('homeAssists', 'N/A')
                    away_assists = end_stats.get('awayAssists', 'N/A')
                    print(f"  → FG%: {home_fg_pct}% vs {away_fg_pct}%, Assists: {home_assists} vs {away_assists}")
            else:
                failed_fetches += 1
                print(f"  → Failed to fetch statistics")
        
        # Save results
        if all_stats:
            fetcher.save_stats_to_file(all_stats, args.output)
        
        print(f"\nDemo Results:")
        print(f"  Successful: {successful_fetches}")
        print(f"  Failed: {failed_fetches}")
        print(f"  Total processed: {len(subset_matches)}")
        
        if successful_fetches > 0:
            print(f"  Output file: {args.output}")
            
            # Show sample statistics structure
            sample_match_id = list(all_stats.keys())[0]
            sample_stats = all_stats[sample_match_id]['statistics']
            periods = [key for key in sample_stats.keys() if key != 'metadata']
            print(f"  Available periods: {', '.join(periods)}")
            
            if 'endMatch' in sample_stats:
                end_match = sample_stats['endMatch']
                stat_categories = [
                    'Points', 'FieldGoals', 'FreeThrows', '3Pointers', 
                    'Rebounds', 'Assists', 'Steals', 'Blocks', 'Turnovers'
                ]
                available_stats = []
                for category in stat_categories:
                    home_key = f'home{category}'
                    away_key = f'away{category}'
                    if any(key.startswith(home_key) or key.startswith(away_key) for key in end_match.keys()):
                        available_stats.append(category)
                
                print(f"  Available stat categories: {', '.join(available_stats)}")
    
    except FileNotFoundError:
        print(f"Error: Matches file '{args.matches_file}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error parsing matches file '{args.matches_file}': {e}")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()