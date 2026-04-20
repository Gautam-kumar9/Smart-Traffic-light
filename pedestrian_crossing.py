"""
Pedestrian Crossing Management System
Ensures pedestrian safety with maximum waiting time enforcement
"""

import random
from datetime import datetime, timedelta


class PedestrianCrossingManager:
    """
    Manages pedestrian crossing signals with safety constraints
    """
    
    def __init__(self, max_waiting_time=120, crossing_time=20):
        """
        Initialize pedestrian crossing manager
        
        Args:
            max_waiting_time: Maximum time pedestrians should wait (seconds)
            crossing_time: Time allocated for pedestrian crossing (seconds)
        """
        self.max_waiting_time = max_waiting_time  # Maximum wait before forcing crossing
        self.crossing_time = crossing_time  # Time for safe pedestrian crossing
        self.current_waiting_time = 0
        self.pedestrians_waiting = 0
        self.crossing_active = False
        self.total_pedestrians_crossed = 0
        self.crossing_requests = 0
        self.forced_crossings = 0  # Crossings triggered by max wait time
    
    def add_pedestrian_request(self, num_pedestrians=1):
        """
        Register pedestrian crossing request
        
        Args:
            num_pedestrians: Number of pedestrians requesting crossing
        """
        self.pedestrians_waiting += num_pedestrians
        self.crossing_requests += 1
    
    def update_waiting_time(self, elapsed_seconds):
        """
        Update pedestrian waiting time
        
        Args:
            elapsed_seconds: Time elapsed since last update
        """
        if self.pedestrians_waiting > 0 and not self.crossing_active:
            self.current_waiting_time += elapsed_seconds
    
    def should_activate_crossing(self, traffic_density=0):
        """
        Determine if pedestrian crossing should be activated
        
        Args:
            traffic_density: Current traffic density (0-100)
        
        Returns:
            Tuple (should_activate, reason)
        """
        # No pedestrians waiting
        if self.pedestrians_waiting == 0:
            return False, "No pedestrians waiting"
        
        # Crossing already active
        if self.crossing_active:
            return False, "Crossing already active"
        
        # Force crossing if max waiting time exceeded (safety priority)
        if self.current_waiting_time >= self.max_waiting_time:
            self.forced_crossings += 1
            return True, f"Maximum wait time ({self.max_waiting_time}s) exceeded - SAFETY OVERRIDE"
        
        # Allow crossing during low traffic
        if traffic_density < 30:
            return True, "Low traffic density - safe to cross"
        
        # Allow crossing if waited more than 60 seconds and medium traffic
        if self.current_waiting_time >= 60 and traffic_density < 60:
            return True, "Moderate wait time with acceptable traffic"
        
        return False, "High traffic - waiting for better opportunity"
    
    def activate_crossing(self):
        """Activate pedestrian crossing signal"""
        if self.pedestrians_waiting > 0:
            self.crossing_active = True
            return True
        return False
    
    def complete_crossing(self):
        """Complete pedestrian crossing cycle"""
        if self.crossing_active:
            self.total_pedestrians_crossed += self.pedestrians_waiting
            self.pedestrians_waiting = 0
            self.current_waiting_time = 0
            self.crossing_active = False
            return True
        return False
    
    def get_crossing_time_needed(self):
        """
        Calculate time needed for all waiting pedestrians to cross
        
        Returns:
            Time in seconds needed for crossing
        """
        if self.pedestrians_waiting == 0:
            return 0
        
        # Base crossing time + additional time for large groups
        extra_time = max(0, (self.pedestrians_waiting - 5) * 2)
        return self.crossing_time + extra_time
    
    def reset_waiting(self):
        """Reset waiting time counter"""
        self.current_waiting_time = 0
    
    def get_statistics(self):
        """Get pedestrian crossing statistics"""
        return {
            'total_pedestrians_crossed': self.total_pedestrians_crossed,
            'crossing_requests': self.crossing_requests,
            'forced_crossings': self.forced_crossings,
            'current_waiting': self.pedestrians_waiting,
            'current_waiting_time': self.current_waiting_time,
            'max_waiting_time': self.max_waiting_time,
            'avg_pedestrians_per_request': (
                self.total_pedestrians_crossed / max(1, self.crossing_requests)
            )
        }
    
    def get_status(self):
        """Get current status summary"""
        status = "CROSSING ACTIVE" if self.crossing_active else "WAITING"
        return {
            'status': status,
            'pedestrians_waiting': self.pedestrians_waiting,
            'waiting_time': self.current_waiting_time,
            'time_until_forced': max(0, self.max_waiting_time - self.current_waiting_time)
        }


