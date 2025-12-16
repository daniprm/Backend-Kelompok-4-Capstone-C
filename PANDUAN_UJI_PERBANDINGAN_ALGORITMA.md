# PANDUAN LENGKAP UJI PERBANDINGAN ALGORITMA

---

## 1. OVERVIEW UJI PERBANDINGAN

### 1.1 Tujuan Uji Perbandingan

Uji perbandingan (comparative testing) bertujuan untuk:

1. **Membuktikan keunggulan** algoritma HGA yang dikembangkan dibanding baseline algorithms
2. **Mengukur improvement** secara kuantitatif (berapa persen lebih baik)
3. **Memvalidasi trade-off** antara kualitas solusi vs waktu komputasi
4. **Memberikan justifikasi ilmiah** mengapa menggunakan HGA dibanding algoritma sederhana

### 1.2 Algoritma yang Akan Dibandingkan

```
┌────────────────────────────────────────────────────────┐
│  1. Random Search (Baseline)                           │
│     - Complexity: O(n)                                 │
│     - Expected Quality: Worst                          │
│     - Use Case: Lower bound performance                │
├────────────────────────────────────────────────────────┤
│  2. Greedy Nearest Neighbor (Baseline)                 │
│     - Complexity: O(n²)                                │
│     - Expected Quality: Moderate                       │
│     - Use Case: Fast approximation benchmark           │
├────────────────────────────────────────────────────────┤
│  3. Pure Genetic Algorithm (Intermediate)              │
│     - Complexity: O(pop × gen × n²)                    │
│     - Expected Quality: Good                           │
│     - Use Case: Prove benefit of GA component          │
├────────────────────────────────────────────────────────┤
│  4. Hybrid Genetic Algorithm (Proposed)                │
│     - Complexity: O(pop × gen × n² × 2opt_iter)        │
│     - Expected Quality: Best                           │
│     - Use Case: Final solution                         │
└────────────────────────────────────────────────────────┘
```

---

## 2. IMPLEMENTASI BASELINE ALGORITHMS

### 2.1 Random Search

**File: `algorithms/baseline_random.py`**

```python
"""
Random Search Algorithm
Generates random valid routes and keeps the best one found.
"""

import random
from typing import List, Tuple
from models.destination import Destination
from models.route import Route

class RandomSearch:
    """
    Baseline algorithm: Random search with constraint satisfaction
    """

    def __init__(self, destinations: List[Destination]):
        """
        Initialize Random Search

        Args:
            destinations: List of all available destinations
        """
        self.destinations = destinations
        self._categorize_destinations()

    def _categorize_destinations(self):
        """Group destinations by category for constraint satisfaction"""
        self.makanan_berat = []
        self.makanan_ringan = []
        self.non_kuliner = []
        self.oleh_oleh = []
        self.all_category = []

        for dest in self.destinations:
            categories = [k.lower() for k in dest.kategori]

            if 'makanan berat' in categories:
                self.makanan_berat.append(dest)
            if 'makanan ringan' in categories:
                self.makanan_ringan.append(dest)
            if 'non-kuliner' in categories:
                self.non_kuliner.append(dest)
            if 'oleh-oleh' in categories:
                self.oleh_oleh.append(dest)
            if 'all' in categories:
                self.all_category.append(dest)

    def _generate_random_valid_route(self, start_point: Tuple[float, float]) -> Route:
        """
        Generate one random valid route that satisfies constraints

        Constraint pattern: K, C, W, K, W, C, K, O

        Args:
            start_point: Starting location (latitude, longitude)

        Returns:
            Valid Route object
        """
        route_destinations = []

        # Position 1: Makanan Berat (K1)
        route_destinations.append(random.choice(self.makanan_berat))

        # Position 2: Makanan Ringan (C1)
        route_destinations.append(random.choice(self.makanan_ringan))

        # Position 3: Non-Kuliner or All (W1)
        candidates = self.non_kuliner + self.all_category
        route_destinations.append(random.choice(candidates))

        # Position 4: Makanan Berat, different from K1 (K2)
        candidates = [d for d in self.makanan_berat if d not in route_destinations]
        route_destinations.append(random.choice(candidates))

        # Position 5: Non-Kuliner or All, different from W1 (W2)
        candidates = [d for d in (self.non_kuliner + self.all_category)
                      if d not in route_destinations]
        route_destinations.append(random.choice(candidates))

        # Position 6: Makanan Ringan, different from C1 (C2)
        candidates = [d for d in self.makanan_ringan if d not in route_destinations]
        route_destinations.append(random.choice(candidates))

        # Position 7: Makanan Berat, different from K1 and K2 (K3)
        candidates = [d for d in self.makanan_berat if d not in route_destinations]
        route_destinations.append(random.choice(candidates))

        # Position 8: Oleh-oleh or All (O)
        candidates = [d for d in (self.oleh_oleh + self.all_category)
                      if d not in route_destinations]
        route_destinations.append(random.choice(candidates))

        return Route(start_point, route_destinations)

    def run(self,
            start_point: Tuple[float, float],
            num_iterations: int = 1000,
            verbose: bool = False) -> Route:
        """
        Run random search for specified number of iterations

        Args:
            start_point: Starting location
            num_iterations: Number of random routes to generate
            verbose: Print progress

        Returns:
            Best route found
        """
        best_route = None
        best_distance = float('inf')

        for i in range(num_iterations):
            # Generate random route
            route = self._generate_random_valid_route(start_point)
            distance = route.calculate_total_distance()

            # Update best if better
            if distance < best_distance:
                best_distance = distance
                best_route = route

                if verbose and i % 100 == 0:
                    print(f"Iteration {i}: Best distance = {best_distance:.2f} km")

        if verbose:
            print(f"\nFinal best distance: {best_distance:.2f} km")

        return best_route


# Example usage
if __name__ == "__main__":
    from utils.data_loader import load_destinations_from_jsonl

    # Load destinations
    destinations = load_destinations_from_jsonl("data/data_wisata.jsonl")

    # Initialize Random Search
    random_search = RandomSearch(destinations)

    # Test location (Surabaya center)
    start_point = (-7.2575, 112.7521)

    # Run random search
    best_route = random_search.run(
        start_point=start_point,
        num_iterations=24000,  # Same as HGA fitness evaluations (600×40)
        verbose=True
    )

    print(f"\nBest route found:")
    for i, dest in enumerate(best_route.destinations, 1):
        print(f"{i}. {dest.nama}")
```

