"""
Hyperparameter Tuning untuk Hybrid Genetic Algorithm (HGA)
Uji performa algoritma dengan berbagai kombinasi parameter
"""

import time
import json
import csv
import os
import pickle
import ctypes
from datetime import datetime
from itertools import product
from typing import List, Dict, Tuple
import statistics
from multiprocessing import Pool, Manager, cpu_count
import threading

from algorithms.hga import HybridGeneticAlgorithm
from utils.data_loader import load_destinations_from_csv
from models.destination import Destination

# # Lokasi start point (contoh: Surabaya pusat)
# START_POINT = (-7.2808, 112.7960)

# Lokasi start point (contoh: Surabaya pusat)
START_POINT = (-7.280710912051268, 112.7968812863991)

# Parameter ranges untuk testing
PARAMETER_GRID = {
    'population_size': [100, 300, 500, 700],
    'generations': [300, 500, 700, 1000],
    'crossover_rate': [0.6, 0.7, 0.8, 0.9],
    'mutation_rate': [0.01, 0.05, 0.2, 0.5],
    'use_2opt': [True],
    # Parameter baru yang ditambahkan
    'elitism_count': [2, 5, 10],
    'tournament_size': [3, 5, 8],
    'two_opt_iterations': [50, 100, 500]
}

# Fixed parameters (tidak ada lagi karena semua sudah masuk ke PARAMETER_GRID)
FIXED_PARAMS = {}

# Number of runs per configuration for statistical significance
NUM_RUNS_PER_CONFIG = 3

# Parallel processing workers (2 = run 2 configs simultaneously)
NUM_WORKERS = 6  # Ubah ke 1 untuk disable parallel, atau 3-4 jika CPU kuat

# Checkpoint file for resume support
CHECKPOINT_FILE = "tuning_checkpoint.pkl"

# Thread lock for checkpoint saving
checkpoint_lock = threading.Lock()


def prevent_sleep():
    """Prevent Windows from sleeping during long execution"""
    try:
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED
        )
        print("✓ Sleep mode disabled during execution")
    except Exception as e:
        print(f"⚠ Could not disable sleep mode: {e}")


def allow_sleep():
    """Allow Windows to sleep again"""
    try:
        ES_CONTINUOUS = 0x80000000
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        print("✓ Sleep mode re-enabled")
    except:
        pass


def save_checkpoint(all_results: List[Dict], config_results: List[Dict], completed_configs: set, current_config_idx: int):
    """Save checkpoint to disk for resume capability (thread-safe)"""
    with checkpoint_lock:
        checkpoint = {
            'all_results': list(all_results),
            'config_results': list(config_results),
            'completed_configs': set(completed_configs),
            'current_config_idx': current_config_idx,
            'timestamp': datetime.now().isoformat()
        }
        try:
            with open(CHECKPOINT_FILE, 'wb') as f:
                pickle.dump(checkpoint, f)
            print(f"💾 Checkpoint saved: {len(completed_configs)} configs completed (Config #{current_config_idx})")
        except Exception as e:
            print(f"⚠ Error saving checkpoint: {e}")


def load_checkpoint():
    """Load checkpoint if exists"""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'rb') as f:
                checkpoint = pickle.load(f)
            print(f"\n✓ Checkpoint found! Loaded {len(checkpoint['completed_configs'])} completed configs")
            print(f"  Last saved: {checkpoint['timestamp']}")
            print(f"  Last config: #{checkpoint['current_config_idx']}")
            return checkpoint
        except Exception as e:
            print(f"⚠ Error loading checkpoint: {e}")
            return None
    return None


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
    """
    Run single HGA experiment with given parameters
    
    Returns:
        Dictionary containing results
    """
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
    
    # Get fitness history for convergence analysis
    stats = hga.get_evolution_statistics()
    fitness_history = stats['best_fitness_history']
    distance_history = stats['best_distance_history']
    
    # Calculate convergence metrics
    initial_distance = distance_history[0]
    final_distance = distance_history[-1]
    improvement = initial_distance - final_distance
    improvement_percentage = (improvement / initial_distance) * 100 if initial_distance > 0 else 0
    
    # Find convergence generation (when improvement < 0.1% for 5 consecutive generations)
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


