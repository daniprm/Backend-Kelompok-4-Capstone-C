"""
Quick Hyperparameter Tuning
Testing dengan subset parameter untuk testing cepat
"""

import time
import json
import csv
from datetime import datetime
from itertools import product
from typing import List, Dict, Tuple
import statistics

from algorithms.hga import HybridGeneticAlgorithm
from utils.data_loader import load_destinations_from_jsonl
from models.destination import Destination

# Lokasi start point
START_POINT = (-7.2575, 112.7521)

# Quick test - subset of parameters
QUICK_PARAMETER_GRID = {
    'population_size': [100, 300, 500],  # 3 values
    'generations': [20, 40],              # 2 values
    'crossover_rate': [0.7, 0.8],         # 2 values
    'mutation_rate': [0.05, 0.2],         # 2 values
    'use_2opt': [True, False]             # 2 values
}

# Fixed parameters
FIXED_PARAMS = {
    'elitism_count': 2,
    'tournament_size': 8,
    'two_opt_iterations': 100
}

# Number of runs per configuration
NUM_RUNS_PER_CONFIG = 2


def load_test_data() -> List[Destination]:
    """Load destinations data"""
    print("Loading destinations data...")
    destinations = load_destinations_from_jsonl("./data/data_wisata.jsonl")
    print(f"Loaded {len(destinations)} destinations")
    return destinations


def run_single_test(
    destinations: List[Destination],
    start_point: Tuple[float, float],
    population_size: int,
    generations: int,
    crossover_rate: float,
    mutation_rate: float,
    use_2opt: bool,
    run_number: int
) -> Dict:
    """Run single test"""
    print(f"\n{'='*60}")
    print(f"Run #{run_number} | Pop:{population_size} Gen:{generations} "
          f"Cross:{crossover_rate} Mut:{mutation_rate} 2Opt:{use_2opt}")
    print(f"{'='*60}")
    
    # Initialize HGA
    hga = HybridGeneticAlgorithm(
        population_size=population_size,
        generations=generations,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        elitism_count=FIXED_PARAMS['elitism_count'],
        tournament_size=FIXED_PARAMS['tournament_size'],
        use_2opt=use_2opt,
        two_opt_iterations=FIXED_PARAMS['two_opt_iterations']
    )
    
    # Run algorithm
    start_time = time.time()
    best_chromosomes = hga.run(
        destinations=destinations,
        start_point=start_point,
        num_solutions=1
    )
    execution_time = time.time() - start_time
    
    # Get results
    best = best_chromosomes[0]
    stats = hga.get_evolution_statistics()
    
    result = {
        'population_size': population_size,
        'generations': generations,
        'crossover_rate': crossover_rate,
        'mutation_rate': mutation_rate,
        'use_2opt': use_2opt,
        'run_number': run_number,
        'distance_km': round(best.get_total_distance(), 2),
        'time_minutes': round(best.get_total_travel_time(), 1),
        'feasible': best.is_feasible(),
        'exec_time_sec': round(execution_time, 2),
        'improvement_pct': round(
            (stats['best_distance_history'][0] - stats['best_distance_history'][-1]) / 
            stats['best_distance_history'][0] * 100, 1
        )
    }
    
    print(f"✓ Distance: {result['distance_km']}km | "
          f"Time: {result['exec_time_sec']}s | "
          f"Feasible: {result['feasible']}")
    
    return result


def run_quick_tuning():
    """Run quick hyperparameter tuning"""
    print("\n" + "="*80)
    print("QUICK HYPERPARAMETER TUNING")
    print("="*80)
    
    destinations = load_test_data()
    
    # Generate combinations
    combinations = list(product(
        QUICK_PARAMETER_GRID['population_size'],
        QUICK_PARAMETER_GRID['generations'],
        QUICK_PARAMETER_GRID['crossover_rate'],
        QUICK_PARAMETER_GRID['mutation_rate'],
        QUICK_PARAMETER_GRID['use_2opt']
    ))
    
    total_configs = len(combinations)
    total_runs = total_configs * NUM_RUNS_PER_CONFIG
    
    print(f"\nConfigurations: {total_configs}")
    print(f"Runs per config: {NUM_RUNS_PER_CONFIG}")
    print(f"Total experiments: {total_runs}")
    print(f"Estimated time: ~{total_runs * 3 / 60:.1f} minutes")
    
    input("\nPress Enter to start...")
    
    all_results = []
    config_summaries = []
    
    start_total = time.time()
    
    for config_idx, (pop, gen, cross, mut, opt) in enumerate(combinations, 1):
        print(f"\n{'#'*80}")
        print(f"Configuration {config_idx}/{total_configs}")
        print(f"{'#'*80}")
        
        config_runs = []
        
        for run_num in range(1, NUM_RUNS_PER_CONFIG + 1):
            result = run_single_test(
                destinations, START_POINT,
                pop, gen, cross, mut, opt, run_num
            )
            config_runs.append(result)
            all_results.append(result)
        
        # Summary
        distances = [r['distance_km'] for r in config_runs]
        times = [r['exec_time_sec'] for r in config_runs]
        
        summary = {
            'population_size': pop,
            'generations': gen,
            'crossover_rate': cross,
            'mutation_rate': mut,
            'use_2opt': opt,
            'mean_distance': round(statistics.mean(distances), 2),
            'std_distance': round(statistics.stdev(distances) if len(distances) > 1 else 0, 2),
            'mean_time': round(statistics.mean(times), 2),
            'feasible_rate': sum(1 for r in config_runs if r['feasible']) / len(config_runs) * 100
        }
        config_summaries.append(summary)
        
        print(f"\n📊 Config Summary: Distance={summary['mean_distance']}±{summary['std_distance']}km, "
              f"Time={summary['mean_time']}s, Feasible={summary['feasible_rate']:.0f}%")
    
    total_time = time.time() - start_total
    
    print(f"\n\n{'='*80}")
    print(f"✅ QUICK TUNING COMPLETED in {total_time/60:.1f} minutes!")
    print(f"{'='*80}")
    
    # Save results
    save_quick_results(all_results, config_summaries)
    
    # Analyze
    analyze_quick_results(config_summaries)
    
    return config_summaries


