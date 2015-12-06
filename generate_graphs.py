import numpy as np
import matplotlib.pyplot as plt
comp = np.loadtxt("parallel_vs_serial.csv", delimiter=",")
print comp.shape
print comp

plt.figure()
plt.title("Comparison of Parallel and Serial Algorithms")
plt.plot(comp[:, 0], comp[:, 3], label="Parallel")
plt.plot(comp[:, 0], comp[:, 4], label="Serial")
plt.legend()
#plt.show()

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
plt.xlim([0, 200])
plt.show()

