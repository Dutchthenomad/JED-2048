#!/usr/bin/env python3
"""
Advanced Leaderboard and Evaluation System
Comprehensive ranking, statistics, and performance analysis for algorithms
"""

import sys
from pathlib import Path
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from algorithms import AlgorithmManager
from student_platform import StudentPlatform

@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    algorithm_id: str
    algorithm_name: str
    algorithm_type: str

    # Game performance
    games_played: int
    average_efficiency: float
    average_score: float
    highest_tile_achieved: int
    consistency_score: float

    # Advanced metrics
    improvement_rate: float
    learning_curve_slope: float
    stability_index: float

    # Ranking
    overall_rank: int
    category_rank: int
    percentile: float

class LeaderboardSystem:
    """
    Advanced leaderboard and evaluation system

    Provides comprehensive ranking, statistics, and performance analysis
    for educational algorithm competition platform.
    """

    def __init__(self, data_dir: str = "leaderboard_data"):
        """Initialize leaderboard system"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize subsystems
        self.algorithm_manager = AlgorithmManager()
        self.student_platform = StudentPlatform()

        # Ranking weights
        self.ranking_weights = {
            'efficiency': 0.4,      # Points per move
            'consistency': 0.3,     # Performance stability
            'highest_tile': 0.2,    # Peak performance
            'improvement': 0.1      # Learning/adaptation
        }

        # Performance history
        self.performance_history: Dict[str, List[Dict]] = defaultdict(list)

        # Load existing data
        self._load_historical_data()

    def generate_comprehensive_leaderboard(self, category: str = "all") -> List[PerformanceMetrics]:
        """
        Generate comprehensive leaderboard with advanced metrics

        Args:
            category: Algorithm category filter ("all", "heuristic", "rl", "student")

        Returns:
            Ranked list of performance metrics
        """
        print(f"📊 Generating comprehensive leaderboard (category: {category})")

        # Get algorithm performance data
        algorithms_data = self._collect_algorithm_data(category)

        if not algorithms_data:
            print("❌ No algorithm data available")
            return []

        # Calculate advanced metrics
        performance_metrics = []

        for algo_id, data in algorithms_data.items():
            metrics = self._calculate_performance_metrics(algo_id, data)
            if metrics:
                performance_metrics.append(metrics)

        # Rank algorithms
        ranked_metrics = self._rank_algorithms(performance_metrics)

        # Display leaderboard
        self._display_advanced_leaderboard(ranked_metrics)

        return ranked_metrics

    def _collect_algorithm_data(self, category: str) -> Dict[str, Dict]:
        """Collect performance data for algorithms"""
        algorithms_data = {}

        # Get from algorithm manager
        for algo_id, history in self.algorithm_manager.performance_history.items():
            if not history:
                continue

            # Filter by category
            if category != "all":
                algo_info = self.algorithm_manager.get_algorithm_info(algo_id)
                if algo_info and algo_info['metadata']['algorithm_type'] != category:
                    continue

            algorithms_data[algo_id] = {
                'history': history,
                'metadata': self.algorithm_manager.algorithm_metadata.get(algo_id)
            }

        # Get student submissions
        if category in ["all", "student"]:
            student_leaderboard = self.student_platform.get_leaderboard()
            for entry in student_leaderboard:
                algo_id = f"student_{entry['submission_id']}"
                algorithms_data[algo_id] = {
                    'history': [{'statistics': entry}],
                    'metadata': None,
                    'student_entry': entry
                }

        return algorithms_data

    def _calculate_performance_metrics(self, algo_id: str, data: Dict) -> Optional[PerformanceMetrics]:
        """Calculate comprehensive performance metrics"""
        try:
            history = data['history']
            metadata = data['metadata']

            if not history:
                return None

            # Extract statistics
            efficiencies = []
            scores = []
            highest_tiles = []
            games_played = 0

            for record in history:
                stats = record.get('statistics', {})
                if 'average_efficiency' in stats:
                    efficiencies.append(stats['average_efficiency'])
                if 'total_score' in stats:
                    scores.append(stats['total_score'])
                if 'highest_tile' in stats:
                    highest_tiles.append(stats['highest_tile'])
                if 'games_played' in stats:
                    games_played += stats['games_played']

            if not efficiencies:
                return None

            # Basic metrics
            avg_efficiency = np.mean(efficiencies)
            avg_score = np.mean(scores) if scores else 0
            max_tile = max(highest_tiles) if highest_tiles else 0

            # Consistency score (inverse of coefficient of variation)
            consistency = 1.0 - (np.std(efficiencies) / max(avg_efficiency, 0.1))
            consistency = max(0, min(1, consistency))

            # Improvement rate (slope of efficiency over time)
            if len(efficiencies) > 1:
                x = np.arange(len(efficiencies))
                improvement_rate = np.polyfit(x, efficiencies, 1)[0]
                learning_curve_slope = improvement_rate
            else:
                improvement_rate = 0.0
                learning_curve_slope = 0.0

            # Stability index (how stable recent performance is)
            if len(efficiencies) >= 5:
                recent_std = np.std(efficiencies[-5:])
                stability_index = 1.0 - min(recent_std / max(avg_efficiency, 0.1), 1.0)
            else:
                stability_index = consistency

            # Get algorithm name and type
            if metadata:
                algo_name = metadata.name
                algo_type = metadata.algorithm_type.value
            elif 'student_entry' in data:
                algo_name = data['student_entry']['algorithm_name']
                algo_type = "student"
            else:
                algo_name = algo_id
                algo_type = "unknown"

            return PerformanceMetrics(
                algorithm_id=algo_id,
                algorithm_name=algo_name,
                algorithm_type=algo_type,
                games_played=games_played,
                average_efficiency=avg_efficiency,
                average_score=avg_score,
                highest_tile_achieved=max_tile,
                consistency_score=consistency,
                improvement_rate=improvement_rate,
                learning_curve_slope=learning_curve_slope,
                stability_index=stability_index,
                overall_rank=0,  # Will be set during ranking
                category_rank=0,  # Will be set during ranking
                percentile=0.0   # Will be set during ranking
            )

        except Exception as e:
            print(f"❌ Error calculating metrics for {algo_id}: {e}")
            return None

    def _rank_algorithms(self, metrics_list: List[PerformanceMetrics]) -> List[PerformanceMetrics]:
        """Rank algorithms using weighted scoring"""
        if not metrics_list:
            return []

        # Normalize metrics for scoring
        normalized_metrics = self._normalize_metrics(metrics_list)

        # Calculate composite scores
        for i, metrics in enumerate(metrics_list):
            norm = normalized_metrics[i]

            composite_score = (
                norm['efficiency'] * self.ranking_weights['efficiency'] +
                norm['consistency'] * self.ranking_weights['consistency'] +
                norm['highest_tile'] * self.ranking_weights['highest_tile'] +
                norm['improvement'] * self.ranking_weights['improvement']
            )

            # Store composite score for sorting
            metrics.composite_score = composite_score

        # Sort by composite score
        ranked_metrics = sorted(metrics_list, key=lambda x: x.composite_score, reverse=True)

        # Assign ranks and percentiles
        total_algorithms = len(ranked_metrics)

        for i, metrics in enumerate(ranked_metrics):
            metrics.overall_rank = i + 1
            metrics.percentile = ((total_algorithms - i) / total_algorithms) * 100

        # Assign category ranks
        category_groups = defaultdict(list)
        for metrics in ranked_metrics:
            category_groups[metrics.algorithm_type].append(metrics)

        for category, group in category_groups.items():
            for i, metrics in enumerate(group):
                metrics.category_rank = i + 1

        return ranked_metrics

    def _normalize_metrics(self, metrics_list: List[PerformanceMetrics]) -> List[Dict[str, float]]:
        """Normalize metrics to 0-1 range for fair comparison"""
        if not metrics_list:
            return []

        # Extract values
        efficiencies = [m.average_efficiency for m in metrics_list]
        consistencies = [m.consistency_score for m in metrics_list]
        highest_tiles = [m.highest_tile_achieved for m in metrics_list]
        improvements = [m.improvement_rate for m in metrics_list]

        # Normalize each metric
        def normalize(values):
            min_val, max_val = min(values), max(values)
            if max_val == min_val:
                return [1.0] * len(values)
            return [(v - min_val) / (max_val - min_val) for v in values]

        norm_efficiency = normalize(efficiencies)
        norm_consistency = normalize(consistencies)
        norm_tiles = normalize([np.log2(max(t, 1)) for t in highest_tiles])  # Log scale for tiles

        # Handle improvement (can be negative)
        if max(improvements) > min(improvements):
            norm_improvement = [(i - min(improvements)) / (max(improvements) - min(improvements)) for i in improvements]
        else:
            norm_improvement = [0.5] * len(improvements)

        normalized = []
        for i in range(len(metrics_list)):
            normalized.append({
                'efficiency': norm_efficiency[i],
                'consistency': norm_consistency[i],
                'highest_tile': norm_tiles[i],
                'improvement': norm_improvement[i]
            })

        return normalized

    def _display_advanced_leaderboard(self, ranked_metrics: List[PerformanceMetrics]):
        """Display comprehensive leaderboard"""
        print(f"\n🏆 ADVANCED ALGORITHM LEADERBOARD")
        print("=" * 100)

        # Header
        print(f"{'Rank':<5} {'Algorithm':<25} {'Type':<12} {'Efficiency':<12} {'Consistency':<12} {'Max Tile':<10} {'Percentile':<10}")
        print("-" * 100)

        # Top algorithms
        for metrics in ranked_metrics[:20]:  # Top 20
            rank = metrics.overall_rank
            name = metrics.algorithm_name[:24]
            algo_type = metrics.algorithm_type[:11]
            efficiency = f"{metrics.average_efficiency:.3f}"
            consistency = f"{metrics.consistency_score:.3f}"
            max_tile = str(metrics.highest_tile_achieved)
            percentile = f"{metrics.percentile:.1f}%"

            print(f"{rank:<5} {name:<25} {algo_type:<12} {efficiency:<12} {consistency:<12} {max_tile:<10} {percentile:<10}")

        # Category winners
        print(f"\n🏅 CATEGORY LEADERS:")
        categories = defaultdict(list)
        for metrics in ranked_metrics:
            categories[metrics.algorithm_type].append(metrics)

        for category, group in categories.items():
            if group:
                best = group[0]  # Already sorted
                print(f"   {category.title()}: {best.algorithm_name} ({best.average_efficiency:.3f} efficiency)")

        # Performance insights
        print(f"\n📈 PERFORMANCE INSIGHTS:")
        if ranked_metrics:
            best = ranked_metrics[0]
            avg_efficiency = np.mean([m.average_efficiency for m in ranked_metrics])

            print(f"   🥇 Top performer: {best.algorithm_name} ({best.average_efficiency:.3f} efficiency)")
            print(f"   📊 Platform average: {avg_efficiency:.3f} efficiency")
            print(f"   🎯 Performance gap: {(best.average_efficiency / avg_efficiency - 1) * 100:.1f}% above average")

    def generate_performance_report(self, algorithm_id: str) -> Dict[str, Any]:
        """Generate detailed performance report for specific algorithm"""
        history = self.algorithm_manager.performance_history.get(algorithm_id, [])

        if not history:
            return {'error': f'No performance data for {algorithm_id}'}

        # Calculate trends
        efficiencies = [h.get('statistics', {}).get('average_efficiency', 0) for h in history]
        scores = [h.get('statistics', {}).get('total_score', 0) for h in history]

        # Performance trends
        if len(efficiencies) > 1:
            x = np.arange(len(efficiencies))
            efficiency_trend = np.polyfit(x, efficiencies, 1)[0]
        else:
            efficiency_trend = 0.0

        # Recent vs historical performance
        recent_performance = np.mean(efficiencies[-5:]) if len(efficiencies) >= 5 else np.mean(efficiencies)
        historical_performance = np.mean(efficiencies[:-5]) if len(efficiencies) > 5 else recent_performance

        report = {
            'algorithm_id': algorithm_id,
            'total_sessions': len(history),
            'current_efficiency': efficiencies[-1] if efficiencies else 0,
            'average_efficiency': np.mean(efficiencies),
            'best_efficiency': max(efficiencies) if efficiencies else 0,
            'efficiency_trend': efficiency_trend,
            'recent_vs_historical': recent_performance - historical_performance,
            'consistency_score': 1.0 - (np.std(efficiencies) / max(np.mean(efficiencies), 0.1)),
            'performance_history': efficiencies,
            'recommendations': self._generate_recommendations(efficiencies, efficiency_trend)
        }

        return report

    def _generate_recommendations(self, efficiencies: List[float], trend: float) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        if not efficiencies:
            return ["No performance data available"]

        avg_efficiency = np.mean(efficiencies)

        # Performance level recommendations
        if avg_efficiency < 1.0:
            recommendations.append("Consider reviewing basic strategy principles")
            recommendations.append("Focus on maintaining empty tiles and corner strategy")
        elif avg_efficiency < 2.0:
            recommendations.append("Implement advanced heuristics like monotonicity")
            recommendations.append("Tune weight parameters for better balance")
        else:
            recommendations.append("Excellent performance! Consider sharing techniques with others")

        # Trend recommendations
        if trend < -0.01:
            recommendations.append("Performance declining - review recent changes")
        elif trend > 0.01:
            recommendations.append("Good improvement trend - continue current approach")
        else:
            recommendations.append("Stable performance - consider experimenting with new strategies")

        # Consistency recommendations
        if len(efficiencies) > 1:
            consistency = 1.0 - (np.std(efficiencies) / max(avg_efficiency, 0.1))
            if consistency < 0.7:
                recommendations.append("Work on consistency - performance varies significantly")

        return recommendations

    def export_leaderboard(self, filepath: str, format: str = "json"):
        """Export leaderboard data"""
        leaderboard = self.generate_comprehensive_leaderboard()

        if format == "json":
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'total_algorithms': len(leaderboard),
                'ranking_weights': self.ranking_weights,
                'leaderboard': [
                    {
                        'rank': m.overall_rank,
                        'algorithm_name': m.algorithm_name,
                        'algorithm_type': m.algorithm_type,
                        'efficiency': m.average_efficiency,
                        'consistency': m.consistency_score,
                        'highest_tile': m.highest_tile_achieved,
                        'percentile': m.percentile
                    }
                    for m in leaderboard
                ]
            }

            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)

        print(f"📁 Leaderboard exported to {filepath}")

    def _load_historical_data(self):
        """Load historical performance data"""
        # Implementation for loading historical data
        pass

    def _save_historical_data(self):
        """Save current performance data"""
        # Implementation for saving historical data
        pass

if __name__ == "__main__":
    # Demo the leaderboard system
    print("🏆 ADVANCED LEADERBOARD SYSTEM DEMO")
    print("=" * 60)

    leaderboard_system = LeaderboardSystem()

    # Generate comprehensive leaderboard
    leaderboard = leaderboard_system.generate_comprehensive_leaderboard()

    if leaderboard:
        print(f"\n📊 Generated leaderboard with {len(leaderboard)} algorithms")

        # Export leaderboard
        export_file = f"leaderboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        leaderboard_system.export_leaderboard(export_file)

    else:
        print("📊 No algorithm data available for leaderboard")

    print("\n✅ Leaderboard system demo completed")