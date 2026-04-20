"""
Traffic Simulation System
Simulates realistic traffic patterns based on time of day, day of week, and randomness
"""

import numpy as np
from datetime import datetime, timedelta
import random


class TrafficSimulator:
    """
    Simulates traffic flow at an intersection
    """
    
    def __init__(self, seed=None):
        """
        Initialize traffic simulator
        
        Args:
            seed: Random seed for reproducibility
        """
        if seed:
            np.random.seed(seed)
            random.seed(seed)
        
        # Base traffic patterns (vehicles per minute)
        self.base_patterns = {
            'weekday': {
                'night': 5,          # 11 PM - 5 AM
                'morning_peak': 85,   # 7 AM - 10 AM
                'normal': 45,         # 10 AM - 4 PM
                'evening_peak': 90,   # 5 PM - 8 PM
            },
            'weekend': {
                'night': 3,
                'morning_peak': 40,
                'normal': 55,
                'evening_peak': 65,
            }
        }
    
    def get_time_slot(self, hour):
        """
        Determine time slot based on hour of day
        
        Args:
            hour: Hour of day (0-23)
        
        Returns:
            Time slot code: 0=night, 1=normal, 2=morning_peak, 3=evening_peak
        """
        if 23 <= hour or hour < 5:
            return 0  # Night
        elif 7 <= hour < 10:
            return 2  # Morning peak
        elif 17 <= hour < 20:
            return 3  # Evening peak
        else:
            return 1  # Normal
    
    def get_time_slot_name(self, time_slot):
        """Get human-readable name for time slot"""
        names = {0: 'night', 1: 'normal', 2: 'morning_peak', 3: 'evening_peak'}
        return names.get(time_slot, 'normal')
    
    def is_weekday(self, date=None):
        """
        Check if given date is a weekday
        
        Args:
            date: datetime object (default: current date)
        
        Returns:
            Boolean indicating if it's a weekday
        """
        if date is None:
            date = datetime.now()
        return date.weekday() < 5  # Monday=0, Sunday=6
    
    def generate_traffic_density(self, hour, is_weekday_flag):
        """
        Generate realistic traffic density based on time and day
        
        Args:
            hour: Hour of day (0-23)
            is_weekday_flag: Boolean indicating if it's a weekday
        
        Returns:
            Traffic density (0-100)
        """
        time_slot = self.get_time_slot(hour)
        time_slot_name = self.get_time_slot_name(time_slot)
        
        day_type = 'weekday' if is_weekday_flag else 'weekend'
        base_density = self.base_patterns[day_type][time_slot_name]
        
        # Add random variation (±15%)
        variation = np.random.normal(0, base_density * 0.15)
        density = base_density + variation
        
        # Clip to valid range
        density = np.clip(density, 0, 100)
        
        return round(density, 1)

    def generate_directional_densities(self, total_density):
        """
        Split total traffic density into North-South and East-West directional densities.

        Args:
            total_density: Combined intersection density (0-100)

        Returns:
            Tuple (ns_density, ew_density)
        """
        # Directional imbalance factor allows one side to become much busier than the other.
        ns_share = np.clip(np.random.normal(0.5, 0.2), 0.2, 0.8)
        ew_share = 1.0 - ns_share

        ns_density = np.clip(total_density * ns_share * 2, 0, 100)
        ew_density = np.clip(total_density * ew_share * 2, 0, 100)

        return round(ns_density, 1), round(ew_density, 1)
    
    def simulate_intersection(self, duration_minutes=60, start_hour=8, is_weekday_flag=True):
        """
        Simulate traffic at an intersection for specified duration
        
        Args:
            duration_minutes: Simulation duration in minutes
            start_hour: Starting hour of simulation (0-23)
            is_weekday_flag: Boolean indicating if it's a weekday
        
        Returns:
            List of traffic density readings (one per minute)
        """
        traffic_data = []
        current_hour = start_hour
        
        for minute in range(duration_minutes):
            # Update hour
            if minute > 0 and minute % 60 == 0:
                current_hour = (current_hour + 1) % 24
            
            density = self.generate_traffic_density(current_hour, is_weekday_flag)
            time_slot = self.get_time_slot(current_hour)
            
            traffic_data.append({
                'minute': minute,
                'hour': current_hour,
                'density': density,
                'time_slot': time_slot,
                'is_weekday': is_weekday_flag
            })
        
        return traffic_data
    
    def generate_multi_scenario_data(self):
        """
        Generate traffic data for multiple scenarios
        
        Returns:
            Dictionary of scenarios with traffic data
        """
        scenarios = {
            'weekday_morning_peak': {
                'duration': 180,  # 3 hours
                'start_hour': 7,
                'is_weekday': True,
                'description': 'Weekday Morning Peak (7 AM - 10 AM)'
            },
            'weekday_evening_peak': {
                'duration': 180,
                'start_hour': 17,
                'is_weekday': True,
                'description': 'Weekday Evening Peak (5 PM - 8 PM)'
            },
            'weekday_normal': {
                'duration': 120,
                'start_hour': 11,
                'is_weekday': True,
                'description': 'Weekday Normal Hours (11 AM - 1 PM)'
            },
            'weekend_day': {
                'duration': 240,
                'start_hour': 10,
                'is_weekday': False,
                'description': 'Weekend Daytime (10 AM - 2 PM)'
            },
            'night_time': {
                'duration': 120,
                'start_hour': 1,
                'is_weekday': True,
                'description': 'Night Time (1 AM - 3 AM)'
            }
        }
        
        results = {}
        for scenario_name, params in scenarios.items():
            data = self.simulate_intersection(
                duration_minutes=params['duration'],
                start_hour=params['start_hour'],
                is_weekday_flag=params['is_weekday']
            )
            results[scenario_name] = {
                'data': data,
                'description': params['description']
            }
        
        return results
    
    def get_vehicle_queue(self, density):
        """
        Estimate number of vehicles waiting based on density
        
        Args:
            density: Traffic density (0-100)
        
        Returns:
            Approximate number of vehicles in queue
        """
        # Rough estimation: density directly correlates with queue length
        # Low density (0-30): 0-10 vehicles
        # Medium density (30-70): 10-30 vehicles
        # High density (70-100): 30-50 vehicles
        
        if density < 30:
            base = density / 3
        elif density < 70:
            base = 10 + (density - 30) / 2
        else:
            base = 30 + (density - 70) * 0.67
        
        # Add some randomness
        variation = np.random.randint(-2, 3)
        vehicles = int(base + variation)
        
        return max(0, vehicles)


