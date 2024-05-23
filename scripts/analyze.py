import numpy as np
import matplotlib.pyplot as plt
from lib.dpc import DPC

# default 20pt
plt.rcParams["font.size"] = 16


sig = np.fromfile("data/frame.cf32", dtype=np.complex64)

dpc = DPC(n_clusters=4)

labels = dpc.fit(sig)
rhos = dpc.rhos_

plt.figure(figsize=(4, 4))
plt.gca().set_aspect("equal", adjustable="box")
plt.scatter(sig.real, sig.imag)
plt.xlabel("In-phase")
plt.ylabel("Quadrature")
plt.tight_layout()
# plt.savefig("/Users/maoyachen/Documents/typst/RFID形变感知/figs/IQ.svg")
plt.show(block=False)

idx = np.argsort(rhos)
plt.figure(figsize=(4, 4))
plt.gca().set_aspect("equal", adjustable="box")
plt.scatter(sig[idx].real, sig[idx].imag, c=rhos[idx], cmap="Oranges")
plt.xlabel("In-phase")
plt.ylabel("Quadrature")
plt.tight_layout()
# plt.savefig("/Users/maoyachen/Documents/typst/RFID形变感知/figs/sample_density.svg")
plt.show(block=False)

index_centers = dpc.index_centers_

gray_samples = np.arange(len(sig))
gray_samples = np.delete(gray_samples, index_centers)

plt.figure(figsize=(6, 4))
plt.scatter(
    dpc.rhos_[gray_samples],
    dpc.deltas_[gray_samples],
    color="gray",
)
plt.scatter(dpc.rhos_[index_centers], dpc.deltas_[index_centers], c="red")
plt.xlabel("$\\rho$")
plt.ylabel("$\\delta$")
plt.tight_layout()
# plt.savefig("/Users/maoyachen/Documents/typst/RFID形变感知/figs/dpc_decision.svg", bbox_inches='tight')
plt.show(block=False)


plt.figure(figsize=(4, 4))
plt.gca().set_aspect("equal", adjustable="box")
for i in range(4):
    plt.scatter(
        sig[dpc.labels_ == i].real, sig[dpc.labels_ == i].imag, alpha=0.2
    )
plt.xlabel("In-phase")
plt.ylabel("Quadrature")
plt.tight_layout()
# plt.savefig("/Users/maoyachen/Documents/typst/RFID形变感知/figs/dpc_result_error.svg", bbox_inches='tight')
plt.show()