def run_config_wrapper(args):
    """
    Wrapper function for parallel execution of a single configuration
    """
    (destinations, start_point, pop_size, gen, cross_rate, mut_rate, 
     use_2opt, elitism, tournament, two_opt_iter, config_idx, total_configs) = args
    
    print(f"\n{'='*80}")
    print(f"⚙️  Config {config_idx}/{total_configs} - Starting...")
    print(f"   Pop: {pop_size}, Gen: {gen}, Cross: {cross_rate}, Mut: {mut_rate}")
    print(f"   Elitism: {elitism}, Tournament: {tournament}, 2-Opt: {use_2opt}")
    print(f"{'='*80}")
    
    config_runs = []
    
    try:
        # Run multiple times for statistical significance
        for run_num in range(1, NUM_RUNS_PER_CONFIG + 1):
            result = run_single_experiment(
                destinations=destinations,
                start_point=start_point,
                population_size=pop_size,
                generations=gen,
                crossover_rate=cross_rate,
                mutation_rate=mut_rate,
                use_2opt=use_2opt,
                elitism_count=elitism,
                tournament_size=tournament,
                two_opt_iterations=two_opt_iter,
                run_number=run_num
            )
            config_runs.append(result)
        
        # Aggregate runs
        aggregated = aggregate_runs(config_runs)
        
        print(f"\n✅ Config {config_idx} completed:")
        print(f"   Mean Distance: {aggregated['mean_distance_km']:.2f} km")
        print(f"   Feasible Rate: {aggregated['feasible_rate']:.1f}%")
        
        return (config_runs, aggregated)
    
    except Exception as e:
        print(f"\n❌ Error in config {config_idx}: {e}")
        return None


def aggregate_runs(runs: List[Dict]) -> Dict:
    """
    Aggregate multiple runs for the same configuration
    
    Returns:
        Dictionary with mean and std dev
    """
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


