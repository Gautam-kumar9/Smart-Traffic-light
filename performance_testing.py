"""
Performance Testing and Results Visualization
Comprehensive testing and visualization of traffic control system performance
"""

import matplotlib.pyplot as plt
import numpy as np
from main_control_system import SmartTrafficLightSystem
from traffic_simulator import TrafficSimulator
from fuzzy_controller import FuzzyTrafficController
import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
FIGURES_DIR = PROJECT_DIR / 'figures'


class PerformanceTester:
    """
    Test and evaluate traffic control system performance
    """
    
    def __init__(self):
        self.system = SmartTrafficLightSystem()
        self.test_results = []
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    def run_comprehensive_tests(self):
        """Run tests across multiple scenarios"""
        print("\n" + "="*70)
        print("COMPREHENSIVE PERFORMANCE TESTING")
        print("="*70 + "\n")
        
        test_scenarios = [
            {
                'name': 'Weekday Morning Peak',
                'duration': 120,
                'start_hour': 8,
                'is_weekday': True
            },
            {
                'name': 'Weekday Evening Peak',
                'duration': 120,
                'start_hour': 17,
                'is_weekday': True
            },
            {
                'name': 'Weekday Normal Hours',
                'duration': 120,
                'start_hour': 11,
                'is_weekday': True
            },
            {
                'name': 'Weekend Midday',
                'duration': 120,
                'start_hour': 12,
                'is_weekday': False
            },
            {
                'name': 'Night Time',
                'duration': 120,
                'start_hour': 2,
                'is_weekday': True
            }
        ]
        
        results = []
        
        for scenario in test_scenarios:
            print(f"\nTesting: {scenario['name']}")
            print("-" * 70)
            
            comparison = self.system.compare_systems(
                duration_minutes=scenario['duration'],
                start_hour=scenario['start_hour'],
                is_weekday=scenario['is_weekday']
            )
            
            result = {
                'scenario': scenario['name'],
                'fixed_avg_delay': comparison['fixed_time']['average_delay'],
                'smart_avg_delay': comparison['smart_control']['average_delay'],
                'improvement_percent': comparison['improvement']['delay_reduction_percent'],
                'total_vehicles': comparison['smart_control']['total_vehicles']
            }
            
            results.append(result)
            
            print(f"  Fixed-Time Avg Delay: {result['fixed_avg_delay']:.2f}s")
            print(f"  Smart Control Avg Delay: {result['smart_avg_delay']:.2f}s")
            print(f"  Improvement: {result['improvement_percent']:.2f}%")
        
        self.test_results = results
        return results
    
    def save_results_to_file(self, filename='test_results.json'):
        """Save test results to JSON file"""
        output_file = PROJECT_DIR / filename
        with output_file.open('w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nResults saved to '{output_file}'")


class ResultsVisualizer:
    """
    Visualize traffic control system performance
    """
    
    def __init__(self):
        plt.style.use('seaborn-v0_8-darkgrid')
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    def plot_comparison_chart(self, test_results):
        """Create comparison bar chart"""
        scenarios = [r['scenario'] for r in test_results]
        fixed_delays = [r['fixed_avg_delay'] for r in test_results]
        smart_delays = [r['smart_avg_delay'] for r in test_results]
        
        x = np.arange(len(scenarios))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(14, 6))
        bars1 = ax.bar(x - width/2, fixed_delays, width, label='Fixed-Time Control', 
                       color='#e74c3c', alpha=0.8)
        bars2 = ax.bar(x + width/2, smart_delays, width, label='Smart Fuzzy Control', 
                       color='#2ecc71', alpha=0.8)
        
        ax.set_xlabel('Traffic Scenarios', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Delay (seconds)', fontsize=12, fontweight='bold')
        ax.set_title('Traffic Control System Performance Comparison', 
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios, rotation=15, ha='right')
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        output_file = FIGURES_DIR / 'performance_comparison.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Performance comparison chart saved to '{output_file}'")
        plt.close()
    
    def plot_improvement_chart(self, test_results):
        """Create improvement percentage chart"""
        scenarios = [r['scenario'] for r in test_results]
        improvements = [r['improvement_percent'] for r in test_results]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = ['#3498db' if imp > 0 else '#e74c3c' for imp in improvements]
        bars = ax.bar(scenarios, improvements, color=colors, alpha=0.7, edgecolor='black')
        
        ax.set_xlabel('Traffic Scenarios', fontsize=12, fontweight='bold')
        ax.set_ylabel('Improvement (%)', fontsize=12, fontweight='bold')
        ax.set_title('Delay Reduction: Smart Control vs Fixed-Time Control', 
                    fontsize=14, fontweight='bold')
        ax.axhline(y=0, color='k', linestyle='-', linewidth=0.8)
        ax.set_xticks(range(len(scenarios)))
        ax.set_xticklabels(scenarios, rotation=15, ha='right')
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}%',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3 if height > 0 else -15),
                       textcoords="offset points",
                       ha='center', va='bottom' if height > 0 else 'top',
                       fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        output_file = FIGURES_DIR / 'improvement_chart.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Improvement chart saved to '{output_file}'")
        plt.close()
    
    def plot_traffic_density_response(self):
        """Visualize how green time adapts to traffic density"""
        controller = FuzzyTrafficController()
        
        densities = range(0, 101, 5)
        
        # Different scenarios
        scenarios = [
            (True, 2, 'Weekday Morning Peak'),
            (True, 3, 'Weekday Evening Peak'),
            (True, 1, 'Weekday Normal'),
            (False, 1, 'Weekend Normal'),
            (True, 0, 'Night Time')
        ]
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        for is_weekday, time_slot, label in scenarios:
            green_times = []
            for density in densities:
                green_time = controller.compute_green_time(density, is_weekday, time_slot)
                green_times.append(green_time)
            ax.plot(densities, green_times, marker='o', markersize=4, label=label, linewidth=2)
        
        ax.set_xlabel('Traffic Density (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Green Signal Time (seconds)', fontsize=12, fontweight='bold')
        ax.set_title('Adaptive Green Time Based on Traffic Density', 
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=10, loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 100)
        
        plt.tight_layout()
        output_file = FIGURES_DIR / 'adaptive_response.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Adaptive response chart saved to '{output_file}'")
        plt.close()
    
    def plot_traffic_patterns(self):
        """Visualize traffic patterns throughout the day"""
        simulator = TrafficSimulator(seed=42)
        
        # Simulate 24-hour period
        weekday_data = []
        weekend_data = []
        
        for hour in range(24):
            # Weekday
            density_wd = simulator.generate_traffic_density(hour, True)
            weekday_data.append(density_wd)
            
            # Weekend
            density_we = simulator.generate_traffic_density(hour, False)
            weekend_data.append(density_we)
        
        hours = list(range(24))
        
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(hours, weekday_data, marker='o', label='Weekday', linewidth=2.5, color='#e74c3c')
        ax.plot(hours, weekend_data, marker='s', label='Weekend', linewidth=2.5, color='#3498db')
        
        # Highlight peak hours
        ax.axvspan(7, 10, alpha=0.2, color='orange', label='Morning Peak')
        ax.axvspan(17, 20, alpha=0.2, color='red', label='Evening Peak')
        ax.axvspan(23, 24, alpha=0.2, color='navy')
        ax.axvspan(0, 5, alpha=0.2, color='navy', label='Night Hours')
        
        ax.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax.set_ylabel('Traffic Density (%)', fontsize=12, fontweight='bold')
        ax.set_title('24-Hour Traffic Pattern Analysis', fontsize=14, fontweight='bold')
        ax.set_xticks(range(0, 24, 2))
        ax.legend(fontsize=10, loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = FIGURES_DIR / 'traffic_patterns.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Traffic patterns chart saved to '{output_file}'")
        plt.close()
    
    def create_summary_report(self, test_results):
        """Create a comprehensive summary report"""
        print("\n" + "="*70)
        print("PERFORMANCE SUMMARY REPORT")
        print("="*70 + "\n")
        
        avg_improvement = np.mean([r['improvement_percent'] for r in test_results])
        total_vehicles = sum([r['total_vehicles'] for r in test_results])
        
        print(f"Total Scenarios Tested: {len(test_results)}")
        print(f"Total Vehicles Processed: {total_vehicles}")
        print(f"Average Improvement: {avg_improvement:.2f}%")
        print(f"\nBest Performance:")
        best = max(test_results, key=lambda x: x['improvement_percent'])
        print(f"  Scenario: {best['scenario']}")
        print(f"  Improvement: {best['improvement_percent']:.2f}%")
        
        print(f"\nWorst Performance:")
        worst = min(test_results, key=lambda x: x['improvement_percent'])
        print(f"  Scenario: {worst['scenario']}")
        print(f"  Improvement: {worst['improvement_percent']:.2f}%")
        
        print("\n" + "="*70)


def run_full_analysis():
    """Run complete analysis with all visualizations"""
    print("\n" + "#"*70)
    print("SMART TRAFFIC LIGHT CONTROL SYSTEM - FULL ANALYSIS")
    print("#"*70)
    
    # Run tests
    tester = PerformanceTester()
    results = tester.run_comprehensive_tests()
    tester.save_results_to_file()
    
    # Create visualizations
    visualizer = ResultsVisualizer()
    
    print("\n\nGenerating Visualizations...")
    print("-" * 70)
    
    visualizer.plot_comparison_chart(results)
    visualizer.plot_improvement_chart(results)
    visualizer.plot_traffic_density_response()
    visualizer.plot_traffic_patterns()
    
    # Generate membership functions visualization
    try:
        controller = FuzzyTrafficController()
        controller.visualize_membership_functions(FIGURES_DIR / 'membership_functions.png')
    except Exception as e:
        print(f"Membership functions visualization skipped: {e}")
    
    # Summary report
    visualizer.create_summary_report(results)
    
    print("\n" + "#"*70)
    print("ANALYSIS COMPLETE!")
    print("Generated files:")
    print("  - test_results.json")
    print("  - figures/performance_comparison.png")
    print("  - figures/improvement_chart.png")
    print("  - figures/adaptive_response.png")
    print("  - figures/traffic_patterns.png")
    print("  - figures/membership_functions.png")
    print("#"*70 + "\n")


if __name__ == "__main__":
    run_full_analysis()
