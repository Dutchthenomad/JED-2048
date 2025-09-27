#!/usr/bin/env python3
"""
Base Algorithm Interface
Abstract base class for all 2048 playing algorithms
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time

class Move(Enum):
    """Valid 2048 moves"""
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

class AlgorithmType(Enum):
    """Algorithm categories"""
    HEURISTIC = "heuristic"
    RULE_BASED = "rule_based"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    DEEP_LEARNING = "deep_learning"
    MINIMAX = "minimax"
    MONTE_CARLO = "monte_carlo"
    STUDENT_SUBMISSION = "student_submission"

@dataclass
class AlgorithmMetadata:
    """Metadata for algorithm registration"""
    name: str
    version: str
    author: str
    description: str
    algorithm_type: AlgorithmType
    parameters: Dict[str, Any]
    performance_baseline: Optional[float] = None
    training_required: bool = False

class BaseAlgorithm(ABC):
    """
    Abstract base class for all 2048 playing algorithms

    This interface ensures consistent algorithm behavior and enables
    easy swapping between different AI approaches.
    """

    def __init__(self, **kwargs):
        """
        Initialize algorithm with configuration parameters

        Args:
            **kwargs: Algorithm-specific configuration
        """
        self.metadata = self._get_metadata()
        self.config = kwargs
        self.stats = {
            'games_played': 0,
            'total_score': 0,
            'total_moves': 0,
            'highest_tile': 0,
            'average_efficiency': 0.0
        }
        self.is_trained = False

    @abstractmethod
    def _get_metadata(self) -> AlgorithmMetadata:
        """Return algorithm metadata"""
        pass

    @abstractmethod
    def get_move(self, board_state: List[List[int]]) -> str:
        """
        Get next move for given board state

        Args:
            board_state: 4x4 board representation (0 = empty)

        Returns:
            Move as string: "UP", "DOWN", "LEFT", "RIGHT"
        """
        pass

    def get_move_scores(self, board_state: List[List[int]]) -> List[float]:
        """
        Get scores for all possible moves

        Args:
            board_state: 4x4 board representation

        Returns:
            List of scores for [UP, DOWN, LEFT, RIGHT]
        """
        # Default implementation - subclasses can override for more detailed scoring
        moves = ["UP", "DOWN", "LEFT", "RIGHT"]
        scores = []

        for move in moves:
            try:
                # Simple simulation-based scoring
                simulated_board = self._simulate_move(board_state, move)
                if simulated_board:
                    score = self._evaluate_board_simple(simulated_board)
                else:
                    score = -999.0  # Invalid move
                scores.append(score)
            except Exception:
                scores.append(-999.0)

        return scores

    def update_stats(self, game_result: Dict[str, Any]):
        """Update algorithm performance statistics"""
        self.stats['games_played'] += 1
        self.stats['total_score'] += game_result.get('final_score', 0)
        self.stats['total_moves'] += game_result.get('moves_completed', 0)
        self.stats['highest_tile'] = max(
            self.stats['highest_tile'],
            game_result.get('highest_tile', 0)
        )

        # Calculate efficiency
        if self.stats['total_moves'] > 0:
            self.stats['average_efficiency'] = self.stats['total_score'] / self.stats['total_moves']

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        return {
            'metadata': {
                'name': self.metadata.name,
                'version': self.metadata.version,
                'author': self.metadata.author,
                'type': self.metadata.algorithm_type.value
            },
            'statistics': self.stats.copy(),
            'configuration': self.config.copy(),
            'is_trained': self.is_trained,
            'timestamp': time.time()
        }

    def save_model(self, filepath: str) -> bool:
        """
        Save trained model (for ML algorithms)

        Args:
            filepath: Path to save model

        Returns:
            True if successful, False otherwise
        """
        # Default implementation for non-trainable algorithms
        return False

    def load_model(self, filepath: str) -> bool:
        """
        Load trained model (for ML algorithms)

        Args:
            filepath: Path to load model from

        Returns:
            True if successful, False otherwise
        """
        # Default implementation for non-trainable algorithms
        return False

    def train(self, training_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Train algorithm (for ML algorithms)

        Args:
            training_data: Training data specific to algorithm
            **kwargs: Training configuration

        Returns:
            Training results and metrics
        """
        # Default implementation for non-trainable algorithms
        return {"error": "This algorithm does not support training"}

    def reset(self):
        """Reset algorithm state (useful for stateful algorithms)"""
        pass

    def _simulate_move(self, board: List[List[int]], move: str) -> Optional[List[List[int]]]:
        """
        Simulate a move and return resulting board
        Simple implementation - can be overridden by subclasses
        """
        import copy
        new_board = copy.deepcopy(board)

        if move == "LEFT":
            moved = self._move_left(new_board)
        elif move == "RIGHT":
            moved = self._move_right(new_board)
        elif move == "UP":
            moved = self._move_up(new_board)
        elif move == "DOWN":
            moved = self._move_down(new_board)
        else:
            return None

        return new_board if moved else None

    def _move_left(self, board: List[List[int]]) -> bool:
        """Move tiles left, return True if board changed"""
        moved = False
        for row in range(4):
            # Extract non-zero tiles
            tiles = [board[row][col] for col in range(4) if board[row][col] != 0]

            # Merge adjacent equal tiles
            merged = []
            i = 0
            while i < len(tiles):
                if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
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
        """Move tiles right"""
        for row in range(4):
            board[row].reverse()
        moved = self._move_left(board)
        for row in range(4):
            board[row].reverse()
        return moved

    def _move_up(self, board: List[List[int]]) -> bool:
        """Move tiles up"""
        self._transpose(board)
        moved = self._move_left(board)
        self._transpose(board)
        return moved

    def _move_down(self, board: List[List[int]]) -> bool:
        """Move tiles down"""
        self._transpose(board)
        moved = self._move_right(board)
        self._transpose(board)
        return moved

    def _transpose(self, board: List[List[int]]):
        """Transpose board in place"""
        for i in range(4):
            for j in range(i + 1, 4):
                board[i][j], board[j][i] = board[j][i], board[i][j]

    def _evaluate_board_simple(self, board: List[List[int]]) -> float:
        """Simple board evaluation for default move scoring"""
        # Count empty tiles
        empty_tiles = sum(1 for row in board for tile in row if tile == 0)

        # Get max tile
        max_tile = max(max(row) for row in board)

        # Simple scoring: prefer more empty tiles and higher max tile
        return empty_tiles * 10.0 + max_tile * 0.1

# Utility functions for algorithm development
def validate_board_state(board_state: List[List[int]]) -> bool:
    """Validate that board state is properly formatted"""
    if not isinstance(board_state, list) or len(board_state) != 4:
        return False

    for row in board_state:
        if not isinstance(row, list) or len(row) != 4:
            return False
        for tile in row:
            if not isinstance(tile, int) or tile < 0:
                return False

    return True

def board_to_string(board_state: List[List[int]]) -> str:
    """Convert board to readable string representation"""
    lines = []
    for row in board_state:
        line = " | ".join(f"{tile:4d}" if tile > 0 else "    " for tile in row)
        lines.append(f"| {line} |")
    return "\n".join(lines)

if __name__ == "__main__":
    # Example usage and testing
    print("🧪 Base Algorithm Interface Test")

    # Test board validation
    valid_board = [[0, 0, 2, 0], [0, 0, 0, 0], [0, 4, 0, 0], [0, 0, 0, 0]]
    invalid_board = [[0, 0], [0, 0]]

    print(f"Valid board test: {validate_board_state(valid_board)}")
    print(f"Invalid board test: {validate_board_state(invalid_board)}")

    print("\nBoard visualization:")
    print(board_to_string(valid_board))