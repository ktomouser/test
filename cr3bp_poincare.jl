#!/usr/bin/env julia

"""
Circular Restricted Three Body Problem (CR3BP) - Planar Case
with Poincare Surface of Section Visualization

This code implements the planar (2D) CR3BP using traditional dimensionless
equations of motion and generates Poincare surfaces of sections based on 
the Jacobi constant.
"""

using DifferentialEquations
using CairoMakie
using LinearAlgebra

# Mass parameter (Earth-Moon system as example: μ ≈ 0.012150)
# For Sun-Jupiter: μ ≈ 0.000954
const μ = 0.012150

"""
    cr3bp_eom!(du, u, p, t)

Equations of motion for the planar circular restricted three body problem.
State vector u = [x, y, vx, vy]
where (x, y) are positions and (vx, vy) are velocities in the rotating frame.
"""
function cr3bp_eom!(du, u, p, t)
    x, y, vx, vy = u
    
    # Distances to primaries
    r1 = sqrt((x + μ)^2 + y^2)
    r2 = sqrt((x - 1 + μ)^2 + y^2)
    
    # Acceleration components
    du[1] = vx
    du[2] = vy
    du[3] = 2*vy + x - (1 - μ)*(x + μ)/r1^3 - μ*(x - 1 + μ)/r2^3
    du[4] = -2*vx + y - (1 - μ)*y/r1^3 - μ*y/r2^3
end

"""
    jacobi_constant(x, y, vx, vy, μ)

Calculate the Jacobi constant (integral of motion) for the CR3BP.
C = 2*U(x,y) - v²
where U is the effective potential.
"""
function jacobi_constant(x, y, vx, vy, μ)
    r1 = sqrt((x + μ)^2 + y^2)
    r2 = sqrt((x - 1 + μ)^2 + y^2)
    
    # Effective potential
    U = 0.5*(x^2 + y^2) + (1 - μ)/r1 + μ/r2
    
    # Velocity squared
    v_squared = vx^2 + vy^2
    
    return 2*U - v_squared
end

"""
    calculate_vy_from_jacobi(x, y, vx, C, μ)

Calculate vy given x, y, vx, and the Jacobi constant C.
Returns the velocity component that satisfies the energy constraint.
"""
function calculate_vy_from_jacobi(x, y, vx, C, μ)
    r1 = sqrt((x + μ)^2 + y^2)
    r2 = sqrt((x - 1 + μ)^2 + y^2)
    
    U = 0.5*(x^2 + y^2) + (1 - μ)/r1 + μ/r2
    
    # From C = 2*U - (vx² + vy²), solve for vy²
    vy_squared = 2*U - C - vx^2
    
    if vy_squared < 0
        return nothing  # No real solution
    end
    
    return sqrt(vy_squared)
end

"""
    poincare_condition(u, t, integrator)

Condition for Poincare surface of section: crossing y = 0 plane.
"""
function poincare_condition(u, t, integrator)
    return u[2]  # y-coordinate
end

"""
    poincare_affect!(integrator)

Record Poincare section points when crossing y = 0 with vy > 0.
"""
function poincare_affect!(integrator)
    # Only record when crossing upward (vy > 0)
    if integrator.u[4] > 0
        push!(integrator.p, (integrator.u[1], integrator.u[3]))  # (x, vx)
    end
end

"""
    compute_poincare_section(x0, y0, vx0, C, t_max, μ)

Compute Poincare surface of section for given initial conditions.
Returns array of (x, vx) points at y = 0 crossings.
"""
function compute_poincare_section(x0, y0, vx0, C, t_max, μ)
    # Calculate vy0 from Jacobi constant
    vy0 = calculate_vy_from_jacobi(x0, y0, vx0, C, μ)
    
    if isnothing(vy0)
        return []
    end
    
    # Initial state
    u0 = [x0, y0, vx0, vy0]
    
    # Storage for Poincare points
    poincare_points = Tuple{Float64, Float64}[]
    
    # Setup continuous callback for y = 0 crossings
    cb = ContinuousCallback(poincare_condition, poincare_affect!)
    
    # Time span
    tspan = (0.0, t_max)
    
    # Solve ODE
    prob = ODEProblem(cr3bp_eom!, u0, tspan, poincare_points)
    sol = solve(prob, Vern9(), callback=cb, abstol=1e-12, reltol=1e-12)
    
    return poincare_points
end

