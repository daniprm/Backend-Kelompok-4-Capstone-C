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

# Parameter Grid Reference
PARAMETER_GRID = {
    'population_size': [100, 300, 500, 700],
    'generations': [300, 500, 700, 1000],
    'crossover_rate': [0.6, 0.7, 0.8, 0.9],
    'mutation_rate': [0.01, 0.05, 0.2, 0.5],
    'elitism_count': [2, 5, 10],
    'tournament_size': [3, 5, 8],
    'two_opt_iterations': [50, 100, 500]
}


def load_latest_results():
    """Load latest tuning results"""
    json_files = list(Path('.').glob('hyperparameter_tuning_full_*.json'))
    if not json_files:
        print("❌ Tidak ada hasil tuning ditemukan!")
        return None
    
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"Memuat: {latest_file}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return data


def create_visualizations(data):
    """Create comprehensive visualizations"""
    
    # Convert to DataFrame
    df = pd.DataFrame(data['aggregated_results'])
    
    # Create figure with subplots (5 rows x 3 columns = 15 subplots)
    fig = plt.figure(figsize=(22, 28))
    
    # 1. Population Size Effect
    ax1 = plt.subplot(5, 3, 1)
    pop_data = df.groupby('population_size').agg({
        'mean_distance_km': 'mean',
        'mean_execution_time': 'mean'
    }).reset_index()
    
    ax1_twin = ax1.twinx()
    ax1.plot(pop_data['population_size'], pop_data['mean_distance_km'], 
             'o-', color='blue', linewidth=2, markersize=8, label='Jarak')
    ax1_twin.plot(pop_data['population_size'], pop_data['mean_execution_time'], 
                  's-', color='red', linewidth=2, markersize=8, label='Waktu')
    
    ax1.set_xlabel('Ukuran Populasi', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Rata-rata Jarak (km)', color='blue', fontsize=10, fontweight='bold')
    ax1_twin.set_ylabel('Rata-rata Waktu Eksekusi (s)', color='red', fontsize=10, fontweight='bold')
    ax1.set_title('Pengaruh Ukuran Populasi', fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1_twin.tick_params(axis='y', labelcolor='red')
    ax1.grid(True, alpha=0.3)
    
    # 2. Generations Effect
    ax2 = plt.subplot(5, 3, 2)
    gen_data = df.groupby('generations').agg({
        'mean_distance_km': 'mean',
        'mean_convergence_gen': 'mean'
    }).reset_index()
    
    ax2_twin = ax2.twinx()
    ax2.plot(gen_data['generations'], gen_data['mean_distance_km'], 
             'o-', color='blue', linewidth=2, markersize=8, label='Jarak')
    ax2_twin.plot(gen_data['generations'], gen_data['mean_convergence_gen'], 
                  's-', color='green', linewidth=2, markersize=8, label='Konvergensi')
    
    ax2.set_xlabel('Jumlah Generasi', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Rata-rata Jarak (km)', color='blue', fontsize=10, fontweight='bold')
    ax2_twin.set_ylabel('Rata-rata Generasi Konvergensi', color='green', fontsize=10, fontweight='bold')
    ax2.set_title('Pengaruh Jumlah Generasi', fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2_twin.tick_params(axis='y', labelcolor='green')
    ax2.grid(True, alpha=0.3)
    
    # 3. Crossover Rate Effect
    ax3 = plt.subplot(5, 3, 3)
    cross_data = df.groupby('crossover_rate').agg({
        'mean_distance_km': 'mean',
        'mean_improvement_pct': 'mean'
    }).reset_index()
    
    ax3_twin = ax3.twinx()
    ax3.plot(cross_data['crossover_rate'], cross_data['mean_distance_km'], 
             'o-', color='blue', linewidth=2, markersize=8, label='Jarak')
    ax3_twin.plot(cross_data['crossover_rate'], cross_data['mean_improvement_pct'], 
                  's-', color='purple', linewidth=2, markersize=8, label='Peningkatan')
    
    ax3.set_xlabel('Tingkat Crossover', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Rata-rata Jarak (km)', color='blue', fontsize=10, fontweight='bold')
    ax3_twin.set_ylabel('Rata-rata Peningkatan (%)', color='purple', fontsize=10, fontweight='bold')
    ax3.set_title('Pengaruh Tingkat Crossover', fontsize=12, fontweight='bold')
    ax3.tick_params(axis='y', labelcolor='blue')
    ax3_twin.tick_params(axis='y', labelcolor='purple')
    ax3.grid(True, alpha=0.3)
    
    # 4. Mutation Rate Effect
    ax4 = plt.subplot(5, 3, 4)
    mut_data = df.groupby('mutation_rate').agg({
        'mean_distance_km': 'mean',
        'mean_improvement_pct': 'mean'
    }).reset_index()
    
    ax4_twin = ax4.twinx()
    ax4.plot(mut_data['mutation_rate'], mut_data['mean_distance_km'], 
             'o-', color='blue', linewidth=2, markersize=8, label='Jarak')
    ax4_twin.plot(mut_data['mutation_rate'], mut_data['mean_improvement_pct'], 
                  's-', color='orange', linewidth=2, markersize=8, label='Peningkatan')
    
    ax4.set_xlabel('Tingkat Mutasi', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Rata-rata Jarak (km)', color='blue', fontsize=10, fontweight='bold')
    ax4_twin.set_ylabel('Rata-rata Peningkatan (%)', color='orange', fontsize=10, fontweight='bold')
    ax4.set_title('Pengaruh Tingkat Mutasi', fontsize=12, fontweight='bold')
    ax4.tick_params(axis='y', labelcolor='blue')
    ax4_twin.tick_params(axis='y', labelcolor='orange')
    ax4.grid(True, alpha=0.3)
    
    # 5. Elitism Count Effect
    ax5 = plt.subplot(5, 3, 5)
    elitism_data = df.groupby('elitism_count').agg({
        'mean_distance_km': 'mean',
        'mean_improvement_pct': 'mean'
    }).reset_index()
    
    ax5_twin = ax5.twinx()
    ax5.plot(elitism_data['elitism_count'], elitism_data['mean_distance_km'], 
             'o-', color='blue', linewidth=2, markersize=8, label='Jarak')
    ax5_twin.plot(elitism_data['elitism_count'], elitism_data['mean_improvement_pct'], 
                  's-', color='teal', linewidth=2, markersize=8, label='Peningkatan')
    
    ax5.set_xlabel('Jumlah Elitisme', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Rata-rata Jarak (km)', color='blue', fontsize=10, fontweight='bold')
    ax5_twin.set_ylabel('Rata-rata Peningkatan (%)', color='teal', fontsize=10, fontweight='bold')
    ax5.set_title('Pengaruh Jumlah Elitisme', fontsize=12, fontweight='bold')
    ax5.tick_params(axis='y', labelcolor='blue')
    ax5_twin.tick_params(axis='y', labelcolor='teal')
    ax5.grid(True, alpha=0.3)
    
    # 6. Tournament Size Effect
    ax6 = plt.subplot(5, 3, 6)
    tournament_data = df.groupby('tournament_size').agg({
        'mean_distance_km': 'mean',
        'mean_execution_time': 'mean'
    }).reset_index()
    
    ax6_twin = ax6.twinx()
    ax6.plot(tournament_data['tournament_size'], tournament_data['mean_distance_km'], 
             'o-', color='blue', linewidth=2, markersize=8, label='Jarak')
    ax6_twin.plot(tournament_data['tournament_size'], tournament_data['mean_execution_time'], 
                  's-', color='crimson', linewidth=2, markersize=8, label='Waktu')
    
    ax6.set_xlabel('Ukuran Turnamen', fontsize=11, fontweight='bold')
    ax6.set_ylabel('Rata-rata Jarak (km)', color='blue', fontsize=10, fontweight='bold')
    ax6_twin.set_ylabel('Rata-rata Waktu Eksekusi (s)', color='crimson', fontsize=10, fontweight='bold')
    ax6.set_title('Pengaruh Ukuran Turnamen', fontsize=12, fontweight='bold')
    ax6.tick_params(axis='y', labelcolor='blue')
    ax6_twin.tick_params(axis='y', labelcolor='crimson')
    ax6.grid(True, alpha=0.3)
    
    # 7. Two-Opt Iterations Effect
    ax7 = plt.subplot(5, 3, 7)
    two_opt_data = df.groupby('two_opt_iterations').agg({
        'mean_distance_km': 'mean',
        'mean_execution_time': 'mean',
        'mean_improvement_pct': 'mean'
    }).reset_index()
    
    x = np.arange(len(two_opt_data))
    width = 0.25
    
    ax7.bar(x - width, two_opt_data['mean_distance_km'], width, label='Jarak (km)', color='blue', alpha=0.8)
    ax7.bar(x, two_opt_data['mean_execution_time'], width, label='Waktu (s)', color='red', alpha=0.8)
    ax7.bar(x + width, two_opt_data['mean_improvement_pct'], width, label='Peningkatan (%)', color='green', alpha=0.8)
    
    ax7.set_xlabel('Iterasi 2-Opt', fontsize=11, fontweight='bold')
    ax7.set_ylabel('Nilai', fontsize=10, fontweight='bold')
    ax7.set_title('Pengaruh Iterasi 2-Opt', fontsize=12, fontweight='bold')
    ax7.set_xticks(x)
    ax7.set_xticklabels(two_opt_data['two_opt_iterations'])
    ax7.legend(fontsize=9)
    ax7.grid(True, alpha=0.3, axis='y')
    
    # 8. Distance vs Execution Time Scatter
    ax8 = plt.subplot(5, 3, 8)
    scatter = ax8.scatter(df['mean_execution_time'], df['mean_distance_km'], 
                          c=df['feasible_rate'], cmap='RdYlGn', s=100, alpha=0.6,
                          edgecolors='black', linewidth=0.5)
    ax8.set_xlabel('Rata-rata Waktu Eksekusi (s)', fontsize=11, fontweight='bold')
    ax8.set_ylabel('Rata-rata Jarak (km)', fontsize=10, fontweight='bold')
    ax8.set_title('Jarak vs Waktu Eksekusi', fontsize=12, fontweight='bold')
    ax8.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax8, label='Tingkat Kelayakan (%)')
    
    # 9. Heatmap: Population vs Generations
    ax9 = plt.subplot(5, 3, 9)
    pivot_pop_gen = df.groupby(['population_size', 'generations'])['mean_distance_km'].mean().unstack()
    sns.heatmap(pivot_pop_gen, annot=True, fmt='.2f', cmap='YlOrRd', ax=ax9, 
                cbar_kws={'label': 'Rata-rata Jarak (km)'})
    ax9.set_title('Populasi vs Generasi\n(Rata-rata Jarak)', fontsize=12, fontweight='bold')
    ax9.set_xlabel('Jumlah Generasi', fontsize=11, fontweight='bold')
    ax9.set_ylabel('Ukuran Populasi', fontsize=10, fontweight='bold')
    
    # 10. Heatmap: Crossover vs Mutation
    ax10 = plt.subplot(5, 3, 10)
    pivot_cross_mut = df.groupby(['crossover_rate', 'mutation_rate'])['mean_distance_km'].mean().unstack()
    sns.heatmap(pivot_cross_mut, annot=True, fmt='.2f', cmap='viridis', ax=ax10,
                cbar_kws={'label': 'Rata-rata Jarak (km)'})
    ax10.set_title('Crossover vs Mutasi\n(Rata-rata Jarak)', fontsize=12, fontweight='bold')
    ax10.set_xlabel('Tingkat Mutasi', fontsize=11, fontweight='bold')
    ax10.set_ylabel('Tingkat Crossover', fontsize=10, fontweight='bold')
    
    # 11. Heatmap: Elitism vs Tournament Size
    ax11 = plt.subplot(5, 3, 11)
    pivot_elite_tour = df.groupby(['elitism_count', 'tournament_size'])['mean_distance_km'].mean().unstack()
    sns.heatmap(pivot_elite_tour, annot=True, fmt='.2f', cmap='coolwarm', ax=ax11,
                cbar_kws={'label': 'Rata-rata Jarak (km)'})
    ax11.set_title('Elitisme vs Ukuran Turnamen\n(Rata-rata Jarak)', fontsize=12, fontweight='bold')
    ax11.set_xlabel('Ukuran Turnamen', fontsize=11, fontweight='bold')
    ax11.set_ylabel('Jumlah Elitisme', fontsize=10, fontweight='bold')
    
    # 12. Top 10 Configurations
    ax12 = plt.subplot(5, 3, 12)
    top_10 = df.nsmallest(10, 'mean_distance_km')
    config_labels = [f"P{int(row['population_size'])}_G{int(row['generations'])}_\n"
                     f"C{row['crossover_rate']}_M{row['mutation_rate']}_\n"
                     f"E{int(row['elitism_count'])}_T{int(row['tournament_size'])}_2O{int(row['two_opt_iterations'])}" 
                     for _, row in top_10.iterrows()]
    
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(top_10)))
    bars = ax12.barh(range(len(top_10)), top_10['mean_distance_km'], color=colors, alpha=0.8)
    ax12.set_yticks(range(len(top_10)))
    ax12.set_yticklabels(config_labels, fontsize=6)
    ax12.set_xlabel('Rata-rata Jarak (km)', fontsize=11, fontweight='bold')
    ax12.set_title('10 Konfigurasi Terbaik', fontsize=12, fontweight='bold')
    ax12.grid(True, alpha=0.3, axis='x')
    ax12.invert_yaxis()
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, top_10['mean_distance_km'])):
        ax12.text(val, i, f' {val:.2f}', va='center', fontsize=8, fontweight='bold')
    
    # 13-15. Convergence Curves for Top 3 Configurations
    top_3 = df.nsmallest(3, 'mean_distance_km')
    
    for idx, (_, config) in enumerate(top_3.iterrows(), 1):
        ax = plt.subplot(5, 3, 12 + idx)
        
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
            ax.plot(mean_distance, color='red', linewidth=2.5, label='Rata-rata', zorder=10)
            ax.fill_between(generations, 
                           mean_distance - std_distance, 
                           mean_distance + std_distance,
                           color='red', alpha=0.2, label='±1 Std Dev')
            
            # Add convergence line
            if 'mean_convergence_gen' in config:
                conv_gen = int(config['mean_convergence_gen'])
                if conv_gen < len(mean_distance):
                    ax.axvline(x=conv_gen, color='green', linestyle='--', linewidth=2, 
                             label=f'Konvergensi (Gen {conv_gen})', alpha=0.7)
        
        ax.set_xlabel('Generasi', fontsize=10, fontweight='bold')
        ax.set_ylabel('Jarak Terbaik (km)', fontsize=10, fontweight='bold')
        ax.set_title(f"Konvergensi Peringkat #{idx}\n"
                    f"Pop={int(config['population_size'])}, Gen={int(config['generations'])}, "
                    f"CR={config['crossover_rate']}, MR={config['mutation_rate']}\n"
                    f"Elite={int(config['elitism_count'])}, Tour={int(config['tournament_size'])}, "
                    f"2Opt={int(config['two_opt_iterations'])} | Jarak={config['mean_distance_km']:.2f}km",
                    fontsize=8, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle=':')
        ax.legend(fontsize=7, loc='upper right')
        
        # Add improvement annotation
        if all_distances and len(mean_distance) > 1:
            initial_dist = mean_distance[0]
            final_dist = mean_distance[-1]
            improvement = ((initial_dist - final_dist) / initial_dist) * 100
            ax.text(0.02, 0.98, f'Peningkatan: {improvement:.1f}%', 
                   transform=ax.transAxes, fontsize=8, 
                   verticalalignment='top', bbox=dict(boxstyle='round', 
                   facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Save figure
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hyperparameter_tuning_visualization_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\n✓ Visualisasi disimpan ke: {filename}")
    
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
        ax.plot(mean_distance, color='red', linewidth=2, label='Rata-rata')
        
        ax.set_xlabel('Generasi', fontsize=10, fontweight='bold')
        ax.set_ylabel('Jarak Terbaik (km)', fontsize=10, fontweight='bold')
        ax.set_title(f"Peringkat #{idx+1}\nP={int(config['population_size'])}, G={int(config['generations'])}, "
                    f"C={config['crossover_rate']}, M={config['mutation_rate']}\n"
                    f"E={int(config['elitism_count'])}, T={int(config['tournament_size'])}, "
                    f"2Opt={int(config['two_opt_iterations'])}\nJarak: {config['mean_distance_km']:.2f}km",
                    fontsize=8, fontweight='bold')
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
    print(f"✓ Kurva konvergensi disimpan ke: {filename}")
    
    plt.show()


def generate_report(data):
    """Generate text report"""
    df = pd.DataFrame(data['aggregated_results'])
    
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hyperparameter_tuning_report_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("LAPORAN HYPERPARAMETER TUNING\n")
        f.write("Hybrid Genetic Algorithm - Rekomendasi Rute Wisata\n")
        f.write("="*80 + "\n\n")
        
        # Summary statistics
        f.write("RINGKASAN STATISTIK\n")
        f.write("-"*80 + "\n")
        f.write(f"Total konfigurasi diuji: {len(df)}\n")
        f.write(f"Jumlah percobaan per konfigurasi: {data['num_runs_per_config']}\n")
        f.write(f"Total eksperimen: {len(data['detailed_results'])}\n\n")
        
        f.write(f"Rentang Jarak: {df['mean_distance_km'].min():.2f} - {df['mean_distance_km'].max():.2f} km\n")
        f.write(f"Rentang Waktu Eksekusi: {df['mean_execution_time'].min():.2f} - {df['mean_execution_time'].max():.2f} s\n")
        f.write(f"Rentang Tingkat Kelayakan: {df['feasible_rate'].min():.1f}% - {df['feasible_rate'].max():.1f}%\n\n")
        
        # Best configuration
        best = df.loc[df['mean_distance_km'].idxmin()]
        f.write("\n" + "="*80 + "\n")
        f.write("KONFIGURASI TERBAIK (Jarak Minimum)\n")
        f.write("="*80 + "\n")
        f.write(f"Ukuran Populasi: {int(best['population_size'])}\n")
        f.write(f"Jumlah Generasi: {int(best['generations'])}\n")
        f.write(f"Tingkat Crossover: {best['crossover_rate']}\n")
        f.write(f"Tingkat Mutasi: {best['mutation_rate']}\n")
        f.write(f"Jumlah Elitisme: {int(best['elitism_count'])}\n")
        f.write(f"Ukuran Turnamen: {int(best['tournament_size'])}\n")
        f.write(f"Iterasi 2-Opt: {int(best['two_opt_iterations'])}\n\n")
        f.write(f"Rata-rata Jarak: {best['mean_distance_km']:.2f} ± {best['std_distance_km']:.2f} km\n")
        f.write(f"Rata-rata Waktu Eksekusi: {best['mean_execution_time']:.2f} ± {best['std_execution_time']:.2f} s\n")
        f.write(f"Tingkat Kelayakan: {best['feasible_rate']:.1f}%\n")
        f.write(f"Rata-rata Peningkatan: {best['mean_improvement_pct']:.1f}%\n")
        f.write(f"Generasi Konvergensi: {best['mean_convergence_gen']:.0f}\n\n")
        
        # Parameter analysis
        f.write("\n" + "="*80 + "\n")
        f.write("ANALISIS PENGARUH PARAMETER\n")
        f.write("="*80 + "\n\n")
        
        # Population
        f.write("UKURAN POPULASI:\n")
        for pop in sorted(df['population_size'].unique()):
            subset = df[df['population_size'] == pop]
            f.write(f"  {int(pop):>4}: Jarak={subset['mean_distance_km'].mean():.2f}km, "
                   f"Waktu={subset['mean_execution_time'].mean():.2f}s\n")
        
        # Generations
        f.write("\nJUMLAH GENERASI:\n")
        for gen in sorted(df['generations'].unique()):
            subset = df[df['generations'] == gen]
            f.write(f"  {int(gen):>4}: Jarak={subset['mean_distance_km'].mean():.2f}km, "
                   f"Waktu={subset['mean_execution_time'].mean():.2f}s, "
                   f"Konvergensi={subset['mean_convergence_gen'].mean():.0f}\n")
        
        # Crossover
        f.write("\nTINGKAT CROSSOVER:\n")
        for cross in sorted(df['crossover_rate'].unique()):
            subset = df[df['crossover_rate'] == cross]
            f.write(f"  {cross:.2f}: Jarak={subset['mean_distance_km'].mean():.2f}km, "
                   f"Peningkatan={subset['mean_improvement_pct'].mean():.1f}%\n")
        
        # Mutation
        f.write("\nTINGKAT MUTASI:\n")
        for mut in sorted(df['mutation_rate'].unique()):
            subset = df[df['mutation_rate'] == mut]
            f.write(f"  {mut:.2f}: Jarak={subset['mean_distance_km'].mean():.2f}km, "
                   f"Peningkatan={subset['mean_improvement_pct'].mean():.1f}%\n")
        
        # Elitism Count
        f.write("\nJUMLAH ELITISME:\n")
        for elite in sorted(df['elitism_count'].unique()):
            subset = df[df['elitism_count'] == elite]
            f.write(f"  {int(elite):>3}: Jarak={subset['mean_distance_km'].mean():.2f}km, "
                   f"Peningkatan={subset['mean_improvement_pct'].mean():.1f}%\n")
        
        # Tournament Size
        f.write("\nUKURAN TURNAMEN:\n")
        for tour in sorted(df['tournament_size'].unique()):
            subset = df[df['tournament_size'] == tour]
            f.write(f"  {int(tour):>3}: Jarak={subset['mean_distance_km'].mean():.2f}km, "
                   f"Waktu={subset['mean_execution_time'].mean():.2f}s\n")
        
        # 2-Opt Iterations
        f.write("\nITERASI 2-OPT:\n")
        for opt_iter in sorted(df['two_opt_iterations'].unique()):
            subset = df[df['two_opt_iterations'] == opt_iter]
            f.write(f"  {int(opt_iter):>4}: Jarak={subset['mean_distance_km'].mean():.2f}km, "
                   f"Waktu={subset['mean_execution_time'].mean():.2f}s, "
                   f"Peningkatan={subset['mean_improvement_pct'].mean():.1f}%\n")
    
    print(f"✓ Laporan disimpan ke: {filename}")


def main():
    print("\n" + "="*80)
    print("HYPERPARAMETER TUNING - VISUALISASI & ANALISIS")
    print("="*80)
    print("\nParameter Grid:")
    for param, values in PARAMETER_GRID.items():
        print(f"  {param}: {values}")
    
    # Load results
    data = load_latest_results()
    if data is None:
        return
    
    print("\n1. Membuat visualisasi komprehensif (15 plot dengan kurva konvergensi)...")
    create_visualizations(data)
    
    print("\n2. Membuat kurva konvergensi detail untuk 5 konfigurasi terbaik...")
    plot_convergence_curves(data)
    
    print("\n3. Membuat laporan teks...")
    generate_report(data)
    
    print("\n" + "="*80)
    print("✅ Semua visualisasi dan laporan berhasil dibuat!")
    print("=" + "="*80)
    print("File yang dihasilkan:")
    print("  📊 hyperparameter_tuning_visualization_[timestamp].png (15 plot)")
    print("  📈 convergence_curves_top5_[timestamp].png (Top 5 detail)")
    print("  📄 hyperparameter_tuning_report_[timestamp].txt")
    print("="*80)


if __name__ == "__main__":
    main()