class PedestrianGenerator:
    """
    Generates realistic pedestrian crossing requests
    """
    
    def __init__(self, seed=None):
        """Initialize pedestrian generator"""
        if seed:
            random.seed(seed)
    
    def generate_pedestrian_requests(self, hour, is_weekday, duration_minutes=60):
        """
        Generate pedestrian crossing requests based on time and day
        
        Args:
            hour: Hour of day (0-23)
            is_weekday: Boolean indicating if it's a weekday
            duration_minutes: Duration to simulate
        
        Returns:
            List of pedestrian request events
        """
        # Define pedestrian patterns (requests per hour)
        patterns = {
            'weekday': {
                'night': 0.5,      # Few pedestrians at night
                'morning': 8,       # Many commuters
                'midday': 12,       # Lunch time peak
                'evening': 10,      # Evening commute
            },
            'weekend': {
                'night': 0.3,
                'morning': 4,
                'midday': 15,       # Shopping/leisure peak
                'evening': 8,
            }
        }
        
        # Determine period
        if 23 <= hour or hour < 6:
            period = 'night'
        elif 7 <= hour < 11:
            period = 'morning'
        elif 11 <= hour < 17:
            period = 'midday'
        else:
            period = 'evening'
        
        day_type = 'weekday' if is_weekday else 'weekend'
        base_rate = patterns[day_type][period]
        
        # Generate requests
        requests = []
        for minute in range(duration_minutes):
            # Probability of request in this minute
            prob = base_rate / 60.0  # Convert hourly rate to per-minute
            
            if random.random() < prob:
                # Number of pedestrians in group (1-8, weighted toward smaller groups)
                num_pedestrians = random.choices(
                    [1, 2, 3, 4, 5, 6, 7, 8],
                    weights=[30, 25, 20, 12, 7, 3, 2, 1]
                )[0]
                
                requests.append({
                    'minute': minute,
                    'num_pedestrians': num_pedestrians,
                    'hour': hour + (minute // 60)
                })
        
        return requests


if __name__ == "__main__":
    print("Testing Pedestrian Crossing Management System\n")
    print("="*70)
    
    # Test pedestrian crossing manager
    manager = PedestrianCrossingManager(max_waiting_time=120, crossing_time=20)
    
    print("\n1. Testing Basic Functionality:")
    print("-" * 70)
    
    # Simulate pedestrian requests
    print("\nAdding 3 pedestrians...")
    manager.add_pedestrian_request(3)
    print(f"Status: {manager.get_status()}")
    
    # Simulate waiting
    print("\nWaiting 30 seconds with low traffic...")
    manager.update_waiting_time(30)
    should_activate, reason = manager.should_activate_crossing(traffic_density=20)
    print(f"Should activate crossing: {should_activate}")
    print(f"Reason: {reason}")
    
    # Activate crossing
    if should_activate:
        print("\nActivating crossing...")
        manager.activate_crossing()
        print(f"Status: {manager.get_status()}")
        print(f"Crossing time needed: {manager.get_crossing_time_needed()} seconds")
        
        print("\nCompleting crossing...")
        manager.complete_crossing()
        print(f"Status: {manager.get_status()}")
    
    print("\n\n2. Testing Maximum Wait Time Enforcement:")
    print("-" * 70)
    
    # Reset and test max wait time
    manager = PedestrianCrossingManager(max_waiting_time=90)
    manager.add_pedestrian_request(5)
    
    print("\nSimulating high traffic scenario...")
    for i in range(0, 100, 20):
        manager.update_waiting_time(20)
        should_activate, reason = manager.should_activate_crossing(traffic_density=85)
        print(f"\nTime: {i+20}s, High traffic (85%)")
        print(f"  Should activate: {should_activate}")
        print(f"  Reason: {reason}")
        print(f"  Waiting time: {manager.current_waiting_time}s")
        
        if should_activate:
            print("  → CROSSING ACTIVATED!")
            manager.activate_crossing()
            manager.complete_crossing()
            break
    
    print("\n\n3. Testing Pedestrian Generator:")
    print("-" * 70)
    
    generator = PedestrianGenerator(seed=42)
    
    test_scenarios = [
        (8, True, "Weekday Morning"),
        (13, True, "Weekday Midday"),
        (19, True, "Weekday Evening"),
        (13, False, "Weekend Midday"),
    ]
    
    for hour, is_weekday, description in test_scenarios:
        requests = generator.generate_pedestrian_requests(hour, is_weekday, 60)
        total_pedestrians = sum(r['num_pedestrians'] for r in requests)
        print(f"\n{description} ({hour}:00):")
        print(f"  Total requests: {len(requests)}")
        print(f"  Total pedestrians: {total_pedestrians}")
        print(f"  Avg group size: {total_pedestrians/max(1, len(requests)):.1f}")
    
    print("\n\n4. Full Statistics:")
    print("-" * 70)
    stats = manager.get_statistics()
    print(f"\nTotal pedestrians crossed: {stats['total_pedestrians_crossed']}")
    print(f"Total crossing requests: {stats['crossing_requests']}")
    print(f"Forced crossings (safety): {stats['forced_crossings']}")
    print(f"Average pedestrians per request: {stats['avg_pedestrians_per_request']:.1f}")
    
    print("\n" + "="*70)
    print("Pedestrian Crossing System Test Completed!")
