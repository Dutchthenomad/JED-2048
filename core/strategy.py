"""
Basic 2048 Strategy System
Simple heuristic-based move selection with comprehensive testing support.

Focuses on proven fundamentals:
- Corner strategy (keep highest tile in corner)
- Empty tile maximization
- Merge opportunity detection
- Monotonic sequence building
"""

import copy
from typing import List, Dict, Tuple, Optional
from enum import Enum
import logging

class Move(Enum):
    """Valid 2048 moves"""
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

class BasicStrategy:
    """
    Simple heuristic-based 2048 strategy
    Uses proven fundamentals with clear, testable scoring
    """

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(__name__)

        # Optimized heuristic weights (tuned for maximum performance)
        self.weights = {
            'empty_tiles': 150.0,      # +50% empty space focus
            'merge_potential': 100.0,  # Double merge priority
            'corner_bonus': 250.0,     # +25% corner strategy
            'monotonicity': 75.0,      # +150% monotonicity emphasis
            'max_tile_value': 15.0     # +50% tile value importance
        }

    def evaluate_board(self, board: List[List[int]]) -> float:
        """
        Evaluate board state using simple heuristics
        Higher score = better position
        """
        if not self._is_valid_board(board):
            return -1000.0  # Invalid board

        score = 0.0

        # Count empty tiles
        empty_count = self._count_empty_tiles(board)
        score += empty_count * self.weights['empty_tiles']

        # Evaluate merge potential
        merge_score = self._evaluate_merge_potential(board)
        score += merge_score * self.weights['merge_potential']

        # Corner bonus (prefer highest tile in corner)
        corner_score = self._evaluate_corner_strategy(board)
        score += corner_score * self.weights['corner_bonus']

        # Monotonicity bonus
        monotonic_score = self._evaluate_monotonicity(board)
        score += monotonic_score * self.weights['monotonicity']

        # Max tile bonus
        max_tile = self._get_max_tile(board)
        score += max_tile * self.weights['max_tile_value']

        if self.debug_mode:
            self.logger.info(f"Board evaluation: empty={empty_count}, merge={merge_score:.1f}, corner={corner_score:.1f}, mono={monotonic_score:.1f}, max={max_tile}, total={score:.1f}")

        return score

    def get_best_move(self, board: List[List[int]]) -> Tuple[Move, Dict]:
        """
        Determine best move for given board state
        Returns (best_move, analysis_data)
        """
        if not self._is_valid_board(board):
            return Move.UP, {"error": "Invalid board state"}

        move_scores = {}
        move_analysis = {}

        # Evaluate each possible move
        for move in Move:
            # Simulate the move
            new_board = self._simulate_move(board, move)

            if new_board is None:
                # Move not possible
                move_scores[move] = -999.0
                move_analysis[move] = {"possible": False, "reason": "No tiles can move"}
            else:
                # Evaluate resulting board
                score = self.evaluate_board(new_board)
                move_scores[move] = score
                move_analysis[move] = {
                    "possible": True,
                    "score": score,
                    "resulting_board": new_board,
                    "empty_tiles": self._count_empty_tiles(new_board)
                }

        # Find best move
        best_move = max(move_scores.keys(), key=lambda m: move_scores[m])
        best_score = move_scores[best_move]

        analysis = {
            "chosen_move": best_move,
            "best_score": best_score,
            "all_scores": move_scores,
            "move_analysis": move_analysis,
            "reasoning": self._explain_move_choice(best_move, move_analysis)
        }

        return best_move, analysis

    def get_move_scores(self, board: List[List[int]]) -> List[float]:
        """
        Get scores for all possible moves using advanced heuristic evaluation
        Returns list of scores in order: [UP, DOWN, LEFT, RIGHT]
        """
        if not self._is_valid_board(board):
            return [-999.0, -999.0, -999.0, -999.0]

        directions = ["UP", "DOWN", "LEFT", "RIGHT"]
        scores = []

        for move_str in directions:
            move_enum = Move(move_str)
            new_board = self._simulate_move(board, move_enum)

            if new_board is not None:
                # Move is valid - evaluate the resulting board using full heuristics
                board_score = self.evaluate_board(new_board)
                scores.append(board_score)
            else:
                # Move is invalid - very low score
                scores.append(-999.0)

        return scores

    def recommend_move(self, board: List[List[int]]) -> str:
        """
        Recommend best move (interface expected by complete bot)
        Returns move as string: "UP", "DOWN", "LEFT", "RIGHT"
        """
        scores = self.get_move_scores(board)
        directions = ["UP", "DOWN", "LEFT", "RIGHT"]

        # Find index of highest scoring move
        best_index = max(range(len(scores)), key=lambda i: scores[i])
        return directions[best_index]

    def _simulate_move(self, board: List[List[int]], move: Move) -> Optional[List[List[int]]]:
        """
        Simulate a move and return resulting board state
        Returns None if move is not possible
        """
        new_board = copy.deepcopy(board)
        moved = False

        if move == Move.LEFT:
            moved = self._move_left(new_board)
        elif move == Move.RIGHT:
            moved = self._move_right(new_board)
        elif move == Move.UP:
            moved = self._move_up(new_board)
        elif move == Move.DOWN:
            moved = self._move_down(new_board)

        return new_board if moved else None

    def _move_left(self, board: List[List[int]]) -> bool:
        """Move all tiles left, return True if any tiles moved"""
        moved = False
        for row in range(4):
            # Extract non-zero tiles
            tiles = [board[row][col] for col in range(4) if board[row][col] != 0]

            # Merge adjacent equal tiles
            merged = []
            i = 0
            while i < len(tiles):
                if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
                    # Merge tiles
                    merged.append(tiles[i] * 2)
                    i += 2
                else:
                    merged.append(tiles[i])
                    i += 1

            # Pad with zeros
            merged.extend([0] * (4 - len(merged)))

            # Check if anything changed
            for col in range(4):
                if board[row][col] != merged[col]:
                    moved = True
                board[row][col] = merged[col]

        return moved

    def _move_right(self, board: List[List[int]]) -> bool:
        """Move all tiles right"""
        # Reverse, move left, reverse back
        for row in range(4):
            board[row].reverse()
        moved = self._move_left(board)
        for row in range(4):
            board[row].reverse()
        return moved

    def _move_up(self, board: List[List[int]]) -> bool:
        """Move all tiles up"""
        # Transpose, move left, transpose back
        self._transpose(board)
        moved = self._move_left(board)
        self._transpose(board)
        return moved

    def _move_down(self, board: List[List[int]]) -> bool:
        """Move all tiles down"""
        # Transpose, move right, transpose back
        self._transpose(board)
        moved = self._move_right(board)
        self._transpose(board)
        return moved

    def _transpose(self, board: List[List[int]]) -> None:
        """Transpose board in place"""
        for i in range(4):
            for j in range(i + 1, 4):
                board[i][j], board[j][i] = board[j][i], board[i][j]

    def _count_empty_tiles(self, board: List[List[int]]) -> int:
        """Count number of empty tiles"""
        return sum(1 for row in board for tile in row if tile == 0)

    def _evaluate_merge_potential(self, board: List[List[int]]) -> float:
        """Evaluate potential for merges"""
        merge_count = 0

        # Check horizontal merges
        for row in range(4):
            for col in range(3):
                if board[row][col] != 0 and board[row][col] == board[row][col + 1]:
                    merge_count += 1

        # Check vertical merges
        for row in range(3):
            for col in range(4):
                if board[row][col] != 0 and board[row][col] == board[row + 1][col]:
                    merge_count += 1

        return float(merge_count)

    def _evaluate_corner_strategy(self, board: List[List[int]]) -> float:
        """Evaluate corner strategy (highest tile in corner)"""
        max_tile = self._get_max_tile(board)
        if max_tile == 0:
            return 0.0

        # Check if max tile is in a corner
        corners = [board[0][0], board[0][3], board[3][0], board[3][3]]
        if max_tile in corners:
            return 1.0
        else:
            return 0.0

    def _evaluate_monotonicity(self, board: List[List[int]]) -> float:
        """Evaluate monotonic sequences"""
        score = 0.0

        # Check rows for monotonic sequences
        for row in range(4):
            non_zero = [board[row][col] for col in range(4) if board[row][col] != 0]
            if len(non_zero) > 1:
                if non_zero == sorted(non_zero, reverse=True):
                    score += 1.0
                elif non_zero == sorted(non_zero):
                    score += 0.5

        # Check columns for monotonic sequences
        for col in range(4):
            non_zero = [board[row][col] for row in range(4) if board[row][col] != 0]
            if len(non_zero) > 1:
                if non_zero == sorted(non_zero, reverse=True):
                    score += 1.0
                elif non_zero == sorted(non_zero):
                    score += 0.5

        return score

    def _get_max_tile(self, board: List[List[int]]) -> int:
        """Get highest tile value on board"""
        return max(max(row) for row in board)

    def _is_valid_board(self, board: List[List[int]]) -> bool:
        """Validate board format"""
        if not board or len(board) != 4:
            return False
        for row in board:
            if not row or len(row) != 4:
                return False
            for tile in row:
                if not isinstance(tile, int) or tile < 0:
                    return False
        return True

    def _explain_move_choice(self, move: Move, analysis: Dict) -> str:
        """Generate human-readable explanation of move choice"""
        if not analysis[move]["possible"]:
            return f"Move {move.value} chosen but not possible"

        score = analysis[move]["score"]
        empty_tiles = analysis[move]["empty_tiles"]

        explanation = f"Move {move.value} chosen (score: {score:.1f}) - "
        explanation += f"results in {empty_tiles} empty tiles"

        return explanation