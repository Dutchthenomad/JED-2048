#!/usr/bin/env python3
"""
Algorithm Manager
Central system for algorithm registration, selection, and management
"""

import importlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Type
import logging
from dataclasses import asdict

from .base_algorithm import BaseAlgorithm, AlgorithmMetadata, AlgorithmType

class AlgorithmManager:
    """
    Central manager for 2048 playing algorithms

    Handles registration, discovery, selection, and performance tracking
    """

    def __init__(self, algorithms_dir: str = "algorithms"):
        """
        Initialize algorithm manager

        Args:
            algorithms_dir: Directory containing algorithm implementations
        """
        self.algorithms_dir = Path(algorithms_dir)
        self.registered_algorithms: Dict[str, Type[BaseAlgorithm]] = {}
        self.algorithm_metadata: Dict[str, AlgorithmMetadata] = {}
        self.performance_history: Dict[str, List[Dict]] = {}

        # Setup logging
        self.logger = logging.getLogger("algorithm_manager")

        # Auto-discover algorithms
        self._discover_algorithms()

    def register_algorithm(self, algorithm_class: Type[BaseAlgorithm],
                          override: bool = False) -> bool:
        """
        Register an algorithm class

        Args:
            algorithm_class: Algorithm class implementing BaseAlgorithm
            override: Allow overriding existing algorithm

        Returns:
            True if registered successfully
        """
        try:
            # Create temporary instance to get metadata
            temp_instance = algorithm_class()
            metadata = temp_instance.metadata

            algorithm_id = f"{metadata.name}_{metadata.version}"

            if algorithm_id in self.registered_algorithms and not override:
                self.logger.warning(f"Algorithm {algorithm_id} already registered")
                return False

            self.registered_algorithms[algorithm_id] = algorithm_class
            self.algorithm_metadata[algorithm_id] = metadata

            self.logger.info(f"✅ Registered algorithm: {algorithm_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to register algorithm: {e}")
            return False

    def get_algorithm(self, algorithm_id: str, **config) -> Optional[BaseAlgorithm]:
        """
        Get algorithm instance by ID

        Args:
            algorithm_id: Algorithm identifier
            **config: Configuration parameters for algorithm

        Returns:
            Algorithm instance or None if not found
        """
        if algorithm_id not in self.registered_algorithms:
            self.logger.error(f"Algorithm {algorithm_id} not found")
            return None

        try:
            algorithm_class = self.registered_algorithms[algorithm_id]
            return algorithm_class(**config)
        except Exception as e:
            self.logger.error(f"Failed to instantiate {algorithm_id}: {e}")
            return None

    def list_algorithms(self, algorithm_type: Optional[AlgorithmType] = None) -> List[Dict[str, Any]]:
        """
        List available algorithms

        Args:
            algorithm_type: Filter by algorithm type

        Returns:
            List of algorithm information
        """
        algorithms = []

        for algorithm_id, metadata in self.algorithm_metadata.items():
            if algorithm_type is None or metadata.algorithm_type == algorithm_type:
                algorithms.append({
                    'id': algorithm_id,
                    'name': metadata.name,
                    'version': metadata.version,
                    'author': metadata.author,
                    'description': metadata.description,
                    'type': metadata.algorithm_type.value,
                    'training_required': metadata.training_required,
                    'performance_baseline': metadata.performance_baseline
                })

        return algorithms

    def get_algorithm_info(self, algorithm_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about specific algorithm"""
        if algorithm_id not in self.algorithm_metadata:
            return None

        metadata = self.algorithm_metadata[algorithm_id]
        performance = self.performance_history.get(algorithm_id, [])

        return {
            'metadata': asdict(metadata),
            'performance_history': performance,
            'is_registered': algorithm_id in self.registered_algorithms,
            'recent_performance': performance[-10:] if performance else []
        }

    def compare_algorithms(self, algorithm_ids: List[str]) -> Dict[str, Any]:
        """
        Compare performance of multiple algorithms

        Args:
            algorithm_ids: List of algorithm IDs to compare

        Returns:
            Comparison results and statistics
        """
        comparison = {
            'algorithms': [],
            'metrics': {
                'games_played': {},
                'average_efficiency': {},
                'highest_tile_achieved': {},
                'consistency_score': {}
            }
        }

        for algorithm_id in algorithm_ids:
            if algorithm_id not in self.performance_history:
                continue

            history = self.performance_history[algorithm_id]
            if not history:
                continue

            # Calculate performance metrics
            efficiencies = [h.get('statistics', {}).get('average_efficiency', 0) for h in history]
            highest_tiles = [h.get('statistics', {}).get('highest_tile', 0) for h in history]
            games_played = sum(h.get('statistics', {}).get('games_played', 0) for h in history)

            avg_efficiency = sum(efficiencies) / len(efficiencies) if efficiencies else 0
            max_tile = max(highest_tiles) if highest_tiles else 0
            consistency = 1.0 - (max(efficiencies) - min(efficiencies)) / max(max(efficiencies), 1) if len(efficiencies) > 1 else 1.0

            algorithm_info = {
                'id': algorithm_id,
                'name': self.algorithm_metadata.get(algorithm_id, {}).name if algorithm_id in self.algorithm_metadata else algorithm_id,
                'games_played': games_played,
                'average_efficiency': avg_efficiency,
                'highest_tile': max_tile,
                'consistency_score': consistency
            }

            comparison['algorithms'].append(algorithm_info)
            comparison['metrics']['games_played'][algorithm_id] = games_played
            comparison['metrics']['average_efficiency'][algorithm_id] = avg_efficiency
            comparison['metrics']['highest_tile_achieved'][algorithm_id] = max_tile
            comparison['metrics']['consistency_score'][algorithm_id] = consistency

        # Rank algorithms
        if comparison['algorithms']:
            comparison['rankings'] = {
                'by_efficiency': sorted(comparison['algorithms'], key=lambda x: x['average_efficiency'], reverse=True),
                'by_highest_tile': sorted(comparison['algorithms'], key=lambda x: x['highest_tile'], reverse=True),
                'by_consistency': sorted(comparison['algorithms'], key=lambda x: x['consistency_score'], reverse=True)
            }

        return comparison

    def record_performance(self, algorithm_id: str, performance_data: Dict[str, Any]):
        """
        Record algorithm performance data

        Args:
            algorithm_id: Algorithm identifier
            performance_data: Performance metrics from algorithm
        """
        if algorithm_id not in self.performance_history:
            self.performance_history[algorithm_id] = []

        self.performance_history[algorithm_id].append(performance_data)

        # Keep only last 100 performance records per algorithm
        if len(self.performance_history[algorithm_id]) > 100:
            self.performance_history[algorithm_id] = self.performance_history[algorithm_id][-100:]

    def save_performance_data(self, filepath: str):
        """Save performance history to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.performance_history, f, indent=2, default=str)
            self.logger.info(f"📁 Performance data saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save performance data: {e}")

    def load_performance_data(self, filepath: str):
        """Load performance history from file"""
        try:
            with open(filepath, 'r') as f:
                self.performance_history = json.load(f)
            self.logger.info(f"📁 Performance data loaded from {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to load performance data: {e}")

    def _discover_algorithms(self):
        """Auto-discover algorithms in subdirectories"""
        if not self.algorithms_dir.exists():
            self.logger.warning(f"Algorithms directory {self.algorithms_dir} not found")
            return

        for subdir in self.algorithms_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('__'):
                self._discover_in_directory(subdir)

    def _discover_in_directory(self, directory: Path):
        """Discover algorithms in specific directory"""
        # Look for algorithm.py or __init__.py files
        algorithm_files = list(directory.glob("algorithm.py")) + list(directory.glob("__init__.py"))

        for algorithm_file in algorithm_files:
            try:
                self._load_algorithm_from_file(algorithm_file)
            except Exception as e:
                self.logger.error(f"Failed to load algorithm from {algorithm_file}: {e}")

    def _load_algorithm_from_file(self, filepath: Path):
        """Load algorithm class from Python file"""
        module_name = f"algorithms.{filepath.parent.name}.{filepath.stem}"

        try:
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Look for classes that inherit from BaseAlgorithm
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        issubclass(attr, BaseAlgorithm) and
                        attr != BaseAlgorithm):

                        self.register_algorithm(attr)

        except Exception as e:
            self.logger.error(f"Error loading module {module_name}: {e}")

    def get_leaderboard(self, metric: str = "average_efficiency", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get algorithm leaderboard based on performance metric

        Args:
            metric: Performance metric to rank by
            limit: Maximum number of algorithms to return

        Returns:
            Ranked list of algorithms
        """
        leaderboard = []

        for algorithm_id, history in self.performance_history.items():
            if not history:
                continue

            latest_performance = history[-1]
            stats = latest_performance.get('statistics', {})

            if metric in stats:
                leaderboard.append({
                    'rank': 0,  # Will be set later
                    'algorithm_id': algorithm_id,
                    'algorithm_name': self.algorithm_metadata.get(algorithm_id, {}).name if algorithm_id in self.algorithm_metadata else algorithm_id,
                    'metric_value': stats[metric],
                    'games_played': stats.get('games_played', 0),
                    'timestamp': latest_performance.get('timestamp', 0)
                })

        # Sort by metric value (descending for most metrics)
        reverse_sort = metric not in ['training_time']  # Most metrics are "higher is better"
        leaderboard.sort(key=lambda x: x['metric_value'], reverse=reverse_sort)

        # Add ranks
        for i, entry in enumerate(leaderboard[:limit]):
            entry['rank'] = i + 1

        return leaderboard[:limit]

# Global algorithm manager instance
algorithm_manager = AlgorithmManager()

if __name__ == "__main__":
    # Test algorithm manager
    print("🧪 Algorithm Manager Test")

    manager = AlgorithmManager()
    algorithms = manager.list_algorithms()

    print(f"Discovered {len(algorithms)} algorithms:")
    for algo in algorithms:
        print(f"  - {algo['name']} v{algo['version']} ({algo['type']})")

    print("✅ Algorithm Manager test completed")