class IntersectionState:
    """Represents the current state of a traffic intersection"""
    
    def __init__(self):
        self.current_density = 0
        self.vehicles_waiting = 0
        self.time_slot = 1
        self.is_weekday = True
        self.current_signal = 'red'  # red, yellow, green
        self.signal_timer = 0
        self.total_vehicles_passed = 0
        self.total_waiting_time = 0
        self.cycle_count = 0
    
    def update(self, density, time_slot, is_weekday):
        """Update intersection state with new traffic data"""
        self.current_density = density
        self.time_slot = time_slot
        self.is_weekday = is_weekday
    
    def get_state_summary(self):
        """Get summary of current state"""
        return {
            'density': self.current_density,
            'vehicles_waiting': self.vehicles_waiting,
            'current_signal': self.current_signal,
            'signal_timer': self.signal_timer,
            'total_vehicles_passed': self.total_vehicles_passed,
            'avg_waiting_time': self.total_waiting_time / max(1, self.total_vehicles_passed)
        }


if __name__ == "__main__":
    # Test the traffic simulator
    print("Testing Traffic Simulator\n")
    print("="*70)
    
    simulator = TrafficSimulator(seed=42)
    
    # Test single scenario
    print("\nSimulating Weekday Morning Peak (30 minutes):")
    print("-" * 70)
    traffic_data = simulator.simulate_intersection(
        duration_minutes=30,
        start_hour=8,
        is_weekday_flag=True
    )
    
    print(f"{'Minute':<8} {'Hour':<6} {'Density':<10} {'Time Slot':<12} {'Weekday'}")
    print("-" * 70)
    for i in range(0, 30, 5):  # Show every 5th minute
        data = traffic_data[i]
        time_slot_names = ['Night', 'Normal', 'Morning Peak', 'Evening Peak']
        print(f"{data['minute']:<8} {data['hour']:<6} {data['density']:<10.1f} "
              f"{time_slot_names[data['time_slot']]:<12} {data['is_weekday']}")
    
    # Test multiple scenarios
    print("\n\nGenerating Multiple Scenarios:")
    print("="*70)
    scenarios = simulator.generate_multi_scenario_data()
    
    for scenario_name, scenario_data in scenarios.items():
        data = scenario_data['data']
        avg_density = np.mean([d['density'] for d in data])
        max_density = max([d['density'] for d in data])
        min_density = min([d['density'] for d in data])
        
        print(f"\n{scenario_data['description']}:")
        print(f"  Duration: {len(data)} minutes")
        print(f"  Average Density: {avg_density:.1f}")
        print(f"  Max Density: {max_density:.1f}")
        print(f"  Min Density: {min_density:.1f}")
    
    print("\n" + "="*70)
    print("Simulation completed successfully!")
