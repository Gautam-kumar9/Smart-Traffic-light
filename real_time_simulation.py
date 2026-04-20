"""
Real-Time Traffic Light Simulation
Interactive visualization of the Smart Traffic Light Control System in action
"""

import time
import os
import sys
from datetime import datetime
from fuzzy_controller import FuzzyTrafficController
from traffic_simulator import TrafficSimulator
from pedestrian_crossing import PedestrianCrossingManager, PedestrianGenerator


class RealTimeSimulation:
    """
    Real-time animated simulation of traffic light control
    """
    
    def __init__(self):
        self.controller = FuzzyTrafficController()
        self.simulator = TrafficSimulator(seed=None)  # Random for realistic variation
        self.pedestrian_manager = PedestrianCrossingManager(max_waiting_time=120)
        self.pedestrian_generator = PedestrianGenerator()
        self.max_consecutive_same_direction = 3
        
        # Simulation state
        self.current_signal = 'RED'
        self.signal_timer = 0
        self.total_vehicles_passed = 0
        self.total_delay = 0
        self.cycle_count = 0
        self.total_arrivals = 0
        self.ns_queue = 0
        self.ew_queue = 0
        self.last_direction = None
        self.consecutive_count = 0
        
        # Color codes for terminal output
        self.COLORS = {
            'RED': '\033[91m',
            'YELLOW': '\033[93m',
            'GREEN': '\033[92m',
            'BLUE': '\033[94m',
            'CYAN': '\033[96m',
            'WHITE': '\033[97m',
            'RESET': '\033[0m',
            'BOLD': '\033[1m'
        }
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def select_green_direction(self, ns_queue, ew_queue, ns_density, ew_density):
        """Select active direction using queue pressure with fairness protection."""
        if self.last_direction == 'NS' and self.consecutive_count >= self.max_consecutive_same_direction and ew_queue > 0:
            return 'EW', 'Fairness override (prevent EW starvation)'

        if self.last_direction == 'EW' and self.consecutive_count >= self.max_consecutive_same_direction and ns_queue > 0:
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

        return ('EW', 'Tie-break alternation') if self.last_direction == 'NS' else ('NS', 'Tie-break alternation')
    
    def print_traffic_light(self, signal):
        """Draw a traffic light"""
        red = '●' if signal == 'RED' else '○'
        yellow = '●' if signal == 'YELLOW' else '○'
        green = '●' if signal == 'GREEN' else '○'
        
        print(f"\n   ┌─────────┐")
        print(f"   │  {self.COLORS['RED']}{red}{self.COLORS['RESET']}  RED  │")
        print(f"   │  {self.COLORS['YELLOW']}{yellow}{self.COLORS['RESET']} YELLOW│")
        print(f"   │  {self.COLORS['GREEN']}{green}{self.COLORS['RESET']} GREEN │")
        print(f"   └─────────┘\n")
    
    def print_traffic_density_bar(self, density, label="Traffic Density"):
        """Draw traffic density as a bar"""
        bar_length = 40
        filled = int((density / 100) * bar_length)
        empty = bar_length - filled
        
        # Color based on density
        if density < 30:
            color = self.COLORS['GREEN']
            level = "LOW"
        elif density < 70:
            color = self.COLORS['YELLOW']
            level = "MEDIUM"
        else:
            color = self.COLORS['RED']
            level = "HIGH"
        
        bar = f"{color}{'█' * filled}{self.COLORS['RESET']}{'░' * empty}"
        print(f"  {label}: [{bar}] {density:.1f}% - {color}{level}{self.COLORS['RESET']}")
    
    def print_vehicles(self, count):
        """Draw waiting vehicles"""
        vehicle = '🚗'
        if count > 20:
            print(f"  Vehicles Waiting: {vehicle} × {count} (HEAVY CONGESTION)")
        elif count > 10:
            print(f"  Vehicles Waiting: {vehicle} × {count}")
        else:
            print(f"  Vehicles Waiting: {vehicle * min(count, 10)}")
    
    def print_pedestrian_status(self):
        """Display pedestrian crossing status"""
        status = self.pedestrian_manager.get_status()
        ped_icon = '🚶'
        
        if status['pedestrians_waiting'] > 0:
            wait_time = status['waiting_time']
            wait_bar_length = min(30, int((wait_time / 120) * 30))
            wait_bar = '▓' * wait_bar_length + '░' * (30 - wait_bar_length)
            
            print(f"\n  {ped_icon} Pedestrians Waiting: {status['pedestrians_waiting']}")
            print(f"  Wait Time: [{wait_bar}] {wait_time}s / 120s")
            
            if status['status'] == 'CROSSING ACTIVE':
                print(f"  {self.COLORS['GREEN']}✓ CROSSING ACTIVE{self.COLORS['RESET']}")
            elif wait_time > 90:
                print(f"  {self.COLORS['RED']}⚠ WARNING: Approaching max wait time!{self.COLORS['RESET']}")
        else:
            print(f"\n  {ped_icon} No pedestrians waiting")
    
    def run_simulation_cycle(self, hour, is_weekday, cycle_number):
        """Run one simulation cycle"""
        self.clear_screen()
        
        # Header
        print(f"\n{self.COLORS['BOLD']}{'='*70}{self.COLORS['RESET']}")
        print(f"{self.COLORS['BOLD']}  SMART TRAFFIC LIGHT CONTROL SYSTEM - REAL-TIME SIMULATION{self.COLORS['RESET']}")
        print(f"{self.COLORS['BOLD']}{'='*70}{self.COLORS['RESET']}\n")
        
        # Current time info
        time_slot_names = ['Night', 'Normal Hours', 'Morning Peak', 'Evening Peak']
        time_slot = self.simulator.get_time_slot(hour)
        day_type = "Weekday" if is_weekday else "Weekend"
        
        print(f"  Cycle: #{cycle_number}")
        print(f"  Time: {hour:02d}:00 - {time_slot_names[time_slot]}")
        print(f"  Day: {day_type}")
        print(f"  {'-'*66}")
        
        # Generate total density and split into directional demand.
        density = self.simulator.generate_traffic_density(hour, is_weekday)
        ns_density, ew_density = self.simulator.generate_directional_densities(density)

        ns_arrivals = self.simulator.get_vehicle_queue(ns_density)
        ew_arrivals = self.simulator.get_vehicle_queue(ew_density)
        self.ns_queue += ns_arrivals
        self.ew_queue += ew_arrivals
        self.total_arrivals += (ns_arrivals + ew_arrivals)

        # Display directional traffic state
        self.print_traffic_density_bar(ns_density, label="NS Density")
        self.print_traffic_density_bar(ew_density, label="EW Density")
        print(f"  NS Queue: {self.ns_queue} vehicles")
        print(f"  EW Queue: {self.ew_queue} vehicles")
        
        # Check for pedestrian requests (random)
        ped_requests = self.pedestrian_generator.generate_pedestrian_requests(
            hour, is_weekday, duration_minutes=1
        )
        for req in ped_requests:
            self.pedestrian_manager.add_pedestrian_request(req['num_pedestrians'])
        
        # Update pedestrian waiting
        self.pedestrian_manager.update_waiting_time(60)
        
        # Display pedestrian status
        self.print_pedestrian_status()
        
        # Check if pedestrian crossing needed
        should_cross, crossing_reason = self.pedestrian_manager.should_activate_crossing(max(ns_density, ew_density))
        
        print(f"\n  {'-'*66}")
        print(f"  {self.COLORS['CYAN']}FUZZY LOGIC DECISION:{self.COLORS['RESET']}\n")
        
        if should_cross:
            # Pedestrian crossing phase
            self.current_signal = 'GREEN'
            crossing_time = self.pedestrian_manager.get_crossing_time_needed()
            
            print(f"  → Activating PEDESTRIAN CROSSING")
            print(f"  → Reason: {crossing_reason}")
            print(f"  → Crossing Time: {crossing_time} seconds")
            
            self.print_traffic_light('RED')
            print(f"  {self.COLORS['GREEN']}🚶 PEDESTRIAN CROSSING ACTIVE{self.COLORS['RESET']}")
            
            # Simulate crossing
            self.pedestrian_manager.activate_crossing()
            time.sleep(2)  # Brief pause to show crossing
            self.pedestrian_manager.complete_crossing()
        
        # Traffic signal phase
        active_direction, direction_reason = self.select_green_direction(
            self.ns_queue, self.ew_queue, ns_density, ew_density
        )

        if active_direction == self.last_direction:
            self.consecutive_count += 1
        else:
            self.consecutive_count = 1
        self.last_direction = active_direction

        active_density = ns_density if active_direction == 'NS' else ew_density
        green_time = self.controller.compute_green_time(active_density, is_weekday, time_slot)
        
        print(f"  → Active Direction: {active_direction}")
        print(f"  → Direction Reason: {direction_reason}")
        print(f"  → Input: Density={active_density:.1f}%, Day={day_type}, Time={time_slot_names[time_slot]}")
        print(f"  → Output: Green Signal = {self.COLORS['GREEN']}{green_time} seconds{self.COLORS['RESET']}")
        
        # Display traffic light
        if active_direction == 'NS':
            self.print_traffic_light('GREEN')
            print(f"  Active Corridor: NS GREEN, EW RED")
        else:
            self.print_traffic_light('GREEN')
            print(f"  Active Corridor: EW GREEN, NS RED")
        
        # Calculate vehicles that can pass
        vehicles_can_pass = int(green_time / 3)
        if active_direction == 'NS':
            vehicles_passed = min(self.ns_queue, vehicles_can_pass)
            self.ns_queue -= vehicles_passed
            vehicles_delayed = self.ns_queue
        else:
            vehicles_passed = min(self.ew_queue, vehicles_can_pass)
            self.ew_queue -= vehicles_passed
            vehicles_delayed = self.ew_queue

        total_waiting = self.ns_queue + self.ew_queue
        
        print(f"  Vehicles Passing: {self.COLORS['GREEN']}{vehicles_passed}{self.COLORS['RESET']}")
        print(f"  Vehicles Delayed: {self.COLORS['RED']}{vehicles_delayed}{self.COLORS['RESET']}")
        print(f"  Total Waiting (NS+EW): {self.COLORS['YELLOW']}{total_waiting}{self.COLORS['RESET']}")
        
        # Update statistics
        self.total_vehicles_passed += vehicles_passed
        self.total_delay += total_waiting * 60
        self.cycle_count += 1
        
        # Statistics
        print(f"\n  {'-'*66}")
        print(f"  {self.COLORS['BOLD']}SESSION STATISTICS:{self.COLORS['RESET']}")
        print(f"  Total Cycles: {self.cycle_count}")
        print(f"  Total Arrivals: {self.total_arrivals}")
        print(f"  Total Vehicles Passed: {self.total_vehicles_passed}")
        print(f"  Current NS Queue: {self.ns_queue}")
        print(f"  Current EW Queue: {self.ew_queue}")
        print(f"  Total Pedestrians Crossed: {self.pedestrian_manager.get_statistics()['total_pedestrians_crossed']}")
        print(f"  Average Delay per Vehicle: {(self.total_delay / max(1, self.total_vehicles_passed)):.2f}s")
        
        print(f"\n{self.COLORS['BOLD']}{'='*70}{self.COLORS['RESET']}")
        print(f"  {self.COLORS['CYAN']}Press Ctrl+C to stop simulation{self.COLORS['RESET']}")
        print(f"{self.COLORS['BOLD']}{'='*70}{self.COLORS['RESET']}\n")
        
        # Wait for next cycle
        time.sleep(3)
    
    def run(self, duration_minutes=10, start_hour=8, is_weekday=True):
        """
        Run the real-time simulation
        
        Args:
            duration_minutes: How long to run (in simulated minutes)
            start_hour: Starting hour (0-23)
            is_weekday: Whether it's a weekday
        """
        print(f"\n{self.COLORS['BOLD']}Starting Real-Time Simulation...{self.COLORS['RESET']}")
        print(f"Duration: {duration_minutes} simulated minutes")
        print(f"Starting at: {start_hour}:00")
        print(f"Day: {'Weekday' if is_weekday else 'Weekend'}\n")
        
        time.sleep(2)
        
        try:
            current_hour = start_hour
            for cycle in range(1, duration_minutes + 1):
                # Update hour if needed
                if cycle > 1 and cycle % 60 == 1:
                    current_hour = (current_hour + 1) % 24
                
                self.run_simulation_cycle(current_hour, is_weekday, cycle)
            
            # Final summary
            self.clear_screen()
            print(f"\n{self.COLORS['BOLD']}{'='*70}{self.COLORS['RESET']}")
            print(f"{self.COLORS['BOLD']}  SIMULATION COMPLETE - FINAL SUMMARY{self.COLORS['RESET']}")
            print(f"{self.COLORS['BOLD']}{'='*70}{self.COLORS['RESET']}\n")
            
            print(f"  Duration: {duration_minutes} cycles")
            print(f"  Total Arrivals: {self.COLORS['CYAN']}{self.total_arrivals}{self.COLORS['RESET']}")
            print(f"  Total Vehicles Passed: {self.COLORS['GREEN']}{self.total_vehicles_passed}{self.COLORS['RESET']}")
            print(f"  Final NS Queue: {self.COLORS['YELLOW']}{self.ns_queue}{self.COLORS['RESET']}")
            print(f"  Final EW Queue: {self.COLORS['YELLOW']}{self.ew_queue}{self.COLORS['RESET']}")
            print(f"  Total Pedestrians Crossed: {self.COLORS['GREEN']}{self.pedestrian_manager.get_statistics()['total_pedestrians_crossed']}{self.COLORS['RESET']}")
            print(f"  Average Delay: {self.COLORS['YELLOW']}{(self.total_delay / max(1, self.total_vehicles_passed)):.2f}s{self.COLORS['RESET']}")
            print(f"  Safety Overrides: {self.COLORS['RED']}{self.pedestrian_manager.get_statistics()['forced_crossings']}{self.COLORS['RESET']}")
            
            print(f"\n{self.COLORS['BOLD']}{'='*70}{self.COLORS['RESET']}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{self.COLORS['YELLOW']}Simulation stopped by user.{self.COLORS['RESET']}")
            print(f"\nFinal Statistics:")
            print(f"  Cycles Completed: {self.cycle_count}")
            print(f"  Total Arrivals: {self.total_arrivals}")
            print(f"  Vehicles Passed: {self.total_vehicles_passed}")
            print(f"  Final NS Queue: {self.ns_queue}")
            print(f"  Final EW Queue: {self.ew_queue}")
            print(f"  Pedestrians Crossed: {self.pedestrian_manager.get_statistics()['total_pedestrians_crossed']}\n")


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("  SMART TRAFFIC LIGHT CONTROL SYSTEM")
    print("  Real-Time Interactive Simulation")
    print("="*70)
    
    # Get user input
    print("\nSelect simulation scenario:")
    print("  1. Weekday Morning Peak (8:00 AM - High Traffic)")
    print("  2. Weekday Evening Peak (5:00 PM - Very High Traffic)")
    print("  3. Weekend Afternoon (12:00 PM - Medium Traffic)")
    print("  4. Night Time (2:00 AM - Low Traffic)")
    print("  5. Custom")
    
    try:
        choice = input("\nEnter choice (1-5) [default: 1]: ").strip() or "1"
        
        scenarios = {
            '1': (30, 8, True, "Weekday Morning Peak"),
            '2': (30, 17, True, "Weekday Evening Peak"),
            '3': (30, 12, False, "Weekend Afternoon"),
            '4': (20, 2, True, "Night Time"),
        }
        
        if choice in scenarios:
            duration, hour, is_weekday, name = scenarios[choice]
            print(f"\n{name} - Simulating {duration} minutes starting at {hour}:00")
        elif choice == '5':
            duration = int(input("Duration (minutes) [default: 30]: ") or "30")
            hour = int(input("Starting hour (0-23) [default: 8]: ") or "8")
            weekday_input = input("Weekday? (y/n) [default: y]: ").strip().lower() or "y"
            is_weekday = weekday_input == 'y'
        else:
            duration, hour, is_weekday = 30, 8, True
        
        print("\nStarting simulation in 3 seconds...")
        time.sleep(3)
        
        # Run simulation
        sim = RealTimeSimulation()
        sim.run(duration_minutes=duration, start_hour=hour, is_weekday=is_weekday)
        
    except KeyboardInterrupt:
        print("\n\nSimulation cancelled.\n")
    except Exception as e:
        print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