---

### 2.2 Greedy Nearest Neighbor

**File: `algorithms/baseline_greedy.py`**

```python
"""
Greedy Nearest Neighbor Algorithm
Always selects the nearest valid destination for each position.
"""

from typing import List, Tuple
from models.destination import Destination
from models.route import Route
from utils.distance import DistanceCalculator

class GreedyNearestNeighbor:
    """
    Baseline algorithm: Greedy nearest neighbor with constraints
    """

    def __init__(self, destinations: List[Destination]):
        """
        Initialize Greedy Nearest Neighbor

        Args:
            destinations: List of all available destinations
        """
        self.destinations = destinations
        self.distance_calculator = DistanceCalculator()
        self._categorize_destinations()

    def _categorize_destinations(self):
        """Group destinations by category"""
        self.makanan_berat = []
        self.makanan_ringan = []
        self.non_kuliner = []
        self.oleh_oleh = []
        self.all_category = []

        for dest in self.destinations:
            categories = [k.lower() for k in dest.kategori]

            if 'makanan berat' in categories:
                self.makanan_berat.append(dest)
            if 'makanan ringan' in categories:
                self.makanan_ringan.append(dest)
            if 'non-kuliner' in categories:
                self.non_kuliner.append(dest)
            if 'oleh-oleh' in categories:
                self.oleh_oleh.append(dest)
            if 'all' in categories:
                self.all_category.append(dest)

    def _find_nearest(self,
                      current_location: Tuple[float, float],
                      candidates: List[Destination],
                      exclude: List[Destination]) -> Destination:
        """
        Find nearest destination from candidates, excluding already selected

        Args:
            current_location: Current position (lat, lon)
            candidates: List of candidate destinations
            exclude: List of destinations to exclude

        Returns:
            Nearest valid destination
        """
        valid_candidates = [d for d in candidates if d not in exclude]

        if not valid_candidates:
            raise ValueError("No valid candidates available")

        # Find nearest
        nearest = min(
            valid_candidates,
            key=lambda d: self.distance_calculator.calculate_distance(
                current_location,
                (d.latitude, d.longitude)
            )
        )

        return nearest

    def run(self, start_point: Tuple[float, float], verbose: bool = False) -> Route:
        """
        Run greedy nearest neighbor algorithm

        Args:
            start_point: Starting location
            verbose: Print progress

        Returns:
            Route found by greedy algorithm
        """
        route_destinations = []
        current_location = start_point

        # Define constraint pattern
        constraint_sequence = [
            ('K1', self.makanan_berat),
            ('C1', self.makanan_ringan),
            ('W1', self.non_kuliner + self.all_category),
            ('K2', self.makanan_berat),
            ('W2', self.non_kuliner + self.all_category),
            ('C2', self.makanan_ringan),
            ('K3', self.makanan_berat),
            ('O', self.oleh_oleh + self.all_category)
        ]

        # Greedily select nearest for each position
        for position, (pos_name, candidates) in enumerate(constraint_sequence, 1):
            nearest = self._find_nearest(current_location, candidates, route_destinations)
            route_destinations.append(nearest)
            current_location = (nearest.latitude, nearest.longitude)

            if verbose:
                distance = self.distance_calculator.calculate_distance(
                    start_point if position == 1 else
                    (route_destinations[-2].latitude, route_destinations[-2].longitude),
                    current_location
                )
                print(f"Position {position} ({pos_name}): {nearest.nama} "
                      f"(distance: {distance:.2f} km)")

        route = Route(start_point, route_destinations)

        if verbose:
            print(f"\nTotal distance: {route.calculate_total_distance():.2f} km")

        return route


# Example usage
if __name__ == "__main__":
    from utils.data_loader import load_destinations_from_jsonl

    # Load destinations
    destinations = load_destinations_from_jsonl("data/data_wisata.jsonl")

    # Initialize Greedy
    greedy = GreedyNearestNeighbor(destinations)

    # Test location
    start_point = (-7.2575, 112.7521)

    # Run greedy
    route = greedy.run(start_point=start_point, verbose=True)
```

