"""
Statistical Analysis of Grover Algorithm Results
Performs statistical tests and generates comprehensive reports.
"""

import numpy as np
from scipy import stats
import json
from grover_optimal_analysis import GroverOptimalAnalysis
from math import pi, sqrt, floor

class StatisticalAnalysis:
    """
    Perform statistical analysis on Grover algorithm results.
    """
    
    def __init__(self, num_qubits, num_runs=10, shots_per_run=1000):
        """
        Initialize statistical analysis.
        
        Args:
            num_qubits (int): Number of qubits
            num_runs (int): Number of independent runs
            shots_per_run (int): Shots per run
        """
        self.num_qubits = num_qubits
        self.num_runs = num_runs
        self.shots_per_run = shots_per_run
        self.analyzer = GroverOptimalAnalysis(num_qubits)
    
    def run_statistical_experiment(self, iterations, verbose=True):
        """
        Run multiple independent experiments for statistical analysis.
        
        Args:
            iterations (int): Number of Grover iterations
            verbose (bool): Print progress
            
        Returns:
            dict: Statistical results
        """
        results = []
        
        if verbose:
            print(f"Running {self.num_runs} independent experiments...")
            print(f"Iterations: {iterations}, Shots per run: {self.shots_per_run}\n")
        
        for run_num in range(self.num_runs):
            qc = self.analyzer.grover_circuit(iterations)
            job = self.analyzer.simulator.run(qc, shots=self.shots_per_run)
            result = job.result()
            counts = result.get_counts(qc)
            
            marked_str = format(0, f'0{self.num_qubits}b')
            success_count = counts.get(marked_str, 0)
            success_prob = success_count / self.shots_per_run
            results.append(success_prob)
            
            if verbose and (run_num + 1) % max(1, self.num_runs // 5) == 0:
                print(f"Run {run_num + 1}/{self.num_runs}: Success Prob = {success_prob:.4f}")
        
        return self._calculate_statistics(results)
    
    def _calculate_statistics(self, results):
        """
        Calculate statistical metrics.
        
        Args:
            results (list): List of success probabilities
            
        Returns:
            dict: Statistical metrics
        """
        results_array = np.array(results)
        
        return {
            'mean': np.mean(results_array),
            'std': np.std(results_array),
            'median': np.median(results_array),
            'min': np.min(results_array),
            'max': np.max(results_array),
            'q25': np.percentile(results_array, 25),
            'q75': np.percentile(results_array, 75),
            'all_results': results
        }
    
    def compare_iterations_statistically(self, iterations_list, verbose=True):
        """
        Compare success probabilities across different iteration counts.
        
        Args:
            iterations_list (list): List of iteration counts to test
            verbose (bool): Print progress
            
        Returns:
            dict: Comparison results
        """
        comparison_results = {}
        
        if verbose:
            print(f"\nStatistical comparison across iterations")
            print(f"Qubits: {self.num_qubits}")
            print(f"Runs per iteration: {self.num_runs}\n")
        
        for iterations in iterations_list:
            stats_dict = self.run_statistical_experiment(iterations, verbose=False)
            comparison_results[iterations] = stats_dict
            
            if verbose:
                print(f"Iterations: {iterations:2d} | Mean: {stats_dict['mean']:.4f} ± {stats_dict['std']:.4f} | "
                      f"Range: [{stats_dict['min']:.4f}, {stats_dict['max']:.4f}]")
        
        return comparison_results
    
    def theoretical_vs_empirical(self, iterations_list, verbose=True):
        """
        Compare theoretical predictions with empirical results.
        
        Args:
            iterations_list (list): List of iteration counts
            verbose (bool): Print progress
            
        Returns:
            dict: Comparison data
        """
        comparison = {}
        theoretical_opt = self.analyzer.theoretical_optimal_iterations()
        
        if verbose:
            print("\n" + "="*70)
            print("THEORETICAL vs EMPIRICAL ANALYSIS")
            print("="*70)
            print(f"Qubits: {self.num_qubits}")
            print(f"Search Space Size: {self.analyzer.N}")
            print(f"Theoretical Optimal Iterations: {theoretical_opt}\n")
        
        empirical_data = self.compare_iterations_statistically(iterations_list, verbose=verbose)
        
        for iterations, stats_dict in empirical_data.items():
            theoretical_prob = self._calculate_theoretical_probability(iterations)
            
            comparison[iterations] = {
                'empirical_mean': stats_dict['mean'],
                'empirical_std': stats_dict['std'],
                'empirical_range': (stats_dict['min'], stats_dict['max']),
                'theoretical': theoretical_prob,
                'error': abs(stats_dict['mean'] - theoretical_prob),
                'relative_error': abs(stats_dict['mean'] - theoretical_prob) / theoretical_prob if theoretical_prob > 0 else 0
            }
        
        return comparison
    
    def _calculate_theoretical_probability(self, iterations):
        """
        Calculate theoretical success probability.
        
        Args:
            iterations (int): Number of iterations
            
        Returns:
            float: Theoretical probability
        """
        theta = np.arcsin(1 / np.sqrt(self.analyzer.N))
        amplitude = np.sin((2 * iterations + 1) * theta)
        probability = amplitude ** 2
        return probability
    
    def confidence_interval_analysis(self, iterations, confidence=0.95):
        """
        Calculate confidence intervals for success probability.
        
        Args:
            iterations (int): Number of iterations
            confidence (float): Confidence level (0.95 = 95%)
            
        Returns:
            dict: Confidence interval data
        """
        results = self.run_statistical_experiment(iterations, verbose=False)
        results_array = np.array(results['all_results'])
        
        mean = results['mean']
        std_error = results['std'] / np.sqrt(len(results_array))
        
        z_score = stats.norm.ppf((1 + confidence) / 2)
        margin_of_error = z_score * std_error
        
        ci_lower = mean - margin_of_error
        ci_upper = mean + margin_of_error
        
        return {
            'mean': mean,
            'std_error': std_error,
            'confidence_level': confidence,
            'margin_of_error': margin_of_error,
            'ci_lower': max(0, ci_lower),
            'ci_upper': min(1, ci_upper),
            'ci_range': (max(0, ci_lower), min(1, ci_upper))
        }
    
    def print_summary_report(self, iterations_list):
        """
        Print comprehensive summary report.
        
        Args:
            iterations_list (list): List of iterations to analyze
        """
        theoretical_opt = self.analyzer.theoretical_optimal_iterations()
        comparison = self.theoretical_vs_empirical(iterations_list)
        
        print("\n" + "="*70)
        print("DETAILED ANALYSIS REPORT")
        print("="*70)
        
        print(f"\nSystem Configuration:")
        print(f"  Qubits: {self.num_qubits}")
        print(f"  Search Space Size (N): {self.analyzer.N}")
        print(f"  Independent Runs: {self.num_runs}")
        print(f"  Shots per Run: {self.shots_per_run}")
        print(f"  Total Measurements: {self.num_runs * self.shots_per_run}")
        
        print(f"\nTheoretical Predictions:")
        print(f"  Optimal Iterations: {theoretical_opt}")
        print(f"  Theoretical Prob at Optimum: {self._calculate_theoretical_probability(theoretical_opt):.4f}")
        
        print(f"\nEmpirical Results:")
        print(f"{'Iter':>6} {'Mean':>10} {'Std':>10} {'Min':>10} {'Max':>10} {'Theory':>10} {'Error':>10}")
        print("-" * 70)
        
        for iterations in sorted(comparison.keys()):
            data = comparison[iterations]
            print(f"{iterations:6d} {data['empirical_mean']:10.4f} {data['empirical_std']:10.4f} "
                  f"{min(data['empirical_range']):10.4f} {max(data['empirical_range']):10.4f} "
                  f"{data['theoretical']:10.4f} {data['error']:10.4f}")
        
        print("\n" + "="*70)


def main():
    """Run statistical analysis examples."""
    
    print("\n" + "#"*70)
    print("# STATISTICAL ANALYSIS OF GROVER ALGORITHM")
    print("#"*70)
    
    # Analyze 3 qubits
    analyzer = StatisticalAnalysis(num_qubits=3, num_runs=20, shots_per_run=1000)
    theoretical_opt = analyzer.analyzer.theoretical_optimal_iterations()
    
    # Test iterations around theoretical optimum
    iterations_to_test = [max(0, theoretical_opt - 2), theoretical_opt - 1, theoretical_opt, 
                         theoretical_opt + 1, theoretical_opt + 2]
    
    # Run full analysis
    analyzer.print_summary_report(iterations_to_test)
    
    # Confidence interval for optimal iterations
    print(f"\n\n[CONFIDENCE INTERVAL ANALYSIS]")
    print("-"*70)
    ci_data = analyzer.confidence_interval_analysis(theoretical_opt, confidence=0.95)
    print(f"\nSuccess Probability at Optimal Iterations ({theoretical_opt}):")
    print(f"  Mean: {ci_data['mean']:.4f}")
    print(f"  95% Confidence Interval: [{ci_data['ci_lower']:.4f}, {ci_data['ci_upper']:.4f}]")
    print(f"  Margin of Error: ±{ci_data['margin_of_error']:.4f}")


if __name__ == "__main__":
    main()
