#!/usr/bin/env python3
"""
Q-Learning Algorithm for 2048
Simple reinforcement learning implementation using Q-learning
"""

import sys
from pathlib import Path
import numpy as np
import json
import random
from typing import List, Dict, Any, Tuple
from collections import defaultdict

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from algorithms.base_algorithm import BaseAlgorithm, AlgorithmMetadata, AlgorithmType
from .environment import Game2048Environment, Action

class QLearning2048Algorithm(BaseAlgorithm):
    """
    Q-Learning algorithm for 2048

    Simple tabular Q-learning implementation for educational purposes.
    Uses state abstraction to make learning tractable.
    """

    def __init__(self, **kwargs):
        """Initialize Q-learning algorithm"""
        # Q-learning parameters need to exist before BaseAlgorithm pulls metadata
        self.learning_rate = kwargs.get('learning_rate', 0.1)
        self.discount_factor = kwargs.get('discount_factor', 0.95)
        self.epsilon = kwargs.get('epsilon', 0.1)  # Exploration rate
        self.epsilon_decay = kwargs.get('epsilon_decay', 0.995)
        self.min_epsilon = kwargs.get('min_epsilon', 0.01)

        super().__init__(**kwargs)

        # Q-table (state -> action values)
        self.q_table = defaultdict(lambda: np.zeros(4))

        # Training environment
        self.env = Game2048Environment()

        # Training statistics
        self.training_episodes = 0
        self.training_rewards = []

        # Store config
        self.config.update({
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon': self.epsilon,
            'epsilon_decay': self.epsilon_decay,
            'min_epsilon': self.min_epsilon
        })

    def _get_metadata(self) -> AlgorithmMetadata:
        """Return algorithm metadata"""
        return AlgorithmMetadata(
            name="Q-Learning",
            version="1.0",
            author="2048 Bot Team",
            description="Simple Q-learning reinforcement learning algorithm with state abstraction. Educational RL implementation.",
            algorithm_type=AlgorithmType.REINFORCEMENT_LEARNING,
            parameters={
                'learning_rate': self.learning_rate,
                'discount_factor': self.discount_factor,
                'exploration_rate': self.epsilon
            },
            performance_baseline=None,  # Will be determined through training
            training_required=True
        )

    def get_move(self, board_state: List[List[int]]) -> str:
        """Get move using trained Q-table"""
        state_key = self._board_to_state_key(board_state)
        q_values = self.q_table[state_key]

        # During inference, use greedy action selection
        action = np.argmax(q_values)

        # Convert action to move string
        action_map = {0: "UP", 1: "DOWN", 2: "LEFT", 3: "RIGHT"}
        return action_map[action]

    def get_move_scores(self, board_state: List[List[int]]) -> List[float]:
        """Get Q-values for all actions"""
        state_key = self._board_to_state_key(board_state)
        q_values = self.q_table[state_key]

        # Return Q-values in order: [UP, DOWN, LEFT, RIGHT]
        return [q_values[0], q_values[1], q_values[2], q_values[3]]

    def train(self, training_data: Any = None, episodes: int = 1000, **kwargs) -> Dict[str, Any]:
        """
        Train Q-learning algorithm

        Args:
            training_data: Not used for Q-learning (learns through interaction)
            episodes: Number of training episodes
            **kwargs: Additional training parameters

        Returns:
            Training results and metrics
        """
        print(f"🤖 Training Q-Learning algorithm for {episodes} episodes...")

        episode_rewards = []
        episode_lengths = []
        highest_tiles = []

        for episode in range(episodes):
            # Reset environment
            observation = self.env.reset()
            total_reward = 0
            steps = 0

            while not self.env.done and steps < 1000:  # Max steps per episode
                # Get current state
                state_key = self._observation_to_state_key(observation)

                # Choose action (epsilon-greedy)
                if random.random() < self.epsilon:
                    # Explore: random action from valid actions
                    valid_actions = self.env.get_valid_actions()
                    action = random.choice(valid_actions) if valid_actions else 0
                else:
                    # Exploit: best action according to Q-table
                    q_values = self.q_table[state_key]
                    action = np.argmax(q_values)

                # Take action
                next_observation, reward, done, info = self.env.step(action)
                next_state_key = self._observation_to_state_key(next_observation)

                # Q-learning update
                old_q_value = self.q_table[state_key][action]
                next_max_q = np.max(self.q_table[next_state_key])

                # Q(s,a) = Q(s,a) + α[r + γ*max(Q(s',a')) - Q(s,a)]
                new_q_value = old_q_value + self.learning_rate * (
                    reward + self.discount_factor * next_max_q - old_q_value
                )
                self.q_table[state_key][action] = new_q_value

                # Update for next iteration
                observation = next_observation
                total_reward += reward
                steps += 1

            # Episode statistics
            episode_rewards.append(total_reward)
            episode_lengths.append(steps)
            highest_tiles.append(info.get('highest_tile', 0))

            # Decay epsilon
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

            # Progress reporting
            if episode % 100 == 0:
                avg_reward = np.mean(episode_rewards[-100:])
                avg_tile = np.mean(highest_tiles[-100:])
                print(f"Episode {episode}: Avg Reward = {avg_reward:.2f}, Avg Highest Tile = {avg_tile:.1f}, Epsilon = {self.epsilon:.3f}")

        # Training completed
        self.training_episodes += episodes
        self.training_rewards.extend(episode_rewards)
        self.is_trained = True

        # Calculate training metrics
        training_results = {
            'episodes_trained': episodes,
            'total_episodes': self.training_episodes,
            'average_reward': np.mean(episode_rewards),
            'average_episode_length': np.mean(episode_lengths),
            'average_highest_tile': np.mean(highest_tiles),
            'max_highest_tile': max(highest_tiles),
            'final_epsilon': self.epsilon,
            'q_table_size': len(self.q_table),
            'converged': self.epsilon <= self.min_epsilon
        }

        print(f"✅ Training completed!")
        print(f"   Average reward: {training_results['average_reward']:.2f}")
        print(f"   Average highest tile: {training_results['average_highest_tile']:.1f}")
        print(f"   Q-table size: {training_results['q_table_size']} states")

        return training_results

    def _board_to_state_key(self, board_state: List[List[int]]) -> str:
        """Convert board state to state key for Q-table"""
        # Simple state abstraction: use board configuration
        # For large state spaces, this could be improved with function approximation
        board_array = np.array(board_state)
        return str(board_array.flatten().tolist())

    def _observation_to_state_key(self, observation: np.ndarray) -> str:
        """Convert environment observation to state key"""
        # Extract board part from observation (excluding score)
        board_part = observation[:-1]  # Remove last element (score)
        return str(board_part.tolist())

    def save_model(self, filepath: str) -> bool:
        """Save trained Q-table"""
        try:
            model_data = {
                'q_table': {k: v.tolist() for k, v in self.q_table.items()},
                'config': self.config,
                'training_episodes': self.training_episodes,
                'is_trained': self.is_trained,
                'epsilon': self.epsilon
            }

            with open(filepath, 'w') as f:
                json.dump(model_data, f, indent=2)

            print(f"💾 Q-learning model saved to {filepath}")
            return True

        except Exception as e:
            print(f"❌ Failed to save model: {e}")
            return False

    def load_model(self, filepath: str) -> bool:
        """Load trained Q-table"""
        try:
            with open(filepath, 'r') as f:
                model_data = json.load(f)

            # Restore Q-table
            self.q_table = defaultdict(lambda: np.zeros(4))
            for state, q_values in model_data['q_table'].items():
                self.q_table[state] = np.array(q_values)

            # Restore config
            self.config.update(model_data.get('config', {}))
            self.training_episodes = model_data.get('training_episodes', 0)
            self.is_trained = model_data.get('is_trained', False)
            self.epsilon = model_data.get('epsilon', self.min_epsilon)

            print(f"📂 Q-learning model loaded from {filepath}")
            print(f"   Q-table size: {len(self.q_table)} states")
            print(f"   Training episodes: {self.training_episodes}")

            return True

        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return False

    def get_training_progress(self) -> Dict[str, Any]:
        """Get training progress information"""
        return {
            'training_episodes': self.training_episodes,
            'is_trained': self.is_trained,
            'epsilon': self.epsilon,
            'q_table_size': len(self.q_table),
            'recent_rewards': self.training_rewards[-100:] if self.training_rewards else []
        }

if __name__ == "__main__":
    # Test Q-learning algorithm
    print("🧪 Q-Learning Algorithm Test")

    # Create algorithm
    algorithm = QLearning2048Algorithm(
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=0.5
    )

    print(f"Algorithm: {algorithm.metadata.name}")
    print(f"Training required: {algorithm.metadata.training_required}")

    # Quick training test (just a few episodes)
    print("\n🏋️ Quick training test (50 episodes)...")
    results = algorithm.train(episodes=50)

    # Test move prediction
    test_board = [
        [2, 4, 0, 0],
        [4, 8, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    move = algorithm.get_move(test_board)
    scores = algorithm.get_move_scores(test_board)

    print(f"\nTest prediction:")
    print(f"Board: {test_board[0]}")
    print(f"       {test_board[1]}")
    print(f"Recommended move: {move}")
    print(f"Q-values: UP={scores[0]:.2f}, DOWN={scores[1]:.2f}, LEFT={scores[2]:.2f}, RIGHT={scores[3]:.2f}")

    print("✅ Q-Learning algorithm test completed")
