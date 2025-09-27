#!/usr/bin/env python3
"""
Basic Priority Algorithm
Simple rule-based 2048 strategy with fixed move priorities
"""

import sys
from pathlib import Path
from typing import List

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from algorithms.base_algorithm import BaseAlgorithm, AlgorithmMetadata, AlgorithmType

class BasicPriorityAlgorithm(BaseAlgorithm):
    """
    Basic priority-based algorithm

    Uses simple move priority: UP > LEFT > DOWN > RIGHT
    This was our original strategy before heuristic optimization.
    """

    def __init__(self, **kwargs):
        """Initialize with move priorities"""
        super().__init__(**kwargs)

        # Move priority order (can be customized)
        self.move_priority = kwargs.get('move_priority', ["UP", "LEFT", "DOWN", "RIGHT"])

    def _get_metadata(self) -> AlgorithmMetadata:
        """Return algorithm metadata"""
        return AlgorithmMetadata(
            name="Basic Priority",
            version="1.0",
            author="2048 Bot Team",
            description="Simple rule-based strategy using fixed move priorities. Educational baseline algorithm.",
            algorithm_type=AlgorithmType.RULE_BASED,
            parameters={
                'move_priority': ["UP", "LEFT", "DOWN", "RIGHT"]
            },
            performance_baseline=1.8,  # Estimated baseline performance
            training_required=False
        )

    def get_move(self, board_state: List[List[int]]) -> str:
        """Get next move using priority-based selection"""
        # Try moves in priority order
        for move in self.move_priority:
            if self._is_move_valid(board_state, move):
                return move

        # If no moves are valid, return first priority (shouldn't happen in normal gameplay)
        return self.move_priority[0]

    def get_move_scores(self, board_state: List[List[int]]) -> List[float]:
        """Get move scores based on priority and validity"""
        moves = ["UP", "DOWN", "LEFT", "RIGHT"]
        scores = []

        for move in moves:
            if self._is_move_valid(board_state, move):
                # Score based on priority (higher priority = higher score)
                try:
                    priority_index = self.move_priority.index(move)
                    score = 100.0 - (priority_index * 10.0)  # UP=100, LEFT=90, DOWN=80, RIGHT=70
                except ValueError:
                    score = 50.0  # Default score for moves not in priority list
            else:
                score = -999.0  # Invalid move

            scores.append(score)

        return scores

    def _is_move_valid(self, board_state: List[List[int]], move: str) -> bool:
        """Check if a move would change the board state"""
        simulated_board = self._simulate_move(board_state, move)
        return simulated_board is not None and simulated_board != board_state

    def set_move_priority(self, new_priority: List[str]):
        """Update move priority order"""
        valid_moves = ["UP", "DOWN", "LEFT", "RIGHT"]
        if all(move in valid_moves for move in new_priority):
            self.move_priority = new_priority
            self.config['move_priority'] = new_priority
        else:
            raise ValueError("Invalid moves in priority list")

class RandomAlgorithm(BaseAlgorithm):
    """
    Random move algorithm for baseline comparison
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="Random",
            version="1.0",
            author="2048 Bot Team",
            description="Random move selection for baseline comparison. Not recommended for actual gameplay.",
            algorithm_type=AlgorithmType.RULE_BASED,
            parameters={},
            performance_baseline=0.5,  # Very low baseline
            training_required=False
        )

    def get_move(self, board_state: List[List[int]]) -> str:
        """Get random valid move"""
        import random

        moves = ["UP", "DOWN", "LEFT", "RIGHT"]
        valid_moves = [move for move in moves if self._is_move_valid(board_state, move)]

        if valid_moves:
            return random.choice(valid_moves)
        else:
            return random.choice(moves)  # Fallback

    def _is_move_valid(self, board_state: List[List[int]], move: str) -> bool:
        """Check if move is valid"""
        simulated_board = self._simulate_move(board_state, move)
        return simulated_board is not None and simulated_board != board_state

if __name__ == "__main__":
    # Test basic algorithms
    print("🧪 Basic Algorithm Test")

    # Test priority algorithm
    priority_algo = BasicPriorityAlgorithm()
    print(f"Priority Algorithm: {priority_algo.metadata.name}")

    test_board = [
        [2, 0, 0, 0],
        [4, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    move = priority_algo.get_move(test_board)
    scores = priority_algo.get_move_scores(test_board)

    print(f"Recommended move: {move}")
    print(f"Move scores: UP={scores[0]}, DOWN={scores[1]}, LEFT={scores[2]}, RIGHT={scores[3]}")

    # Test random algorithm
    random_algo = RandomAlgorithm()
    print(f"\nRandom Algorithm: {random_algo.metadata.name}")

    random_move = random_algo.get_move(test_board)
    print(f"Random move: {random_move}")

    print("✅ Basic algorithm test completed")