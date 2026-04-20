"""
Fuzzy Logic Controller for Smart Traffic Light System
Implements fuzzy rules for dynamic signal timing based on traffic conditions
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from pathlib import Path


class FuzzyTrafficController:
    """
    Fuzzy Logic Controller for traffic signal timing
    """
    
    def __init__(self):
        """Initialize fuzzy variables and rules"""
        self.setup_fuzzy_system()
    
    def setup_fuzzy_system(self):
        """Setup fuzzy variables, membership functions and rules"""
        
        # Input variables
        # Traffic density (vehicles per minute)
        self.traffic_density = ctrl.Antecedent(np.arange(0, 101, 1), 'traffic_density')
        
        # Day type: 0 = weekend, 1 = weekday
        self.day_type = ctrl.Antecedent(np.arange(0, 2, 1), 'day_type')
        
        # Time slot: 0 = night, 1 = normal, 2 = morning peak, 3 = evening peak
        self.time_slot = ctrl.Antecedent(np.arange(0, 4, 1), 'time_slot')
        
        # Output variable
        # Green signal time (seconds)
        self.green_time = ctrl.Consequent(np.arange(10, 121, 1), 'green_time')
        
        # Define membership functions for traffic density
        self.traffic_density['low'] = fuzz.trapmf(self.traffic_density.universe, [0, 0, 20, 35])
        self.traffic_density['medium'] = fuzz.trimf(self.traffic_density.universe, [25, 50, 75])
        self.traffic_density['high'] = fuzz.trapmf(self.traffic_density.universe, [65, 80, 100, 100])
        
        # Define membership functions for day type
        self.day_type['weekend'] = fuzz.trimf(self.day_type.universe, [0, 0, 0.5])
        self.day_type['weekday'] = fuzz.trimf(self.day_type.universe, [0.5, 1, 1])
        
        # Define membership functions for time slot
        self.time_slot['night'] = fuzz.trimf(self.time_slot.universe, [0, 0, 1])
        self.time_slot['normal'] = fuzz.trimf(self.time_slot.universe, [0.5, 1.5, 2.5])
        self.time_slot['morning_peak'] = fuzz.trimf(self.time_slot.universe, [1.5, 2, 2.5])
        self.time_slot['evening_peak'] = fuzz.trimf(self.time_slot.universe, [2.5, 3, 3])
        
        # Define membership functions for green time
        self.green_time['very_short'] = fuzz.trapmf(self.green_time.universe, [10, 10, 20, 30])
        self.green_time['short'] = fuzz.trimf(self.green_time.universe, [25, 35, 45])
        self.green_time['medium'] = fuzz.trimf(self.green_time.universe, [40, 55, 70])
        self.green_time['long'] = fuzz.trimf(self.green_time.universe, [65, 80, 95])
        self.green_time['very_long'] = fuzz.trapmf(self.green_time.universe, [90, 100, 120, 120])
        
        # Define fuzzy rules
        rules = [
            # Night time rules (low traffic expected)
            ctrl.Rule(self.traffic_density['low'] & self.time_slot['night'], 
                     self.green_time['very_short']),
            ctrl.Rule(self.traffic_density['medium'] & self.time_slot['night'], 
                     self.green_time['short']),
            ctrl.Rule(self.traffic_density['high'] & self.time_slot['night'], 
                     self.green_time['medium']),
            
            # Normal time - Weekend
            ctrl.Rule(self.traffic_density['low'] & self.day_type['weekend'] & 
                     self.time_slot['normal'], self.green_time['short']),
            ctrl.Rule(self.traffic_density['medium'] & self.day_type['weekend'] & 
                     self.time_slot['normal'], self.green_time['medium']),
            ctrl.Rule(self.traffic_density['high'] & self.day_type['weekend'] & 
                     self.time_slot['normal'], self.green_time['long']),
            
            # Normal time - Weekday
            ctrl.Rule(self.traffic_density['low'] & self.day_type['weekday'] & 
                     self.time_slot['normal'], self.green_time['short']),
            ctrl.Rule(self.traffic_density['medium'] & self.day_type['weekday'] & 
                     self.time_slot['normal'], self.green_time['medium']),
            ctrl.Rule(self.traffic_density['high'] & self.day_type['weekday'] & 
                     self.time_slot['normal'], self.green_time['long']),
            
            # Morning Peak - Weekday (high traffic expected)
            ctrl.Rule(self.traffic_density['low'] & self.day_type['weekday'] & 
                     self.time_slot['morning_peak'], self.green_time['medium']),
            ctrl.Rule(self.traffic_density['medium'] & self.day_type['weekday'] & 
                     self.time_slot['morning_peak'], self.green_time['long']),
            ctrl.Rule(self.traffic_density['high'] & self.day_type['weekday'] & 
                     self.time_slot['morning_peak'], self.green_time['very_long']),
            
            # Morning Peak - Weekend (moderate traffic)
            ctrl.Rule(self.traffic_density['low'] & self.day_type['weekend'] & 
                     self.time_slot['morning_peak'], self.green_time['short']),
            ctrl.Rule(self.traffic_density['medium'] & self.day_type['weekend'] & 
                     self.time_slot['morning_peak'], self.green_time['medium']),
            ctrl.Rule(self.traffic_density['high'] & self.day_type['weekend'] & 
                     self.time_slot['morning_peak'], self.green_time['long']),
            
            # Evening Peak - Weekday (highest traffic expected)
            ctrl.Rule(self.traffic_density['low'] & self.day_type['weekday'] & 
                     self.time_slot['evening_peak'], self.green_time['medium']),
            ctrl.Rule(self.traffic_density['medium'] & self.day_type['weekday'] & 
                     self.time_slot['evening_peak'], self.green_time['long']),
            ctrl.Rule(self.traffic_density['high'] & self.day_type['weekday'] & 
                     self.time_slot['evening_peak'], self.green_time['very_long']),
            
            # Evening Peak - Weekend
            ctrl.Rule(self.traffic_density['low'] & self.day_type['weekend'] & 
                     self.time_slot['evening_peak'], self.green_time['short']),
            ctrl.Rule(self.traffic_density['medium'] & self.day_type['weekend'] & 
                     self.time_slot['evening_peak'], self.green_time['medium']),
            ctrl.Rule(self.traffic_density['high'] & self.day_type['weekend'] & 
                     self.time_slot['evening_peak'], self.green_time['long']),
        ]
        
        # Create control system
        self.traffic_ctrl = ctrl.ControlSystem(rules)
        self.traffic_simulation = ctrl.ControlSystemSimulation(self.traffic_ctrl)
    
    def compute_green_time(self, density, is_weekday, time_period):
        """
        Compute optimal green signal time using fuzzy logic
        
        Args:
            density: Traffic density (0-100)
            is_weekday: Boolean indicating if it's a weekday
            time_period: Time slot (0=night, 1=normal, 2=morning peak, 3=evening peak)
        
        Returns:
            Optimal green signal time in seconds
        """
        # Set inputs
        self.traffic_simulation.input['traffic_density'] = density
        self.traffic_simulation.input['day_type'] = 1 if is_weekday else 0
        self.traffic_simulation.input['time_slot'] = time_period
        
        # Compute result
        self.traffic_simulation.compute()
        
        return round(self.traffic_simulation.output['green_time'])
    
    def visualize_membership_functions(self, output_path='membership_functions.png'):
        """Visualize and save membership functions."""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15, 10))
        
        # Traffic Density
        self.traffic_density.view(ax=axes[0, 0])
        axes[0, 0].set_title('Traffic Density Membership Functions')
        
        # Day Type
        self.day_type.view(ax=axes[0, 1])
        axes[0, 1].set_title('Day Type Membership Functions')
        
        # Time Slot
        self.time_slot.view(ax=axes[1, 0])
        axes[1, 0].set_title('Time Slot Membership Functions')
        
        # Green Time
        self.green_time.view(ax=axes[1, 1])
        axes[1, 1].set_title('Green Signal Time Membership Functions')
        
        plt.tight_layout()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Membership functions saved to '{output_file}'")
        plt.close()


if __name__ == "__main__":
    # Test the fuzzy controller
    controller = FuzzyTrafficController()
    
    # Test scenarios
    print("Testing Fuzzy Traffic Light Controller\n")
    print("="*60)
    
    test_cases = [
        (80, True, 3, "High density, Weekday, Evening Peak"),
        (30, True, 2, "Low density, Weekday, Morning Peak"),
        (50, False, 1, "Medium density, Weekend, Normal time"),
        (15, True, 0, "Low density, Weekday, Night"),
        (90, True, 2, "High density, Weekday, Morning Peak"),
    ]
    
    for density, is_weekday, time_slot, description in test_cases:
        green_time = controller.compute_green_time(density, is_weekday, time_slot)
        day = "Weekday" if is_weekday else "Weekend"
        time_names = ["Night", "Normal", "Morning Peak", "Evening Peak"]
        print(f"\n{description}")
        print(f"  Density: {density}%, Day: {day}, Time: {time_names[time_slot]}")
        print(f"  → Green Signal Time: {green_time} seconds")
    
    print("\n" + "="*60)
    
    # Visualize membership functions
    try:
        controller.visualize_membership_functions()
    except Exception as e:
        print(f"\nVisualization skipped: {e}")