---

### 2.3 Pure Genetic Algorithm (GA tanpa 2-Opt)

**File: `algorithms/pure_ga.py`**

```python
"""
Pure Genetic Algorithm (without 2-Opt local search)
Used to measure the contribution of hybridization.
"""

from algorithms.hga import HybridGeneticAlgorithm
from algorithms.population import Population
from algorithms.operators import GAOperators

class PureGeneticAlgorithm(HybridGeneticAlgorithm):
    """
    Pure GA: Disables 2-Opt local search to measure its contribution
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize Pure GA (force use_2opt=False)
        """
        # Force 2-Opt disabled
        if 'use_2opt' in kwargs:
            kwargs['use_2opt'] = False
        else:
            kwargs['use_2opt'] = False

        super().__init__(*args, **kwargs)

        print("Initialized Pure GA (2-Opt disabled)")


# Example usage
if __name__ == "__main__":
    from utils.data_loader import load_destinations_from_jsonl

    destinations = load_destinations_from_jsonl("data/data_wisata.jsonl")
    start_point = (-7.2575, 112.7521)

    # Pure GA
    pure_ga = PureGeneticAlgorithm(
        population_size=600,
        generations=40,
        use_2opt=False  # Explicitly disabled
    )

    best_routes = pure_ga.run(
        destinations=destinations,
        start_point=start_point,
        num_solutions=1
    )

    print(f"Pure GA Best Distance: {best_routes[0].get_total_distance():.2f} km")
```

---

## 3. TOOLS UNTUK UJI PERBANDINGAN

### 3.1 Statistical Analysis Tools

#### A. **NumPy & SciPy** (Statistical Tests)

```python
import numpy as np
from scipy import stats

# Install
# pip install numpy scipy
```

**Fungsi:**

