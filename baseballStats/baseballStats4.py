# Import libraries
import pandas as pd
import numpy as np
from sklearn import linear_model
from scipy import stats
import matplotlib.pyplot as plt

# Method to compute value function and decision for the "to steal or not to steal" problem
# p is probability
def run_dynamic_program(R, p, p_steal):

    # Value function
    V = np.zeros([4, 3])

    # Decision to steal vs. no-steal
    steal_decision = np.zeros([3, 1])

    for out in range(2, -1, -1):
        # Runner on 2nd
        V[out, 2] = p[0] * R[out+1, 2] + p[1] * (R[out, 1] + 1) + p[2] * (R[out, 2] + 1) + p[3] * (R[out, 3] + 1) + p[4]*(R[out, 0] + 2)

        # Bases empty
        V[out, 0] = p[0] * R[out+1, 0] + p[1] * R[out, 1] + p[2] * R[out, 2] + p[3] * R[out, 3] + p[4] * (R[out, 0] + 1)

        # Runner on 1st
        value_steal = p_steal * V[out, 2] + (1 - p_steal) * V[out+1, 0]
        value_no_steal = p[0] * R[out+1, 1] + p[1] * R[out, 3] + p[2] * R[out, 6] + p[3] * (R[out, 4] + 1) + p[4] * (R[out, 0] + 2)
        V[out, 1] = np.max([value_steal, value_no_steal])

        # Optimal decision
        steal_decision[out] = (value_steal > value_no_steal)
    return V, steal_decision

# Run expectancy matrix
# taken from http://www.tangotiger.net/re24.html
R = np.matrix([[0.481, 0.254, 0.098, 0],
               [0.859, 0.509, 0.224, 0],
               [1.100, 0.664, 0.319, 0],
               [1.437, 0.884, 0.429, 0],
               [1.350, 0.950, 0.353, 0],
               [1.784, 1.130, 0.478, 0],
               [1.964, 1.376, 0.580, 0],
               [2.292, 1.541, 0.752, 0]])
R = R.transpose()

# Batter stats (Mike Trout, 2016 season)
p_out = 0.559
p_single_or_walk = 0.343
p_double = 0.047
p_triple = 0.007
p_home_run = 0.043

p_batter = np.array([p_out, p_single_or_walk, p_double, p_triple, p_home_run])

# Probability of stealing
p_steal = 0.7

# Solve dynamic program
V, steal_decision = run_dynamic_program(R, p_batter, p_steal)

# Display steal decision
print("When the probability of a successful steal is ", p_steal, ":")
for out in range(0, 3):
    if (steal_decision[out]):
        print("With ", out, "out(s), optimal decision is to steal")
    else:
        print("With ", out, "out(s), optimal decision is to not steal")

# Loop over probability of successful steal
opt_decision= np.empty([0, 3])
for p_steal in np.arange(0, 1, 0.05):
    # Solve dynamic program
    V, steal_decision = run_dynamic_program(R, p_batter, p_steal)
    opt_decision =  np.append(opt_decision, steal_decision.reshape([1, 3]), axis=0)

# Plot and visualize
plt.plot(np.arange(0, 1, 0.05), opt_decision[:, 0], 'b', label="0 outs")
plt.plot(np.arange(0, 1, 0.05), opt_decision[:, 1], 'r', label="1 out")
plt.plot(np.arange(0, 1, 0.05), opt_decision[:, 2], 'g', label="2 outs")
plt.xlabel("Probability of successful steal")
plt.ylabel("Optimal decision (1 = steal)")
plt.legend(loc="upper left")
plt.show()