def run_hyperparameter_tuning():
    """
    Main function to run complete hyperparameter tuning with checkpoint support
    """
    print("\n" + "="*80)
    print("HYPERPARAMETER TUNING - HYBRID GENETIC ALGORITHM (WITH CHECKPOINTS)")
    print("="*80)
    
    # Load data
    destinations = load_test_data()
    
    # Generate all parameter combinations
    param_combinations = list(product(
        PARAMETER_GRID['population_size'],
        PARAMETER_GRID['generations'],
        PARAMETER_GRID['crossover_rate'],
        PARAMETER_GRID['mutation_rate'],
        PARAMETER_GRID['use_2opt'],
        PARAMETER_GRID['elitism_count'],
        PARAMETER_GRID['tournament_size'],
        PARAMETER_GRID['two_opt_iterations']
    ))
    
    total_configs = len(param_combinations)
    total_runs = total_configs * NUM_RUNS_PER_CONFIG
    
    # Try to load checkpoint
    checkpoint = load_checkpoint()
    if checkpoint:
        all_results = checkpoint['all_results']
        config_results = checkpoint['config_results']
        completed_configs = checkpoint['completed_configs']
        start_config_idx = checkpoint['current_config_idx'] + 1
        print(f"\n🔄 RESUMING from config #{start_config_idx}/{total_configs}")
        print(f"   Progress: {len(completed_configs)}/{total_configs} configs completed")
        print(f"   Remaining: {total_configs - len(completed_configs)} configs")
    else:
        all_results = []
        config_results = []
        completed_configs = set()
        start_config_idx = 1
        print("\n🆕 Starting fresh (no checkpoint found)")
    
    print(f"\nTotal configurations: {total_configs}")
    print(f"Runs per configuration: {NUM_RUNS_PER_CONFIG}")
    print(f"Total experiments: {total_runs}")
    print(f"\n⚡ PARALLEL MODE: Using {NUM_WORKERS} workers")
    print(f"   Speed boost: ~{NUM_WORKERS}x faster than sequential")
    print(f"   Estimated time: {total_runs * 10 / (3600 * NUM_WORKERS):.1f} - {total_runs * 20 / (3600 * NUM_WORKERS):.1f} hours")
    
    if checkpoint:
        response = input("\nPress Enter to RESUME tuning (or Ctrl+C to cancel)...")
    else:
        response = input("\nPress Enter to START tuning (or Ctrl+C to cancel)...")
    
    start_time_total = time.time()
    
    # Prepare configurations to process
    configs_to_process = []
    for config_idx, (pop_size, gen, cross_rate, mut_rate, use_2opt, elitism, tournament, two_opt_iter) in enumerate(param_combinations, 1):
        # Create unique config key
        config_key = f"{pop_size}_{gen}_{cross_rate}_{mut_rate}_{use_2opt}_{elitism}_{tournament}_{two_opt_iter}"
        
        # Skip if already completed
        if config_key in completed_configs:
            continue
        
        # Skip configs before resume point
        if config_idx < start_config_idx:
            continue
        
        # Add to processing queue
        configs_to_process.append((
            destinations, START_POINT, pop_size, gen, cross_rate, mut_rate,
            use_2opt, elitism, tournament, two_opt_iter, config_idx, total_configs
        ))
    
    print(f"\n📋 Configs to process: {len(configs_to_process)}")
    print(f"\n🚀 Starting parallel execution with {NUM_WORKERS} workers...\n")
    
    # Process configurations in parallel
    try:
        if NUM_WORKERS > 1:
            # Parallel execution
            with Pool(processes=NUM_WORKERS) as pool:
                results_iter = pool.imap_unordered(run_config_wrapper, configs_to_process)
                
                for idx, result in enumerate(results_iter, 1):
                    if result is None:
                        continue
                    
                    config_runs, aggregated = result
                    
                    # Add results
                    all_results.extend(config_runs)
                    config_results.append(aggregated)
                    
                    # Mark as completed
                    config_key = f"{aggregated['population_size']}_{aggregated['generations']}_{aggregated['crossover_rate']}_{aggregated['mutation_rate']}_{aggregated['use_2opt']}_{aggregated['elitism_count']}_{aggregated['tournament_size']}_{aggregated['two_opt_iterations']}"
                    completed_configs.add(config_key)
                    
                    print(f"\n📊 Progress: {len(completed_configs)}/{len(configs_to_process) + len(completed_configs) - len(configs_to_process)} ({len(completed_configs)/len(configs_to_process)*100:.1f}%)")
                    
                    # Save checkpoint every 5 configs
                    if len(completed_configs) % 5 == 0:
                        save_checkpoint(all_results, config_results, completed_configs, len(completed_configs))
        else:
            # Sequential execution (fallback)
            print("⚠️  Running in sequential mode (NUM_WORKERS=1)\n")
            for config_data in configs_to_process:
                result = run_config_wrapper(config_data)
                if result is None:
                    continue
                
                config_runs, aggregated = result
                all_results.extend(config_runs)
                config_results.append(aggregated)
                
                config_key = f"{aggregated['population_size']}_{aggregated['generations']}_{aggregated['crossover_rate']}_{aggregated['mutation_rate']}_{aggregated['use_2opt']}_{aggregated['elitism_count']}_{aggregated['tournament_size']}_{aggregated['two_opt_iterations']}"
                completed_configs.add(config_key)
                
                # Save checkpoint every 5 configs
                if len(completed_configs) % 5 == 0:
                    save_checkpoint(all_results, config_results, completed_configs, len(completed_configs))
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user - saving checkpoint...")
        save_checkpoint(all_results, config_results, completed_configs, len(completed_configs))
        raise
    except Exception as e:
        print(f"\n\n❌ Error during parallel execution: {e}")
        save_checkpoint(all_results, config_results, completed_configs, len(completed_configs))
        raise
    
    # Final checkpoint save
    save_checkpoint(all_results, config_results, completed_configs, len(completed_configs))
    
    end_time_total = time.time()
    total_duration = end_time_total - start_time_total
    
    print(f"\n\n{'='*80}")
    print(f"🎉 TUNING COMPLETED!")
    print(f"{'='*80}")
    print(f"Total configurations: {len(completed_configs)}")
    print(f"Total runs: {len(all_results)}")
    print(f"Total time: {total_duration / 3600:.2f} hours ({total_duration / 60:.1f} minutes)")
    print(f"Average time per config: {total_duration / len(completed_configs):.2f} seconds")
    print(f"Speed boost with {NUM_WORKERS} workers: ~{NUM_WORKERS}x faster!")
    
    # Save results
    save_results(all_results, config_results)
    
    # Analyze and print best configurations
    analyze_results(config_results)
    
    return config_results