- Descriptive statistics (mean, median, std)
- Statistical hypothesis testing (t-test, ANOVA)
- Effect size calculation (Cohen's d)

#### B. **Pandas** (Data Management)

```python
import pandas as pd

# Install
# pip install pandas
```

**Fungsi:**

- Organize experiment results dalam DataFrame
- Easy aggregation dan grouping
- Export ke CSV/Excel untuk laporan

#### C. **Matplotlib & Seaborn** (Visualization)

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Install
# pip install matplotlib seaborn
```

**Fungsi:**

- Box plots untuk distribution comparison
- Line plots untuk convergence curves
- Scatter plots untuk trade-off analysis
- Heatmaps untuk parameter sensitivity

---

### 3.2 Experiment Management Tools

#### A. **MLflow** (Experiment Tracking) [OPTIONAL]

```bash
pip install mlflow
```

**Kegunaan:**

- Track semua experiment runs
- Compare multiple algorithms side-by-side
- Visualize metrics dengan UI
- Store models dan artifacts

**Example:**

```python
import mlflow

mlflow.start_run()
mlflow.log_param("algorithm", "HGA")
mlflow.log_param("population_size", 600)
mlflow.log_metric("best_distance", 32.5)
mlflow.log_metric("execution_time", 28.3)
mlflow.end_run()
```

#### B. **Weights & Biases (wandb)** [OPTIONAL]

```bash
pip install wandb
```

**Kegunaan:**

- Cloud-based experiment tracking
- Real-time visualization
- Collaborative research
- Free untuk academic use

---

### 3.3 Performance Profiling Tools

#### A. **cProfile** (Built-in Python)

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run algorithm
best_route = algorithm.run(destinations, start_point)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

**Output:** Time spent in each function

#### B. **line_profiler** (Line-by-line profiling)

```bash
pip install line_profiler
```

**Usage:**

```python
from line_profiler import LineProfiler

lp = LineProfiler()
lp.add_function(algorithm.run)
lp.enable_by_count()

# Run code
result = algorithm.run(destinations, start_point)

lp.print_stats()
```

#### C. **memory_profiler** (Memory usage)

```bash
pip install memory_profiler
```

**Usage:**

```python
from memory_profiler import profile

@profile
def run_algorithm():
    return hga.run(destinations, start_point, num_solutions=3)

run_algorithm()
```

---

## 4. IMPLEMENTASI COMPARISON FRAMEWORK

### 4.1 Comparison Runner Class

**File: `experiments/algorithm_comparison.py`**

```python
"""
Framework untuk systematic algorithm comparison
"""

import time
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Callable
from models.destination import Destination
from models.route import Route

class AlgorithmComparison:
    """
    Framework for comparing multiple algorithms systematically
    """

    def __init__(self, output_dir: str = "experiment_results"):
        """
        Initialize comparison framework

        Args:
            output_dir: Directory to save results
        """
        self.output_dir = output_dir
        self.results = []

    def add_algorithm(self,
                     name: str,
                     algorithm_func: Callable,
                     params: Dict[str, Any] = None):
        """
        Register an algorithm for comparison

        Args:
            name: Algorithm name (e.g., "HGA", "Greedy", "Random")
            algorithm_func: Function that runs the algorithm
            params: Additional parameters for the algorithm
        """
        # Implementation would store algorithm info
        pass

    def run_comparison(self,
                      destinations: List[Destination],
                      start_points: List[tuple],
                      n_runs: int = 30):
        """
        Run comparison experiments

        Args:
            destinations: List of destinations
            start_points: List of start points to test
            n_runs: Number of runs per algorithm per start point
        """
        # Implementation would run all algorithms and collect results
        pass

    def generate_report(self):
        """Generate comprehensive comparison report"""
        # Implementation would create statistical analysis and visualizations
        pass


# Practical implementation
class PracticalAlgorithmComparison:
    """
    Simplified, practical comparison framework
    """

    def __init__(self):
        self.results = []

    def run_single_test(self,
                       algorithm_name: str,
                       algorithm_runner: Callable,
                       destinations: List[Destination],
                       start_point: tuple,
                       run_id: int) -> Dict[str, Any]:
        """
        Run single algorithm test and collect metrics

        Returns:
            Dictionary with results
        """
        # Measure execution time
        start_time = time.time()

        try:
            # Run algorithm
            route = algorithm_runner(destinations, start_point)

            execution_time = time.time() - start_time

            # Collect metrics
            result = {
                'algorithm': algorithm_name,
                'run_id': run_id,
                'start_point': start_point,
                'distance': route.calculate_total_distance(),
                'execution_time': execution_time,
                'is_valid': route.is_valid_route_order(),
                'num_destinations': len(route.destinations),
                'destinations': [d.nama for d in route.destinations]
            }

            return result

        except Exception as e:
            print(f"Error in {algorithm_name}: {e}")
            return {
                'algorithm': algorithm_name,
                'run_id': run_id,
                'start_point': start_point,
                'distance': None,
                'execution_time': None,
                'is_valid': False,
                'error': str(e)
            }

    def run_comparison(self,
                      algorithms: Dict[str, Callable],
                      destinations: List[Destination],
                      start_points: List[tuple],
                      n_runs: int = 30) -> pd.DataFrame:
        """
        Run full comparison

        Args:
            algorithms: Dict mapping algorithm name to runner function
            destinations: List of destinations
            start_points: List of start points
            n_runs: Number of runs per configuration

        Returns:
            DataFrame with all results
        """
        print("="*60)
        print("STARTING ALGORITHM COMPARISON")
        print("="*60)
        print(f"Algorithms: {list(algorithms.keys())}")
        print(f"Start points: {len(start_points)}")
        print(f"Runs per config: {n_runs}")
        print(f"Total experiments: {len(algorithms) * len(start_points) * n_runs}")
        print("="*60)

        for algo_name, algo_func in algorithms.items():
            print(f"\nTesting {algo_name}...")

            for sp_idx, start_point in enumerate(start_points):
                print(f"  Start point {sp_idx+1}/{len(start_points)}: {start_point}")

                for run in range(n_runs):
                    print(f"    Run {run+1}/{n_runs}...", end=" ")

                    result = self.run_single_test(
                        algo_name,
                        algo_func,
                        destinations,
                        start_point,
                        run
                    )

                    self.results.append(result)

                    if result['distance']:
                        print(f"Distance: {result['distance']:.2f} km, "
                              f"Time: {result['execution_time']:.2f}s")
                    else:
                        print("FAILED")

        # Convert to DataFrame
        df = pd.DataFrame(self.results)

        # Save to CSV
        import os
        os.makedirs(self.output_dir, exist_ok=True)
        filename = f"{self.output_dir}/comparison_results.csv"
        df.to_csv(filename, index=False)
        print(f"\nResults saved to: {filename}")

        return df

    def analyze_results(self, df: pd.DataFrame):
        """
        Statistical analysis of comparison results

        Args:
            df: DataFrame with results
        """
        print("\n" + "="*60)
        print("STATISTICAL ANALYSIS")
        print("="*60)

        # Group by algorithm
        grouped = df.groupby('algorithm')['distance']

        print("\nDescriptive Statistics:")
        print(grouped.describe())

        # Pairwise t-tests
        print("\n" + "-"*60)
        print("Pairwise Statistical Tests (t-test):")
        print("-"*60)

        algorithms = df['algorithm'].unique()

        for i, algo1 in enumerate(algorithms):
            for algo2 in algorithms[i+1:]:
                data1 = df[df['algorithm'] == algo1]['distance'].dropna()
                data2 = df[df['algorithm'] == algo2]['distance'].dropna()

                # Independent samples t-test
                t_stat, p_value = stats.ttest_ind(data1, data2)

                # Cohen's d (effect size)
                mean_diff = data1.mean() - data2.mean()
                pooled_std = np.sqrt((data1.std()**2 + data2.std()**2) / 2)
                cohens_d = mean_diff / pooled_std

                print(f"\n{algo1} vs {algo2}:")
                print(f"  Mean difference: {mean_diff:.2f} km")
                print(f"  t-statistic: {t_stat:.4f}")
                print(f"  p-value: {p_value:.6f}")
                print(f"  Cohen's d: {cohens_d:.4f}")

                if p_value < 0.05:
                    print(f"  ✓ SIGNIFICANT difference (p < 0.05)")
                    if abs(cohens_d) > 0.8:
                        print(f"  ✓ LARGE effect size (|d| > 0.8)")
                    elif abs(cohens_d) > 0.5:
                        print(f"  ✓ MEDIUM effect size (|d| > 0.5)")
                else:
                    print(f"  ✗ NOT significant (p >= 0.05)")

        # ANOVA test
        print("\n" + "-"*60)
        print("One-way ANOVA:")
        print("-"*60)

        groups = [df[df['algorithm'] == algo]['distance'].dropna()
                  for algo in algorithms]
        f_stat, p_value = stats.f_oneway(*groups)

        print(f"F-statistic: {f_stat:.4f}")
        print(f"P-value: {p_value:.6f}")

        if p_value < 0.05:
            print("✓ At least one algorithm is significantly different")
        else:
            print("✗ No significant difference between algorithms")

    def visualize_results(self, df: pd.DataFrame):
        """
        Create visualizations for comparison

        Args:
            df: DataFrame with results
        """
        import matplotlib.pyplot as plt
        import seaborn as sns

        sns.set_style("whitegrid")

        # 1. Box plot comparison
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df, x='algorithm', y='distance')
        plt.ylabel('Total Distance (km)', fontsize=12)
        plt.xlabel('Algorithm', fontsize=12)
        plt.title('Distance Distribution Comparison', fontsize=14, fontweight='bold')
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/comparison_boxplot.png', dpi=300)
        print(f"Saved: {self.output_dir}/comparison_boxplot.png")
        plt.close()

        # 2. Execution time vs Distance scatter
        plt.figure(figsize=(10, 6))
        for algo in df['algorithm'].unique():
            algo_data = df[df['algorithm'] == algo]
            plt.scatter(algo_data['execution_time'], algo_data['distance'],
                       label=algo, alpha=0.6, s=100)
        plt.xlabel('Execution Time (seconds)', fontsize=12)
        plt.ylabel('Total Distance (km)', fontsize=12)
        plt.title('Quality vs Speed Trade-off', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/comparison_tradeoff.png', dpi=300)
        print(f"Saved: {self.output_dir}/comparison_tradeoff.png")
        plt.close()

        # 3. Summary bar chart
        summary = df.groupby('algorithm').agg({
            'distance': 'mean',
            'execution_time': 'mean'
        })

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Average distance
        summary['distance'].plot(kind='bar', ax=ax1, color='steelblue')
        ax1.set_ylabel('Average Distance (km)', fontsize=12)
        ax1.set_xlabel('Algorithm', fontsize=12)
        ax1.set_title('Average Solution Quality', fontsize=13, fontweight='bold')
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=15)

        # Average time
        summary['execution_time'].plot(kind='bar', ax=ax2, color='coral')
        ax2.set_ylabel('Average Time (seconds)', fontsize=12)
        ax2.set_xlabel('Algorithm', fontsize=12)
        ax2.set_title('Average Execution Time', fontsize=13, fontweight='bold')
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=15)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/comparison_summary.png', dpi=300)
        print(f"Saved: {self.output_dir}/comparison_summary.png")
        plt.close()

        print("\n✓ All visualizations generated successfully")


