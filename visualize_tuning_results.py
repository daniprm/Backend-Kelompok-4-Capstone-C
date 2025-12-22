"""
Visualisasi hasil Hyperparameter Tuning
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def load_latest_results():
    """Load latest tuning results"""
    json_files = list(Path('.').glob('hyperparameter_tuning_full_*.json'))
    if not json_files:
        print("❌ No tuning results found!")
        return None
    
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading: {latest_file}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return data


def create_visualizations(data):
    """Create comprehensive visualizations"""
    
    # Convert to DataFrame
    df = pd.DataFrame(data['aggregated_results'])
    
    # Create figure with subplots (4 rows x 3 columns = 12 subplots)
    fig = plt.figure(figsize=(20, 22))
    
    # 1. Population Size Effect
    ax1 = plt.subplot(4, 3, 1)
    pop_data = df.groupby('population_size').agg({
        'mean_distance_km': 'mean',
        'mean_execution_time': 'mean'
    }).reset_index()
    
    ax1_twin = ax1.twinx()
    ax1.plot(pop_data['population_size'], pop_data['mean_distance_km'], 
             'o-', color='blue', linewidth=2, markersize=8, label='Distance')
    ax1_twin.plot(pop_data['population_size'], pop_data['mean_execution_time'], 
                  's-', color='red', linewidth=2, markersize=8, label='Time')
    
    ax1.set_xlabel('Population Size', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Mean Distance (km)', color='blue', fontsize=10, fontweight='bold')
    ax1_twin.set_ylabel('Mean Execution Time (s)', color='red', fontsize=10, fontweight='bold')
    ax1.set_title('Effect of Population Size', fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1_twin.tick_params(axis='y', labelcolor='red')
    ax1.grid(True, alpha=0.3)
    
    # 2. Generations Effect
    ax2 = plt.subplot(4, 3, 2)
    gen_data = df.groupby('generations').agg({
        'mean_distance_km': 'mean',
        'mean_convergence_gen': 'mean'
    }).reset_index()
    
    ax2_twin = ax2.twinx()
    ax2.plot(gen_data['generations'], gen_data['mean_distance_km'], 
             'o-', color='blue', linewidth=2, markersize=8, label='Distance')
    ax2_twin.plot(gen_data['generations'], gen_data['mean_convergence_gen'], 
                  's-', color='green', linewidth=2, markersize=8, label='Convergence')
    
    ax2.set_xlabel('Generations', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Mean Distance (km)', color='blue', fontsize=10, fontweight='bold')
    ax2_twin.set_ylabel('Mean Convergence Gen', color='green', fontsize=10, fontweight='bold')
    ax2.set_title('Effect of Generations', fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2_twin.tick_params(axis='y', labelcolor='green')
    ax2.grid(True, alpha=0.3)
    
    # 3. Crossover Rate Effect
    ax3 = plt.subplot(4, 3, 3)
    cross_data = df.groupby('crossover_rate').agg({
        'mean_distance_km': 'mean',
        'mean_improvement_pct': 'mean'
    }).reset_index()
    
    ax3_twin = ax3.twinx()
    ax3.plot(cross_data['crossover_rate'], cross_data['mean_distance_km'], 
             'o-', color='blue', linewidth=2, markersize=8, label='Distance')
    ax3_twin.plot(cross_data['crossover_rate'], cross_data['mean_improvement_pct'], 
                  's-', color='purple', linewidth=2, markersize=8, label='Improvement')
    
    ax3.set_xlabel('Crossover Rate', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Mean Distance (km)', color='blue', fontsize=10, fontweight='bold')
    ax3_twin.set_ylabel('Mean Improvement (%)', color='purple', fontsize=10, fontweight='bold')
    ax3.set_title('Effect of Crossover Rate', fontsize=12, fontweight='bold')
    ax3.tick_params(axis='y', labelcolor='blue')
    ax3_twin.tick_params(axis='y', labelcolor='purple')
    ax3.grid(True, alpha=0.3)
    
    # 4. Mutation Rate Effect
    ax4 = plt.subplot(4, 3, 4)
    mut_data = df.groupby('mutation_rate').agg({
        'mean_distance_km': 'mean',
        'mean_improvement_pct': 'mean'
    }).reset_index()
    
    ax4_twin = ax4.twinx()
    ax4.plot(mut_data['mutation_rate'], mut_data['mean_distance_km'], 
             'o-', color='blue', linewidth=2, markersize=8, label='Distance')
    ax4_twin.plot(mut_data['mutation_rate'], mut_data['mean_improvement_pct'], 
                  's-', color='orange', linewidth=2, markersize=8, label='Improvement')
    
    ax4.set_xlabel('Mutation Rate', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Mean Distance (km)', color='blue', fontsize=10, fontweight='bold')
    ax4_twin.set_ylabel('Mean Improvement (%)', color='orange', fontsize=10, fontweight='bold')
    ax4.set_title('Effect of Mutation Rate', fontsize=12, fontweight='bold')
    ax4.tick_params(axis='y', labelcolor='blue')
    ax4_twin.tick_params(axis='y', labelcolor='orange')
    ax4.grid(True, alpha=0.3)
    
    # 5. 2-Opt Effect
    ax5 = plt.subplot(4, 3, 5)
    opt_data = df.groupby('use_2opt').agg({
        'mean_distance_km': 'mean',
        'mean_execution_time': 'mean',
        'mean_improvement_pct': 'mean'
    }).reset_index()
    opt_data['use_2opt'] = opt_data['use_2opt'].map({True: 'With 2-Opt', False: 'Without 2-Opt'})
    
    x = np.arange(len(opt_data))
    width = 0.25
    
    ax5.bar(x - width, opt_data['mean_distance_km'], width, label='Distance (km)', color='blue', alpha=0.8)
    ax5.bar(x, opt_data['mean_execution_time'], width, label='Time (s)', color='red', alpha=0.8)
    ax5.bar(x + width, opt_data['mean_improvement_pct'], width, label='Improvement (%)', color='green', alpha=0.8)
    
    ax5.set_xlabel('2-Opt Usage', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Value', fontsize=10, fontweight='bold')
    ax5.set_title('Effect of 2-Opt Local Search', fontsize=12, fontweight='bold')
    ax5.set_xticks(x)
    ax5.set_xticklabels(opt_data['use_2opt'])
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 6. Distance vs Execution Time Scatter
    ax6 = plt.subplot(4, 3, 6)
    scatter = ax6.scatter(df['mean_execution_time'], df['mean_distance_km'], 
                          c=df['feasible_rate'], cmap='RdYlGn', s=100, alpha=0.6,
                          edgecolors='black', linewidth=0.5)
    ax6.set_xlabel('Mean Execution Time (s)', fontsize=11, fontweight='bold')
    ax6.set_ylabel('Mean Distance (km)', fontsize=10, fontweight='bold')
    ax6.set_title('Distance vs Execution Time', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax6, label='Feasible Rate (%)')
    
    # 7. Heatmap: Population vs Generations
    ax7 = plt.subplot(4, 3, 7)
    pivot_pop_gen = df.groupby(['population_size', 'generations'])['mean_distance_km'].mean().unstack()
    sns.heatmap(pivot_pop_gen, annot=True, fmt='.2f', cmap='YlOrRd', ax=ax7, 
                cbar_kws={'label': 'Mean Distance (km)'})
    ax7.set_title('Population vs Generations\n(Mean Distance)', fontsize=12, fontweight='bold')
    ax7.set_xlabel('Generations', fontsize=11, fontweight='bold')
    ax7.set_ylabel('Population Size', fontsize=10, fontweight='bold')
    
    # 8. Heatmap: Crossover vs Mutation
    ax8 = plt.subplot(4, 3, 8)
    pivot_cross_mut = df.groupby(['crossover_rate', 'mutation_rate'])['mean_distance_km'].mean().unstack()
    sns.heatmap(pivot_cross_mut, annot=True, fmt='.2f', cmap='viridis', ax=ax8,
                cbar_kws={'label': 'Mean Distance (km)'})
    ax8.set_title('Crossover vs Mutation Rate\n(Mean Distance)', fontsize=12, fontweight='bold')
    ax8.set_xlabel('Mutation Rate', fontsize=11, fontweight='bold')
    ax8.set_ylabel('Crossover Rate', fontsize=10, fontweight='bold')
    
    # 9. Top 10 Configurations
    ax9 = plt.subplot(4, 3, 9)
    top_10 = df.nsmallest(10, 'mean_distance_km')
    config_labels = [f"P{int(row['population_size'])}_G{int(row['generations'])}_\nC{row['crossover_rate']}_M{row['mutation_rate']}" 
                     for _, row in top_10.iterrows()]
    
    colors = ['green' if x else 'orange' for x in top_10['use_2opt']]
    bars = ax9.barh(range(len(top_10)), top_10['mean_distance_km'], color=colors, alpha=0.7)
    ax9.set_yticks(range(len(top_10)))
    ax9.set_yticklabels(config_labels, fontsize=7)
    ax9.set_xlabel('Mean Distance (km)', fontsize=11, fontweight='bold')
    ax9.set_title('Top 10 Configurations\n(Green=2-Opt, Orange=No 2-Opt)', fontsize=12, fontweight='bold')
    ax9.grid(True, alpha=0.3, axis='x')
    ax9.invert_yaxis()
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, top_10['mean_distance_km'])):
        ax9.text(val, i, f' {val:.2f}', va='center', fontsize=8, fontweight='bold')
    
    # 10-12. Convergence Curves for Top 3 Configurations
    top_3 = df.nsmallest(3, 'mean_distance_km')
    
    for idx, (_, config) in enumerate(top_3.iterrows(), 1):
        ax = plt.subplot(4, 3, 9 + idx)
        
        # Get all runs for this configuration
        all_distances = []
        for run_idx, run in enumerate(config['all_runs']):
            if 'distance_history' in run and run['distance_history']:
                distance_history = run['distance_history']
                ax.plot(distance_history, alpha=0.3, color='steelblue', linewidth=1)
                all_distances.append(distance_history)
        
        # Plot mean convergence if we have data
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
        
        ax.set_xlabel('Generation', fontsize=10, fontweight='bold')
        ax.set_ylabel('Best Distance (km)', fontsize=10, fontweight='bold')
        ax.set_title(f"Rank #{idx} Convergence\n"
                    f"Pop={int(config['population_size'])}, Gen={int(config['generations'])}, "
                    f"CR={config['crossover_rate']}, MR={config['mutation_rate']}\n"
                    f"2-Opt={config['use_2opt']} | Dist={config['mean_distance_km']:.2f}km",
                    fontsize=9, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle=':')
        ax.legend(fontsize=7, loc='upper right')
        
        # Add improvement annotation
        if all_distances and len(mean_distance) > 1:
            initial_dist = mean_distance[0]
            final_dist = mean_distance[-1]
            improvement = ((initial_dist - final_dist) / initial_dist) * 100
            ax.text(0.02, 0.98, f'Improvement: {improvement:.1f}%', 
                   transform=ax.transAxes, fontsize=8, 
                   verticalalignment='top', bbox=dict(boxstyle='round', 
                   facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Save figure
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hyperparameter_tuning_visualization_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\n✓ Visualization saved to: {filename}")
    
    plt.show()


def plot_convergence_curves(data):
    """Plot convergence curves for best configurations"""
    df = pd.DataFrame(data['aggregated_results'])
    
    # Get top 5 configurations
    top_5 = df.nsmallest(5, 'mean_distance_km')
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    
    for idx, (_, config) in enumerate(top_5.iterrows()):
        ax = axes[idx]
        
        # Get all runs for this configuration
        for run in config['all_runs']:
            distance_history = run['distance_history']
            ax.plot(distance_history, alpha=0.3, color='blue')
        
        # Plot mean convergence
        all_distances = [run['distance_history'] for run in config['all_runs']]
        max_len = max(len(d) for d in all_distances)
        
        # Pad shorter sequences
        padded = []
        for d in all_distances:
            if len(d) < max_len:
                padded.append(d + [d[-1]] * (max_len - len(d)))
            else:
                padded.append(d)
        
        mean_distance = np.mean(padded, axis=0)
        ax.plot(mean_distance, color='red', linewidth=2, label='Mean')
        
        ax.set_xlabel('Generation', fontsize=10, fontweight='bold')
        ax.set_ylabel('Best Distance (km)', fontsize=10, fontweight='bold')
        ax.set_title(f"Rank #{idx+1}\nP={int(config['population_size'])}, G={int(config['generations'])}, "
                    f"C={config['crossover_rate']}, M={config['mutation_rate']}, "
                    f"2Opt={config['use_2opt']}\nDist: {config['mean_distance_km']:.2f}km",
                    fontsize=9, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    
    # Hide last subplot if not needed
    if len(top_5) < 6:
        axes[-1].axis('off')
    
    plt.tight_layout()
    
    # Save figure
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    filename = f"convergence_curves_top5_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Convergence curves saved to: {filename}")
    
    plt.show()


def generate_report(data):
    """Generate text report"""
    df = pd.DataFrame(data['aggregated_results'])
    
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hyperparameter_tuning_report_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("HYPERPARAMETER TUNING REPORT\n")
        f.write("Hybrid Genetic Algorithm - Tourism Route Recommendation\n")
        f.write("="*80 + "\n\n")
        
        # Summary statistics
        f.write("SUMMARY STATISTICS\n")
        f.write("-"*80 + "\n")
        f.write(f"Total configurations tested: {len(df)}\n")
        f.write(f"Runs per configuration: {data['num_runs_per_config']}\n")
        f.write(f"Total experiments: {len(data['detailed_results'])}\n\n")
        
        f.write(f"Distance Range: {df['mean_distance_km'].min():.2f} - {df['mean_distance_km'].max():.2f} km\n")
        f.write(f"Execution Time Range: {df['mean_execution_time'].min():.2f} - {df['mean_execution_time'].max():.2f} s\n")
        f.write(f"Feasible Rate Range: {df['feasible_rate'].min():.1f}% - {df['feasible_rate'].max():.1f}%\n\n")
        
        # Best configuration
        best = df.loc[df['mean_distance_km'].idxmin()]
        f.write("\n" + "="*80 + "\n")
        f.write("BEST CONFIGURATION (Minimum Distance)\n")
        f.write("="*80 + "\n")
        f.write(f"Population Size: {int(best['population_size'])}\n")
        f.write(f"Generations: {int(best['generations'])}\n")
        f.write(f"Crossover Rate: {best['crossover_rate']}\n")
        f.write(f"Mutation Rate: {best['mutation_rate']}\n")
        f.write(f"Use 2-Opt: {best['use_2opt']}\n\n")
        f.write(f"Mean Distance: {best['mean_distance_km']:.2f} ± {best['std_distance_km']:.2f} km\n")
        f.write(f"Mean Execution Time: {best['mean_execution_time']:.2f} ± {best['std_execution_time']:.2f} s\n")
        f.write(f"Feasible Rate: {best['feasible_rate']:.1f}%\n")
        f.write(f"Mean Improvement: {best['mean_improvement_pct']:.1f}%\n")
        f.write(f"Convergence Generation: {best['mean_convergence_gen']:.0f}\n\n")
        
        # Parameter analysis
        f.write("\n" + "="*80 + "\n")
        f.write("PARAMETER EFFECT ANALYSIS\n")
        f.write("="*80 + "\n\n")
        
        # Population
        f.write("POPULATION SIZE:\n")
        for pop in sorted(df['population_size'].unique()):
            subset = df[df['population_size'] == pop]
            f.write(f"  {pop:>4}: Distance={subset['mean_distance_km'].mean():.2f}km, "
                   f"Time={subset['mean_execution_time'].mean():.2f}s\n")
        
        # Generations
        f.write("\nGENERATIONS:\n")
        for gen in sorted(df['generations'].unique()):
            subset = df[df['generations'] == gen]
            f.write(f"  {gen:>3}: Distance={subset['mean_distance_km'].mean():.2f}km, "
                   f"Time={subset['mean_execution_time'].mean():.2f}s, "
                   f"Convergence={subset['mean_convergence_gen'].mean():.0f}\n")
        
        # Crossover
        f.write("\nCROSSOVER RATE:\n")
        for cross in sorted(df['crossover_rate'].unique()):
            subset = df[df['crossover_rate'] == cross]
            f.write(f"  {cross:.1f}: Distance={subset['mean_distance_km'].mean():.2f}km, "
                   f"Improvement={subset['mean_improvement_pct'].mean():.1f}%\n")
        
        # Mutation
        f.write("\nMUTATION RATE:\n")
        for mut in sorted(df['mutation_rate'].unique()):
            subset = df[df['mutation_rate'] == mut]
            f.write(f"  {mut:.2f}: Distance={subset['mean_distance_km'].mean():.2f}km, "
                   f"Improvement={subset['mean_improvement_pct'].mean():.1f}%\n")
        
        # 2-Opt
        f.write("\n2-OPT:\n")
        for opt in [True, False]:
            subset = df[df['use_2opt'] == opt]
            status = "With 2-Opt" if opt else "Without 2-Opt"
            f.write(f"  {status:>15}: Distance={subset['mean_distance_km'].mean():.2f}km, "
                   f"Time={subset['mean_execution_time'].mean():.2f}s\n")
    
    print(f"✓ Report saved to: {filename}")


def main():
    print("\n" + "="*80)
    print("HYPERPARAMETER TUNING - VISUALIZATION & ANALYSIS")
    print("="*80)
    
    # Load results
    data = load_latest_results()
    if data is None:
        return
    
    print("\n1. Creating comprehensive visualizations (12 plots with convergence curves)...")
    create_visualizations(data)
    
    print("\n2. Plotting detailed convergence curves for top 5 configurations...")
    plot_convergence_curves(data)
    
    print("\n3. Generating text report...")
    generate_report(data)
    
    print("\n" + "="*80)
    print("✅ All visualizations and reports generated successfully!")
    print("=" + "="*80)
    print("Generated files:")
    print("  📊 hyperparameter_tuning_visualization_[timestamp].png (12 plots)")
    print("  📈 convergence_curves_top5_[timestamp].png (Top 5 detailed)")
    print("  📄 hyperparameter_tuning_report_[timestamp].txt")
    print("="*80)


if __name__ == "__main__":
    main()
