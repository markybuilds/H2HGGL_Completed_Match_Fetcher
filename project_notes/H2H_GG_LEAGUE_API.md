# H2H GG League API Documentation

## Base URL
`https://h2hggl.com/api`

## Authentication
Authentication details to be determined (not visible in current data)

## Endpoints

### 1. Player Statistics

#### Get All Players
```
GET /en/ebasketball/standings
```

**Response:**
```json
{
  "players": [
    {
      "rank": 1,
      "name": "PLAYER_NAME",
      "matches_played": 50,
      "win_percentage": 85.2,
      "points_for": 2500,
      "points_against": 1200,
      "form": ["W", "W", "L", "W", "L"]
    },
    // ... more players
  ]
}
```

#### Get Player Details
```
GET /en/ebasketball/player/{playerId}
```

**Response:**
```json
{
  "id": "player123",
  "name": "PLAYER_NAME",
  "team": "TEAM_NAME",
  "matches_played": 50,
  "win_percentage": 85.2,
  "points_for": 2500,
  "points_against": 1200,
  "longest_win_streak": 12,
  "current_form": ["W", "W", "L", "W", "L"],
  "rank": 1
}
```

### 2. Match Schedule

#### Get Upcoming Matches
```
GET /en/ebasketball/schedule
```

**Response:**
```json
{
  "upcoming_matches": [
    {
      "id": "match123",
      "time": "22:35",
      "player1": "PLAYER_1",
      "player1_team": "TEAM_1",
      "player2": "PLAYER_2",
      "player2_team": "TEAM_2",
      "court": "Ebasketball 2"
    },
    // ... more matches
  ]
}
```

### 3. Match Details

#### Get Match by ID
```
GET /en/ebasketball/match/{matchId}
```

**Response:**
```json
{
  "id": "match123",
  "player1": "PLAYER_1",
  "player1_team": "TEAM_1",
  "player1_score": 58,
  "player2": "PLAYER_2",
  "player2_team": "TEAM_2",
  "player2_score": 57,
  "status": "completed",
  "start_time": "2025-06-11T22:03:00Z",
  "quarters": [
    {
      "number": 1,
      "player1_score": 16,
      "player2_score": 13
    },
    {
      "number": 2,
      "player1_score": 15,
      "player2_score": 16
    },
    {
      "number": 3,
      "player1_score": 14,
      "player2_score": 15
    },
    {
      "number": 4,
      "player1_score": 13,
      "player2_score": 13
    }
  ],
  "timeline": [
    {
      "time": "Q4 00:06",
      "event_type": "foul",
      "player": "PLAYER_2",
      "description": "Foul (Reach in)"
    },
    {
      "time": "Q4 00:06",
      "event_type": "score",
      "player": "PLAYER_2",
      "points": 2,
      "score": "58 - 57"
    },
    // ... more events
  ]
}
```

### 4. Player Comparison

#### Compare Two Players
```
GET /en/ebasketball/comparePlayers/{player1Id}/{player2Id}
```

**Response:**
```json
{
  "player1": {
    "id": "player123",
    "name": "PLAYER_1",
    "team": "TEAM_1",
    "win_percentage": 49,
    "longest_win_streak": 12,
    "current_form": ["W", "W", "L", "W", "L"],
    "recent_matches": [
      {
        "opponent": "OPPONENT_NAME",
        "score": "52-61",
        "result": "L",
        "date": "2025-06-11"
      },
      // ... more matches
    ]
  },
  "player2": {
    "id": "player456",
    "name": "PLAYER_2",
    "team": "TEAM_2",
    "win_percentage": 49,
    "longest_win_streak": 15,
    "current_form": ["W", "W", "W", "W", "L"],
    "recent_matches": [
      {
        "opponent": "OPPONENT_NAME",
        "score": "58-74",
        "result": "W",
        "date": "2025-06-11"
      },
      // ... more matches
    ]
  },
  "head_to_head": [
    {
      "date": "2025-06-11",
      "player1_score": 58,
      "player2_score": 57,
      "winner": "PLAYER_1"
    },
    // ... more head-to-head matches
  ]
}
```

## Data Models

### Player
```typescript
interface Player {
  id: string;
  name: string;
  team: string;
  matches_played: number;
  win_percentage: number;
  points_for: number;
  points_against: number;
  longest_win_streak: number;
  current_form: ('W' | 'L')[];
  rank: number;
}
```

### Match
```typescript
interface Match {
  id: string;
  player1: string;
  player1_team: string;
  player1_score: number;
  player2: string;
  player2_team: string;
  player2_score: number;
  status: 'upcoming' | 'in_progress' | 'completed';
  start_time: string; // ISO 8601 format
  court: string;
  quarters: {
    number: number;
    player1_score: number;
    player2_score: number;
  }[];
  timeline: MatchEvent[];
}

interface MatchEvent {
  time: string; // e.g., "Q4 00:06"
  event_type: 'score' | 'foul' | 'timeout' | 'substitution' | 'turnover' | 'other';
  player?: string;
  team?: string;
  points?: number;
  score?: string;
  description?: string;
}
```

### PlayerComparison
```typescript
interface PlayerComparison {
  player1: {
    id: string;
    name: string;
    team: string;
    win_percentage: number;
    longest_win_streak: number;
    current_form: ('W' | 'L')[];
    recent_matches: RecentMatch[];
  };
  player2: {
    id: string;
    name: string;
    team: string;
    win_percentage: number;
    longest_win_streak: number;
    current_form: ('W' | 'L')[];
    recent_matches: RecentMatch[];
  };
  head_to_head: HeadToHeadMatch[];
}

interface RecentMatch {
  opponent: string;
  score: string;
  result: 'W' | 'L';
  date: string;
}

interface HeadToHeadMatch {
  date: string;
  player1_score: number;
  player2_score: number;
  winner: string;
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request parameters",
  "details": "Detailed error message"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found",
  "message": "The requested resource was not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting
Rate limiting details to be determined (not visible in current data)

## Versioning
API versioning details to be determined (not visible in current data)

## Changelog
- 2025-06-11: Initial API documentation
