"""
Quick Start Script for Smart Traffic Light Control System
Run this file to quickly test the system
"""

import sys

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'numpy': 'numpy',
        'skfuzzy': 'scikit-fuzzy',
        'matplotlib': 'matplotlib'
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            print(f"✗ {package_name} is NOT installed")
            missing.append(package_name)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\nPlease install them using:")
        print("  pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies are installed!\n")
    return True


def run_demo():
    """Run a quick demonstration"""
    print("="*70)
    print("SMART TRAFFIC LIGHT CONTROL SYSTEM - QUICK START")
    print("="*70)
    print("\nChecking dependencies...")
    print("-"*70)
    
    if not check_dependencies():
        sys.exit(1)
    
    print("\nStarting demonstration...")
    print("-"*70)
    
    try:
        from main_control_system import SmartTrafficLightSystem
        
        # Create and run system
        system = SmartTrafficLightSystem(intersection_id="DEMO-001")
        
        # Run a quick 60-minute comparison
        comparison = system.compare_systems(
            duration_minutes=60,
            start_hour=8,
            is_weekday=True
        )
        
        # Print results
        system.print_comparison_results(comparison)
        
        print("\n" + "="*70)
        print("QUICK START COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("  1. Run 'python performance_testing.py' for comprehensive analysis")
        print("  2. Check generated PNG files for visualizations")
        print("  3. Read README.md for detailed documentation")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error running demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_demo()