# Example usage
if __name__ == "__main__":
    from utils.data_loader import load_destinations_from_jsonl
    from algorithms.baseline_random import RandomSearch
    from algorithms.baseline_greedy import GreedyNearestNeighbor
    from algorithms.hga import HybridGeneticAlgorithm

    # Load data
    destinations = load_destinations_from_jsonl("data/data_wisata.jsonl")

    # Define start points
    start_points = [
        (-7.2575, 112.7521),  # Surabaya center
        (-7.3166, 112.7789),  # Surabaya east
        (-7.2464, 112.6340),  # Surabaya west
    ]

    # Define algorithm runners
    def run_random(dests, start):
        rs = RandomSearch(dests)
        return rs.run(start, num_iterations=24000)

    def run_greedy(dests, start):
        greedy = GreedyNearestNeighbor(dests)
        return greedy.run(start)

    def run_hga(dests, start):
        hga = HybridGeneticAlgorithm(population_size=600, generations=40)
        routes = hga.run(dests, start, num_solutions=1)
        return routes[0]

    algorithms = {
        'Random Search': run_random,
        'Greedy NN': run_greedy,
        'HGA': run_hga
    }

    # Run comparison
    comparison = PracticalAlgorithmComparison()
    df = comparison.run_comparison(algorithms, destinations, start_points, n_runs=10)

    # Analyze
    comparison.analyze_results(df)

    # Visualize
    comparison.visualize_results(df)