"""
    generate_poincare_map(C, x_range, vx_range, n_x, n_vx, t_max, μ)

Generate a full Poincare map for a given Jacobi constant C.
Tests multiple initial conditions on a grid.
"""
function generate_poincare_map(C, x_range, vx_range, n_x, n_vx, t_max, μ)
    all_points = Tuple{Float64, Float64}[]
    
    x_values = range(x_range[1], x_range[2], length=n_x)
    vx_values = range(vx_range[1], vx_range[2], length=n_vx)
    
    for x0 in x_values
        for vx0 in vx_values
            points = compute_poincare_section(x0, 0.0, vx0, C, t_max, μ)
            append!(all_points, points)
        end
    end
    
    return all_points
end

"""
    plot_poincare_sections(jacobi_constants; μ=0.012150)

Create Poincare surface of section plots for multiple Jacobi constants.
"""
function plot_poincare_sections(jacobi_constants; μ=0.012150, t_max=50.0)
    fig = Figure(size=(1200, 800))
    
    n_plots = length(jacobi_constants)
    n_cols = min(3, n_plots)
    n_rows = ceil(Int, n_plots / n_cols)
    
    for (idx, C) in enumerate(jacobi_constants)
        row = div(idx - 1, n_cols) + 1
        col = mod(idx - 1, n_cols) + 1
        
        ax = Axis(fig[row, col],
                  xlabel="x",
                  ylabel="vx",
                  title="C = $(round(C, digits=4))")
        
        # Generate initial conditions
        # Sample x from reasonable range around Lagrange points
        x_range = (0.7, 1.1)
        vx_range = (-0.5, 0.5)
        n_x = 8
        n_vx = 8
        
        println("Computing Poincare section for C = $C...")
        
        points = generate_poincare_map(C, x_range, vx_range, n_x, n_vx, t_max, μ)
        
        if !isempty(points)
            x_coords = [p[1] for p in points]
            vx_coords = [p[2] for p in points]
            scatter!(ax, x_coords, vx_coords, markersize=2, color=(:blue, 0.5))
            println("  Generated $(length(points)) points")
        else
            println("  No valid points generated")
        end
    end
    
    Label(fig[0, :], "Poincare Surfaces of Section for Planar CR3BP", 
          fontsize=20, font=:bold)
    
    return fig
end

"""
    main()

Main function to demonstrate the CR3BP Poincare sections.
"""
function main()
    println("="^60)
    println("Circular Restricted Three Body Problem")
    println("Poincare Surface of Section Analysis")
    println("="^60)
    println()
    println("Mass parameter μ = $μ (Earth-Moon system)")
    println()
    
    # Test with a single trajectory first
    println("Testing single trajectory...")
    x0, y0, vx0 = 0.8, 0.0, 0.0
    # Use vy0 = 0.3 as a test value for a periodic orbit near L4/L5
    test_vy0 = 0.3
    C = jacobi_constant(x0, y0, vx0, test_vy0, μ)
    println("Initial condition: x0=$x0, y0=$y0, vx0=$vx0")
    println("Jacobi constant C = $C")
    
    vy0 = calculate_vy_from_jacobi(x0, y0, vx0, C, μ)
    if !isnothing(vy0)
        println("Calculated vy0 = $vy0")
        println()
        
        # Compute trajectory
        u0 = [x0, y0, vx0, vy0]
        tspan = (0.0, 20.0)
        prob = ODEProblem(cr3bp_eom!, u0, tspan)
        sol = solve(prob, Vern9(), abstol=1e-12, reltol=1e-12)
        
        # Verify Jacobi constant is conserved
        C_final = jacobi_constant(sol.u[end]..., μ)
        println("Final Jacobi constant: C = $C_final")
        println("Conservation error: $(abs(C - C_final))")
        println()
    end
    
    # Generate Poincare sections for different energy levels
    println("Generating Poincare surfaces of section...")
    println()
    
    # Different Jacobi constants to explore
    # Lower C means higher energy
    jacobi_constants = [3.0, 3.1, 3.2, 3.3]
    
    fig = plot_poincare_sections(jacobi_constants, μ=μ, t_max=100.0)
    
    # Save figure
    output_file = "poincare_sections.png"
    save(output_file, fig)
    println()
    println("="^60)
    println("Poincare sections saved to: $output_file")
    println("="^60)
    
    return fig
end

# Run the main function if script is executed directly
if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
