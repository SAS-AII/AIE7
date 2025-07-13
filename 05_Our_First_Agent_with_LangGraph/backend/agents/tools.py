import httpx
import json
from typing import Dict, List, Any, Optional
from langchain.tools import BaseTool
from pydantic import Field

from utils.logging import get_logger
from utils.chess_parsers import parse_pgn_game, extract_game_stats, analyze_multiple_games

logger = get_logger(__name__)

class ChessComPlayerTool(BaseTool):
    """Tool to fetch Chess.com player profile and statistics"""
    
    name: str = "chess_com_player"
    description: str = "Get Chess.com player profile, stats, and basic information. Input should be a Chess.com username."
    
    def _run(self, username: str) -> str:
        """Fetch player profile and stats from Chess.com API"""
        logger.info(f"Fetching player data for: {username}")
        
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
                rating_categories = ["chess_rapid", "chess_blitz", "chess_bullet", "chess_daily"]
                for category in rating_categories:
                    if category in stats_data and "last" in stats_data[category]:
                        result["current_ratings"][category.replace("chess_", "")] = stats_data[category]["last"]["rating"]
                
                logger.info(f"Successfully fetched player data for {username}")
                return json.dumps(result, indent=2)
                
        except Exception as e:
            error_msg = f"Error fetching player data: {str(e)}"
            logger.error(error_msg)
            return error_msg

class ChessComGameAnalyzerTool(BaseTool):
    """Tool to download and analyze Chess.com games or analyze provided PGN"""
    
    name: str = "chess_com_game_analyzer"
    description: str = "Download Chess.com games and analyze them, or analyze provided PGN games. Input: 'username/YYYY/MM' for downloads or raw PGN text for analysis."
    
    def _run(self, input_text: str) -> str:
        """Analyze games from Chess.com or provided PGN"""
        logger.info(f"Analyzing games: {input_text[:100]}...")
        
        try:
            # Check if input is PGN content or download request
            if self._is_pgn_content(input_text):
                return self._analyze_pgn_content(input_text)
            else:
                return self._download_and_analyze_games(input_text)
                
        except Exception as e:
            error_msg = f"Error analyzing games: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _is_pgn_content(self, text: str) -> bool:
        """Check if text contains PGN game data"""
        return ("1." in text and any(move in text for move in ["e4", "d4", "Nf3", "c4"])) or "[Event" in text
    
    def _analyze_pgn_content(self, pgn_text: str) -> str:
        """Analyze provided PGN game content"""
        game = parse_pgn_game(pgn_text)
        if not game:
            return "Failed to parse PGN content"
        
        stats = extract_game_stats(game)
        analysis = {
            "game_analysis": stats,
            "type": "single_pgn_analysis"
        }
        
        return json.dumps(analysis, indent=2)
    
    def _download_and_analyze_games(self, query: str) -> str:
        """Download games from Chess.com and analyze them"""
        # Parse query format: username/year/month or just username
        parts = query.strip().split("/")
        
        if len(parts) == 1:
            # Just username, get recent games
            username = parts[0]
            return self._get_recent_games(username)
        elif len(parts) == 3:
            # username/year/month format
            username, year, month = parts
            return self._get_monthly_games(username, year, month)
        else:
            return "Invalid query format. Use 'username' or 'username/YYYY/MM'"
    
    def _get_recent_games(self, username: str, limit: int = 10) -> str:
        """Get and analyze recent games for a user"""
        try:
            with httpx.Client(timeout=30.0) as client:
                # Get list of available archives
                archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
                archives_response = client.get(archives_url)
                
                if archives_response.status_code != 200:
                    return f"Could not fetch game archives for {username}"
                
                archives = archives_response.json().get("archives", [])
                if not archives:
                    return f"No game archives found for {username}"
                
                # Get games from most recent archive
                recent_archive = archives[-1]  # Most recent
                games_response = client.get(recent_archive)
                
                if games_response.status_code != 200:
                    return f"Could not fetch games from recent archive"
                
                games_data = games_response.json().get("games", [])
                if not games_data:
                    return f"No games found in recent archive"
                
                # Analyze recent games (limit to specified number)
                recent_games = games_data[-limit:] if len(games_data) > limit else games_data
                pgn_list = [game.get("pgn", "") for game in recent_games if game.get("pgn")]
                
                if not pgn_list:
                    return "No PGN data found in recent games"
                
                analysis = analyze_multiple_games(pgn_list)
                analysis["type"] = "recent_games_analysis"
                analysis["username"] = username
                analysis["games_analyzed"] = len(pgn_list)
                
                return json.dumps(analysis, indent=2)
                
        except Exception as e:
            return f"Error fetching recent games: {str(e)}"
    
    def _get_monthly_games(self, username: str, year: str, month: str) -> str:
        """Get and analyze games from a specific month"""
        try:
            with httpx.Client(timeout=30.0) as client:
                games_url = f"https://api.chess.com/pub/player/{username}/games/{year}/{month}"
                games_response = client.get(games_url)
                
                if games_response.status_code != 200:
                    return f"Could not fetch games for {username} in {year}/{month}"
                
                games_data = games_response.json().get("games", [])
                if not games_data:
                    return f"No games found for {username} in {year}/{month}"
                
                pgn_list = [game.get("pgn", "") for game in games_data if game.get("pgn")]
                
                if not pgn_list:
                    return "No PGN data found in monthly games"
                
                analysis = analyze_multiple_games(pgn_list)
                analysis["type"] = "monthly_games_analysis"
                analysis["username"] = username
                analysis["period"] = f"{year}/{month}"
                analysis["games_analyzed"] = len(pgn_list)
                
                return json.dumps(analysis, indent=2)
                
        except Exception as e:
            return f"Error fetching monthly games: {str(e)}"