```

---

## 5. PROSEDUR UJI PERBANDINGAN STEP-BY-STEP

### Step 1: Preparation

```bash
# 1. Install dependencies
pip install numpy scipy pandas matplotlib seaborn

# 2. Create directory structure
mkdir -p experiments
mkdir -p experiment_results
mkdir -p algorithms/baseline

# 3. Implement baseline algorithms
# - algorithms/baseline_random.py
# - algorithms/baseline_greedy.py
```

### Step 2: Verification Test

```python
# File: experiments/verify_baselines.py

"""Quick test to verify baseline implementations"""

from utils.data_loader import load_destinations_from_jsonl
from algorithms.baseline_random import RandomSearch
from algorithms.baseline_greedy import GreedyNearestNeighbor

destinations = load_destinations_from_jsonl("data/data_wisata.jsonl")
start_point = (-7.2575, 112.7521)

print("Testing Random Search...")
rs = RandomSearch(destinations)
route = rs.run(start_point, num_iterations=1000, verbose=True)
print(f"✓ Random Search works! Distance: {route.calculate_total_distance():.2f} km\n")

print("Testing Greedy NN...")
greedy = GreedyNearestNeighbor(destinations)
route = greedy.run(start_point, verbose=True)
print(f"✓ Greedy NN works! Distance: {route.calculate_total_distance():.2f} km")
```

### Step 3: Run Small-Scale Test

```python
# File: experiments/small_scale_test.py

"""Small-scale test with 5 runs to verify everything works"""

from experiments.algorithm_comparison import PracticalAlgorithmComparison
from utils.data_loader import load_destinations_from_jsonl

# ... (define algorithms as shown above)

comparison = PracticalAlgorithmComparison()
df = comparison.run_comparison(algorithms, destinations, [start_point], n_runs=5)

print("\nSmall-scale test completed!")
print(df.groupby('algorithm')['distance'].describe())
```

### Step 4: Run Full Comparison

```python
# File: experiments/full_comparison.py

"""Full-scale comparison experiment"""

import sys
sys.path.append('..')

