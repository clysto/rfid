import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import iqr


sns.set_theme()


def outliers(data, m=4):
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr_ = iqr(data)
    mask = (data > q1 - m * iqr_) & (data < q3 + m * iqr_)
    return np.argwhere(mask == 0).flatten()


for i in range(1, 4):
    data12 = np.load(f"data/1-2#{i}.npz")
    data32 = np.load(f"data/3-2#{i}.npz")

    frames12 = data12["frames"]
    frames32 = data32["frames"]

    frames_dc12 = data12["frames_dc"]
    frames_dc32 = data32["frames_dc"]

    inter_est12 = data12["inter_est"]
    inter_est32 = data32["inter_est"]

    outliers12 = outliers(np.abs(inter_est12))
    outliers32 = outliers(np.abs(inter_est32))

    dc_time = np.arange(0, frames_dc12.shape[1])
    rn16_time = np.arange(0, frames12.shape[1]) + len(dc_time)

    # plt.figure()
    # plt.plot(dc_time, frames_dc12[0].real, color="C0", alpha=0.5)
    # plt.plot(dc_time, frames_dc12[0].imag, "--", color="C0", alpha=0.5)

    # plt.plot(dc_time, frames_dc32[0].real, color="C1", alpha=0.5)
    # plt.plot(dc_time, frames_dc32[0].imag, "--", color="C1", alpha=0.5)

    # plt.plot(rn16_time, frames12[0].real, color="C0")
    # plt.plot(rn16_time, frames12[0].imag, "--", color="C0")

    # plt.plot(rn16_time, frames32[0].real, color="C1")
    # plt.plot(rn16_time, frames32[0].imag, "--", color="C1")
    # plt.show(block=False)

    plt.figure()
    plt.ylim(0, 0.02)
    plt.plot(np.abs(inter_est12), label="Tag1-Tag2")
    plt.plot(np.abs(inter_est32), label="Tag3-Tag2")
    plt.plot(outliers12, np.abs(inter_est12[outliers12]), "o", color="r")
    plt.plot(outliers32, np.abs(inter_est32[outliers32]), "o", color="r")
    plt.legend()
    plt.show(block=False)

    plt.figure()
    sns.kdeplot(
        np.delete(np.abs(inter_est12), outliers12), label="Tag1-Tag2", fill=True
    )
    sns.kdeplot(
        np.delete(np.abs(inter_est32), outliers32), label="Tag3-Tag2", fill=True
    )
    plt.legend()
    plt.show(block=False)

plt.show()
