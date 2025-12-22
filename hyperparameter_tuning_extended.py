"""
Extended Hyperparameter Tuning - Fokus pada parameter baru
Menguji parameter: elitism_count, tournament_size, two_opt_iterations
dengan kombinasi parameter lain yang sudah terbukti baik
"""

import time
import json
import csv
from datetime import datetime
from itertools import product
from typing import List, Dict, Tuple
import statistics

from algorithms.hga import HybridGeneticAlgorithm
from utils.data_loader import load_destinations_from_csv
from models.destination import Destination

# Lokasi start point
START_POINT = (-7.2808, 112.7960)

# Parameter baru yang ingin diuji (dari hasil user)
NEW_PARAMETER_GRID = {
    'elitism_count': [2, 5, 10],
    'tournament_size': [3, 5, 8],
    'two_opt_iterations': [50, 100, 500]
}

# Parameter dasar yang sudah diketahui baik (dari user)
BASE_CONFIG = {
    'population_size': 700,
    'generations': 20,
    'crossover_rate': 0.8,
    'mutation_rate': 0.01,
    'use_2opt': True
}

# Variasi parameter dasar untuk melihat interaksi
VARIANT_CONFIGS = [
    # Config user (baseline)
    {'population_size': 700, 'generations': 20, 'crossover_rate': 0.8, 'mutation_rate': 0.01, 'use_2opt': True},
    # Variasi population
    {'population_size': 500, 'generations': 20, 'crossover_rate': 0.8, 'mutation_rate': 0.01, 'use_2opt': True},
    {'population_size': 300, 'generations': 20, 'crossover_rate': 0.8, 'mutation_rate': 0.01, 'use_2opt': True},
    # Variasi generations
    {'population_size': 700, 'generations': 40, 'crossover_rate': 0.8, 'mutation_rate': 0.01, 'use_2opt': True},
    {'population_size': 700, 'generations': 80, 'crossover_rate': 0.8, 'mutation_rate': 0.01, 'use_2opt': True},
    # Variasi mutation
    {'population_size': 700, 'generations': 20, 'crossover_rate': 0.8, 'mutation_rate': 0.05, 'use_2opt': True},
]

# Number of runs per configuration
NUM_RUNS_PER_CONFIG = 3


def load_test_data() -> List[Destination]:
    """Load destinations data for testing"""
    print("Loading destinations data...")
    destinations = load_destinations_from_csv("./data/data_wisata.jsonl")
    print(f"Loaded {len(destinations)} destinations")
    return destinations


def run_single_experiment(
    destinations: List[Destination],
    start_point: Tuple[float, float],
    population_size: int,
    generations: int,
    crossover_rate: float,
    mutation_rate: float,
    use_2opt: bool,
    elitism_count: int,
    tournament_size: int,
    two_opt_iterations: int,
    run_number: int
) -> Dict:
    """Run single HGA experiment"""
    print(f"\n{'='*80}")
    print(f"Run #{run_number}")
    print(f"Population: {population_size}, Generations: {generations}")
    print(f"Crossover: {crossover_rate}, Mutation: {mutation_rate}, 2-Opt: {use_2opt}")
    print(f"Elitism: {elitism_count}, Tournament: {tournament_size}, 2-Opt Iter: {two_opt_iterations}")
    print(f"{'='*80}")
    
    # Initialize HGA
    hga = HybridGeneticAlgorithm(
        population_size=population_size,
        generations=generations,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        elitism_count=elitism_count,
        tournament_size=tournament_size,
        use_2opt=use_2opt,
        two_opt_iterations=two_opt_iterations
    )
    
    # Measure execution time
    start_time = time.time()
    
    # Run algorithm
    best_chromosomes = hga.run(
        destinations=destinations,
        start_point=start_point,
        num_solutions=1
    )
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Get results
    best_chromosome = best_chromosomes[0]
    best_distance = best_chromosome.get_total_distance()
    best_fitness = best_chromosome.get_fitness()
    best_time = best_chromosome.get_total_travel_time()
    is_feasible = best_chromosome.is_feasible()
    
    # Get fitness history
    stats = hga.get_evolution_statistics()
    fitness_history = stats['best_fitness_history']
    distance_history = stats['best_distance_history']
    
    # Calculate convergence metrics
    initial_distance = distance_history[0]
    final_distance = distance_history[-1]
    improvement = initial_distance - final_distance
    improvement_percentage = (improvement / initial_distance) * 100 if initial_distance > 0 else 0
    
    # Find convergence generation
    convergence_gen = generations
    for i in range(5, len(distance_history)):
        recent_improvements = [
            abs(distance_history[i-j] - distance_history[i-j-1]) / distance_history[i-j-1] * 100
            for j in range(5)
        ]
        if all(imp < 0.1 for imp in recent_improvements):
            convergence_gen = i - 4
            break
    
    results = {
        'population_size': population_size,
        'generations': generations,
        'crossover_rate': crossover_rate,
        'mutation_rate': mutation_rate,
        'use_2opt': use_2opt,
        'elitism_count': elitism_count,
        'tournament_size': tournament_size,
        'two_opt_iterations': two_opt_iterations,
        'run_number': run_number,
        'best_distance_km': round(best_distance, 4),
        'best_fitness': round(best_fitness, 6),
        'travel_time_minutes': round(best_time, 2),
        'is_feasible': is_feasible,
        'execution_time_seconds': round(execution_time, 2),
        'initial_distance_km': round(initial_distance, 4),
        'final_distance_km': round(final_distance, 4),
        'improvement_km': round(improvement, 4),
        'improvement_percentage': round(improvement_percentage, 2),
        'convergence_generation': convergence_gen,
        'fitness_history': fitness_history,
        'distance_history': distance_history
    }
    
    print(f"\n✓ Results:")
    print(f"  Best Distance: {best_distance:.2f} km")
    print(f"  Travel Time: {best_time:.1f} min")
    print(f"  Feasible: {'Yes' if is_feasible else 'No'}")
    print(f"  Execution Time: {execution_time:.2f} seconds")
    print(f"  Improvement: {improvement:.2f} km ({improvement_percentage:.1f}%)")
    print(f"  Convergence at generation: {convergence_gen}")
    
    return results


