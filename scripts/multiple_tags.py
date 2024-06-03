import numpy as np
import matplotlib.pyplot as plt

frames12 = np.load("data/1-2.npy")
frames32 = np.load("data/3-2.npy")

plt.figure()
plt.plot(frames12[0].real, color="C0")
plt.plot(frames12[0].imag, "--", color="C0")

plt.plot(frames32[0].real, color="C1")
plt.plot(frames32[0].imag, "--", color="C1")
plt.show()
