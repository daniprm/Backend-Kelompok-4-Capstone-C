"""
Test script untuk memverifikasi visualisasi konvergensi
"""

import json
import matplotlib.pyplot as plt
import numpy as np

# Create sample data untuk testing visualisasi
sample_data = {
    "aggregated_results": [
        {
            "population_size": 300,
            "generations": 40,
            "crossover_rate": 0.8,
            "mutation_rate": 0.05,
            "use_2opt": True,
            "num_runs": 3,
            "mean_distance_km": 16.8,
            "std_distance_km": 0.3,
            "min_distance_km": 16.5,
            "max_distance_km": 17.1,
            "mean_execution_time": 8.2,
            "std_execution_time": 0.5,
            "mean_improvement_pct": 35.2,
            "mean_convergence_gen": 28,
            "feasible_rate": 100.0,
            "all_runs": [
                {
                    "distance_history": [26.5, 24.2, 22.1, 20.5, 19.2, 18.1, 17.5, 17.2, 
                                       17.0, 16.9, 16.85, 16.8, 16.75, 16.7, 16.65, 16.6,
                                       16.58, 16.56, 16.54, 16.52, 16.5] + [16.5] * 19
                },
                {
                    "distance_history": [27.1, 25.0, 23.2, 21.8, 20.1, 18.9, 18.0, 17.5,
                                       17.2, 17.0, 16.95, 16.9, 16.85, 16.8, 16.75, 16.7,
                                       16.68, 16.66, 16.64, 16.62, 16.6] + [16.6] * 19
                },
                {
                    "distance_history": [26.8, 24.5, 22.5, 21.0, 19.8, 18.5, 17.8, 17.3,
                                       17.1, 16.95, 16.9, 16.85, 16.8, 16.75, 16.7, 16.65,
                                       16.63, 16.61, 16.59, 16.57, 16.55] + [16.55] * 19
                }
            ]
        },
        {
            "population_size": 500,
            "generations": 40,
            "crossover_rate": 0.7,
            "mutation_rate": 0.05,
            "use_2opt": True,
            "num_runs": 3,
            "mean_distance_km": 17.2,
            "std_distance_km": 0.4,
            "min_distance_km": 16.9,
            "max_distance_km": 17.6,
            "mean_execution_time": 12.5,
            "std_execution_time": 0.8,
            "mean_improvement_pct": 33.8,
            "mean_convergence_gen": 30,
            "feasible_rate": 100.0,
            "all_runs": [
                {
                    "distance_history": [27.2, 25.1, 23.5, 22.0, 20.5, 19.2, 18.5, 18.0,
                                       17.7, 17.5, 17.4, 17.3, 17.25, 17.2, 17.15, 17.1,
                                       17.08, 17.06, 17.04, 17.02, 17.0] + [17.0] * 19
                },
                {
                    "distance_history": [26.9, 24.8, 23.0, 21.5, 20.2, 19.0, 18.3, 17.8,
                                       17.6, 17.45, 17.4, 17.35, 17.3, 17.25, 17.2, 17.15,
                                       17.13, 17.11, 17.09, 17.07, 17.05] + [17.05] * 19
                },
                {
                    "distance_history": [27.5, 25.3, 23.8, 22.3, 20.8, 19.5, 18.8, 18.2,
                                       17.9, 17.7, 17.6, 17.5, 17.45, 17.4, 17.35, 17.3,
                                       17.28, 17.26, 17.24, 17.22, 17.2] + [17.2] * 19
                }
            ]
        },
        {
            "population_size": 100,
            "generations": 20,
            "crossover_rate": 0.8,
            "mutation_rate": 0.2,
            "use_2opt": False,
            "num_runs": 3,
            "mean_distance_km": 19.5,
            "std_distance_km": 0.6,
            "min_distance_km": 19.0,
            "max_distance_km": 20.1,
            "mean_execution_time": 2.8,
            "std_execution_time": 0.3,
            "mean_improvement_pct": 25.5,
            "mean_convergence_gen": 15,
            "feasible_rate": 100.0,
            "all_runs": [
                {
                    "distance_history": [26.0, 24.5, 23.0, 22.0, 21.2, 20.5, 20.0, 19.7, 
                                       19.5, 19.4, 19.35, 19.3, 19.28, 19.26, 19.25, 19.24,
                                       19.23, 19.22, 19.21, 19.2]
                },
                {
                    "distance_history": [26.5, 25.0, 23.5, 22.5, 21.8, 21.0, 20.5, 20.2,
                                       20.0, 19.9, 19.85, 19.8, 19.78, 19.76, 19.75, 19.74,
                                       19.73, 19.72, 19.71, 19.7]
                },
                {
                    "distance_history": [25.8, 24.2, 22.8, 21.8, 21.0, 20.3, 19.9, 19.6,
                                       19.4, 19.3, 19.25, 19.2, 19.18, 19.16, 19.15, 19.14,
                                       19.13, 19.12, 19.11, 19.1]
                }
            ]
        }
    ],
    "detailed_results": [],
    "parameter_grid": {
        "population_size": [100, 300, 500],
        "generations": [20, 40],
        "crossover_rate": [0.7, 0.8],
        "mutation_rate": [0.05, 0.2],
        "use_2opt": [True, False]
    },
    "fixed_parameters": {
        "elitism_count": 2,
        "tournament_size": 8,
        "two_opt_iterations": 100
    },
    "num_runs_per_config": 3
}

