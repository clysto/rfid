from lib.dpc import DPC
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

sig = np.fromfile(Path(__file__).parent / "frame1.cf32", dtype=np.complex64)
dpc = DPC(n_clusters=4, filter_halo=True)
dpc.fit(sig)

plt.figure()
plt.xlabel("$\\rho$")
plt.ylabel("$\\delta$")
plt.grid(True)
plt.plot(dpc.rhos_, dpc.deltas_, "o", alpha=0.5)
plt.show(block=False)


plt.figure()
plt.grid()
plt.xlabel("In-phase")
plt.ylabel("Quadrature")
plt.scatter(
    sig[dpc.labels_ == -1].real, sig[dpc.labels_ == -1].imag, color="gray", alpha=0.2
)
for i in range(4):
    plt.scatter(sig[dpc.labels_ == i].real, sig[dpc.labels_ == i].imag, alpha=0.2)
plt.show()
