"""
Visual Traffic Light Simulation (No SUMO Required)
An animated visualization showing the smart traffic control system in action
"""

import time
import random
import os
from fuzzy_controller import FuzzyTrafficController
from traffic_simulator import TrafficSimulator


class VisualTrafficSimulation:
    """
    Visual simulation with animated traffic and signals
    """
    
    def __init__(self):
        self.controller = FuzzyTrafficController()
        self.simulator = TrafficSimulator(seed=None)
        self.max_consecutive_same_direction = 3
        
        # Colors
        self.RED = '\033[91m'
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.BLUE = '\033[94m'
        self.CYAN = '\033[96m'
        self.WHITE = '\033[97m'
        self.GRAY = '\033[90m'
        self.BOLD = '\033[1m'
        self.RESET = '\033[0m'

    def select_green_direction(self, ns_queue, ew_queue, ns_density, ew_density,
                               last_direction, consecutive_count):
        """Select active direction using queue pressure with fairness protection."""
        if last_direction == 'NS' and consecutive_count >= self.max_consecutive_same_direction and ew_queue > 0:
            return 'EW', 'Fairness override (prevent EW starvation)'

        if last_direction == 'EW' and consecutive_count >= self.max_consecutive_same_direction and ns_queue > 0:
            return 'NS', 'Fairness override (prevent NS starvation)'

        ns_pressure = ns_queue + (0.5 * ns_density)
        ew_pressure = ew_queue + (0.5 * ew_density)

        if ns_pressure > ew_pressure:
            return 'NS', 'Higher NS pressure'

        if ew_pressure > ns_pressure:
            return 'EW', 'Higher EW pressure'

        if ns_queue == 0 and ew_queue > 0:
            return 'EW', 'Only EW queue active'

        if ew_queue == 0 and ns_queue > 0:
            return 'NS', 'Only NS queue active'

        return ('EW', 'Tie-break alternation') if last_direction == 'NS' else ('NS', 'Tie-break alternation')
    
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def draw_intersection(self, ns_signal, ew_signal, ns_vehicles, ew_vehicles, cycle):
        """Draw the intersection with traffic"""
        self.clear()
        
        print(f"\n{self.BOLD}{'='*80}{self.RESET}")
        print(f"{self.BOLD}        SMART TRAFFIC LIGHT SYSTEM - VISUAL SIMULATION{self.RESET}")
        print(f"{self.BOLD}{'='*80}{self.RESET}\n")
        
        print(f"  Cycle: {cycle}  |  {self.CYAN}Fuzzy Logic Active{self.RESET}\n")
        
        # North vehicles
        ns_cars = min(ns_vehicles, 8)
        north_line = "      " + "🚗" * ns_cars + f" ({ns_vehicles} waiting)"
        print(f"{north_line:^80}")
        print(f"{'↓':^80}")
        
        # North signal
        ns_color = self.GREEN if ns_signal == 'GREEN' else (self.YELLOW if ns_signal == 'YELLOW' else self.RED)
        print(f"{ns_color}{'▓▓▓':^80}{self.RESET}")
        print()
        
        # West vehicles and signals
        ew_cars = min(ew_vehicles, 10)
        ew_color = self.GREEN if ew_signal == 'GREEN' else (self.YELLOW if ew_signal == 'YELLOW' else self.RED)
        
        west_cars = "🚗" * ew_cars
        print(f"  {west_cars:>30}  →  {ew_color}▓{self.RESET}  ╔═══════════╗  {ew_color}▓{self.RESET}  ←  ")
        print(f"  {' ':>33}  {ew_color}▓{self.RESET}  ║           ║  {ew_color}▓{self.RESET}")
        print(f"  {' ':>33}  {ew_color}▓{self.RESET}  ║ JUNCTION  ║  {ew_color}▓{self.RESET}")
        print(f"  {' ':>33}  {ew_color}▓{self.RESET}  ║           ║  {ew_color}▓{self.RESET}")
        print(f"  {' ':>33}  {ew_color}▓{self.RESET}  ╚═══════════╝  {ew_color}▓{self.RESET}")
        
        print()
        
        # South signal
        print(f"{ns_color}{'▓▓▓':^80}{self.RESET}")
        print(f"{'↑':^80}")
        south_line = "      " + "🚗" * min(ns_vehicles // 2, 6)
        print(f"{south_line:^80}")
        
        print(f"\n{self.GRAY}{'-'*80}{self.RESET}")
    
    def show_decision_info(self, direction, density, green_time, vehicles_passing,
                           reason, ns_density, ew_density):
        """Show fuzzy logic decision"""
        arrow = "↕" if direction == "NS" else "↔"
        
        if density < 30:
            level = f"{self.GREEN}LOW{self.RESET}"
        elif density < 70:
            level = f"{self.YELLOW}MEDIUM{self.RESET}"
        else:
            level = f"{self.RED}HIGH{self.RESET}"
        
        print(f"\n  {self.BOLD}Fuzzy Logic Decision for {direction} {arrow}:{self.RESET}")
        print(f"    Traffic Density: {level} ({density:.1f}%)")
        print(f"    Direction Split: NS={ns_density:.1f}% | EW={ew_density:.1f}%")
        print(f"    Selection Reason: {reason}")
        print(f"    {self.GREEN}→ Green Signal: {green_time} seconds{self.RESET}")
        print(f"    Vehicles Passing: {self.CYAN}{vehicles_passing}{self.RESET}")
    
    def show_statistics(self, total_vehicles, total_passed, avg_delay, efficiency):
        """Show running statistics"""
        print(f"\n{self.GRAY}{'-'*80}{self.RESET}")
        print(f"\n  {self.BOLD}SESSION STATISTICS:{self.RESET}")
        print(f"    Total Vehicles: {total_vehicles}")
        print(f"    Vehicles Passed: {self.GREEN}{total_passed}{self.RESET}")
        print(f"    Average Delay: {avg_delay:.2f}s")
        print(f"    System Efficiency: {self.CYAN}{efficiency:.1f}%{self.RESET}")
        print(f"\n{self.BOLD}{'='*80}{self.RESET}")
        print(f"  {self.GRAY}Press Ctrl+C to stop{self.RESET}")
        print(f"{self.BOLD}{'='*80}{self.RESET}\n")
    
    def run(self, duration_cycles=30, hour=8, is_weekday=True):
        """Run the visual simulation"""
        
        print(f"\n{self.BOLD}Starting Visual Simulation...{self.RESET}")
        print(f"  Scenario: {'Weekday' if is_weekday else 'Weekend'} at {hour}:00")
        print(f"  Duration: {duration_cycles} cycles\n")
        time.sleep(2)
        
        total_vehicles = 0
        total_passed = 0
        total_delay = 0
        ns_queue = 0
        ew_queue = 0
        last_direction = None
        consecutive_count = 0
        
        try:
            for cycle in range(1, duration_cycles + 1):
                # Get traffic density and split it into directional demand.
                time_slot = self.simulator.get_time_slot(hour)
                density = self.simulator.generate_traffic_density(hour, is_weekday)
                ns_density, ew_density = self.simulator.generate_directional_densities(density)

                ns_arrivals = int(self.simulator.get_vehicle_queue(ns_density))
                ew_arrivals = int(self.simulator.get_vehicle_queue(ew_density))
                ns_queue += ns_arrivals
                ew_queue += ew_arrivals
                total_vehicles += ns_arrivals + ew_arrivals

                direction, direction_reason = self.select_green_direction(
                    ns_queue, ew_queue, ns_density, ew_density, last_direction, consecutive_count
                )

                if direction == last_direction:
                    consecutive_count += 1
                else:
                    consecutive_count = 1
                last_direction = direction

                active_density = ns_density if direction == "NS" else ew_density
                
                # Fuzzy logic decision
                green_time = self.controller.compute_green_time(active_density, is_weekday, time_slot)
                vehicles_can_pass = int(green_time / 3)
                
                if direction == "NS":
                    vehicles_waiting_active = ns_queue
                    passing = min(ns_queue, vehicles_can_pass)
                    ns_queue -= passing
                else:
                    vehicles_waiting_active = ew_queue
                    passing = min(ew_queue, vehicles_can_pass)
                    ew_queue -= passing

                total_passed += passing
                total_delay += (ns_queue + ew_queue) * 60
                
                ns_vehicles = ns_queue
                ew_vehicles = ew_queue
                
                # Phase 1: Red signal
                ns_sig = 'RED' if direction == 'EW' else 'GREEN'
                ew_sig = 'GREEN' if direction == 'EW' else 'RED'
                
                self.draw_intersection(ns_sig, ew_sig, ns_vehicles, ew_vehicles, cycle)
                self.show_decision_info(
                    direction,
                    active_density,
                    green_time,
                    passing,
                    direction_reason,
                    ns_density,
                    ew_density
                )
                
                avg_delay = total_delay / max(1, total_passed)
                efficiency = (total_passed / max(1, total_vehicles)) * 100
                
                self.show_statistics(total_vehicles, total_passed, avg_delay, efficiency)
                
                # Simulate green time (sped up)
                time.sleep(min(2.5, green_time / 20))
                
                # Yellow phase
                if direction == 'NS':
                    ns_sig = 'YELLOW'
                else:
                    ew_sig = 'YELLOW'
                
                self.draw_intersection(ns_sig, ew_sig, 
                    max(0, ns_vehicles - passing) if direction == 'NS' else ns_vehicles,
                    max(0, ew_vehicles - passing) if direction == 'EW' else ew_vehicles,
                    cycle)
                self.show_decision_info(
                    direction,
                    active_density,
                    green_time,
                    passing,
                    direction_reason,
                    ns_density,
                    ew_density
                )
                self.show_statistics(total_vehicles, total_passed, avg_delay, efficiency)
                
                time.sleep(0.5)
            
            # Final summary
            self.clear()
            print(f"\n{self.BOLD}{'='*80}{self.RESET}")
            print(f"{self.BOLD}                    SIMULATION COMPLETE{self.RESET}")
            print(f"{self.BOLD}{'='*80}{self.RESET}\n")
            print(f"  Total Cycles: {duration_cycles}")
            print(f"  Total Vehicles: {total_vehicles}")
            print(f"  Vehicles Passed: {self.GREEN}{total_passed}{self.RESET}")
            print(f"  Average Delay: {avg_delay:.2f}s")
            print(f"  System Efficiency: {self.CYAN}{efficiency:.1f}%{self.RESET}")
            print(f"\n{self.BOLD}{'='*80}{self.RESET}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{self.YELLOW}Simulation stopped by user.{self.RESET}\n")


def main():
    print("="*80)
    print("  SMART TRAFFIC LIGHT CONTROL SYSTEM")
    print("  Visual Simulation (No SUMO Required)")
    print("="*80)
    
    print("\nSelect Scenario:")
    print("  1. Weekday Morning Peak (High Traffic)")
    print("  2. Weekday Evening Peak (Very High Traffic)")
    print("  3. Weekend Afternoon (Medium Traffic)")
    print("  4. Night Time (Low Traffic)")
    
    try:
        choice = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"
        
        scenarios = {
            '1': (40, 8, True, "Weekday Morning Peak"),
            '2': (40, 17, True, "Weekday Evening Peak"),
            '3': (30, 13, False, "Weekend Afternoon"),
            '4': (20, 2, True, "Night Time")
        }
        
        if choice in scenarios:
            cycles, hour, is_weekday, name = scenarios[choice]
        else:
            cycles, hour, is_weekday = 30, 8, True
        
        print(f"\nStarting in 2 seconds...\n")
        time.sleep(2)
        
        sim = VisualTrafficSimulation()
        sim.run(duration_cycles=cycles, hour=hour, is_weekday=is_weekday)
        
    except KeyboardInterrupt:
        print("\n\nSimulation cancelled.\n")
    except Exception as e:
        print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
