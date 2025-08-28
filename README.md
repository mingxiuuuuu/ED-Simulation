# Emergency Department (ED) Simulation Model

This project implements a **discrete-event simulation** of a hospital Emergency Department (ED) using [SimPy](https://simpy.readthedocs.io/)  with intelligent overflow routing and strategic capacity planning analysis.

It models two patient streams with overflow:
- **Fast Track**: low-acuity patients, always discharged.
- **Main ED**: all other patients, with probabilities of needing labs and admission. Admitted patients "board" (hold their ED bed) until ward transfer.
- **Overflow**: Fast Track patients automatically routed to Main ED when queues exceed overflow threshold

The simulation provides **both operational insights and strategic decision support** for capacity planning with 95% confidence levels.

---

## Project Structure
```
ED Simulation/
├── ed_sim/                          # Core simulation package
│   ├── __init__.py                  # Package initialization
│   ├── params.py                    # Simulation parameters
│   ├── entities.py                  # Patient & Stats dataclasses
│   ├── samplers.py                  # Random distribution samplers
│   ├── model.py                     # EDModel (SimPy engine)
│   ├── reports.py                   # Reporting with strategic KPIs
│   ├── scenarios.py                 # Strategic scenario runners
│   └── utils.py                     # Utility functions
├── Tasks/                           # Project documentation
│   ├── Task1.md                     # Task 1 write up
│   ├── Task 2.md                    # Task 2 write up
│   └── task3_writeup.md             # Task 3 write up
├── images/                         
│   └── task2_flowchart.png          # Process flow diagram
├── main.py                          # Comprehensive analysis script
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── .gitignore                       # Git ignore rules
└── results/                         # Generated output files
    ├── strategic_analysis.csv       # Complete scenario results
    ├── roi_analysis.csv             # ROI comparison data
    ├── ed_strategic_dashboard.png   # Performance dashboard (PNG)
    └── ed_strategic_dashboard.pdf   # Performance dashboard (PDF)
```

---

## Installation

### Requirements
- **Python 3.11** (Required for optimal compatibility)
- ⚠️ **Important**: Use Python 3.11 to avoid dependency issues with newer versions (3.12+)

Clone the repo and install dependencies:

```bash
git clone https://github.com/mingxiuuuuu/ED-Simulation.git
cd ED-Simulation
pip install -r requirements.txt
```
---

## Running the Simulation

```bash
python main.py
```

The simulation will run a comprehensive analysis including:
1. **Strategic Scenario Analysis** - Multiple capacity configurations
2. **ROI Analysis** - Resource allocation optimization
3. **Statistical Validation** - 95% confidence intervals
4. **Performance Dashboard** - Visual analytics (PNG & PDF)

---

## Output Files

After running the simulation, the following files are generated:

- **`results/strategic_analysis.csv`** - Complete results for all scenarios with KPIs
- **`results/roi_analysis.csv`** - ROI comparison data for resource prioritization
- **`results/ed_strategic_dashboard.png`** - Performance dashboard (high-resolution PNG)
- **`results/ed_strategic_dashboard.pdf`** - Performance dashboard (PDF for presentations)

---

## Customization
- **Custom Configuration**
The configuration file `params.py` contains all simulation parameters. 

- **Custom Scenarios** (in `scenarios.py`)
Add new experiments by modifying resource configurations and demand parameters.

---
