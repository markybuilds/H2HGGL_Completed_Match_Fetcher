# H2H GG League Research Tools

This repository contains tools for fetching and analyzing data from the H2H GG League API.

## Overview

The main script `fetch_completed_matches.py` allows you to retrieve completed match results from the H2H GG League API and save them to JSON files for further analysis.

## Features

- Fetch completed matches within a specified date range
- Support for different tournament IDs
- Automatic pagination handling
- Configurable output file location
- **Automatic authentication token refresh** using browser automation
- Authentication support with fallback token fetching
- Comprehensive error handling
- Verbose logging option

## Installation

1. **Clone or download this repository**

2. **Install Chrome/Chromium browser** (required for automatic token refresh):
   - The script uses Selenium WebDriver to automatically fetch authentication tokens
   - Ensure Chrome or Chromium is installed and accessible in your system PATH

3. **Set up a Python virtual environment** (recommended):
   ```bash
   python -m venv .venv
   
   # On Windows:
   .venv\Scripts\activate
   
   # On macOS/Linux:
   source .venv/bin/activate
   ```

4. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage Examples

### Fetching Completed Matches

```bash
# Fetch matches for a specific date range
python fetch_completed_matches.py --from "2024-12-01" --to "2024-12-31"

# Fetch matches for a specific tournament
python fetch_completed_matches.py --tournament-id 123 --from "2024-12-01" --to "2024-12-31"

# Use custom output file
python fetch_completed_matches.py --from "2024-12-01" --to "2024-12-31" --output "my_matches.json"

# Enable verbose output
python fetch_completed_matches.py --from "2024-12-01" --to "2024-12-31" --verbose
```

### Fetching Match Statistics

```bash
# Fetch statistics for a single match
python fetch_match_stats.py --match-id "233333" --verbose

# Fetch statistics for all matches in a completed matches file
python fetch_match_stats.py --matches-file "h2hggl_data/completed_matches.json" --output "all_stats.json"

# Demo: Fetch statistics for first 5 matches (for testing)
python demo_match_stats.py --count 5 --verbose

# Demo: Fetch statistics for first 10 matches with custom output
python demo_match_stats.py --count 10 --output "sample_stats.json"
```

## Match Statistics Data Structure

The match statistics API provides comprehensive data for each match, organized by periods:

### Available Periods
- `endMatch` - Final game statistics
- `quarter1` - First quarter statistics
- `quarter2` - Second quarter statistics  
- `quarter3` - Third quarter statistics
- `quarter4` - Fourth quarter statistics

### Available Statistics Categories
- **Scoring**: Points, Field Goals (made/attempted/percentage), Free Throws, 3-Pointers
- **Rebounds**: Offensive Rebounds, Defensive Rebounds, Total Rebounds
- **Playmaking**: Assists, Turnovers
- **Defense**: Steals, Blocks, Team Fouls
- **Advanced**: Points in the Paint, Second Chance Points, Biggest Lead, Time of Possession
- **Game Flow**: Timeouts Remaining, Dunks

### Example Output Structure
```json
{
  "metadata": {
    "total_matches": 3,
    "fetched_at": "2025-06-12T11:10:01.450490",
    "api_endpoint": "https://api-sis-stats.hudstats.com/v1/match/[match_id]/stats"
  },
  "matches_statistics": {
    "233333": {
      "match_info": {
        "matchId": "233333",
        "homeTeamName": "Los Angeles Lakers",
        "awayTeamName": "Boston Celtics",
        "homeScore": 48,
        "awayScore": 71
      },
      "statistics": {
        "endMatch": {
          "homePoints": 48,
          "awayPoints": 71,
          "homeFieldGoalsPercent": 37,
          "awayFieldGoalsPercent": 63,
          "homeAssists": 7,
          "awayAssists": 13
        }
      }
    }
  }
}
```

### Basic Usage

Fetch matches from the last 30 days:
```bash
python fetch_completed_matches.py
```

### Advanced Usage

**Specify date range:**
```bash
python fetch_completed_matches.py --from "2025-04-29 04:00" --to "2025-04-30 03:59"
```

**Different tournament:**
```bash
python fetch_completed_matches.py --tournament-id 2 --output "tournament_2_matches.json"
```

**With authentication token:**
```bash
python fetch_completed_matches.py --auth-token "your-api-token"
```