def aggregate_runs(runs: List[Dict]) -> Dict:
    """Aggregate multiple runs for the same configuration"""
    distances = [r['best_distance_km'] for r in runs]
    exec_times = [r['execution_time_seconds'] for r in runs]
    improvements = [r['improvement_percentage'] for r in runs]
    convergence_gens = [r['convergence_generation'] for r in runs]
    feasible_count = sum(1 for r in runs if r['is_feasible'])
    
    return {
        'population_size': runs[0]['population_size'],
        'generations': runs[0]['generations'],
        'crossover_rate': runs[0]['crossover_rate'],
        'mutation_rate': runs[0]['mutation_rate'],
        'use_2opt': runs[0]['use_2opt'],
        'elitism_count': runs[0]['elitism_count'],
        'tournament_size': runs[0]['tournament_size'],
        'two_opt_iterations': runs[0]['two_opt_iterations'],
        'num_runs': len(runs),
        'mean_distance_km': round(statistics.mean(distances), 4),
        'std_distance_km': round(statistics.stdev(distances) if len(distances) > 1 else 0, 4),
        'min_distance_km': round(min(distances), 4),
        'max_distance_km': round(max(distances), 4),
        'mean_execution_time': round(statistics.mean(exec_times), 2),
        'std_execution_time': round(statistics.stdev(exec_times) if len(exec_times) > 1 else 0, 2),
        'mean_improvement_pct': round(statistics.mean(improvements), 2),
        'mean_convergence_gen': round(statistics.mean(convergence_gens), 1),
        'feasible_rate': round((feasible_count / len(runs)) * 100, 1),
        'all_runs': runs
    }


