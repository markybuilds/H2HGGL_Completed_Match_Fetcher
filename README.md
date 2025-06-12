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

## Usage

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
├── h2hggl_data/                    # Output directory for match data
├── fetch_completed_matches.py      # Main script for fetching matches
├── fetch_auth_token.py            # Authentication token fetcher (Selenium)
├── example_usage.py               # Example usage demonstrations
├── requirements.txt               # Python dependencies
├── H2H_GG_LEAGUE_API.md          # API documentation
├── token_error_reference.md       # Token error troubleshooting guide
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