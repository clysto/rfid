# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from utils import arg_outliers

sns.set_theme()
sns.set_context("notebook")

pt = 1 / 72

# %%
for i in range(1, 4):
    data12 = np.load(f"../data/2024-06-04/1-2#{i}.npz")
    data32 = np.load(f"../data/2024-06-04/3-2#{i}.npz")

    frames12 = data12["frames"]
    frames32 = data32["frames"]

    frames_dc12 = data12["frames_dc"]
    frames_dc32 = data32["frames_dc"]

    inter_est12 = data12["inter_est"]
    inter_est32 = data32["inter_est"]

    outliers12 = arg_outliers(np.abs(inter_est12))
    outliers32 = arg_outliers(np.abs(inter_est32))

    dc_time = np.arange(0, frames_dc12.shape[1])
    rn16_time = np.arange(0, frames12.shape[1]) + len(dc_time)

    plt.figure(figsize=(200 * pt, 110 * pt))
    plt.xlabel("Frame index")
    plt.ylabel("Magnitude")
    plt.plot(np.abs(inter_est12), label="Tag1-Tag2")
    plt.plot(np.abs(inter_est32), label="Tag3-Tag2")
    plt.plot(outliers12, np.abs(inter_est12[outliers12]), "o", color="r")
    plt.plot(outliers32, np.abs(inter_est32[outliers32]), "o", color="r")
    plt.legend()
    plt.savefig(f"../data/2tags-time-{i}.svg", bbox_inches="tight")
    plt.show()

    plt.figure(figsize=(200 * pt, 110 * pt))
    sns.kdeplot(
        np.delete(np.abs(inter_est12), outliers12), label="Tag1-Tag2", fill=True
    )
    sns.kdeplot(
        np.delete(np.abs(inter_est32), outliers32), label="Tag3-Tag2", fill=True
    )
    plt.xlabel("Inter-channel magnitude")
    plt.legend()
    plt.savefig(f"../data/2tags-pdf-{i}.svg", bbox_inches="tight")
    plt.show(block=False)

# %%
# datas_path = [
#     "../data/20240612235057",
#     "../data/20240612235255",
#     "../data/20240612235433",
#     "../data/20240612235529",
#     "../data/20240612235636",
# ]

datas_path = [
    "../data/20240613000439",
    "../data/20240613000934",
    "../data/20240613001046",
    "../data/20240613001158",
    "../data/20240613001241",
]

distances = [7, 8, 9, 10, 11]

df = None

for path, distance in zip(datas_path, distances):
    data12 = np.load(f"{path}/1-2.npz")
    data13 = np.load(f"{path}/1-3.npz")
    # data23 = np.load(f"{path}/2-3.npz")

    inter_est12 = data12["inter_est"][:100]
    inter_est13 = data13["inter_est"][:100]
    # inter_est23 = data23["inter_est"]

    outliers12 = arg_outliers(np.abs(inter_est12))
    outliers13 = arg_outliers(np.abs(inter_est13))
    # outliers23 = arg_outliers(np.abs(inter_est23))

    inter_est12_filtered = np.delete(inter_est12, outliers12)
    inter_est13_filtered = np.delete(inter_est13, outliers13)
    # inter_est23_filtered = np.delete(inter_est23, outliers23)

    df_tmp = pd.DataFrame(
        {
            "Inter-channel magnitude": np.hstack(
                (
                    np.abs(inter_est12_filtered),
                    np.abs(inter_est13_filtered),
                    # np.abs(inter_est23_filtered),
                )
            ),
            "Inter-channel phase": np.hstack(
                (
                    np.angle(inter_est12_filtered),
                    np.angle(inter_est13_filtered),
                    # np.angle(inter_est23_filtered),
                )
            ),
            "Channel": ["Tag1-Tag2"] * len(inter_est12_filtered)
            + ["Tag1-Tag3"] * len(inter_est13_filtered),
            # + ["Tag2-Tag3"] * len(inter_est23_filtered),
            "Distance": [f"{distance}cm"]
            * (
                len(inter_est12_filtered)
                + len(inter_est13_filtered)
                # + len(inter_est23_filtered)
            ),
        }
    )

    df = pd.concat([df, df_tmp])

df

# %%
plt.figure(figsize=(600 * pt, 300 * pt))
sns.boxplot(
    x="Distance",
    y="Inter-channel magnitude",
    hue="Channel",
    data=df,
)
plt.show()
