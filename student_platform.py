#!/usr/bin/env python3
"""
Student Competition Platform
Educational platform for algorithm development and competition
"""

import sys
from pathlib import Path
import time
import json
import shutil
import importlib.util
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from enhanced_2048_bot import Enhanced2048Bot
from algorithms import AlgorithmManager, BaseAlgorithm

@dataclass
class StudentSubmission:
    """Student algorithm submission"""
    student_name: str
    algorithm_name: str
    submission_id: str
    file_path: str
    timestamp: datetime
    validated: bool = False
    performance_score: Optional[float] = None
    ranking: Optional[int] = None

@dataclass
class CompetitionResults:
    """Competition results data"""
    competition_id: str
    timestamp: datetime
    submissions: List[StudentSubmission]
    leaderboard: List[Dict[str, Any]]
    test_games: int
    baseline_comparison: Dict[str, float]

class StudentPlatform:
    """
    Educational platform for student algorithm competition

    Provides framework for students to submit algorithms,
    automated testing, and leaderboard management.
    """

    def __init__(self, platform_dir: str = "student_platform"):
        """
        Initialize student platform

        Args:
            platform_dir: Directory for platform data
        """
        self.platform_dir = Path(platform_dir)
        self.submissions_dir = self.platform_dir / "submissions"
        self.results_dir = self.platform_dir / "results"
        self.leaderboard_file = self.platform_dir / "leaderboard.json"

        # Create directories
        self.platform_dir.mkdir(exist_ok=True)
        self.submissions_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)

        # Initialize systems
        self.algorithm_manager = AlgorithmManager()
        self.submissions: List[StudentSubmission] = []
        self.leaderboard: List[Dict[str, Any]] = []

        # Competition settings
        self.test_games_per_submission = 5
        self.max_moves_per_game = 100

        # Setup logging
        self.logger = logging.getLogger("student_platform")

        # Load existing data
        self._load_platform_data()

    def submit_algorithm(self, student_name: str, algorithm_file: str,
                        algorithm_name: str = None) -> Dict[str, Any]:
        """
        Submit student algorithm for competition

        Args:
            student_name: Name of the student
            algorithm_file: Path to Python file containing algorithm
            algorithm_name: Optional custom algorithm name

        Returns:
            Submission result with validation status
        """
        print(f"📝 Processing submission from {student_name}...")

        # Generate submission ID
        timestamp = datetime.now()
        submission_id = f"{student_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        if not algorithm_name:
            algorithm_name = f"{student_name}_Algorithm"

        # Validate file exists
        algorithm_path = Path(algorithm_file)
        if not algorithm_path.exists():
            return {
                'success': False,
                'error': f"Algorithm file not found: {algorithm_file}"
            }

        # Copy to submissions directory
        submission_file = self.submissions_dir / f"{submission_id}.py"
        try:
            shutil.copy2(algorithm_path, submission_file)
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to copy submission: {e}"
            }

        # Create submission record
        submission = StudentSubmission(
            student_name=student_name,
            algorithm_name=algorithm_name,
            submission_id=submission_id,
            file_path=str(submission_file),
            timestamp=timestamp
        )

        # Validate submission
        validation_result = self._validate_submission(submission)

        if validation_result['valid']:
            submission.validated = True
            self.submissions.append(submission)
            self._save_platform_data()

            print(f"✅ Submission accepted: {submission_id}")
            return {
                'success': True,
                'submission_id': submission_id,
                'validation': validation_result,
                'message': 'Algorithm submitted successfully and validated'
            }
        else:
            # Remove invalid submission file
            submission_file.unlink(missing_ok=True)

            print(f"❌ Submission rejected: {validation_result['error']}")
            return {
                'success': False,
                'error': validation_result['error'],
                'validation_details': validation_result
            }

    def _validate_submission(self, submission: StudentSubmission) -> Dict[str, Any]:
        """
        Validate student submission

        Args:
            submission: Student submission to validate

        Returns:
            Validation results
        """
        try:
            # Load the submitted module
            spec = importlib.util.spec_from_file_location(
                f"student_{submission.submission_id}",
                submission.file_path
            )

            if not spec or not spec.loader:
                return {
                    'valid': False,
                    'error': 'Invalid Python file format'
                }

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for algorithm class
            algorithm_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, BaseAlgorithm) and
                    attr != BaseAlgorithm):
                    algorithm_class = attr
                    break

            if not algorithm_class:
                return {
                    'valid': False,
                    'error': 'No valid algorithm class found (must inherit from BaseAlgorithm)'
                }

            # Test instantiation
            try:
                test_instance = algorithm_class()
                metadata = test_instance.metadata

                # Validate metadata
                if not metadata.name or not metadata.version:
                    return {
                        'valid': False,
                        'error': 'Algorithm metadata incomplete (name and version required)'
                    }

                # Test basic functionality
                test_board = [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
                move = test_instance.get_move(test_board)

                if move not in ["UP", "DOWN", "LEFT", "RIGHT"]:
                    return {
                        'valid': False,
                        'error': f'Invalid move returned: {move}'
                    }

                return {
                    'valid': True,
                    'algorithm_class': algorithm_class,
                    'metadata': asdict(metadata),
                    'test_move': move
                }

            except Exception as e:
                return {
                    'valid': False,
                    'error': f'Algorithm instantiation failed: {e}'
                }

        except Exception as e:
            return {
                'valid': False,
                'error': f'Failed to load submission: {e}'
            }

    def run_competition(self, competition_name: str = None) -> CompetitionResults:
        """
        Run competition with all validated submissions

        Args:
            competition_name: Optional competition identifier

        Returns:
            Competition results
        """
        if not competition_name:
            competition_name = f"competition_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"🏆 Running Competition: {competition_name}")
        print("=" * 60)

        validated_submissions = [s for s in self.submissions if s.validated]

        if not validated_submissions:
            print("❌ No validated submissions found")
            return CompetitionResults(
                competition_id=competition_name,
                timestamp=datetime.now(),
                submissions=[],
                leaderboard=[],
                test_games=0,
                baseline_comparison={}
            )

        print(f"🎯 Testing {len(validated_submissions)} submissions")
        print(f"⚡ {self.test_games_per_submission} games per submission")
        print(f"🎮 {self.max_moves_per_game} max moves per game")
        print()

        # Test each submission
        results = []

        for i, submission in enumerate(validated_submissions, 1):
            print(f"🧪 Testing {i}/{len(validated_submissions)}: {submission.student_name}")

            # Load algorithm
            try:
                algorithm_class = self._load_algorithm_class(submission)
                if not algorithm_class:
                    print(f"   ❌ Failed to load algorithm")
                    continue

                # Register and test algorithm
                algorithm_id = f"student_{submission.submission_id}"
                self.algorithm_manager.register_algorithm(algorithm_class, override=True)

                # Run test games
                submission_results = self._test_submission(algorithm_id, submission)
                results.append((submission, submission_results))

                print(f"   ✅ Completed: {submission_results['average_efficiency']:.2f} avg efficiency")

            except Exception as e:
                print(f"   ❌ Testing failed: {e}")
                continue

        # Generate leaderboard
        leaderboard = self._generate_leaderboard(results)

        # Create competition results
        competition_results = CompetitionResults(
            competition_id=competition_name,
            timestamp=datetime.now(),
            submissions=validated_submissions,
            leaderboard=leaderboard,
            test_games=self.test_games_per_submission,
            baseline_comparison=self._calculate_baseline_comparison(leaderboard)
        )

        # Save results
        self._save_competition_results(competition_results)

        # Update leaderboard
        self.leaderboard = leaderboard
        self._save_platform_data()

        # Display results
        self._display_competition_results(competition_results)

        return competition_results

    def _test_submission(self, algorithm_id: str, submission: StudentSubmission) -> Dict[str, Any]:
        """Test individual submission with multiple games"""
        total_score = 0
        total_moves = 0
        highest_tiles = []
        game_results = []

        for game_num in range(self.test_games_per_submission):
            try:
                # Create bot with student algorithm
                bot = Enhanced2048Bot(
                    headless=True,  # Fast testing
                    debug=False,
                    algorithm_id=algorithm_id
                )

                if bot.connect_to_game():
                    result = bot.play_autonomous_game(max_moves=self.max_moves_per_game)

                    total_score += result.get('final_score', 0)
                    total_moves += result.get('moves_completed', 0)
                    highest_tiles.append(result.get('highest_tile', 0))
                    game_results.append(result)

                bot.cleanup()

            except Exception as e:
                self.logger.error(f"Game {game_num + 1} failed for {submission.student_name}: {e}")

        # Calculate performance metrics
        games_completed = len(game_results)
        average_efficiency = total_score / max(total_moves, 1)
        average_score = total_score / max(games_completed, 1)
        max_tile = max(highest_tiles) if highest_tiles else 0

        return {
            'games_completed': games_completed,
            'total_score': total_score,
            'total_moves': total_moves,
            'average_efficiency': average_efficiency,
            'average_score': average_score,
            'highest_tile': max_tile,
            'game_results': game_results
        }

    def _load_algorithm_class(self, submission: StudentSubmission):
        """Load algorithm class from submission file"""
        try:
            spec = importlib.util.spec_from_file_location(
                f"student_{submission.submission_id}",
                submission.file_path
            )

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find algorithm class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, BaseAlgorithm) and
                    attr != BaseAlgorithm):
                    return attr

            return None

        except Exception as e:
            self.logger.error(f"Failed to load algorithm from {submission.file_path}: {e}")
            return None

    def _generate_leaderboard(self, results: List[Tuple[StudentSubmission, Dict]]) -> List[Dict[str, Any]]:
        """Generate leaderboard from competition results"""
        leaderboard = []

        for submission, test_results in results:
            entry = {
                'rank': 0,  # Will be set later
                'student_name': submission.student_name,
                'algorithm_name': submission.algorithm_name,
                'submission_id': submission.submission_id,
                'average_efficiency': test_results['average_efficiency'],
                'average_score': test_results['average_score'],
                'highest_tile': test_results['highest_tile'],
                'games_completed': test_results['games_completed'],
                'submission_date': submission.timestamp.isoformat()
            }
            leaderboard.append(entry)

        # Sort by average efficiency (descending)
        leaderboard.sort(key=lambda x: x['average_efficiency'], reverse=True)

        # Assign ranks
        for i, entry in enumerate(leaderboard):
            entry['rank'] = i + 1

        return leaderboard

    def _calculate_baseline_comparison(self, leaderboard: List[Dict]) -> Dict[str, float]:
        """Calculate comparison with baseline algorithms"""
        if not leaderboard:
            return {}

        best_student = leaderboard[0]

        # Compare with known baselines
        baselines = {
            'enhanced_heuristic': 2.36,  # Our optimized heuristic
            'basic_priority': 1.8,       # Simple priority algorithm
            'random': 0.5                # Random baseline
        }

        comparisons = {}
        student_efficiency = best_student['average_efficiency']

        for baseline_name, baseline_score in baselines.items():
            if baseline_score > 0:
                ratio = student_efficiency / baseline_score
                comparisons[baseline_name] = ratio

        return comparisons

    def _display_competition_results(self, results: CompetitionResults):
        """Display competition results"""
        print(f"\n🏆 COMPETITION RESULTS: {results.competition_id}")
        print("=" * 70)

        if not results.leaderboard:
            print("❌ No successful submissions")
            return

        print(f"{'Rank':<5} {'Student':<15} {'Algorithm':<20} {'Efficiency':<12} {'Highest Tile':<12}")
        print("-" * 70)

        for entry in results.leaderboard[:10]:  # Top 10
            rank = entry['rank']
            student = entry['student_name'][:14]
            algorithm = entry['algorithm_name'][:19]
            efficiency = f"{entry['average_efficiency']:.2f}"
            tile = entry['highest_tile']

            print(f"{rank:<5} {student:<15} {algorithm:<20} {efficiency:<12} {tile:<12}")

        # Baseline comparison
        if results.baseline_comparison:
            print(f"\n📊 Baseline Comparison (Best Student vs Known Algorithms):")
            best_efficiency = results.leaderboard[0]['average_efficiency']

            for baseline, ratio in results.baseline_comparison.items():
                comparison = "better" if ratio > 1.0 else "worse"
                print(f"   vs {baseline}: {ratio:.2f}x {comparison}")

        print(f"\n📁 Results saved to: {self.results_dir}/{results.competition_id}.json")

    def _save_competition_results(self, results: CompetitionResults):
        """Save competition results to file"""
        results_file = self.results_dir / f"{results.competition_id}.json"

        results_data = {
            'competition_id': results.competition_id,
            'timestamp': results.timestamp.isoformat(),
            'submissions_count': len(results.submissions),
            'leaderboard': results.leaderboard,
            'test_games': results.test_games,
            'baseline_comparison': results.baseline_comparison
        }

        try:
            with open(results_file, 'w') as f:
                json.dump(results_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save competition results: {e}")

    def _save_platform_data(self):
        """Save platform state"""
        try:
            platform_data = {
                'submissions': [asdict(s) for s in self.submissions],
                'leaderboard': self.leaderboard,
                'last_updated': datetime.now().isoformat()
            }

            with open(self.leaderboard_file, 'w') as f:
                json.dump(platform_data, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Failed to save platform data: {e}")

    def _load_platform_data(self):
        """Load existing platform data"""
        try:
            if self.leaderboard_file.exists():
                with open(self.leaderboard_file, 'r') as f:
                    data = json.load(f)

                # Load submissions
                for sub_data in data.get('submissions', []):
                    submission = StudentSubmission(
                        student_name=sub_data['student_name'],
                        algorithm_name=sub_data['algorithm_name'],
                        submission_id=sub_data['submission_id'],
                        file_path=sub_data['file_path'],
                        timestamp=datetime.fromisoformat(sub_data['timestamp']),
                        validated=sub_data.get('validated', False),
                        performance_score=sub_data.get('performance_score'),
                        ranking=sub_data.get('ranking')
                    )
                    self.submissions.append(submission)

                # Load leaderboard
                self.leaderboard = data.get('leaderboard', [])

        except Exception as e:
            self.logger.error(f"Failed to load platform data: {e}")

    def get_leaderboard(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get current leaderboard"""
        return self.leaderboard[:limit]

    def get_student_progress(self, student_name: str) -> Dict[str, Any]:
        """Get progress for specific student"""
        student_submissions = [s for s in self.submissions if s.student_name == student_name]

        if not student_submissions:
            return {'error': f'No submissions found for {student_name}'}

        # Find best submission
        best_ranking = float('inf')
        best_submission = None

        for entry in self.leaderboard:
            if entry['student_name'] == student_name and entry['rank'] < best_ranking:
                best_ranking = entry['rank']
                best_submission = entry

        return {
            'student_name': student_name,
            'total_submissions': len(student_submissions),
            'best_ranking': best_ranking if best_ranking != float('inf') else None,
            'best_submission': best_submission,
            'all_submissions': [asdict(s) for s in student_submissions]
        }

if __name__ == "__main__":
    # Demo the student platform
    print("🎓 STUDENT COMPETITION PLATFORM DEMO")
    print("=" * 50)

    platform = StudentPlatform()

    # Show current leaderboard
    leaderboard = platform.get_leaderboard()
    if leaderboard:
        print("📊 Current Leaderboard:")
        for entry in leaderboard[:5]:
            print(f"   {entry['rank']}. {entry['student_name']}: {entry['average_efficiency']:.2f}")
    else:
        print("📊 No leaderboard data available")

    print("\n✅ Student platform demo completed")