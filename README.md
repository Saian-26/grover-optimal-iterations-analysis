# Experimental Analysis of Optimal Grover Iterations

A comprehensive Qiskit-based implementation for analyzing and optimizing the number of iterations in Grover's quantum search algorithm.

## Overview

Grover's algorithm provides a quadratic speedup for unstructured quantum search problems. A critical aspect of the algorithm is determining the **optimal number of iterations** to maximize the probability of finding the marked state. This project provides experimental tools to:

1. **Analyze theoretical optimal iterations** using the formula: $k_{opt} = \lfloor \frac{\pi}{4}\sqrt{\frac{N}{M}} \rfloor$
2. **Measure empirical success probabilities** across varying iteration counts
3. **Compare theoretical predictions with experimental results**
4. **Study the effects of noise** on algorithm performance
5. **Perform statistical analysis** with confidence intervals and comparative metrics

## Project Structure

```
.
├── grover_optimal_analysis.py      # Main analysis framework
├── advanced_analysis.py            # Multiple marked elements, noise models
├── statistical_analysis.py         # Statistical tests and metrics
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone this repository:
```bash
git clone https://github.com/Saian-26/grover-optimal-iterations-analysis.git
cd grover-optimal-iterations-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Analysis

Run the main analysis for different problem sizes:

```python
from grover_optimal_analysis import GroverOptimalAnalysis

# Analyze 3-qubit system (search space size = 8)
analyzer = GroverOptimalAnalysis(num_qubits=3, marked_element=0)

# Run experiments
iterations, success_probs = analyzer.run_experiment(shots=1000)

# Analyze and plot results
analyzer.analyze_success_curve(iterations, success_probs)
analyzer.plot_results(iterations, success_probs)
```

### Advanced Analysis

Analyze multiple marked elements with noise simulation:

```python
from advanced_analysis import AdvancedGroverAnalysis

# Multiple marked elements
analyzer = AdvancedGroverAnalysis(num_qubits=3, marked_elements=[0, 3, 5])
iterations, probs = analyzer.run_multiple_marked_experiment(shots=1000)

# Noisy circuit analysis
noisy_probs = analyzer.run_noisy_experiment(iterations, depol_rate=0.02)
```

### Statistical Analysis

Perform rigorous statistical analysis:

```python
from statistical_analysis import StatisticalAnalysis

analyzer = StatisticalAnalysis(num_qubits=3, num_runs=20, shots_per_run=1000)

# Compare multiple iteration counts statistically
results = analyzer.compare_iterations_statistically([2, 3, 4, 5])

# Calculate confidence intervals
ci_data = analyzer.confidence_interval_analysis(iterations=3, confidence=0.95)
```

## Key Concepts

### Theoretical Optimal Iterations

For **M** marked states in a search space of size **N**, the optimal number of Grover iterations is:

$$k_{opt} = \left\lfloor \frac{\pi}{4}\sqrt{\frac{N}{M}} \right\rfloor$$

### Success Probability Evolution

The success probability follows a sinusoidal pattern:

$$P(k) = \sin^2((2k+1)\theta)$$

where $\sin(\theta) = \frac{1}{\sqrt{N}}$ and $k$ is the number of iterations.

### Key Findings

1. **Optimal Performance**: The empirically determined optimal iteration count closely matches theoretical predictions
2. **Over-iteration Penalty**: Exceeding the optimal iterations significantly reduces success probability
3. **Quadratic Speedup**: Grover achieves O(√N) speedup compared to classical O(N) search
4. **Noise Sensitivity**: Algorithm performance degrades with increasing error rates

## Usage Examples

### Example 1: Basic 4-Qubit Analysis

```bash
python grover_optimal_analysis.py
```

This runs analysis for 2, 3, and 4 qubits, generating plots showing success probability vs iterations.

### Example 2: Advanced Multi-Element Analysis

```bash
python advanced_analysis.py
```

Analyzes:
- Multiple marked elements
- Noisy quantum circuits
- Performance across problem sizes

### Example 3: Statistical Analysis with Confidence Intervals

```bash
python statistical_analysis.py
```

Provides:
- Multiple independent runs
- Confidence interval calculations
- Theoretical vs empirical comparison

## Output

The scripts generate:

1. **Console Output**: Real-time progress and analysis results
2. **Plots**: High-resolution visualizations
   - `grover_optimal_iterations.png` - Success probability curve
   - `grover_comparison.png` - Cross-size comparison
   - `grover_noise_comparison.png` - Noise impact analysis

## API Reference

