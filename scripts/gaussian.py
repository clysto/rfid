import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal
import seaborn as sns
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

plt.rcParams["font.size"] = 14

sig = np.fromfile("data/tone.cf32", dtype=np.complex64)[:1000]
mag_var = np.var(np.abs(sig))
phase_var = np.var(np.angle(sig))
mag_mean = np.mean(np.abs(sig))
phase_mean = np.mean(np.angle(sig))
cov = np.array([[phase_var, 0], [0, mag_var]])
rv = multivariate_normal([phase_mean, mag_mean], cov)

plt.subplots(1, 3, figsize=(8, 2))
plt.subplot(1, 3, 1)
plt.xlabel("In-phase")
plt.ylabel("Quadrature")
plt.scatter(np.real(sig), np.imag(sig), marker="x")

plt.subplot(1, 3, 2)
plt.xlabel("Phase")
plt.ylabel("Mag")
plt.scatter(np.angle(sig), np.abs(sig), marker="x")


scale = np.sqrt(phase_var / mag_var)
plt.subplot(1, 3, 3)
plt.xlabel("Phase")
plt.ylabel("Mag (scaled)")
plt.scatter(np.angle(sig), np.abs(sig) * scale, marker="x")

plt.tight_layout()
plt.savefig("tone.svg", bbox_inches="tight")
plt.show()


# fig, ax = plt.subplots(2, 2, figsize=(10, 6))
# plt.subplot(2, 2, 1)
# # plt.gca().set_aspect("equal", adjustable="box")
# plt.scatter(sig.real, sig.imag, marker="x")
# plt.xlabel("In-phase")
# plt.ylabel("Quadrature")

# plt.subplot(2, 2, 2)
# plt.scatter(np.angle(sig), np.abs(sig), marker="x")
# plt.xlabel("Phase")
# plt.ylabel("Magnitude")

# plt.subplot(2, 2, 3)
# sns.kdeplot(x=np.angle(sig), y=np.abs(sig), cmap="Blues", fill=True)
# xlim = plt.gca().get_xlim()
# ylim = plt.gca().get_ylim()
# plt.xlabel("Phase")
# plt.ylabel("Magnitude")


# step = 0.0001
# x, y = np.mgrid[xlim[0] : xlim[1] : step, ylim[0] : ylim[1] : step]
# pos = np.dstack((x, y))


# plt.subplot(2, 2, 4)
# plt.contourf(x, y, rv.pdf(pos), levels=15, cmap="Blues")
# plt.xlabel("Phase")
# plt.ylabel("Magnitude")


# plt.tight_layout()
# plt.show()


# cov = np.cov([np.abs(sig), np.angle(sig)])
# rv = multivariate_normal([mag_mean, phase_mean], cov)
# # rv = multivariate_normal([mag_mean, phase_mean], [[mag_var, 0], [0, phase_var]])

# xlim = (-1, 1)
# ylim = (-1, 1)

# step = 0.0001
# x, y = np.mgrid[xlim[0] : xlim[1] : step, ylim[0] : ylim[1] : step]
# pos = np.zeros(x.shape + (2,))
# pos[:, :, 0] = np.abs(x + 1j * y)
# pos[:, :, 1] = np.angle(x + 1j * y)
# print(pos.shape)

# plt.figure()
# plt.gca().set_aspect("equal", adjustable="box")
# plt.contourf(x, y, rv.pdf(pos), levels=20, cmap="Blues")
# plt.colorbar()
# plt.scatter(sig.real, sig.imag, alpha=0.1)
# plt.xlabel("In-phase")
# plt.ylabel("Quadrature")
# plt.title("Probability Density of the IQ Data")
# plt.show()
