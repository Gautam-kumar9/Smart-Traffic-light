# Smart Traffic Light Control System

An adaptive traffic signal control project based on fuzzy logic and soft computing.
The system compares fixed-time control against smart fuzzy control under realistic traffic patterns and pedestrian crossing demand.

## Overview

Traditional fixed-time traffic signals do not adapt to changing demand and can increase congestion during peak periods. This project uses fuzzy logic to dynamically choose green signal duration using:

- Traffic density
- Day type (weekday or weekend)
- Time period (night, normal, morning peak, evening peak)

It also includes pedestrian safety logic with a maximum waiting-time policy.

## Core Features

- Adaptive green timing using a 24-rule fuzzy inference controller
- Side-by-side comparison: fixed-time vs smart fuzzy control
- Pedestrian crossing manager with safety overrides
- Scenario-based performance testing and chart generation
- Interactive dashboard for analysis and presentation
- SUMO scenario files for external simulation integration

## Current Project Structure

```text
Smart-Traffic-light/
+-- fuzzy_controller.py
+-- traffic_simulator.py
+-- pedestrian_crossing.py
+-- main_control_system.py
+-- performance_testing.py
+-- quick_start.py
+-- real_time_simulation.py
+-- visual_simulation.py
+-- streamlit_dashboard.py
+-- sumo_fuzzy_simulation.py
+-- requirements.txt
+-- README.md
+-- sumo_scenario/
    +-- intersection.net.xml
    +-- intersection.sumocfg
    +-- routes.rou.xml
    +-- trips.trips.xml
```

## Installation

### 1. Clone Repository

```powershell
git clone https://github.com/Gautam-kumar9/Smart-Traffic-light.git
cd Smart-Traffic-light
```

### 2. Create and Activate Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

## Usage

### Quick Demo

```powershell
python quick_start.py
```

### Main Comparison Run

```powershell
python main_control_system.py
```

### Full Performance Analysis (Generates Charts + JSON)

```powershell
python performance_testing.py
```

### Interactive Dashboard

```powershell
streamlit run streamlit_dashboard.py
```

### Real-Time Console Simulations

```powershell
python real_time_simulation.py
python visual_simulation.py
```

### SUMO Integration Entry Point

```powershell
python sumo_fuzzy_simulation.py
```

## Verified Results

The following results were produced from the current codebase using:

```powershell
python quick_start.py
```

Run date: April 20, 2026  
Scenario: 60-minute weekday morning simulation

| Metric | Fixed-Time | Smart Fuzzy Control |
|---|---:|---:|
| Total Vehicles Processed | 4179 | 4275 |
| Total Delay (seconds) | 5,485,200.0 | 4,381,500.0 |
| Average Delay (seconds) | 1312.56 | 1024.91 |
| Number of Cycles | 60 | 60 |
| Delay Reduction | - | 21.92% |
| Total Delay Saved (seconds) | - | 1,103,700.0 |

Pedestrian safety outcomes in the same run:

- Pedestrians crossed: 29
- Crossing requests: 11
- Safety overrides: 7

## Generated Outputs

When you run the full analysis script, it generates:

- test_results.json
- performance_comparison.png
- improvement_chart.png
- adaptive_response.png
- traffic_patterns.png
- membership_functions.png

These files are generated on demand and are not required to keep in the repository.

## Technical Notes

- Fuzzy logic implemented with scikit-fuzzy
- Numerical simulation with NumPy and SciPy
- Visualization with Matplotlib and Plotly
- Dashboard built with Streamlit and Pandas

## Limitations

- Current simulation models a single intersection at a simplified level
- Vehicle behavior and sensor inputs are synthetic (simulated)
- Real-world deployment would need calibration using field traffic data

## Future Improvements

- Multi-intersection coordination
- Emergency vehicle prioritization
- Camera or IoT based real-time density estimation
- Learning-based optimization of fuzzy membership functions and rules

## License

This project is intended for academic and educational use.
