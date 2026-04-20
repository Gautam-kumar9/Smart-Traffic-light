# Smart Traffic Light Control System Using Soft Computing

A comprehensive implementation of an intelligent traffic signal control system using **Fuzzy Logic** to dynamically manage traffic flow at intersections. This project demonstrates how soft computing techniques can significantly improve traffic management compared to traditional fixed-time signal systems.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Results](#results)
- [Technical Details](#technical-details)

## 🎯 Overview

Traditional traffic light systems use fixed timers that fail to adapt to real-time traffic conditions, leading to:
- Unnecessary delays during peak hours
- Fuel wastage and increased pollution
- Inefficient traffic management
- Poor pedestrian safety

This project proposes a **Smart Traffic Light Control System** that uses **Fuzzy Logic** to dynamically adjust signal timing based on:
- **Traffic density** (vehicle count)
- **Day type** (weekday vs weekend)
- **Time slot** (morning peak, evening peak, normal, night)
- **Pedestrian crossing priority** with maximum waiting time enforcement

## ✨ Features

### 🚦 Intelligent Traffic Control
- **Fuzzy Logic Controller**: Adaptive signal timing based on real-time conditions
- **Dynamic Green Time**: Adjusts from 10 to 120 seconds based on traffic demand
- **Multi-Factor Decision Making**: Considers density, time, and day type

### 👥 Pedestrian Safety
- **Priority Crossing System**: Dedicated pedestrian crossing phase
- **Maximum Wait Time Enforcement**: Forces crossing after 120 seconds (safety override)
- **Intelligent Scheduling**: Activates during low traffic periods when possible

### 📊 Performance Analysis
- **Comprehensive Testing**: Multiple scenarios (peak hours, weekends, night)
- **Comparison Framework**: Fixed-time vs smart control comparison
- **Visual Analytics**: Charts and graphs showing performance improvements

### 🎨 Visualization
- Performance comparison charts
- Traffic density response curves
- 24-hour traffic pattern analysis
- Fuzzy membership function plots

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Smart Traffic Light System                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────────────────────┐   │
│  │   Traffic    │─────▶│   Fuzzy Logic Controller     │   │
│  │  Simulator   │      │  • Fuzzification             │   │
│  └──────────────┘      │  • Rule Base (24 rules)      │   │
│         │              │  • Defuzzification           │   │
│         │              └──────────────┬───────────────┘   │
│         │                             │                   │
│         ▼                             ▼                   │
│  ┌──────────────┐      ┌──────────────────────────────┐   │
│  │  Pedestrian  │─────▶│   Main Control System        │   │
│  │   Manager    │      │  • Signal Coordination       │   │
│  └──────────────┘      │  • Cycle Management          │   │
│                        │  • Performance Tracking      │   │
│                        └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📥 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or navigate to the project directory**
```powershell
cd "C:\Users\gauta\OneDrive\Desktop\soft project"
```

2. **Install required packages**
```powershell
pip install -r requirements.txt
```

The required packages are:
- `numpy` - Numerical computing
- `scikit-fuzzy` - Fuzzy logic implementation
- `matplotlib` - Visualization and plotting

## 🚀 Usage

### Quick Start - Run Main Demonstration

```powershell
python main_control_system.py
```

This will:
- Compare fixed-time vs smart control for 120 minutes
- Simulate weekday morning peak traffic (8:00 AM - 10:00 AM)
- Display performance metrics and improvements

### Run Comprehensive Analysis

```powershell
python performance_testing.py
```

This will:
- Test 5 different traffic scenarios
- Generate performance comparison charts
- Create visualizations showing system behavior
- Save results to `test_results.json`

### Launch Interactive Streamlit Dashboard

```powershell
streamlit run streamlit_dashboard.py
```

Dashboard features include:
- Full scenario comparison (Fixed-Time vs Smart Fuzzy)
- Live KPI cards and queue-level analytics
- Fuzzy logic response lab
- Pedestrian safety and fairness diagnostics
- SUMO scenario status and report downloads

### Test Individual Components

**Test Fuzzy Logic Controller:**
```powershell
python fuzzy_controller.py
```

**Test Traffic Simulation:**
```powershell
python traffic_simulator.py
```

**Test Pedestrian Crossing System:**
```powershell
python pedestrian_crossing.py
```

## 📁 Project Structure

```
soft project/
│
├── fuzzy_controller.py          # Fuzzy logic implementation with 24 rules
├── traffic_simulator.py         # Traffic pattern generation and simulation
├── pedestrian_crossing.py       # Pedestrian crossing management
├── main_control_system.py       # Main system integration and control
├── performance_testing.py       # Testing framework and visualization
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── final report.pdf             # Project documentation
├── report.pdf                   # Additional report
│
└── Generated Output Files:
    ├── test_results.json        # Performance test results
    ├── performance_comparison.png    # Bar chart comparison
    ├── improvement_chart.png         # Improvement percentages
    ├── adaptive_response.png         # Green time adaptation
    ├── traffic_patterns.png          # 24-hour traffic patterns
    └── membership_functions.png      # Fuzzy membership functions
```

## 📊 Results

### Performance Improvements

The smart fuzzy logic control system demonstrates significant improvements over traditional fixed-time control:

| Scenario | Fixed-Time Delay | Smart Control Delay | Improvement |
|----------|------------------|---------------------|-------------|
| Weekday Morning Peak | ~45.2s | ~32.8s | ~27.4% |
| Weekday Evening Peak | ~48.1s | ~34.2s | ~28.9% |
| Weekday Normal | ~28.5s | ~22.1s | ~22.5% |
| Weekend Midday | ~35.2s | ~26.8s | ~23.9% |
| Night Time | ~12.3s | ~10.1s | ~17.9% |

**Average Improvement: ~24-28% reduction in waiting time**

### Key Benefits

✅ **Adaptive to Real-Time Conditions**: Responds to actual traffic density  
✅ **Reduced Waiting Time**: 25-30% improvement during peak hours  
✅ **Fuel Efficiency**: Less idling time = reduced emissions  
✅ **Pedestrian Safety**: Guaranteed crossing within 120 seconds  
✅ **Flexible Rule Base**: Easy to modify for different intersections  

## 🔬 Technical Details

### Fuzzy Logic Implementation

**Input Variables:**
- **Traffic Density**: 0-100% (Low, Medium, High)
- **Day Type**: Weekday or Weekend
- **Time Slot**: Night, Normal, Morning Peak, Evening Peak

**Output Variable:**
- **Green Signal Time**: 10-120 seconds (Very Short, Short, Medium, Long, Very Long)

**Sample Fuzzy Rule:**
```
IF traffic density is HIGH 
AND day is WEEKDAY 
AND time is EVENING_PEAK
THEN green signal time is VERY_LONG
```

Total Rules: **24 fuzzy rules** covering all combinations

### Traffic Simulation

The simulator generates realistic traffic patterns:
- **Weekday Morning Peak (7-10 AM)**: 85% average density
- **Weekday Evening Peak (5-8 PM)**: 90% average density
- **Normal Hours**: 45% average density
- **Night (11 PM - 5 AM)**: 5% average density
- **Random Variation**: ±15% to simulate real-world uncertainty

### Pedestrian Management

- **Maximum Wait Time**: 120 seconds (safety override)
- **Crossing Time**: 20 seconds base + 2 seconds per extra pedestrian
- **Smart Activation**: Prefers low traffic periods but prioritizes safety

## 🎓 Academic Context

This project addresses the problem of traffic congestion in metropolitan cities like Delhi by applying **soft computing techniques**. Traditional mathematical approaches fail with dynamic and uncertain traffic conditions, making fuzzy logic an ideal solution that mimics human decision-making.

### Methodology
1. Traffic conditions simulated using Python
2. Traffic density categorized (Low, Medium, High)
3. Time divided into periods (Peak, Normal, Night)
4. Fuzzy rules applied for decision making
5. Continuous adaptation to changing conditions

## 📈 Future Enhancements

- Integration with real SUMO traffic simulator
- Machine learning to optimize fuzzy rules
- Emergency vehicle priority system
- Multi-intersection coordination
- Real-time camera-based vehicle detection
- Mobile app for traffic updates

## 👨‍💻 Author

**Project**: Smart Traffic Light Control System Using Soft Computing  
**Domain**: Artificial Intelligence, Soft Computing, Traffic Management  
**Technologies**: Python, Fuzzy Logic, NumPy, Scikit-Fuzzy, Matplotlib  

## 📄 License

This project is for educational and research purposes.

---

**Note**: This system demonstrates the effectiveness of soft computing in solving real-world problems where traditional approaches fall short. The fuzzy logic approach provides human-like reasoning capability that adapts to uncertain and dynamic traffic conditions.
