"""
Experimental Analysis of the Optimal Number of Grover Iterations
This script analyzes how the number of Grover iterations affects the success probability
of finding a marked state in an unstructured search problem.
"""

import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.primitives import Sampler
from math import pi, sqrt, floor, sin

class GroverOptimalAnalysis:
    """
    Analyze the optimal number of Grover iterations for different problem sizes.
    """
    
    def __init__(self, num_qubits, marked_element=None):
        """
        Initialize Grover's algorithm analysis.
        
        Args:
            num_qubits (int): Number of qubits (search space size N = 2^num_qubits)
            marked_element (int): The element to mark (default: 0)
        """
        self.num_qubits = num_qubits
        self.N = 2 ** num_qubits  # Search space size
        self.marked_element = marked_element if marked_element is not None else 0
        self.simulator = AerSimulator()
        
    def oracle(self, qc, marked_element):
        """
        Create an oracle that marks the target state with a phase flip.
        
        Args:
            qc (QuantumCircuit): Quantum circuit
            marked_element (int): The element to mark
        """
        # Convert marked element to binary representation
        target_bits = format(marked_element, f'0{self.num_qubits}b')
        
        # Apply X gates to qubits that should be 0 in the target state
        for i, bit in enumerate(reversed(target_bits)):
            if bit == '0':
                qc.x(i)
        
        # Multi-controlled Z gate (phase flip)
        if self.num_qubits == 1:
            qc.z(0)
        elif self.num_qubits == 2:
            qc.cz(0, 1)
        else:
            # For more qubits, use multi-controlled Z
            qc.mcz(list(range(self.num_qubits - 1)), self.num_qubits - 1)
        
        # Undo X gates
        for i, bit in enumerate(reversed(target_bits)):
            if bit == '0':
                qc.x(i)
    
    def diffusion_operator(self, qc):
        """
        Create the diffusion operator (inversion about average).
        
        Args:
            qc (QuantumCircuit): Quantum circuit
        """
        # Apply Hadamard gates
        for i in range(self.num_qubits):
            qc.h(i)
        
        # Apply X gates
        for i in range(self.num_qubits):
            qc.x(i)
        
        # Multi-controlled Z gate
        if self.num_qubits == 1:
            qc.z(0)
        elif self.num_qubits == 2:
            qc.cz(0, 1)
        else:
            qc.mcz(list(range(self.num_qubits - 1)), self.num_qubits - 1)
        
        # Apply X gates
        for i in range(self.num_qubits):
            qc.x(i)
        
        # Apply Hadamard gates
        for i in range(self.num_qubits):
            qc.h(i)
    
    def grover_circuit(self, iterations):
        """
        Create a Grover circuit with the specified number of iterations.
        
        Args:
            iterations (int): Number of Grover iterations
            
        Returns:
            QuantumCircuit: The complete Grover circuit
        """
        qc = QuantumCircuit(self.num_qubits, self.num_qubits, name=f'Grover_{iterations}')
        
        # Initialize with Hadamard gates (equal superposition)
        for i in range(self.num_qubits):
            qc.h(i)
        
        # Apply Grover iterations
        for _ in range(iterations):
            self.oracle(qc, self.marked_element)
            self.diffusion_operator(qc)
        
        # Measure
        for i in range(self.num_qubits):
            qc.measure(i, i)
        
        return qc
    
    def theoretical_optimal_iterations(self, num_solutions=1):
        """
        Calculate theoretical optimal number of iterations.
        
        Args:
            num_solutions (int): Number of marked states
            
        Returns:
            int: Optimal number of iterations
        """
        return floor(pi / 4 * sqrt(self.N / num_solutions))
    
    def run_experiment(self, max_iterations=None, shots=1000):
        """
        Run experiments varying the number of iterations.
        
        Args:
            max_iterations (int): Maximum number of iterations to test
            shots (int): Number of shots per experiment
            
        Returns:
            tuple: (iterations, success_probabilities)
        """
        if max_iterations is None:
            max_iterations = self.theoretical_optimal_iterations() * 2
        
        iterations_list = list(range(max_iterations + 1))
        success_probs = []
        
        print(f"Running Grover algorithm for {self.num_qubits} qubits...")
        print(f"Search space size: {self.N}")
        print(f"Marked element: {self.marked_element}")
        print(f"Theoretical optimal iterations: {self.theoretical_optimal_iterations()}\n")
        
        for num_iterations in iterations_list:
            # Create circuit
            qc = self.grover_circuit(num_iterations)
            
            # Run on simulator
            job = self.simulator.run(qc, shots=shots)
            result = job.result()
            counts = result.get_counts(qc)
            
            # Calculate success probability
            marked_str = format(self.marked_element, f'0{self.num_qubits}b')
            success_count = counts.get(marked_str, 0)
            success_prob = success_count / shots
            success_probs.append(success_prob)
            
            if num_iterations % max(1, max_iterations // 10) == 0 or num_iterations <= 5:
                print(f"Iterations: {num_iterations:3d} | Success Prob: {success_prob:.4f}")
        
        print()
        return iterations_list, success_probs
    
    def plot_results(self, iterations, success_probs):
        """
        Plot the success probability vs number of iterations.
        
        Args:
            iterations (list): List of iteration counts
            success_probs (list): List of success probabilities
        """
        theoretical_opt = self.theoretical_optimal_iterations()
        max_prob = max(success_probs)
        max_iter = iterations[success_probs.index(max_prob)]
        
        plt.figure(figsize=(12, 6))
        
        # Plot success probability
        plt.plot(iterations, success_probs, 'b-o', linewidth=2, markersize=6, label='Experimental')
        
        # Plot theoretical optimum
        plt.axvline(x=theoretical_opt, color='r', linestyle='--', linewidth=2, label=f'Theoretical Optimum ({theoretical_opt})')
        
        # Plot empirical maximum
        plt.axvline(x=max_iter, color='g', linestyle=':', linewidth=2, label=f'Empirical Maximum ({max_iter})')
        
        plt.xlabel('Number of Grover Iterations', fontsize=12)
        plt.ylabel('Success Probability', fontsize=12)
        plt.title(f'Grover Algorithm: Optimal Iterations Analysis\n({self.num_qubits} qubits, Search Space Size: {self.N})', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=11)
        plt.ylim([0, 1.05])
        
        # Add text annotation
        textstr = f'Max Probability: {max_prob:.4f}\nEmpirical Optimum: {max_iter}\nTheoretical Optimum: {theoretical_opt}'
        plt.text(0.98, 0.05, textstr, transform=plt.gca().transAxes, fontsize=10,
                verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('grover_optimal_iterations.png', dpi=300, bbox_inches='tight')
        print("Plot saved as 'grover_optimal_iterations.png'")
        plt.show()
    
    def analyze_success_curve(self, iterations, success_probs):
        """
        Analyze the success probability curve.
        
        Args:
            iterations (list): List of iteration counts
            success_probs (list): List of success probabilities
        """
        max_prob = max(success_probs)
        max_iter = iterations[success_probs.index(max_prob)]
        theoretical_opt = self.theoretical_optimal_iterations()
        
        print("=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        print(f"Number of Qubits: {self.num_qubits}")
        print(f"Search Space Size (N): {self.N}")
        print(f"Marked Element: {self.marked_element}")
        print(f"\nTheoretical Optimal Iterations: {theoretical_opt}")
        print(f"Empirical Optimal Iterations: {max_iter}")
        print(f"Difference: {abs(max_iter - theoretical_opt)}")
        print(f"\nMaximum Success Probability: {max_prob:.4f}")
        print(f"Success Probability at Theoretical Optimum: {success_probs[theoretical_opt]:.4f}")
        
        # Calculate accuracy
        if theoretical_opt < len(success_probs):
            accuracy_ratio = success_probs[theoretical_opt] / max_prob if max_prob > 0 else 0
            print(f"Accuracy Ratio (Theoretical/Empirical): {accuracy_ratio:.2%}")
        
        print("=" * 60)


def main():
    """Main function to run the Grover optimal iterations analysis."""
    
    # Test different problem sizes
    problem_sizes = [2, 3, 4]  # Number of qubits
    
    for num_qubits in problem_sizes:
        print(f"\n{'='*60}")
        print(f"ANALYZING {num_qubits} QUBITS")
        print(f"{'='*60}\n")
        
        # Create analyzer
        analyzer = GroverOptimalAnalysis(num_qubits, marked_element=0)
        
        # Run experiment
        iterations, success_probs = analyzer.run_experiment(shots=1000)
        
        # Analyze results
        analyzer.analyze_success_curve(iterations, success_probs)
        
        # Plot results
        analyzer.plot_results(iterations, success_probs)


if __name__ == "__main__":
    main()