**Verbose output:**
```bash
python fetch_completed_matches.py --verbose
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|----------|
| `--from` | Start date and time (YYYY-MM-DD HH:MM) | 30 days ago |
| `--to` | End date and time (YYYY-MM-DD HH:MM) | Current date/time |
| `--tournament-id` | Tournament ID to fetch matches from | 1 |
| `--output` | Output file path | `h2hggl_data/completed_matches.json` |
| `--auth-token` | API authentication token (if required) | None |
| `--verbose` | Enable verbose output | False |
| `--help` | Show help message | - |

## Output Format

The script saves data in JSON format with the following structure:

```json
{
  "metadata": {
    "total_matches": 96,
    "fetched_at": "2025-01-08T10:30:00.123456",
    "api_endpoint": "https://api-sis-stats.hudstats.com/v1/schedule"
  },
  "matches": [
    {
      "id": 208594,
      "tournamentId": 1,
      "roundId": 1,
      "teamAId": 1,
      "teamBId": 2,
      "teamAName": "Los Angeles Lakers",
      "teamBName": "Boston Celtics",
      "participantAId": 1203,
      "participantBId": 127,
      "participantAName": "VELOCITY",
      "participantBName": "RAZE",
      "startDate": "2025-04-29T22:30:00Z",
      "status": "finished",
      "teamAScore": 78,
      "teamBScore": 65,
      "streamName": "Ebasketball 4"
    }
  ]
}
```

## Example Scripts

Run the example usage script to see different ways to use the fetcher:

```bash
python example_usage.py
```

## API Information

### Endpoint
```
GET https://api-sis-stats.hudstats.com/v1/schedule
```

### Parameters
- `schedule-type`: Set to "match" for completed games
- `from`: Start date in format YYYY-MM-DD HH:MM (URL encoded)
- `to`: End date in format YYYY-MM-DD HH:MM (URL encoded)
- `order`: Sort order (desc for most recent first)
- `tournament-id`: ID of the tournament
- `page`: Page number for pagination
- `page-size`: Number of results per page

### Authentication

The script features **automatic authentication token refresh** using browser automation:

- **Default behavior**: Uses a test token that intentionally triggers authentication errors
- **Automatic refresh**: When authentication fails, the script automatically:
  1. Launches a headless Chrome browser using Selenium
  2. Navigates to the H2H GG League website
  3. Extracts a fresh authentication token from the browser's local storage
  4. Retries the API request with the new token
  5. Continues fetching data seamlessly

**Manual token usage** (optional):
```bash
python fetch_completed_matches.py --auth-token "your_token_here"
```

**Token refresh script** (can be used independently):
```bash
python fetch_auth_token.py --headless --output my_token.json
```

The automatic token refresh eliminates the need for manual token management and ensures uninterrupted data collection.

## Error Handling

The script handles various error conditions:

- **Authentication errors**: Clear message when API token is required
- **Network errors**: Timeout and connection error handling
- **Invalid date formats**: Validation of date/time parameters
- **File I/O errors**: Proper error messages for file operations
- **JSON parsing errors**: Handling of malformed API responses

## File Structure

```
h2hggl_research/
├── .venv/                          # Python virtual environment
├── h2hggl_data/                    # Output directory for match data and statistics
├── fetch_completed_matches.py      # Main script for fetching matches
├── fetch_match_stats.py           # Script to fetch detailed match statistics
├── demo_match_stats.py            # Demo script for testing match statistics functionality
├── fetch_auth_token.py            # Authentication token fetcher (Selenium)
├── example_usage.py               # Example usage demonstrations
├── requirements.txt               # Python dependencies
├── H2H_GG_LEAGUE_API.md          # API documentation
├── token_error_reference.md       # Token error troubleshooting guide
├── match_stats_information.txt     # API documentation and examples for match statistics
└── README.md                      # This file
```

## Troubleshooting

### Common Issues

1. **"Unauthenticated" error**
   - The API requires authentication
   - Obtain an API token and use `--auth-token` parameter

2. **"requests library not found"**
   - Install dependencies: `pip install -r requirements.txt`

3. **Invalid date format**
   - Use format: "YYYY-MM-DD HH:MM"
   - Example: "2025-04-29 04:00"

4. **No matches found**
   - Check if the date range contains any completed matches
   - Verify the tournament ID is correct
   - Check API endpoint availability

### Debug Mode

Use the `--verbose` flag to get detailed information about the fetching process:

```bash
python fetch_completed_matches.py --verbose
```

## Contributing

When adding new features or fixing bugs:

1. Follow PEP 8 coding standards
2. Add comprehensive docstrings
3. Include error handling
4. Update this README if needed

## License

This project is for research purposes. Please respect the H2H GG League API terms of service.