class ChessComRatingTrackerTool(BaseTool):
    """Tool to track rating changes and performance trends"""
    
    name: str = "chess_com_rating_tracker"
    description: str = "Track Chess.com rating changes, performance trends, and opening repertoire analysis. Input should be a Chess.com username."
    
    def _run(self, username: str) -> str:
        """Track rating trends and analyze performance patterns"""
        logger.info(f"Tracking rating trends for: {username}")
        
        try:
            with httpx.Client(timeout=30.0) as client:
                # Get player stats
                stats_url = f"https://api.chess.com/pub/player/{username}/stats"
                stats_response = client.get(stats_url)
                
                if stats_response.status_code != 200:
                    return f"Could not fetch stats for {username}"
                
                stats_data = stats_response.json()
                
                # Analyze rating data across different time controls
                rating_analysis = self._analyze_ratings(stats_data)
                
                # Get recent games for opening analysis
                archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
                archives_response = client.get(archives_url)
                
                opening_analysis = {}
                if archives_response.status_code == 200:
                    archives = archives_response.json().get("archives", [])
                    if archives:
                        # Analyze openings from recent archive
                        recent_archive = archives[-1]
                        games_response = client.get(recent_archive)
                        
                        if games_response.status_code == 200:
                            games_data = games_response.json().get("games", [])
                            opening_analysis = self._analyze_openings(games_data)
                
                result = {
                    "username": username,
                    "rating_analysis": rating_analysis,
                    "opening_repertoire": opening_analysis,
                    "type": "rating_trend_analysis"
                }
                
                logger.info(f"Successfully analyzed rating trends for {username}")
                return json.dumps(result, indent=2)
                
        except Exception as e:
            error_msg = f"Error tracking ratings: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _analyze_ratings(self, stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze rating data across time controls"""
        analysis = {}
        
        time_controls = ["chess_rapid", "chess_blitz", "chess_bullet", "chess_daily"]
        
        for control in time_controls:
            if control in stats_data:
                control_data = stats_data[control]
                control_name = control.replace("chess_", "")
                
                analysis[control_name] = {
                    "current_rating": control_data.get("last", {}).get("rating", 0),
                    "best_rating": control_data.get("best", {}).get("rating", 0),
                    "games_played": self._calculate_total_games(control_data.get("record", {})),
                    "win_rate": self._calculate_win_rate(control_data.get("record", {}))
                }
        
        return analysis
    
    def _calculate_total_games(self, record: Dict[str, Any]) -> int:
        """Calculate total games from record"""
        return record.get("win", 0) + record.get("loss", 0) + record.get("draw", 0)
    
    def _calculate_win_rate(self, record: Dict[str, Any]) -> float:
        """Calculate win rate percentage"""
        total = self._calculate_total_games(record)
        if total == 0:
            return 0.0
        return round((record.get("win", 0) / total) * 100, 1)
    
    def _analyze_openings(self, games_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze opening repertoire from games data"""
        white_openings = {}
        black_openings = {}
        
        for game in games_data:
            white_player = game.get("white", {}).get("username", "")
            black_player = game.get("black", {}).get("username", "")
            
            # Extract opening from game data or PGN
            opening = "Unknown"
            if "eco" in game:
                # Use ECO code if available
                eco_url = game["eco"]
                if eco_url:
                    # Extract opening name from URL (simplified)
                    opening = eco_url.split("/")[-1].replace("-", " ").title()
            
            # Categorize by color played
            if white_player and "white" in str(game.get("white", {})):
                white_openings[opening] = white_openings.get(opening, 0) + 1
            if black_player and "black" in str(game.get("black", {})):
                black_openings[opening] = black_openings.get(opening, 0) + 1
        
        return {
            "as_white": dict(sorted(white_openings.items(), key=lambda x: x[1], reverse=True)[:5]),
            "as_black": dict(sorted(black_openings.items(), key=lambda x: x[1], reverse=True)[:5]),
            "total_white_games": sum(white_openings.values()),
            "total_black_games": sum(black_openings.values())
        } 