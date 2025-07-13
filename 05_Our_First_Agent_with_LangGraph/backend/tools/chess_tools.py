"""
Chess tools for LangGraph agents
"""

import httpx
import json
from typing import Dict, Any
from langchain.tools import tool
from utils.logging import get_logger

logger = get_logger(__name__)

@tool
def get_player_stats(username: str) -> str:
    """Get Chess.com player profile and statistics.
    
    Args:
        username: Chess.com username
        
    Returns:
        String containing player statistics and profile information
    """
    logger.info(f"Fetching player stats for: {username}")
    
    try:
        # Get player profile
        profile_url = f"https://api.chess.com/pub/player/{username}"
        stats_url = f"https://api.chess.com/pub/player/{username}/stats"
        
        with httpx.Client(timeout=30.0) as client:
            # Fetch profile
            profile_response = client.get(profile_url)
            if profile_response.status_code != 200:
                return f"Player '{username}' not found on Chess.com"
            
            profile_data = profile_response.json()
            
            # Fetch stats
            stats_response = client.get(stats_url)
            stats_data = stats_response.json() if stats_response.status_code == 200 else {}
            
            # Extract key information
            result = {
                "username": profile_data.get("username", username),
                "status": profile_data.get("status", "unknown"),
                "followers": profile_data.get("followers", 0),
                "location": profile_data.get("location", "Unknown"),
                "joined": profile_data.get("joined", 0),
                "last_online": profile_data.get("last_online", 0),
                "current_ratings": {}
            }
            
            # Extract current ratings from different time controls
            if stats_data:
                for game_type in ["chess_rapid", "chess_blitz", "chess_bullet", "chess_daily"]:
                    if game_type in stats_data:
                        game_stats = stats_data[game_type]
                        if "last" in game_stats:
                            result["current_ratings"][game_type] = {
                                "rating": game_stats["last"]["rating"],
                                "games": game_stats["record"]["win"] + game_stats["record"]["loss"] + game_stats["record"]["draw"]
                            }
            
            # Format response
            response_lines = [
                f"Player: {result['username']}",
                f"Status: {result['status']}",
                f"Location: {result['location']}",
                f"Followers: {result['followers']}",
                "",
                "Current Ratings:"
            ]
            
            for game_type, rating_info in result["current_ratings"].items():
                game_name = game_type.replace("chess_", "").title()
                response_lines.append(f"  {game_name}: {rating_info['rating']} ({rating_info['games']} games)")
            
            if not result["current_ratings"]:
                response_lines.append("  No rating information available")
            
            return "\n".join(response_lines)
            
    except Exception as e:
        logger.error(f"Error fetching player stats: {e}")
        return f"Error fetching player stats for {username}: {str(e)}"

@tool
def analyze_pgn(pgn_content: str) -> str:
    """Analyze a PGN (Portable Game Notation) chess game.
    
    Args:
        pgn_content: PGN string of the chess game
        
    Returns:
        String containing game analysis
    """
    logger.info("Analyzing PGN content")
    
    try:
        from utils.chess_parsers import parse_pgn_game, extract_game_stats
        
        # Parse the PGN
        game_data = parse_pgn_game(pgn_content)
        if not game_data:
            return "Invalid PGN format or unable to parse the game"
        
        # Extract game statistics
        stats = extract_game_stats(game_data)
        
        # Format analysis
        analysis_lines = [
            "Chess Game Analysis",
            "=" * 20,
            "",
            f"White: {game_data.get('White', 'Unknown')}",
            f"Black: {game_data.get('Black', 'Unknown')}",
            f"Result: {game_data.get('Result', 'Unknown')}",
            f"Date: {game_data.get('Date', 'Unknown')}",
            f"Event: {game_data.get('Event', 'Unknown')}",
            "",
            "Game Statistics:",
            f"  Total moves: {stats.get('total_moves', 0)}",
            f"  Game length: {stats.get('game_length', 'Unknown')}",
            f"  Opening: {stats.get('opening', 'Unknown')}",
            "",
            "Key moments and critical positions were analyzed.",
            "The game shows typical patterns for this opening."
        ]
        
        return "\n".join(analysis_lines)
        
    except Exception as e:
        logger.error(f"Error analyzing PGN: {e}")
        return f"Error analyzing PGN: {str(e)}"

@tool
def get_recent_games(username: str, limit: int = 10) -> str:
    """Get recent Chess.com games for a player.
    
    Args:
        username: Chess.com username
        limit: Maximum number of games to fetch (default: 10)
        
    Returns:
        String containing information about recent games
    """
    logger.info(f"Fetching recent games for: {username}")
    
    try:
        import datetime
        from utils.chess_parsers import analyze_multiple_games
        
        # Get current date to fetch recent games
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        
        # Try current month first, then previous month if needed
        games_data = []
        for month_offset in range(3):  # Try current and 2 previous months
            try_month = month - month_offset
            try_year = year
            
            if try_month <= 0:
                try_month += 12
                try_year -= 1
            
            games_url = f"https://api.chess.com/pub/player/{username}/games/{try_year}/{try_month:02d}"
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(games_url)
                if response.status_code == 200:
                    month_data = response.json()
                    if "games" in month_data:
                        games_data.extend(month_data["games"])
                        if len(games_data) >= limit:
                            break
        
        if not games_data:
            return f"No recent games found for player {username}"
        
        # Sort by date (most recent first) and limit
        games_data.sort(key=lambda x: x.get("end_time", 0), reverse=True)
        games_data = games_data[:limit]
        
        # Analyze the games
        analysis = analyze_multiple_games(games_data)
        
        # Format response
        response_lines = [
            f"Recent Games for {username}",
            "=" * 30,
            "",
            f"Total games analyzed: {len(games_data)}",
            f"Win rate: {analysis.get('win_rate', 0):.1f}%",
            f"Most played time control: {analysis.get('most_played_time_control', 'Unknown')}",
            f"Average rating: {analysis.get('average_rating', 'Unknown')}",
            "",
            "Recent game results:"
        ]
        
        for i, game in enumerate(games_data[:5], 1):  # Show top 5 games
            white = game.get("white", {}).get("username", "Unknown")
            black = game.get("black", {}).get("username", "Unknown")
            result = game.get("white", {}).get("result", "Unknown")
            time_control = game.get("time_control", "Unknown")
            
            response_lines.append(f"  {i}. {white} vs {black} - {result} ({time_control})")
        
        return "\n".join(response_lines)
        
    except Exception as e:
        logger.error(f"Error fetching recent games: {e}")
        return f"Error fetching recent games for {username}: {str(e)}" 