def save_results(all_results: List[Dict], config_results: List[Dict]):
    """Save results to CSV files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save detailed results
    detailed_file = f"hyperparameter_tuning_detailed_{timestamp}.csv"
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
                # Remove history fields for CSV
                row = {k: v for k, v in result.items() if not k.endswith('_history')}
                writer.writerow(row)
    
    print(f"\n✓ Detailed results saved to: {detailed_file}")
    
    # Save aggregated results
    aggregated_file = f"hyperparameter_tuning_aggregated_{timestamp}.csv"
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
                # Remove all_runs field for CSV
                row = {k: v for k, v in result.items() if k != 'all_runs'}
                writer.writerow(row)
    
    print(f"✓ Aggregated results saved to: {aggregated_file}")
    
    # Save full results with history as JSON
    json_file = f"hyperparameter_tuning_full_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'detailed_results': all_results,
            'aggregated_results': config_results,
            'parameter_grid': PARAMETER_GRID,
            'fixed_parameters': FIXED_PARAMS,
            'num_runs_per_config': NUM_RUNS_PER_CONFIG
        }, f, indent=2)
    
    print(f"✓ Full results (with history) saved to: {json_file}")


def analyze_results(config_results: List[Dict]):
    """Analyze and print best configurations"""
    print("\n\n" + "="*80)
    print("ANALYSIS - BEST CONFIGURATIONS")
    print("="*80)
    
    # Sort by mean distance (lower is better)
    sorted_by_distance = sorted(config_results, key=lambda x: x['mean_distance_km'])
    
    print("\n📊 TOP 5 CONFIGURATIONS BY DISTANCE:")
    print("-" * 80)
    for i, config in enumerate(sorted_by_distance[:5], 1):
        print(f"\n#{i} - Mean Distance: {config['mean_distance_km']:.2f} km")
        print(f"   Population: {config['population_size']}, Generations: {config['generations']}")
        print(f"   Crossover: {config['crossover_rate']}, Mutation: {config['mutation_rate']}")
        print(f"   2-Opt: {config['use_2opt']}, Elitism: {config['elitism_count']}, Tournament: {config['tournament_size']}")
        print(f"   2-Opt Iterations: {config['two_opt_iterations']}")
        print(f"   Execution Time: {config['mean_execution_time']:.2f}s")
        print(f"   Feasible Rate: {config['feasible_rate']:.1f}%")
        print(f"   Convergence: Gen {config['mean_convergence_gen']:.0f}")
    
    # Best by execution time (considering only feasible solutions)
    feasible_configs = [c for c in config_results if c['feasible_rate'] >= 50]
    if feasible_configs:
        sorted_by_time = sorted(feasible_configs, key=lambda x: x['mean_execution_time'])
        
        print("\n\n⚡ TOP 5 CONFIGURATIONS BY SPEED (Feasible solutions only):")
        print("-" * 80)
        for i, config in enumerate(sorted_by_time[:5], 1):
            print(f"\n#{i} - Execution Time: {config['mean_execution_time']:.2f}s")
            print(f"   Population: {config['population_size']}, Generations: {config['generations']}")
            print(f"   Distance: {config['mean_distance_km']:.2f} km")
            print(f"   Crossover: {config['crossover_rate']}, Mutation: {config['mutation_rate']}")
            print(f"   2-Opt: {config['use_2opt']}, Elitism: {config['elitism_count']}, Tournament: {config['tournament_size']}")
    
    # Analyze parameter effects
    print("\n\n" + "="*80)
    print("PARAMETER EFFECT ANALYSIS")
    print("="*80)
    
    # Population size effect
    print("\n📈 POPULATION SIZE EFFECT:")
    for pop_size in PARAMETER_GRID['population_size']:
        pop_configs = [c for c in config_results if c['population_size'] == pop_size]
        mean_dist = statistics.mean([c['mean_distance_km'] for c in pop_configs])
        mean_time = statistics.mean([c['mean_execution_time'] for c in pop_configs])
        print(f"  {pop_size:>4} → Distance: {mean_dist:.2f} km, Time: {mean_time:.2f}s")
    
    # Generations effect
    print("\n📈 GENERATIONS EFFECT:")
    for gen in PARAMETER_GRID['generations']:
        gen_configs = [c for c in config_results if c['generations'] == gen]
        mean_dist = statistics.mean([c['mean_distance_km'] for c in gen_configs])
        mean_time = statistics.mean([c['mean_execution_time'] for c in gen_configs])
        mean_conv = statistics.mean([c['mean_convergence_gen'] for c in gen_configs])
        print(f"  {gen:>3} → Distance: {mean_dist:.2f} km, Time: {mean_time:.2f}s, Convergence: {mean_conv:.0f}")
    
    # Crossover rate effect
    print("\n📈 CROSSOVER RATE EFFECT:")
    for cross_rate in PARAMETER_GRID['crossover_rate']:
        cross_configs = [c for c in config_results if c['crossover_rate'] == cross_rate]
        mean_dist = statistics.mean([c['mean_distance_km'] for c in cross_configs])
        mean_imp = statistics.mean([c['mean_improvement_pct'] for c in cross_configs])
        print(f"  {cross_rate:.1f} → Distance: {mean_dist:.2f} km, Improvement: {mean_imp:.1f}%")
    
    # Mutation rate effect
    print("\n📈 MUTATION RATE EFFECT:")
    for mut_rate in PARAMETER_GRID['mutation_rate']:
        mut_configs = [c for c in config_results if c['mutation_rate'] == mut_rate]
        mean_dist = statistics.mean([c['mean_distance_km'] for c in mut_configs])
        mean_imp = statistics.mean([c['mean_improvement_pct'] for c in mut_configs])
        print(f"  {mut_rate:.2f} → Distance: {mean_dist:.2f} km, Improvement: {mean_imp:.1f}%")
    
    # 2-Opt effect
    print("\n📈 2-OPT EFFECT:")
    for use_2opt in [True, False]:
        opt_configs = [c for c in config_results if c['use_2opt'] == use_2opt]
        mean_dist = statistics.mean([c['mean_distance_km'] for c in opt_configs])
        mean_time = statistics.mean([c['mean_execution_time'] for c in opt_configs])
        mean_imp = statistics.mean([c['mean_improvement_pct'] for c in opt_configs])
        status = "With 2-Opt" if use_2opt else "Without 2-Opt"
        print(f"  {status:>15} → Distance: {mean_dist:.2f} km, Time: {mean_time:.2f}s, Improvement: {mean_imp:.1f}%")
    
    # Elitism count effect
    print("\n📈 ELITISM COUNT EFFECT:")
    for elitism in PARAMETER_GRID['elitism_count']:
        elitism_configs = [c for c in config_results if c['elitism_count'] == elitism]
        mean_dist = statistics.mean([c['mean_distance_km'] for c in elitism_configs])
        mean_time = statistics.mean([c['mean_execution_time'] for c in elitism_configs])
        print(f"  {elitism:>3} → Distance: {mean_dist:.2f} km, Time: {mean_time:.2f}s")
    
    # Tournament size effect
    print("\n📈 TOURNAMENT SIZE EFFECT:")
    for tournament in PARAMETER_GRID['tournament_size']:
        tournament_configs = [c for c in config_results if c['tournament_size'] == tournament]
        mean_dist = statistics.mean([c['mean_distance_km'] for c in tournament_configs])
        mean_conv = statistics.mean([c['mean_convergence_gen'] for c in tournament_configs])
        print(f"  {tournament:>2} → Distance: {mean_dist:.2f} km, Convergence: {mean_conv:.0f}")
    
    # 2-Opt iterations effect
    print("\n📈 2-OPT ITERATIONS EFFECT:")
    for two_opt_iter in PARAMETER_GRID['two_opt_iterations']:
        opt_iter_configs = [c for c in config_results if c['two_opt_iterations'] == two_opt_iter]
        mean_dist = statistics.mean([c['mean_distance_km'] for c in opt_iter_configs])
        mean_time = statistics.mean([c['mean_execution_time'] for c in opt_iter_configs])
        print(f"  {two_opt_iter:>4} → Distance: {mean_dist:.2f} km, Time: {mean_time:.2f}s")
    
    # Best balanced configuration
    print("\n\n" + "="*80)
    print("🏆 RECOMMENDED CONFIGURATION")
    print("="*80)
    
    # Score: weighted combination of distance (70%) and time (30%)
    # Normalize values first
    min_dist = min(c['mean_distance_km'] for c in config_results)
    max_dist = max(c['mean_distance_km'] for c in config_results)
    min_time = min(c['mean_execution_time'] for c in config_results)
    max_time = max(c['mean_execution_time'] for c in config_results)
    
    for config in config_results:
        norm_dist = (config['mean_distance_km'] - min_dist) / (max_dist - min_dist) if max_dist > min_dist else 0
        norm_time = (config['mean_execution_time'] - min_time) / (max_time - min_time) if max_time > min_time else 0
        config['balanced_score'] = 0.7 * (1 - norm_dist) + 0.3 * (1 - norm_time)
    
    best_balanced = max(config_results, key=lambda x: x['balanced_score'])
    
    print(f"\nBest Balanced Configuration (70% distance, 30% speed):")
    print(f"  Population Size: {best_balanced['population_size']}")
    print(f"  Generations: {best_balanced['generations']}")
    print(f"  Crossover Rate: {best_balanced['crossover_rate']}")
    print(f"  Mutation Rate: {best_balanced['mutation_rate']}")
    print(f"  Use 2-Opt: {best_balanced['use_2opt']}")
    print(f"  Elitism Count: {best_balanced['elitism_count']}")
    print(f"  Tournament Size: {best_balanced['tournament_size']}")
    print(f"  2-Opt Iterations: {best_balanced['two_opt_iterations']}")
    print(f"\n  Performance:")
    print(f"    Mean Distance: {best_balanced['mean_distance_km']:.2f} km")
    print(f"    Mean Execution Time: {best_balanced['mean_execution_time']:.2f}s")
    print(f"    Feasible Rate: {best_balanced['feasible_rate']:.1f}%")
    print(f"    Mean Improvement: {best_balanced['mean_improvement_pct']:.1f}%")
    print(f"    Convergence Generation: {best_balanced['mean_convergence_gen']:.0f}")
    print(f"    Balanced Score: {best_balanced['balanced_score']:.4f}")


if __name__ == "__main__":
    # Required for Windows multiprocessing
    from multiprocessing import freeze_support
    freeze_support()
    
    try:
        # Prevent sleep mode during execution
        prevent_sleep()
        
        results = run_hyperparameter_tuning()
        print("\n✅ Hyperparameter tuning completed successfully!")
        
        # Remove checkpoint file after successful completion
        if os.path.exists(CHECKPOINT_FILE):
            try:
                os.remove(CHECKPOINT_FILE)
                print(f"\n✓ Checkpoint file removed (tuning completed successfully)")
            except:
                pass
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tuning interrupted by user")
        print("\n💡 To resume: Just run the script again!")
        print(f"   Checkpoint saved in: {CHECKPOINT_FILE}")
    except Exception as e:
        print(f"\n\n❌ Error during tuning: {str(e)}")
        print("\n💡 To resume: Just run the script again!")
        raise
    finally:
        # Re-enable sleep mode
        allow_sleep()
