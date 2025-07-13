import chess.pgn
import chess
from io import StringIO
from typing import Dict, List, Optional, Any
from backend.utils.logging import get_logger

logger = get_logger(__name__)

def parse_pgn_game(pgn_string: str) -> Optional[chess.pgn.Game]:
    """Parse a PGN string into a chess game object"""
    try:
        game = chess.pgn.read_game(StringIO(pgn_string))
        return game
    except Exception as e:
        logger.error(f"Failed to parse PGN: {e}")
        return None

def extract_game_stats(game: chess.pgn.Game) -> Dict[str, Any]:
    """Extract comprehensive statistics from a chess game"""
    if not game:
        return {}
    
    try:
        # Basic game information
        stats = {
            "white_player": game.headers.get("White", "Unknown"),
            "black_player": game.headers.get("Black", "Unknown"),
            "result": game.headers.get("Result", "*"),
            "date": game.headers.get("Date", "Unknown"),
            "event": game.headers.get("Event", "Unknown"),
            "site": game.headers.get("Site", "Unknown"),
            "round": game.headers.get("Round", "Unknown"),
            "time_control": game.headers.get("TimeControl", "Unknown"),
            "eco": game.headers.get("ECO", "Unknown"),
            "opening": game.headers.get("Opening", "Unknown")
        }
        
        # Count moves
        moves = list(game.mainline_moves())
        stats["total_moves"] = len(moves)
        stats["total_plies"] = len(moves)
        
        # Analyze positions for tactical complexity
        board = game.board()
        captures = 0
        checks = 0
        
        for move in moves:
            if board.is_capture(move):
                captures += 1
            board.push(move)
            if board.is_check():
                checks += 1
        
        stats["captures"] = captures
        stats["checks"] = checks
        stats["tactical_complexity"] = (captures + checks) / max(len(moves), 1)
        
        # Game length classification
        if len(moves) < 40:
            stats["game_length"] = "short"
        elif len(moves) < 80:
            stats["game_length"] = "medium"
        else:
            stats["game_length"] = "long"
            
        return stats
        
    except Exception as e:
        logger.error(f"Failed to extract game stats: {e}")
        return {"error": str(e)}

def get_opening_classification(game: chess.pgn.Game) -> Dict[str, str]:
    """Extract opening information and classify opening family"""
    opening_info = {
        "eco": game.headers.get("ECO", "Unknown"),
        "opening": game.headers.get("Opening", "Unknown"),
        "variation": game.headers.get("Variation", "Unknown")
    }
    
    # Basic opening family classification
    opening_name = opening_info["opening"].lower()
    
    if "sicilian" in opening_name:
        opening_info["family"] = "Sicilian Defense"
    elif "french" in opening_name:
        opening_info["family"] = "French Defense"
    elif "caro-kann" in opening_name:
        opening_info["family"] = "Caro-Kann Defense"
    elif "queen's gambit" in opening_name:
        opening_info["family"] = "Queen's Gambit"
    elif "king's indian" in opening_name:
        opening_info["family"] = "King's Indian Defense"
    elif "english" in opening_name:
        opening_info["family"] = "English Opening"
    elif "ruy lopez" in opening_name or "spanish" in opening_name:
        opening_info["family"] = "Ruy Lopez"
    else:
        opening_info["family"] = "Other"
    
    return opening_info

def analyze_multiple_games(pgn_list: List[str]) -> Dict[str, Any]:
    """Analyze multiple games and provide aggregate statistics"""
    if not pgn_list:
        return {"error": "No games provided"}
    
    all_stats = []
    opening_counts = {}
    results = {"1-0": 0, "0-1": 0, "1/2-1/2": 0, "*": 0}
    
    for pgn in pgn_list:
        game = parse_pgn_game(pgn)
        if game:
            stats = extract_game_stats(game)
            all_stats.append(stats)
            
            # Count openings
            opening = stats.get("opening", "Unknown")
            opening_counts[opening] = opening_counts.get(opening, 0) + 1
            
            # Count results
            result = stats.get("result", "*")
            if result in results:
                results[result] += 1
    
    if not all_stats:
        return {"error": "No valid games found"}
    
    # Calculate aggregate statistics
    total_games = len(all_stats)
    avg_moves = sum(s.get("total_moves", 0) for s in all_stats) / total_games
    avg_complexity = sum(s.get("tactical_complexity", 0) for s in all_stats) / total_games
    
    return {
        "total_games": total_games,
        "average_moves": round(avg_moves, 1),
        "average_tactical_complexity": round(avg_complexity, 3),
        "most_common_openings": dict(sorted(opening_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
        "results_distribution": results,
        "win_percentage": round((results["1-0"] / total_games) * 100, 1) if total_games > 0 else 0
    } 