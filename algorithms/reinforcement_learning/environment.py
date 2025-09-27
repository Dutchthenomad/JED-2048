#!/usr/bin/env python3
"""
2048 Reinforcement Learning Environment
OpenAI Gym-style environment for training RL agents
"""

import numpy as np
import copy
from typing import Tuple, Dict, Any, Optional, List
from enum import IntEnum
import random

class Action(IntEnum):
    """Action space for 2048 game"""
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

class Game2048Environment:
    """
    2048 Game Environment for Reinforcement Learning

    Compatible with OpenAI Gym interface for easy integration
    with RL libraries like Stable Baselines3, Ray RLlib, etc.
    """

    def __init__(self, grid_size: int = 4, max_tile: int = 2048):
        """
        Initialize 2048 environment

        Args:
            grid_size: Size of the game grid (default 4x4)
            max_tile: Maximum tile value to track (default 2048)
        """
        self.grid_size = grid_size
        self.max_tile = max_tile
        self.board = np.zeros((grid_size, grid_size), dtype=np.int32)
        self.score = 0
        self.done = False
        self.info = {}

        # Action space: 4 possible moves
        self.action_space = list(range(4))  # [UP, DOWN, LEFT, RIGHT]

        # Observation space: flattened board + score
        self.observation_space_size = grid_size * grid_size + 1

        # Game statistics
        self.total_moves = 0
        self.highest_tile = 0

    def reset(self) -> np.ndarray:
        """
        Reset environment to initial state

        Returns:
            Initial observation
        """
        self.board = np.zeros((self.grid_size, self.grid_size), dtype=np.int32)
        self.score = 0
        self.done = False
        self.total_moves = 0
        self.highest_tile = 0
        self.info = {}

        # Add two initial tiles
        self._add_random_tile()
        self._add_random_tile()

        return self._get_observation()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute action in environment

        Args:
            action: Action to take (0=UP, 1=DOWN, 2=LEFT, 3=RIGHT)

        Returns:
            observation: New state after action
            reward: Reward from this action
            done: Whether episode is finished
            info: Additional information
        """
        if self.done:
            raise ValueError("Episode is finished. Call reset() to start new episode.")

        # Store previous state for reward calculation
        prev_score = self.score
        prev_board = copy.deepcopy(self.board)

        # Execute move
        moved = self._execute_move(action)
        self.total_moves += 1

        # Calculate reward
        reward = self._calculate_reward(prev_board, prev_score, moved)

        # Add new tile if move was valid
        if moved:
            self._add_random_tile()

        # Check if game is over
        self.done = self._is_game_over()

        # Update highest tile
        self.highest_tile = max(self.highest_tile, np.max(self.board))

        # Update info
        self.info = {
            'moved': moved,
            'highest_tile': self.highest_tile,
            'empty_tiles': np.sum(self.board == 0),
            'total_moves': self.total_moves,
            'efficiency': self.score / max(self.total_moves, 1)
        }

        return self._get_observation(), reward, self.done, self.info

    def _execute_move(self, action: int) -> bool:
        """
        Execute move and return whether board changed

        Args:
            action: Action to execute

        Returns:
            True if board changed, False otherwise
        """
        old_board = copy.deepcopy(self.board)

        if action == Action.UP:
            self._move_up()
        elif action == Action.DOWN:
            self._move_down()
        elif action == Action.LEFT:
            self._move_left()
        elif action == Action.RIGHT:
            self._move_right()
        else:
            raise ValueError(f"Invalid action: {action}")

        return not np.array_equal(old_board, self.board)

    def _move_left(self):
        """Move tiles left"""
        for row in range(self.grid_size):
            # Extract non-zero tiles
            tiles = [self.board[row, col] for col in range(self.grid_size) if self.board[row, col] != 0]

            # Merge tiles
            merged = []
            i = 0
            while i < len(tiles):
                if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
                    # Merge tiles
                    merged_value = tiles[i] * 2
                    merged.append(merged_value)
                    self.score += merged_value
                    i += 2
                else:
                    merged.append(tiles[i])
                    i += 1

            # Fill row with merged tiles and zeros
            for col in range(self.grid_size):
                if col < len(merged):
                    self.board[row, col] = merged[col]
                else:
                    self.board[row, col] = 0

    def _move_right(self):
        """Move tiles right"""
        # Reverse board, move left, reverse back
        self.board = np.fliplr(self.board)
        self._move_left()
        self.board = np.fliplr(self.board)

    def _move_up(self):
        """Move tiles up"""
        # Transpose, move left, transpose back
        self.board = self.board.T
        self._move_left()
        self.board = self.board.T

    def _move_down(self):
        """Move tiles down"""
        # Transpose, move right, transpose back
        self.board = self.board.T
        self._move_right()
        self.board = self.board.T

    def _add_random_tile(self):
        """Add random tile (2 or 4) to empty position"""
        empty_positions = list(zip(*np.where(self.board == 0)))

        if empty_positions:
            pos = random.choice(empty_positions)
            # 90% chance of 2, 10% chance of 4
            value = 2 if random.random() < 0.9 else 4
            self.board[pos] = value

    def _is_game_over(self) -> bool:
        """Check if game is over (no valid moves available)"""
        # Check if there are empty tiles
        if np.sum(self.board == 0) > 0:
            return False

        # Check if any merges are possible
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                current_tile = self.board[row, col]

                # Check adjacent tiles
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    new_row, new_col = row + dr, col + dc

                    if (0 <= new_row < self.grid_size and
                        0 <= new_col < self.grid_size and
                        self.board[new_row, new_col] == current_tile):
                        return False

        return True

    def _calculate_reward(self, prev_board: np.ndarray, prev_score: int, moved: bool) -> float:
        """
        Calculate reward for the action

        Args:
            prev_board: Board state before action
            prev_score: Score before action
            moved: Whether the action resulted in a move

        Returns:
            Reward value
        """
        if not moved:
            # Penalty for invalid moves
            return -10.0

        # Base reward from score increase
        score_reward = self.score - prev_score

        # Additional rewards for good strategies
        empty_tiles = np.sum(self.board == 0)
        empty_reward = empty_tiles * 2.0  # Reward for maintaining empty tiles

        # Reward for higher tiles (exponential)
        max_tile = np.max(self.board)
        tile_reward = np.log2(max_tile) if max_tile > 0 else 0

        # Monotonicity reward (prefer organized boards)
        monotonicity_reward = self._calculate_monotonicity() * 5.0

        # Total reward
        total_reward = score_reward + empty_reward + tile_reward + monotonicity_reward

        return total_reward

    def _calculate_monotonicity(self) -> float:
        """Calculate board monotonicity (higher is better)"""
        score = 0.0

        # Check row monotonicity
        for row in range(self.grid_size):
            row_values = [self.board[row, col] for col in range(self.grid_size) if self.board[row, col] > 0]
            if len(row_values) > 1:
                # Check if sorted in ascending or descending order
                if row_values == sorted(row_values) or row_values == sorted(row_values, reverse=True):
                    score += 1.0

        # Check column monotonicity
        for col in range(self.grid_size):
            col_values = [self.board[row, col] for row in range(self.grid_size) if self.board[row, col] > 0]
            if len(col_values) > 1:
                if col_values == sorted(col_values) or col_values == sorted(col_values, reverse=True):
                    score += 1.0

        return score

    def _get_observation(self) -> np.ndarray:
        """
        Get current observation

        Returns:
            Flattened board state with normalized values
        """
        # Normalize board values using log2 (0 stays 0)
        normalized_board = np.zeros_like(self.board, dtype=np.float32)
        mask = self.board > 0
        normalized_board[mask] = np.log2(self.board[mask])

        # Flatten board and add normalized score
        observation = normalized_board.flatten()

        # Add normalized score (divided by 10000 to keep in reasonable range)
        score_normalized = self.score / 10000.0
        observation = np.append(observation, score_normalized)

        return observation.astype(np.float32)

    def render(self, mode: str = 'human'):
        """
        Render the current state

        Args:
            mode: Render mode ('human' for console output)
        """
        if mode == 'human':
            print(f"\nScore: {self.score}")
            print(f"Moves: {self.total_moves}")
            print("Board:")
            for row in self.board:
                print("  " + " ".join(f"{tile:4d}" if tile > 0 else "   ." for tile in row))
            print()

    def get_valid_actions(self) -> List[int]:
        """Get list of valid actions from current state"""
        valid_actions = []

        for action in range(4):
            # Simulate action to check if it's valid
            temp_board = copy.deepcopy(self.board)
            temp_env = Game2048Environment(self.grid_size, self.max_tile)
            temp_env.board = temp_board
            temp_env.score = self.score

            if temp_env._execute_move(action):
                valid_actions.append(action)

        return valid_actions

    def get_state_representation(self) -> Dict[str, Any]:
        """Get detailed state representation for analysis"""
        return {
            'board': self.board.copy(),
            'score': self.score,
            'highest_tile': self.highest_tile,
            'empty_tiles': np.sum(self.board == 0),
            'total_moves': self.total_moves,
            'done': self.done,
            'valid_actions': self.get_valid_actions(),
            'monotonicity': self._calculate_monotonicity()
        }

# Example RL algorithm interface
class BaseRLAlgorithm:
    """Base class for RL algorithms using the 2048 environment"""

    def __init__(self, environment: Game2048Environment):
        self.env = environment
        self.training_data = []

    def train(self, episodes: int = 1000):
        """Train the RL algorithm"""
        raise NotImplementedError("Subclasses must implement train method")

    def predict(self, observation: np.ndarray) -> int:
        """Predict action for given observation"""
        raise NotImplementedError("Subclasses must implement predict method")

    def save_model(self, filepath: str):
        """Save trained model"""
        raise NotImplementedError("Subclasses must implement save_model method")

    def load_model(self, filepath: str):
        """Load trained model"""
        raise NotImplementedError("Subclasses must implement load_model method")

if __name__ == "__main__":
    # Test the environment
    print("🧪 2048 RL Environment Test")

    env = Game2048Environment()
    observation = env.reset()

    print(f"Initial observation shape: {observation.shape}")
    print(f"Action space: {env.action_space}")

    env.render()

    # Play a few random moves
    for step in range(10):
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            break

        action = random.choice(valid_actions)
        observation, reward, done, info = env.step(action)

        print(f"Step {step + 1}: Action {action}, Reward {reward:.2f}")
        env.render()

        if done:
            print("Game over!")
            break

    print("✅ RL Environment test completed")