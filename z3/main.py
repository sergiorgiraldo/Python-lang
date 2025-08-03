from z3 import *

def solve_quadratic_z3(a, b, c):
    # Create a real variable
    x = Real("x")
    
    # Create the solver
    s = Solver()
    
    # Add the quadratic equation constraint
    s.add(a * x * x + b * x + c == 0)
    
    # List to store solutions
    solutions = []
    
    # Check solutions while they"re available
    while s.check() == sat:
        model = s.model()
        sol = model[x]
        solutions.append(sol)
        
        # Add constraint to exclude this solution
        s.add(x != sol)
    
    return solutions

def solve_cubic_z3(a, b, c, d):
    # Create a real variable
    x = Real("x")
    
    # Create the solver
    s = Solver()
    
    # Add the quadratic equation constraint
    s.add(a * x * x * x + b * x * x + c * x + d == 0)
    
    # List to store solutions
    solutions = []
    
    # Check solutions while they"re available
    while s.check() == sat:
        model = s.model()
        sol = model[x]
        solutions.append(sol)
        
        # Add constraint to exclude this solution
        s.add(x != sol)
    
    return solutions

def main():
    a, b, c, d = 1, -5, 6, 10
    
    z3_solutions = solve_quadratic_z3(a, b, c)
    print("Z3 for x^2 - 5x + 6 = 0")
    print(f"Solutions: {z3_solutions}")

    z3_solutions = solve_cubic_z3(a, b, c, d)
    print("Z3 for x^3 - 5x^2 + 6x + 10 = 0")
    print(f"Solutions: {z3_solutions}")

if __name__ == "__main__":
    main()