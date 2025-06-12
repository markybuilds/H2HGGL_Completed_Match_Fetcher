#!/usr/bin/env python3
"""
Example usage of the H2H GG League Match Fetcher

This script demonstrates different ways to use the fetch_completed_matches.py script
to retrieve completed match data from the H2H GG League API.
"""

import subprocess
import sys
from datetime import datetime, timedelta


def run_command(command: list) -> None:
    """Run a command and print the output."""
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings/Errors: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        print(f"Standard output: {e.stdout}")
    except FileNotFoundError:
        print("Error: Python not found. Make sure Python is installed and in your PATH.")


def main():
    """Demonstrate various usage examples."""
    
    print("H2H GG League Match Fetcher - Usage Examples")
    print("============================================")
    
    # Example 1: Basic usage with default parameters
    print("\n1. Basic usage (last 30 days):")
    run_command([sys.executable, "fetch_completed_matches.py"])
    
    # Example 2: Specific date range
    print("\n2. Specific date range:")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    run_command([
        sys.executable, "fetch_completed_matches.py",
        "--from", f"{yesterday} 04:00",
        "--to", f"{today} 03:59",
        "--verbose"
    ])
    
    # Example 3: Different tournament ID
    print("\n3. Different tournament ID:")
    run_command([
        sys.executable, "fetch_completed_matches.py",
        "--tournament-id", "2",
        "--output", "h2hggl_data/tournament_2_matches.json",
        "--verbose"
    ])
    
    # Example 4: Using a custom authentication token
    print("\n4. Using a custom authentication token:")
    run_command([
        sys.executable, "fetch_completed_matches.py",
        "--auth-token", "your_custom_token_here",
        "--verbose"
    ])
    
    # Example 5: Show help
    print("\n5. Help information:")
    run_command([sys.executable, "fetch_completed_matches.py", "--help"])
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("Check the h2hggl_data/ directory for output files.")
    print("="*60)


if __name__ == "__main__":
    main()