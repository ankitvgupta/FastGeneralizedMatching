import numpy as np
import matplotlib.pyplot as plt
comp = np.loadtxt("parallel_vs_serial.csv", delimiter=",")
print comp.shape
print comp

plt.figure()
plt.title("Comparison of Parallel and Serial Algorithms")
plt.plot(comp[:, 0], comp[:, 3], label="Parallel", c='red')
plt.plot(comp[:, 0], comp[:, 4], label="Serial", c='blue')
plt.xlabel("Number of doctors (size of problem)")
plt.ylabel("Time (sec)")
plt.legend()

# To zoom in, uncomment these two lines
#############################
plt.xlim([-5, 50000])
plt.ylim([-5, 2500])
#######################

import csv

rows = []
with open("alg1_vs_alg2.txt") as f:
    reader = csv.reader(f, delimiter=",")
    for row in reader:
        rows.append(map(int, row))
print rows

plt.figure()
plt.title("Comparison of Algorithm 1 and Algorithm 2")
plt.plot(range(len(rows[0])), rows[0], label="Algorithm 1")
plt.plot(range(len(rows[1])), rows[1], label="Algorithm 2")
plt.xlabel("Number of iterations")
plt.ylabel("Number of doctors whose match changed")
plt.legend()
plt.xlim([0, 150])
#plt.show()


knapsack_rows = []
with open("knapsack_runs.txt") as f:
    reader = csv.reader(f, delimiter=",")
    for row in reader:
        knapsack_rows.append(map(int, row))
print knapsack_rows


plt.figure()
plt.title("Comparison of Knapsack Runs")
for i, row in enumerate(knapsack_rows):
    plt.plot(range(len(row)), row, label="Run "+str(i))
plt.legend()
plt.xlabel("Number of iterations")
plt.ylabel("Number of changes")
plt.show()