def run_extended_tuning():
    """Main function to run extended hyperparameter tuning"""
    print("\n" + "="*80)
    print("EXTENDED HYPERPARAMETER TUNING - PARAMETER BARU")
    print("="*80)
    
    # Load data
    destinations = load_test_data()
    
    # Generate all parameter combinations for new parameters
    new_param_combinations = list(product(
        NEW_PARAMETER_GRID['elitism_count'],
        NEW_PARAMETER_GRID['tournament_size'],
        NEW_PARAMETER_GRID['two_opt_iterations']
    ))
    
    # Total combinations = variant configs × new params
    total_configs = len(VARIANT_CONFIGS) * len(new_param_combinations)
    total_runs = total_configs * NUM_RUNS_PER_CONFIG
    
    print(f"\nVariant base configurations: {len(VARIANT_CONFIGS)}")
    print(f"New parameter combinations: {len(new_param_combinations)}")
    print(f"Total configurations: {total_configs}")
    print(f"Runs per configuration: {NUM_RUNS_PER_CONFIG}")
    print(f"Total experiments: {total_runs}")
    print(f"\nEstimated time: {total_runs * 10 / 3600:.1f} - {total_runs * 20 / 3600:.1f} hours")
    
    input("\nPress Enter to start extended tuning...")
    
    # Store results
    all_results = []
    config_results = []
    
    start_time_total = time.time()
    config_counter = 0
    
    # Run experiments
    for variant_config in VARIANT_CONFIGS:
        for elitism, tournament, two_opt_iter in new_param_combinations:
            config_counter += 1
            
            print(f"\n\n{'#'*80}")
            print(f"Configuration {config_counter}/{total_configs}")
            print(f"{'#'*80}")
            
            config_runs = []
            
            # Run multiple times for statistical significance
            for run_num in range(1, NUM_RUNS_PER_CONFIG + 1):
                result = run_single_experiment(
                    destinations=destinations,
                    start_point=START_POINT,
                    population_size=variant_config['population_size'],
                    generations=variant_config['generations'],
                    crossover_rate=variant_config['crossover_rate'],
                    mutation_rate=variant_config['mutation_rate'],
                    use_2opt=variant_config['use_2opt'],
                    elitism_count=elitism,
                    tournament_size=tournament,
                    two_opt_iterations=two_opt_iter,
                    run_number=run_num
                )
                config_runs.append(result)
                all_results.append(result)
            
            # Aggregate runs
            aggregated = aggregate_runs(config_runs)
            config_results.append(aggregated)
            
            print(f"\n✓ Configuration Summary:")
            print(f"  Mean Distance: {aggregated['mean_distance_km']:.2f} ± {aggregated['std_distance_km']:.2f} km")
            print(f"  Mean Execution Time: {aggregated['mean_execution_time']:.2f} ± {aggregated['std_execution_time']:.2f} s")
            print(f"  Feasible Rate: {aggregated['feasible_rate']:.1f}%")
    
    end_time_total = time.time()
    total_time = end_time_total - start_time_total
    
    print(f"\n\n{'='*80}")
    print("TUNING COMPLETED")
    print(f"{'='*80}")
    print(f"Total configurations tested: {total_configs}")
    print(f"Total runs: {total_runs}")
    print(f"Total time: {total_time / 3600:.2f} hours")
    print(f"Average time per run: {total_time / total_runs:.2f} seconds")
    
    # Save results
    save_results(all_results, config_results)
    
    # Analyze results
    analyze_extended_results(config_results)
    
    return config_results