from experiments.algorithm_comparison import PracticalAlgorithmComparison
from utils.data_loader import load_destinations_from_jsonl
from algorithms.baseline_random import RandomSearch
from algorithms.baseline_greedy import GreedyNearestNeighbor
from algorithms.hga import HybridGeneticAlgorithm

# Load data
destinations = load_destinations_from_jsonl("data/data_wisata.jsonl")

# Multiple start points
start_points = [
    (-7.2575, 112.7521),  # Center
    (-7.3166, 112.7789),  # East
    (-7.2464, 112.6340),  # West
    (-7.2417, 112.7810),  # North
    (-7.3272, 112.6972),  # South
]

# Algorithm configurations
def run_random(dests, start):
    rs = RandomSearch(dests)
    return rs.run(start, num_iterations=24000)

def run_greedy(dests, start):
    greedy = GreedyNearestNeighbor(dests)
    return greedy.run(start)

def run_pure_ga(dests, start):
    from algorithms.pure_ga import PureGeneticAlgorithm
    ga = PureGeneticAlgorithm(population_size=600, generations=40)
    routes = ga.run(dests, start, num_solutions=1)
    return routes[0]

def run_hga(dests, start):
    hga = HybridGeneticAlgorithm(
        population_size=600,
        generations=40,
        use_2opt=True
    )
    routes = hga.run(dests, start, num_solutions=1)
    return routes[0]

algorithms = {
    'Random Search': run_random,
    'Greedy NN': run_greedy,
    'Pure GA': run_pure_ga,
    'HGA (Proposed)': run_hga
}

# Run comparison
print("Starting full comparison experiment...")
print("This will take approximately 2-3 hours...")

comparison = PracticalAlgorithmComparison()
df = comparison.run_comparison(
    algorithms=algorithms,
    destinations=destinations,
    start_points=start_points,
    n_runs=30  # 30 runs for statistical significance
)

# Analyze
print("\n" + "="*60)
print("ANALYSIS")
print("="*60)

comparison.analyze_results(df)
comparison.visualize_results(df)

print("\n" + "="*60)
print("COMPARISON COMPLETE!")
print("="*60)
print(f"Results saved in: {comparison.output_dir}/")
```

### Step 5: Generate Report

```python
# File: experiments/generate_report.py

"""Generate comprehensive comparison report"""

import pandas as pd
from experiments.algorithm_comparison import PracticalAlgorithmComparison

# Load results
df = pd.read_csv("experiment_results/comparison_results.csv")

# Generate LaTeX table for thesis
def generate_latex_table(df):
    summary = df.groupby('algorithm').agg({
        'distance': ['mean', 'std', 'min', 'max'],
        'execution_time': ['mean', 'std']
    })

    print("\n\\begin{table}[h]")
    print("\\centering")
    print("\\caption{Comparison of Algorithm Performance}")
    print("\\begin{tabular}{lcccccc}")
    print("\\hline")
    print("Algorithm & Mean Dist. & Std Dev & Min & Max & Mean Time \\\\")
    print("         & (km) & (km) & (km) & (km) & (s) \\\\")
    print("\\hline")

    for algo in summary.index:
        row = summary.loc[algo]
        print(f"{algo} & {row[('distance', 'mean')]:.2f} & "
              f"{row[('distance', 'std')]:.2f} & "
              f"{row[('distance', 'min')]:.2f} & "
              f"{row[('distance', 'max')]:.2f} & "
              f"{row[('execution_time', 'mean')]:.2f} \\\\")

    print("\\hline")
    print("\\end{tabular}")
    print("\\end{table}")

generate_latex_table(df)

# Calculate improvement percentages
hga_mean = df[df['algorithm'] == 'HGA (Proposed)']['distance'].mean()
random_mean = df[df['algorithm'] == 'Random Search']['distance'].mean()
greedy_mean = df[df['algorithm'] == 'Greedy NN']['distance'].mean()

print("\n" + "="*60)
print("KEY FINDINGS:")
print("="*60)
print(f"HGA improvement over Random Search: "
      f"{(random_mean - hga_mean) / random_mean * 100:.1f}%")
print(f"HGA improvement over Greedy NN: "
      f"{(greedy_mean - hga_mean) / greedy_mean * 100:.1f}%")
```

---

## 6. INTERPRETASI HASIL

### 6.1 Expected Results Template

```
COMPARISON RESULTS SUMMARY
======================================================

Algorithm Performance (30 runs, 5 start points):

