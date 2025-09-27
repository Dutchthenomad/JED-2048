#!/usr/bin/env python3
"""
Enhanced Heuristic Algorithm
Advanced heuristic-based 2048 strategy with optimized weights
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from algorithms.base_algorithm import BaseAlgorithm, AlgorithmMetadata, AlgorithmType
from core.strategy import BasicStrategy

class EnhancedHeuristicAlgorithm(BaseAlgorithm):
    """
    Enhanced heuristic algorithm using optimized weights

    This algorithm represents our current best-performing strategy
    with tuned weights from Phase 2B optimization.
    """

    def __init__(self, **kwargs):
        """Initialize with optimized heuristic weights"""
        super().__init__(**kwargs)

        # Use optimized weights from Phase 2B
        weights = kwargs.get('weights', {
            'empty_tiles': 150.0,      # +50% empty space focus
            'merge_potential': 100.0,  # Double merge priority
            'corner_bonus': 250.0,     # +25% corner strategy
            'monotonicity': 75.0,      # +150% monotonicity emphasis
            'max_tile_value': 15.0     # +50% tile value importance
        })

        # Initialize the underlying strategy engine
        self.strategy = BasicStrategy()
        self.strategy.weights = weights

        # Store weights in config
        self.config['weights'] = weights

    def _get_metadata(self) -> AlgorithmMetadata:
        """Return algorithm metadata"""
        return AlgorithmMetadata(
            name="Enhanced Heuristic",
            version="2.1",
            author="2048 Bot Team",
            description="Optimized heuristic algorithm with corner strategy, monotonicity, and merge detection. Achieved 2.36 points/move efficiency.",
            algorithm_type=AlgorithmType.HEURISTIC,
            parameters={
                'empty_tiles_weight': 150.0,
                'merge_potential_weight': 100.0,
                'corner_bonus_weight': 250.0,
                'monotonicity_weight': 75.0,
                'max_tile_value_weight': 15.0
            },
            performance_baseline=2.36,  # Our measured efficiency
            training_required=False
        )

    def get_move(self, board_state: List[List[int]]) -> str:
        """Get next move using enhanced heuristic strategy"""
        try:
            # Use the proven strategy engine
            move = self.strategy.recommend_move(board_state)
            return move
        except Exception as e:
            # Fallback to simple heuristic if strategy fails
            self.logger.warning(f"Strategy failed, using fallback: {e}")
            return self._fallback_move(board_state)

    def get_move_scores(self, board_state: List[List[int]]) -> List[float]:
        """Get detailed move scores using heuristic evaluation"""
        try:
            return self.strategy.get_move_scores(board_state)
        except Exception:
            # Fallback to parent implementation
            return super().get_move_scores(board_state)

    def _fallback_move(self, board_state: List[List[int]]) -> str:
        """Simple fallback move selection"""
        # Priority order: UP > LEFT > DOWN > RIGHT
        moves = ["UP", "LEFT", "DOWN", "RIGHT"]

        for move in moves:
            if self._simulate_move(board_state, move) is not None:
                return move

        return "UP"  # Default fallback

    def get_strategy_explanation(self, board_state: List[List[int]]) -> Dict[str, Any]:
        """Get detailed explanation of strategy decision"""
        try:
            move, analysis = self.strategy.get_best_move(board_state)

            return {
                'recommended_move': move.value,
                'reasoning': analysis.get('reasoning', ''),
                'all_move_scores': analysis.get('all_scores', {}),
                'best_score': analysis.get('best_score', 0),
                'heuristic_breakdown': self._get_heuristic_breakdown(board_state)
            }
        except Exception as e:
            return {
                'recommended_move': self.get_move(board_state),
                'reasoning': f"Fallback due to error: {e}",
                'error': str(e)
            }

    def _get_heuristic_breakdown(self, board_state: List[List[int]]) -> Dict[str, float]:
        """Break down heuristic scores for educational purposes"""
        try:
            empty_count = self.strategy._count_empty_tiles(board_state)
            merge_score = self.strategy._evaluate_merge_potential(board_state)
            corner_score = self.strategy._evaluate_corner_strategy(board_state)
            mono_score = self.strategy._evaluate_monotonicity(board_state)
            max_tile = self.strategy._get_max_tile(board_state)

            return {
                'empty_tiles': {
                    'raw_value': empty_count,
                    'weight': self.strategy.weights['empty_tiles'],
                    'weighted_score': empty_count * self.strategy.weights['empty_tiles']
                },
                'merge_potential': {
                    'raw_value': merge_score,
                    'weight': self.strategy.weights['merge_potential'],
                    'weighted_score': merge_score * self.strategy.weights['merge_potential']
                },
                'corner_bonus': {
                    'raw_value': corner_score,
                    'weight': self.strategy.weights['corner_bonus'],
                    'weighted_score': corner_score * self.strategy.weights['corner_bonus']
                },
                'monotonicity': {
                    'raw_value': mono_score,
                    'weight': self.strategy.weights['monotonicity'],
                    'weighted_score': mono_score * self.strategy.weights['monotonicity']
                },
                'max_tile_value': {
                    'raw_value': max_tile,
                    'weight': self.strategy.weights['max_tile_value'],
                    'weighted_score': max_tile * self.strategy.weights['max_tile_value']
                }
            }
        except Exception:
            return {}

    def configure_weights(self, new_weights: Dict[str, float]):
        """Update heuristic weights (useful for experimentation)"""
        self.strategy.weights.update(new_weights)
        self.config['weights'].update(new_weights)

if __name__ == "__main__":
    # Test the enhanced heuristic algorithm
    print("🧪 Enhanced Heuristic Algorithm Test")

    algorithm = EnhancedHeuristicAlgorithm()

    # Test metadata
    metadata = algorithm.metadata
    print(f"Algorithm: {metadata.name} v{metadata.version}")
    print(f"Type: {metadata.algorithm_type.value}")
    print(f"Performance baseline: {metadata.performance_baseline}")

    # Test with sample board
    test_board = [
        [2, 4, 8, 16],
        [4, 8, 16, 32],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    print(f"\nTest board:")
    for row in test_board:
        print(f"  {row}")

    move = algorithm.get_move(test_board)
    scores = algorithm.get_move_scores(test_board)
    explanation = algorithm.get_strategy_explanation(test_board)

    print(f"\nRecommended move: {move}")
    print(f"Move scores: UP={scores[0]:.1f}, DOWN={scores[1]:.1f}, LEFT={scores[2]:.1f}, RIGHT={scores[3]:.1f}")
    print(f"Reasoning: {explanation.get('reasoning', 'N/A')}")

    print("✅ Enhanced Heuristic Algorithm test completed")