def save_quick_results(all_results: List[Dict], summaries: List[Dict]):
    """Save quick tuning results"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Detailed results
    detail_file = f"quick_tuning_detailed_{timestamp}.csv"
    with open(detail_file, 'w', newline='', encoding='utf-8') as f:
        if all_results:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
    print(f"\n✓ Detailed results: {detail_file}")
    
    # Summary
    summary_file = f"quick_tuning_summary_{timestamp}.csv"
    with open(summary_file, 'w', newline='', encoding='utf-8') as f:
        if summaries:
            writer = csv.DictWriter(f, fieldnames=summaries[0].keys())
            writer.writeheader()
            writer.writerows(summaries)
    print(f"✓ Summary results: {summary_file}")


def analyze_quick_results(summaries: List[Dict]):
    """Analyze quick tuning results"""
    print("\n\n" + "="*80)
    print("QUICK ANALYSIS")
    print("="*80)
    
    # Best by distance
    best_dist = min(summaries, key=lambda x: x['mean_distance'])
    print(f"\n🏆 BEST DISTANCE: {best_dist['mean_distance']}km")
    print(f"   Population: {best_dist['population_size']}")
    print(f"   Generations: {best_dist['generations']}")
    print(f"   Crossover: {best_dist['crossover_rate']}")
    print(f"   Mutation: {best_dist['mutation_rate']}")
    print(f"   2-Opt: {best_dist['use_2opt']}")
    print(f"   Execution Time: {best_dist['mean_time']}s")
    
    # Best by speed
    feasible = [s for s in summaries if s['feasible_rate'] >= 50]
    if feasible:
        best_speed = min(feasible, key=lambda x: x['mean_time'])
        print(f"\n⚡ FASTEST (Feasible): {best_speed['mean_time']}s")
        print(f"   Distance: {best_speed['mean_distance']}km")
        print(f"   Population: {best_speed['population_size']}")
        print(f"   Generations: {best_speed['generations']}")
    
    # Parameter effects
    print("\n\n📈 PARAMETER EFFECTS:")
    
    print("\nPopulation Size:")
    for pop in sorted(set(s['population_size'] for s in summaries)):
        subset = [s for s in summaries if s['population_size'] == pop]
        avg_dist = statistics.mean([s['mean_distance'] for s in subset])
        avg_time = statistics.mean([s['mean_time'] for s in subset])
        print(f"  {pop:>4}: Dist={avg_dist:.2f}km, Time={avg_time:.2f}s")
    
    print("\nGenerations:")
    for gen in sorted(set(s['generations'] for s in summaries)):
        subset = [s for s in summaries if s['generations'] == gen]
        avg_dist = statistics.mean([s['mean_distance'] for s in subset])
        avg_time = statistics.mean([s['mean_time'] for s in subset])
        print(f"  {gen:>3}: Dist={avg_dist:.2f}km, Time={avg_time:.2f}s")
    
    print("\n2-Opt Effect:")
    for opt in [True, False]:
        subset = [s for s in summaries if s['use_2opt'] == opt]
        avg_dist = statistics.mean([s['mean_distance'] for s in subset])
        avg_time = statistics.mean([s['mean_time'] for s in subset])
        status = "With 2-Opt" if opt else "No 2-Opt"
        print(f"  {status:>12}: Dist={avg_dist:.2f}km, Time={avg_time:.2f}s")


if __name__ == "__main__":
    try:
        results = run_quick_tuning()
        print("\n✅ Quick tuning completed!")
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise
