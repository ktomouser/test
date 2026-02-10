# Circular Restricted Three Body Problem (CR3BP) - Poincare Sections

This repository contains a Julia implementation of the planar (2D) Circular Restricted Three Body Problem (CR3BP) with Poincare surface of section visualization.

## Overview

The CR3BP models the motion of a massless particle under the gravitational influence of two massive bodies (primaries) that orbit their common center of mass in circular orbits. This implementation uses traditional dimensionless equations of motion and generates Poincare surfaces of section based on the Jacobi constant (energy level).

## Features

- **Dimensionless Equations of Motion**: Implements the standard CR3BP equations in the rotating frame
- **Jacobi Constant**: Calculates and conserves the Jacobi constant (integral of motion)
- **Initial Condition Generation**: Automatically calculates initial velocities from energy constraints
- **Numerical Integration**: Uses high-precision ODE solvers (Vern9) for accurate trajectory integration
- **Poincare Sections**: Generates Poincare surfaces of section at y=0 plane crossings
- **Visualization**: Creates publication-quality plots using CairoMakie

## Mathematical Background

### Equations of Motion

In the rotating frame, the dimensionless equations of motion are:

```
ẍ = 2ẏ + x - (1-μ)(x+μ)/r₁³ - μ(x-1+μ)/r₂³
ÿ = -2ẋ + y - (1-μ)y/r₁³ - μy/r₂³
```

where:
- `μ` is the mass parameter (ratio of smaller mass to total mass)
- `r₁ = √((x+μ)² + y²)` is the distance to the first primary
- `r₂ = √((x-1+μ)² + y²)` is the distance to the second primary

### Jacobi Constant

The Jacobi constant is an integral of motion:

```
C = 2U(x,y) - v²
```

where `U(x,y)` is the effective potential and `v²` is the velocity squared.

### Poincare Surface of Section

The Poincare section is constructed by recording the state (x, vx) whenever the trajectory crosses the y=0 plane with vy>0. This technique reduces the 4D phase space to a 2D map, revealing the structure of periodic and quasi-periodic orbits.

## Installation

### Prerequisites

- Julia 1.6 or higher
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ktomouser/test.git
cd test
```

2. Install dependencies:
```bash
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

This will install:
- DifferentialEquations.jl (for numerical integration)
- CairoMakie.jl (for visualization)
- LinearAlgebra (standard library)

## Usage

Run the main script:

```bash
julia --project=. cr3bp_poincare.jl
```

This will:
1. Test a single trajectory to verify Jacobi constant conservation
2. Generate Poincare sections for four different energy levels (C = 3.0, 3.1, 3.2, 3.3)
3. Save the visualization to `poincare_sections.png`

## Output

The script generates a PNG file showing four Poincare sections:

- **C = 3.0**: Lower energy, more confined orbits
- **C = 3.1**: Intermediate energy level
- **C = 3.2**: Higher energy, showing more complex structures
- **C = 3.3**: Shows periodic and quasi-periodic orbits near Lagrange points

Each plot shows the position (x) vs. velocity (vx) at y=0 crossings, revealing the phase space structure.

## Customization

You can modify the following parameters in `cr3bp_poincare.jl`:

```julia
# Mass parameter (default: Earth-Moon system)
const μ = 0.012150

# Jacobi constants to explore
jacobi_constants = [3.0, 3.1, 3.2, 3.3]

# Integration time
t_max = 100.0

# Initial condition grid
x_range = (0.7, 1.1)
vx_range = (-0.5, 0.5)
n_x = 8
n_vx = 8
```

## Example Systems

Common mass parameters:
- **Earth-Moon**: μ ≈ 0.012150
- **Sun-Jupiter**: μ ≈ 0.000954
- **Sun-Earth**: μ ≈ 0.000003

## References

1. Szebehely, V. (1967). Theory of Orbits: The Restricted Problem of Three Bodies. Academic Press.
2. Koon, W. S., Lo, M. W., Marsden, J. E., & Ross, S. D. (2011). Dynamical Systems, the Three-Body Problem and Space Mission Design.

## License

This code is provided as-is for educational and research purposes.

## Author

Generated for the CR3BP Poincare Section visualization project.
