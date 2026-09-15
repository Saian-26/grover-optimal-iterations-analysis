"""
Advanced Analysis of Grover's Algorithm Optimal Iterations
Includes:
- Multiple marked elements analysis
- Noisy circuit simulation
- Comparative performance metrics
- Statistical analysis
"""

import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, amplitude_damping_error
from math import pi, sqrt, floor
from grover_optimal_analysis import GroverOptimalAnalysis
import json

class AdvancedGroverAnalysis(GroverOptimalAnalysis):
    """
    Extended analysis with multiple marked elements and noise models.
    """
    
    def __init__(self, num_qubits, marked_elements=None):
        """
        Initialize with support for multiple marked elements.
        
        Args:
            num_qubits (int): Number of qubits
            marked_elements (list): List of marked element indices
        """
        super().__init__(num_qubits, marked_elements[0] if marked_elements else 0)
        self.marked_elements = marked_elements if marked_elements else [0]
        self.num_marked = len(self.marked_elements)
    
    def oracle_multiple(self, qc, marked_elements):
        """
        Oracle for multiple marked states.
        
        Args:
            qc (QuantumCircuit): Quantum circuit
            marked_elements (list): List of marked element indices
        """
        for marked_element in marked_elements:
            target_bits = format(marked_element, f'0{self.num_qubits}b')
            
            for i, bit in enumerate(reversed(target_bits)):
                if bit == '0':
                    qc.x(i)
            
            if self.num_qubits == 1:
                qc.z(0)
            elif self.num_qubits == 2:
                qc.cz(0, 1)
            else:
                qc.mcz(list(range(self.num_qubits - 1)), self.num_qubits - 1)
            
            for i, bit in enumerate(reversed(target_bits)):
                if bit == '0':
                    qc.x(i)
    
    def grover_circuit_multiple(self, iterations):
        """
        Grover circuit for multiple marked elements.
        
        Args:
            iterations (int): Number of iterations
            
        Returns:
            QuantumCircuit: The circuit
        """
        qc = QuantumCircuit(self.num_qubits, self.num_qubits)
        
        for i in range(self.num_qubits):
            qc.h(i)
        
        for _ in range(iterations):
            self.oracle_multiple(qc, self.marked_elements)
            self.diffusion_operator(qc)
        
        for i in range(self.num_qubits):
            qc.measure(i, i)
        
        return qc
    
    def theoretical_optimal_multiple(self):
        """
        Calculate optimal iterations for multiple marked elements.
        
        Returns:
            int: Optimal iterations
        """
        return floor(pi / 4 * sqrt(self.N / self.num_marked))
    
    def run_multiple_marked_experiment(self, max_iterations=None, shots=1000):
        """
        Run experiment with multiple marked elements.
        
        Args:
            max_iterations (int): Maximum iterations
            shots (int): Number of shots
            
        Returns:
            tuple: (iterations, success_probabilities)
        """
        if max_iterations is None:
            max_iterations = self.theoretical_optimal_multiple() * 2
        
        iterations_list = list(range(max_iterations + 1))
        success_probs = []
        
        print(f"\nAnalyzing {self.num_qubits} qubits with {self.num_marked} marked elements")
        print(f"Marked elements: {self.marked_elements}")
        print(f"Theoretical optimal iterations: {self.theoretical_optimal_multiple()}\n")
        
        for num_iterations in iterations_list:
            qc = self.grover_circuit_multiple(num_iterations)
            job = self.simulator.run(qc, shots=shots)
            result = job.result()
            counts = result.get_counts(qc)
            
            success_count = 0
            for marked in self.marked_elements:
                marked_str = format(marked, f'0{self.num_qubits}b')
                success_count += counts.get(marked_str, 0)
            
            success_prob = success_count / shots
            success_probs.append(success_prob)
            
            if num_iterations % max(1, max_iterations // 10) == 0 or num_iterations <= 5:
                print(f"Iterations: {num_iterations:3d} | Success Prob: {success_prob:.4f}")
        
        return iterations_list, success_probs
    
    def create_noisy_simulator(self, depol_error_rate=0.01, decay_rate=0.01):
        """
        Create a noisy quantum simulator.
        
        Args:
            depol_error_rate (float): Depolarizing error rate
            decay_rate (float): Amplitude damping rate
            
        Returns:
            AerSimulator: Noisy simulator
        """
        noise_model = NoiseModel()
        
        # Add depolarizing error to single-qubit gates
        depol_1q = depolarizing_error(depol_error_rate, 1)
        noise_model.add_all_qubit_quantum_error(depol_1q, ['h', 'x', 'z'])
        
        # Add depolarizing error to two-qubit gates
        depol_2q = depolarizing_error(depol_error_rate * 2, 2)
        noise_model.add_all_qubit_quantum_error(depol_2q, ['cz', 'cx'])
        
        # Add amplitude damping
        damp = amplitude_damping_error(decay_rate)
        noise_model.add_all_qubit_quantum_error(damp, ['h', 'x', 'z'])
        
        return AerSimulator(noise_model=noise_model)
    
    def run_noisy_experiment(self, iterations_range, shots=1000, depol_rate=0.01):
        """
        Run experiment with noisy simulator.
        
        Args:
            iterations_range (list): Range of iterations to test
            shots (int): Number of shots
            depol_rate (float): Depolarizing error rate
            
        Returns:
            tuple: (iterations, success_probabilities)
        """
        noisy_sim = self.create_noisy_simulator(depol_error_rate=depol_rate)
        original_sim = self.simulator
        self.simulator = noisy_sim
        
        success_probs = []
        
        print(f"\nRunning noisy simulation (depol_rate={depol_rate})...")
        for num_iterations in iterations_range:
            qc = self.grover_circuit(num_iterations)
            job = self.simulator.run(qc, shots=shots)
            result = job.result()
            counts = result.get_counts(qc)
            
            marked_str = format(self.marked_element, f'0{self.num_qubits}b')
            success_count = counts.get(marked_str, 0)
            success_prob = success_count / shots
            success_probs.append(success_prob)
        
        self.simulator = original_sim
        return success_probs
    
    def compare_performance(self, num_qubits_list, shots=1000):
        """
        Compare performance across different problem sizes.
        
        Args:
            num_qubits_list (list): List of qubit counts
            shots (int): Number of shots
            
        Returns:
            dict: Performance metrics
        """
        results = {}
        
        for num_qubits in num_qubits_list:
            analyzer = GroverOptimalAnalysis(num_qubits, 0)
            theoretical_opt = analyzer.theoretical_optimal_iterations()
            
            # Run a few iterations around theoretical optimum
            test_range = max(1, theoretical_opt - 2)
            max_range = theoretical_opt + 3
            
            qc = analyzer.grover_circuit(theoretical_opt)
            job = analyzer.simulator.run(qc, shots=shots)
            result = job.result()
            counts = result.get_counts(qc)
            
            marked_str = format(0, f'0{num_qubits}b')
            success_prob = counts.get(marked_str, 0) / shots
            
            results[num_qubits] = {
                'N': 2 ** num_qubits,
                'theoretical_optimal': theoretical_opt,
                'success_probability': success_prob,
                'sqrt_N': sqrt(2 ** num_qubits)
            }
        
        return results
    
    def plot_comparison(self, results):
        """
        Plot comparison of results across problem sizes.
        
        Args:
            results (dict): Performance metrics from compare_performance
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        qubits = list(results.keys())
        N_values = [results[q]['N'] for q in qubits]
        opt_iters = [results[q]['theoretical_optimal'] for q in qubits]
        success_probs = [results[q]['success_probability'] for q in qubits]
        
        # Plot 1: Optimal iterations vs problem size
        axes[0].plot(qubits, opt_iters, 'bo-', linewidth=2, markersize=8)
        axes[0].set_xlabel('Number of Qubits', fontsize=11)
        axes[0].set_ylabel('Optimal Iterations', fontsize=11)
        axes[0].set_title('Optimal Iterations vs Problem Size', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Success probability comparison
        axes[1].plot(qubits, success_probs, 'ro-', linewidth=2, markersize=8)
        axes[1].set_xlabel('Number of Qubits', fontsize=11)
        axes[1].set_ylabel('Success Probability at Theoretical Optimum', fontsize=11)
        axes[1].set_title('Success Probability vs Problem Size', fontsize=12, fontweight='bold')
        axes[1].set_ylim([0, 1.05])
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('grover_comparison.png', dpi=300, bbox_inches='tight')
        print("Comparison plot saved as 'grover_comparison.png'")
        plt.show()


def main():
    """Run advanced analysis examples."""
    
    print("=" * 70)
    print("ADVANCED GROVER ANALYSIS")
    print("=" * 70)
    
    # Example 1: Multiple marked elements
    print("\n[1] MULTIPLE MARKED ELEMENTS ANALYSIS")
    print("-" * 70)
    
    analyzer = AdvancedGroverAnalysis(num_qubits=3, marked_elements=[0, 3, 5])
    iterations, probs = analyzer.run_multiple_marked_experiment(shots=1000)
    analyzer.analyze_success_curve(iterations, probs)
    
    # Example 2: Noisy circuit analysis
    print("\n[2] NOISY CIRCUIT ANALYSIS")
    print("-" * 70)
    
    analyzer_clean = AdvancedGroverAnalysis(num_qubits=2, marked_elements=[0])
    theoretical_opt = analyzer_clean.theoretical_optimal_iterations()
    iterations_test = list(range(max(1, theoretical_opt - 3), theoretical_opt + 5))
    
    clean_probs = []
    for it in iterations_test:
        qc = analyzer_clean.grover_circuit(it)
        job = analyzer_clean.simulator.run(qc, shots=1000)
        result = job.result()
        counts = result.get_counts(qc)
        clean_probs.append(counts.get('00', 0) / 1000)
    
    noisy_probs = analyzer_clean.run_noisy_experiment(iterations_test, depol_rate=0.02)
    
    plt.figure(figsize=(10, 6))
    plt.plot(iterations_test, clean_probs, 'b-o', label='Ideal Circuit', linewidth=2, markersize=8)
    plt.plot(iterations_test, noisy_probs, 'r-s', label='Noisy Circuit (2% error)', linewidth=2, markersize=8)
    plt.xlabel('Number of Iterations', fontsize=12)
    plt.ylabel('Success Probability', fontsize=12)
    plt.title('Impact of Noise on Grover Algorithm Performance', fontsize=13, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('grover_noise_comparison.png', dpi=300, bbox_inches='tight')
    print("Noise comparison plot saved as 'grover_noise_comparison.png'")
    plt.show()
    
    # Example 3: Performance comparison
    print("\n[3] PERFORMANCE COMPARISON ACROSS PROBLEM SIZES")
    print("-" * 70)
    
    analyzer_perf = AdvancedGroverAnalysis(num_qubits=2)
    results = analyzer_perf.compare_performance([2, 3, 4, 5])
    
    print("\nPerformance Metrics:")
    for num_qubits, metrics in results.items():
        print(f"\nQubits: {num_qubits}")
        print(f"  Search Space (N): {metrics['N']}")
        print(f"  Optimal Iterations: {metrics['theoretical_optimal']}")
        print(f"  Success Probability: {metrics['success_probability']:.4f}")
        print(f"  sqrt(N): {metrics['sqrt_N']:.2f}")
    
    analyzer_perf.plot_comparison(results)
    
    print("\n" + "=" * 70)
    print("Advanced analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
