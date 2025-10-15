"""
Modul untuk plotting grafik konvergensi algoritma HGA
"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend non-GUI untuk server
from typing import List, Dict
import os

class ConvergencePlotter:
    """
    Class untuk membuat visualisasi grafik konvergensi HGA
    """
    
    def __init__(self, output_dir: str = "visualization/outputs"):
        """
        Inisialisasi convergence plotter
        
        Args:
            output_dir: Directory untuk menyimpan output
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_fitness_evolution(self, 
                               best_fitness_history: List[float],
                               average_fitness_history: List[float],
                               filename: str = "fitness_evolution.png"):
        """
        Plot evolusi fitness (best dan average) sepanjang generasi
        
        Args:
            best_fitness_history: List fitness terbaik per generasi
            average_fitness_history: List average fitness per generasi
            filename: Nama file output
        """
        generations = range(len(best_fitness_history))
        
        plt.figure(figsize=(12, 6))
        
        # Plot best fitness
        plt.plot(generations, best_fitness_history, 
                label='Best Fitness', 
                color='blue', 
                linewidth=2,
                marker='o',
                markersize=3,
                markevery=max(1, len(generations)//20))
        
        # Plot average fitness
        plt.plot(generations, average_fitness_history, 
                label='Average Fitness', 
                color='orange', 
                linewidth=2,
                linestyle='--',
                marker='s',
                markersize=3,
                markevery=max(1, len(generations)//20))
        
        plt.xlabel('Generasi', fontsize=12, fontweight='bold')
        plt.ylabel('Fitness (1/Distance)', fontsize=12, fontweight='bold')
        plt.title('Evolusi Fitness HGA - Konvergensi Algorithm', 
                 fontsize=14, 
                 fontweight='bold',
                 pad=20)
        plt.legend(fontsize=11, loc='best')
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        # Save
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Grafik fitness evolution disimpan ke: {filepath}")
        return filepath
    
    def plot_distance_evolution(self,
                               best_fitness_history: List[float],
                               average_fitness_history: List[float],
                               filename: str = "distance_evolution.png"):
        """
        Plot evolusi distance (inverse dari fitness)
        
        Args:
            best_fitness_history: List fitness terbaik per generasi
            average_fitness_history: List average fitness per generasi
            filename: Nama file output
        """
        generations = range(len(best_fitness_history))
        
        # Convert fitness to distance (1/fitness)
        best_distance = [1/f if f > 0 else float('inf') for f in best_fitness_history]
        avg_distance = [1/f if f > 0 else float('inf') for f in average_fitness_history]
        
        plt.figure(figsize=(12, 6))
        
        # Plot best distance
        plt.plot(generations, best_distance, 
                label='Best Distance', 
                color='green', 
                linewidth=2,
                marker='o',
                markersize=3,
                markevery=max(1, len(generations)//20))
        
        # Plot average distance
        plt.plot(generations, avg_distance, 
                label='Average Distance', 
                color='red', 
                linewidth=2,
                linestyle='--',
                marker='s',
                markersize=3,
                markevery=max(1, len(generations)//20))
        
        plt.xlabel('Generasi', fontsize=12, fontweight='bold')
        plt.ylabel('Jarak (km)', fontsize=12, fontweight='bold')
        plt.title('Evolusi Jarak Rute - Optimasi HGA', 
                 fontsize=14, 
                 fontweight='bold',
                 pad=20)
        plt.legend(fontsize=11, loc='best')
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        # Save
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Grafik distance evolution disimpan ke: {filepath}")
        return filepath
    
    def plot_convergence_analysis(self,
                                  best_fitness_history: List[float],
                                  filename: str = "convergence_analysis.png"):
        """
        Plot analisis konvergensi dengan improvement rate
        
        Args:
            best_fitness_history: List fitness terbaik per generasi
            filename: Nama file output
        """
        generations = range(len(best_fitness_history))
        
        # Hitung improvement rate per generasi
        improvement_rate = [0]
        for i in range(1, len(best_fitness_history)):
            if best_fitness_history[i-1] > 0:
                rate = ((best_fitness_history[i] - best_fitness_history[i-1]) / 
                       best_fitness_history[i-1] * 100)
                improvement_rate.append(rate)
            else:
                improvement_rate.append(0)
        
        # Create subplot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Subplot 1: Best fitness
        ax1.plot(generations, best_fitness_history, 
                color='blue', 
                linewidth=2,
                marker='o',
                markersize=3,
                markevery=max(1, len(generations)//20))
        ax1.set_xlabel('Generasi', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Best Fitness', fontsize=11, fontweight='bold')
        ax1.set_title('Konvergensi Best Fitness', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # Subplot 2: Improvement rate
        ax2.plot(generations, improvement_rate, 
                color='red', 
                linewidth=2,
                marker='s',
                markersize=2,
                markevery=max(1, len(generations)//20))
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
        ax2.set_xlabel('Generasi', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Improvement Rate (%)', fontsize=11, fontweight='bold')
        ax2.set_title('Rate of Improvement per Generasi', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        # Save
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Grafik convergence analysis disimpan ke: {filepath}")
        return filepath
    
    def plot_statistics_summary(self,
                               stats: Dict,
                               filename: str = "statistics_summary.png"):
        """
        Plot ringkasan statistik HGA
        
        Args:
            stats: Dictionary berisi statistik dari HGA
            filename: Nama file output
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Subplot 1: Fitness evolution
        generations = range(len(stats['best_fitness_history']))
        ax1.plot(generations, stats['best_fitness_history'], 
                label='Best', color='blue', linewidth=2)
        ax1.plot(generations, stats['average_fitness_history'], 
                label='Average', color='orange', linewidth=2, linestyle='--')
        ax1.set_xlabel('Generasi', fontweight='bold')
        ax1.set_ylabel('Fitness', fontweight='bold')
        ax1.set_title('Fitness Evolution', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: Distance evolution
        best_distance = [1/f if f > 0 else 0 for f in stats['best_fitness_history']]
        avg_distance = [1/f if f > 0 else 0 for f in stats['average_fitness_history']]
        ax2.plot(generations, best_distance, 
                label='Best', color='green', linewidth=2)
        ax2.plot(generations, avg_distance, 
                label='Average', color='red', linewidth=2, linestyle='--')
        ax2.set_xlabel('Generasi', fontweight='bold')
        ax2.set_ylabel('Jarak (km)', fontweight='bold')
        ax2.set_title('Distance Evolution', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Subplot 3: Summary statistics (text)
        ax3.axis('off')
        summary_text = f"""
        RINGKASAN STATISTIK HGA
        ========================
        
        Total Generasi: {stats['total_generations']}
        
        Best Distance: {stats['best_distance']:.2f} km
        
        Initial Fitness: {stats['best_fitness_history'][0]:.6f}
        Final Fitness: {stats['best_fitness_history'][-1]:.6f}
        
        Improvement: {((stats['best_fitness_history'][-1] - stats['best_fitness_history'][0]) / stats['best_fitness_history'][0] * 100):.2f}%
        
        Convergence: Generation {stats['total_generations']}
        """
        ax3.text(0.1, 0.5, summary_text, 
                fontsize=11, 
                verticalalignment='center',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Subplot 4: Distribution
        if len(best_distance) > 10:
            # Histogram of improvement
            improvements = []
            for i in range(1, len(stats['best_fitness_history'])):
                if stats['best_fitness_history'][i] != stats['best_fitness_history'][i-1]:
                    improvements.append(i)
            
            ax4.hist(improvements, bins=20, color='purple', alpha=0.7, edgecolor='black')
            ax4.set_xlabel('Generasi', fontweight='bold')
            ax4.set_ylabel('Frequency', fontweight='bold')
            ax4.set_title('Distribusi Improvement per Generasi', fontweight='bold')
            ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # Save
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Grafik statistics summary disimpan ke: {filepath}")
        return filepath
    
    def create_all_plots(self, stats: Dict) -> List[str]:
        """
        Membuat semua plot sekaligus
        
        Args:
            stats: Dictionary statistik dari HGA
            
        Returns:
            List filepath dari semua plot yang dibuat
        """
        print("\n" + "="*70)
        print("MEMBUAT VISUALISASI GRAFIK KONVERGENSI")
        print("="*70)
        
        filepaths = []
        
        # Plot 1: Fitness evolution
        fp1 = self.plot_fitness_evolution(
            stats['best_fitness_history'],
            stats['average_fitness_history']
        )
        filepaths.append(fp1)
        
        # Plot 2: Distance evolution
        fp2 = self.plot_distance_evolution(
            stats['best_fitness_history'],
            stats['average_fitness_history']
        )
        filepaths.append(fp2)
        
        # Plot 3: Convergence analysis
        fp3 = self.plot_convergence_analysis(
            stats['best_fitness_history']
        )
        filepaths.append(fp3)
        
        # Plot 4: Statistics summary
        fp4 = self.plot_statistics_summary(stats)
        filepaths.append(fp4)
        
        print("="*70)
        print(f"Total {len(filepaths)} grafik berhasil dibuat!")
        print("="*70 + "\n")
        
        return filepaths