def save_results(all_results: List[Dict], config_results: List[Dict]):
    """Save results to CSV and JSON files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save detailed results
    detailed_file = f"extended_tuning_detailed_{timestamp}.csv"
    with open(detailed_file, 'w', newline='', encoding='utf-8') as f:
        if all_results:
            writer = csv.DictWriter(f, fieldnames=[
                'population_size', 'generations', 'crossover_rate', 'mutation_rate', 
                'use_2opt', 'elitism_count', 'tournament_size', 'two_opt_iterations',
                'run_number', 'best_distance_km', 'best_fitness',
                'travel_time_minutes', 'is_feasible', 'execution_time_seconds',
                'initial_distance_km', 'final_distance_km', 'improvement_km',
                'improvement_percentage', 'convergence_generation'
            ])
            writer.writeheader()
            for result in all_results:
                row = {k: v for k, v in result.items() if not k.endswith('_history')}
                writer.writerow(row)
    
    print(f"\n✓ Detailed results saved to: {detailed_file}")
    
    # Save aggregated results
    aggregated_file = f"extended_tuning_aggregated_{timestamp}.csv"
    with open(aggregated_file, 'w', newline='', encoding='utf-8') as f:
        if config_results:
            writer = csv.DictWriter(f, fieldnames=[
                'population_size', 'generations', 'crossover_rate', 'mutation_rate',
                'use_2opt', 'elitism_count', 'tournament_size', 'two_opt_iterations',
                'num_runs', 'mean_distance_km', 'std_distance_km',
                'min_distance_km', 'max_distance_km', 'mean_execution_time',
                'std_execution_time', 'mean_improvement_pct', 'mean_convergence_gen',
                'feasible_rate'
            ])
            writer.writeheader()
            for result in config_results:
                row = {k: v for k, v in result.items() if k != 'all_runs'}
                writer.writerow(row)
    
    print(f"✓ Aggregated results saved to: {aggregated_file}")
    
    # Save full results as JSON
    json_file = f"extended_tuning_full_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'detailed_results': all_results,
            'aggregated_results': config_results,
            'new_parameter_grid': NEW_PARAMETER_GRID,
            'base_config': BASE_CONFIG,
            'variant_configs': VARIANT_CONFIGS,
            'num_runs_per_config': NUM_RUNS_PER_CONFIG
        }, f, indent=2)
    
    print(f"✓ Full results (with history) saved to: {json_file}")


def analyze_extended_results(config_results: List[Dict]):
    """Analyze and print best configurations for new parameters"""
    print("\n\n" + "="*80)
    print("ANALYSIS - PARAMETER BARU")
    print("="*80)
    
    # Sort by mean distance
    sorted_by_distance = sorted(config_results, key=lambda x: x['mean_distance_km'])
    
    print("\n📊 TOP 5 CONFIGURATIONS:")
    print("-" * 80)
    for i, config in enumerate(sorted_by_distance[:5], 1):
        print(f"\n#{i} - Mean Distance: {config['mean_distance_km']:.2f} km")
        print(f"   Base: Pop={config['population_size']}, Gen={config['generations']}, "
              f"Cross={config['crossover_rate']}, Mut={config['mutation_rate']}")
        print(f"   NEW PARAMS → Elitism: {config['elitism_count']}, "
              f"Tournament: {config['tournament_size']}, "
              f"2-Opt Iter: {config['two_opt_iterations']}")
        print(f"   Execution Time: {config['mean_execution_time']:.2f}s")
        print(f"   Feasible Rate: {config['feasible_rate']:.1f}%")
    
    # Analyze new parameter effects
    print("\n\n📈 EFEK PARAMETER BARU:")
    print("-" * 80)
    
    # Elitism count effect
    print("\n1. ELITISM COUNT EFFECT:")
    for elitism in NEW_PARAMETER_GRID['elitism_count']:
        elitism_configs = [c for c in config_results if c['elitism_count'] == elitism]
        mean_dist = statistics.mean([c['mean_distance_km'] for c in elitism_configs])
        mean_time = statistics.mean([c['mean_execution_time'] for c in elitism_configs])
        mean_feas = statistics.mean([c['feasible_rate'] for c in elitism_configs])
        print(f"   {elitism:>2} → Distance: {mean_dist:.2f} km, Time: {mean_time:.2f}s, Feasible: {mean_feas:.1f}%")
    
    # Tournament size effect
    print("\n2. TOURNAMENT SIZE EFFECT:")
    for tournament in NEW_PARAMETER_GRID['tournament_size']:
        tournament_configs = [c for c in config_results if c['tournament_size'] == tournament]
        mean_dist = statistics.mean([c['mean_distance_km'] for c in tournament_configs])
        mean_conv = statistics.mean([c['mean_convergence_gen'] for c in tournament_configs])
        mean_feas = statistics.mean([c['feasible_rate'] for c in tournament_configs])
        print(f"   {tournament:>2} → Distance: {mean_dist:.2f} km, Convergence: {mean_conv:.0f}, Feasible: {mean_feas:.1f}%")
    
    # 2-Opt iterations effect
    print("\n3. 2-OPT ITERATIONS EFFECT:")
    for two_opt_iter in NEW_PARAMETER_GRID['two_opt_iterations']:
        opt_iter_configs = [c for c in config_results if c['two_opt_iterations'] == two_opt_iter]
        mean_dist = statistics.mean([c['mean_distance_km'] for c in opt_iter_configs])
        mean_time = statistics.mean([c['mean_execution_time'] for c in opt_iter_configs])
        mean_imp = statistics.mean([c['mean_improvement_pct'] for c in opt_iter_configs])
        print(f"   {two_opt_iter:>4} → Distance: {mean_dist:.2f} km, Time: {mean_time:.2f}s, Improvement: {mean_imp:.1f}%")
    
    # Best configuration
    best_config = sorted_by_distance[0]
    
    print("\n\n" + "="*80)
    print("🏆 KONFIGURASI TERBAIK (PARAMETER LENGKAP)")
    print("="*80)
    print(f"\nParameter Dasar:")
    print(f"  Population Size: {best_config['population_size']}")
    print(f"  Generations: {best_config['generations']}")
    print(f"  Crossover Rate: {best_config['crossover_rate']}")
    print(f"  Mutation Rate: {best_config['mutation_rate']}")
    print(f"  Use 2-Opt: {best_config['use_2opt']}")
    print(f"\nParameter Baru:")
    print(f"  Elitism Count: {best_config['elitism_count']}")
    print(f"  Tournament Size: {best_config['tournament_size']}")
    print(f"  2-Opt Iterations: {best_config['two_opt_iterations']}")
    print(f"\nPerformance:")
    print(f"  Mean Distance: {best_config['mean_distance_km']:.2f} ± {best_config['std_distance_km']:.2f} km")
    print(f"  Mean Execution Time: {best_config['mean_execution_time']:.2f} ± {best_config['std_execution_time']:.2f}s")
    print(f"  Feasible Rate: {best_config['feasible_rate']:.1f}%")
    print(f"  Mean Improvement: {best_config['mean_improvement_pct']:.1f}%")
    print(f"  Convergence Generation: {best_config['mean_convergence_gen']:.0f}")


if __name__ == "__main__":
    try:
        results = run_extended_tuning()
        print("\n✅ Extended hyperparameter tuning completed successfully!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Tuning interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during tuning: {str(e)}")
        raise
