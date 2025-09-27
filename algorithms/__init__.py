"""
2048 Algorithm Framework
Pluggable algorithm system for educational AI platform
"""

from .base_algorithm import BaseAlgorithm, AlgorithmMetadata
from .algorithm_manager import AlgorithmManager

__all__ = ['BaseAlgorithm', 'AlgorithmMetadata', 'AlgorithmManager']