Algorithm         | Mean Dist | Std Dev | Min Dist | Max Dist | Mean Time
------------------|-----------|---------|----------|----------|----------
Random Search     | 48.5 km   | 9.2 km  | 35.1 km  | 68.4 km  | 0.8s
Greedy NN         | 42.3 km   | 2.1 km  | 38.7 km  | 46.9 km  | 0.3s
Pure GA           | 36.8 km   | 3.5 km  | 31.2 km  | 42.1 km  | 22.1s
HGA (Proposed)    | 31.4 km   | 2.8 km  | 27.9 km  | 36.3 km  | 28.7s

Statistical Tests:
- HGA vs Random Search: p < 0.001, Cohen's d = 2.15 (LARGE effect)
- HGA vs Greedy NN:     p < 0.001, Cohen's d = 1.87 (LARGE effect)
- HGA vs Pure GA:       p < 0.001, Cohen's d = 0.92 (LARGE effect)

Key Findings:
✓ HGA achieves 35.2% better distance than Random Search
✓ HGA achieves 25.8% better distance than Greedy NN
✓ HGA achieves 14.7% better distance than Pure GA
✓ 2-Opt contribution: ~15% distance improvement
✓ All differences are statistically significant (p < 0.001)

Trade-off Analysis:
- Greedy: Fastest (0.3s) but 34% worse than HGA
- HGA: Best quality with acceptable time (~29s)
- Recommendation: Use HGA for final recommendations
```

### 6.2 Interpretation Guidelines

**Statistical Significance (p-value):**

- p < 0.001: Very strong evidence of difference ✓✓✓
- p < 0.01: Strong evidence ✓✓
- p < 0.05: Moderate evidence ✓
- p >= 0.05: No significant difference ✗

**Effect Size (Cohen's d):**

- |d| > 0.8: Large effect (substantial practical difference)
- |d| > 0.5: Medium effect (noticeable difference)
- |d| > 0.2: Small effect (minor difference)
- |d| ≤ 0.2: Negligible effect

**Improvement Calculation:**

```
Improvement% = (Baseline_Distance - Proposed_Distance) / Baseline_Distance × 100%
```

---

## 7. COMMON PITFALLS & SOLUTIONS

### Pitfall 1: Unfair Comparison

**Problem:** Comparing algorithms with different computational budgets

**Solution:**

```python
# Ensure equal fitness evaluations
random_iterations = population_size × generations  # 24,000
pure_ga_evaluations = population_size × generations  # 24,000
hga_evaluations = population_size × generations  # 24,000
```

### Pitfall 2: Insufficient Statistical Power

**Problem:** Too few runs, results not significant

**Solution:**

- Minimum 30 runs per configuration
- Use power analysis to determine sample size

```python
from statsmodels.stats.power import ttest_power

# Calculate required sample size
effect_size = 0.8  # Expected Cohen's d
alpha = 0.05
power = 0.8

required_n = ttest_power(effect_size, n=None, alpha=alpha, power=power)
print(f"Required sample size: {required_n:.0f}")
```

### Pitfall 3: Cherry-picking Results

**Problem:** Only reporting best results

**Solution:**

- Report all metrics (mean, std, min, max)
- Use fixed random seeds for reproducibility
- Document all experiments, including "failed" ones

---

## 8. CHECKLIST

### Pre-Experiment ✓

- [ ] Baseline algorithms implemented and tested
- [ ] Comparison framework ready
- [ ] Statistical tools installed
- [ ] Start points selected (diverse locations)

### During Experiment ✓

- [ ] Equal computational budget across algorithms
- [ ] Sufficient runs (≥30) for significance
- [ ] Progress tracking and logging
- [ ] Error handling for failed runs

### Post-Experiment ✓

- [ ] Statistical tests conducted (t-test, ANOVA)
- [ ] Effect sizes calculated (Cohen's d)
- [ ] Visualizations generated (plots)
- [ ] Results documented (tables, figures)

### Reporting ✓

- [ ] All metrics reported transparently
- [ ] Statistical significance stated
- [ ] Trade-offs discussed
- [ ] Limitations acknowledged

---

## SUMMARY

**Tools Required:**

1. **NumPy/SciPy** - Statistical analysis ✓
2. **Pandas** - Data management ✓
3. **Matplotlib/Seaborn** - Visualization ✓
4. **cProfile** - Performance profiling ✓

**Baseline Algorithms:**

1. Random Search - Lower bound
2. Greedy NN - Fast approximation
3. Pure GA - Measure hybridization benefit

**Key Metrics:**

- Distance (quality)
- Execution time (efficiency)
- Statistical significance (p-value)
- Effect size (Cohen's d)

**Expected Outcome:**
HGA demonstrates **statistically significant** improvement (p < 0.001) with **large effect size** (d > 0.8) compared to all baselines, justifying its complexity.