# Save sample data
with open('sample_tuning_results.json', 'w') as f:
    json.dump(sample_data, f, indent=2)

print("✓ Sample data created: sample_tuning_results.json")

# Test convergence plot
print("\nTesting convergence visualization...")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for idx, config in enumerate(sample_data['aggregated_results'][:3]):
    ax = axes[idx]
    
    all_distances = []
    for run in config['all_runs']:
        if 'distance_history' in run and run['distance_history']:
            distance_history = run['distance_history']
            ax.plot(distance_history, alpha=0.3, color='steelblue', linewidth=1)
            all_distances.append(distance_history)
    
    if all_distances:
        max_len = max(len(d) for d in all_distances)
        
        # Pad shorter sequences
        padded = []
        for d in all_distances:
            if len(d) < max_len:
                padded.append(d + [d[-1]] * (max_len - len(d)))
            else:
                padded.append(d)
        
        mean_distance = np.mean(padded, axis=0)
        std_distance = np.std(padded, axis=0)
        generations = np.arange(len(mean_distance))
        
        # Plot mean with confidence interval
        ax.plot(mean_distance, color='red', linewidth=2.5, label='Mean', zorder=10)
        ax.fill_between(generations, 
                       mean_distance - std_distance, 
                       mean_distance + std_distance,
                       color='red', alpha=0.2, label='±1 Std Dev')
        
        # Add convergence line
        if 'mean_convergence_gen' in config:
            conv_gen = int(config['mean_convergence_gen'])
            if conv_gen < len(mean_distance):
                ax.axvline(x=conv_gen, color='green', linestyle='--', linewidth=2, 
                         label=f'Convergence (Gen {conv_gen})', alpha=0.7)
    
    ax.set_xlabel('Generation', fontsize=11, fontweight='bold')
    ax.set_ylabel('Best Distance (km)', fontsize=11, fontweight='bold')
    ax.set_title(f"Config #{idx+1}\n"
                f"Pop={int(config['population_size'])}, Gen={int(config['generations'])}, "
                f"CR={config['crossover_rate']}, MR={config['mutation_rate']}\n"
                f"2-Opt={config['use_2opt']} | Dist={config['mean_distance_km']:.2f}km",
                fontsize=10, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.legend(fontsize=9, loc='upper right')
    
    # Add improvement annotation
    if all_distances and len(mean_distance) > 1:
        initial_dist = mean_distance[0]
        final_dist = mean_distance[-1]
        improvement = ((initial_dist - final_dist) / initial_dist) * 100
        ax.text(0.02, 0.98, f'Improvement: {improvement:.1f}%', 
               transform=ax.transAxes, fontsize=9, 
               verticalalignment='top', bbox=dict(boxstyle='round', 
               facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('test_convergence_visualization.png', dpi=300, bbox_inches='tight')
print("✓ Test visualization saved: test_convergence_visualization.png")
plt.show()

print("\n" + "="*80)
print("✅ Convergence visualization test completed!")
print("="*80)
print("\nVisualisasi sekarang menampilkan:")
print("  1. Individual runs (garis biru transparan)")
print("  2. Mean convergence (garis merah tebal)")
print("  3. Confidence interval (area merah transparan)")
print("  4. Convergence point (garis hijau putus-putus)")
print("  5. Improvement percentage (kotak kuning)")
print("\nSemua grafik ini akan muncul di plot 10, 11, 12 pada main visualization!")
