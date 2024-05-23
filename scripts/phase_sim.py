import numpy as np
import matplotlib.pyplot as plt

x = np.arange(0, 10, 0.001)
dis = np.exp(-(x**2))

plt.figure()
plt.plot(x, dis)
plt.show()