### GroverOptimalAnalysis

```python
class GroverOptimalAnalysis:
    def __init__(self, num_qubits, marked_element=None)
    def run_experiment(self, max_iterations=None, shots=1000)
    def theoretical_optimal_iterations(self, num_solutions=1)
    def analyze_success_curve(self, iterations, success_probs)
    def plot_results(self, iterations, success_probs)
```

### AdvancedGroverAnalysis

```python
class AdvancedGroverAnalysis(GroverOptimalAnalysis):
    def run_multiple_marked_experiment(self, max_iterations=None, shots=1000)
    def create_noisy_simulator(self, depol_error_rate=0.01, decay_rate=0.01)
    def run_noisy_experiment(self, iterations_range, shots=1000, depol_rate=0.01)
    def compare_performance(self, num_qubits_list, shots=1000)
```

### StatisticalAnalysis

```python
class StatisticalAnalysis:
    def run_statistical_experiment(self, iterations, verbose=True)
    def compare_iterations_statistically(self, iterations_list, verbose=True)
    def theoretical_vs_empirical(self, iterations_list, verbose=True)
    def confidence_interval_analysis(self, iterations, confidence=0.95)
```

## Theoretical Background

### Grover's Algorithm Steps

1. **Initialization**: Create equal superposition of all basis states
   $$|\psi\rangle = \frac{1}{\sqrt{N}} \sum_{x=0}^{N-1} |x\rangle$$

2. **Oracle Query**: Apply phase flip to marked state(s)
   $$U_f |x\rangle = (-1)^{f(x)} |x\rangle$$

3. **Diffusion Operator**: Inversion about average amplitude
   $$D = 2|\psi\rangle\langle\psi| - I$$

4. **Iteration**: Repeat oracle + diffusion k times

5. **Measurement**: Measure to obtain marked state with high probability

### Amplitude Amplification

Grover's algorithm amplifies the amplitude of the marked state while suppressing others:
- Initial amplitude: $\frac{1}{\sqrt{N}}$
- After k iterations: $\sin((2k+1)\theta)$ where $\sin(\theta) \approx \frac{1}{\sqrt{N}}$

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Query Complexity | O(√N) |
| Circuit Depth | O(√N) |
| Space Complexity | O(log N) |
| Optimal Iterations | $\frac{\pi}{4}\sqrt{N}$ |
| Peak Success Prob | > 99% (ideal) |

## References

1. **Grover, L.K. (1996)** - "A fast quantum mechanical algorithm for database search"
   - Original algorithm proposal
   - STOC 1996

2. **Nielsen & Chuang (2010)** - "Quantum Computation and Quantum Information"
   - Chapter 6: Quantum Search by a Quantum Computer
   - Cambridge University Press

3. **Brassard et al. (2000)** - "Quantum Amplitude Amplification and Estimation"
   - Generalization of Grover's algorithm
   - arXiv:quant-ph/0005055

4. **Boyer et al. (1998)** - "Tight bounds on quantum searching"
   - Optimal iteration analysis
   - Fortschritte der Physik

## Hardware Considerations

### Ideal Simulator (Current)
- Used for theoretical analysis
- 100% fidelity operations
- No decoherence or gate errors

### Noisy Simulation (Advanced)
- Depolarizing errors on single/two-qubit gates
- Amplitude damping (T1 relaxation)
- Configurable error rates

### Real Hardware (Future)
- IBM Quantum devices
- Error mitigation techniques
- Limited qubit counts

## Limitations and Future Work

### Current Limitations
- Simulator limited to ~20 qubits
- No error mitigation strategies
- Fixed oracle structure

### Future Enhancements
- Integration with real quantum hardware (IBMQ, IonQ)
- Error mitigation techniques (ZNE, MEAS, etc.)
- Parameterized oracle support
- Adaptive iteration counting
- Hybrid classical-quantum optimization

## Contributing

Contributions are welcome! Areas of interest:
- Additional noise models
- Real hardware testing
- Performance optimizations
- Documentation improvements

## License

MIT License - See LICENSE file for details

## Citation

If you use this code in your research, please cite:

```bibtex
@software{grover_optimal_iterations_2024,
  title={Experimental Analysis of Optimal Grover Iterations},
  author={Sai Anand},
  url={https://github.com/Saian-26/grover-optimal-iterations-analysis},
  year={2024}
}
```

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: tsanand2686@gmail.com

## Acknowledgments

- IBM Qiskit team for the excellent quantum computing framework
- Quantum computing community for theoretical foundations
- Contributors and testers
