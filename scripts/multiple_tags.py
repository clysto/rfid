import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import iqr

sns.set_theme()


def outliers(data, m=2):
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr_ = iqr(data)
    mask = (data > q1 - m * iqr_) & (data < q3 + m * iqr_)
    return np.argwhere(mask == 0).flatten()


datas_path = [
    "data/20240604191302",
    "data/20240604191910",
    "data/20240604192125",
    "data/20240604192221",
    "data/20240604192407",
    "data/20240604192532",
    "data/20240604192646",
    "data/20240604192807",
    "data/20240604192925",
]

distances = [4, 5, 6, 7, 8, 9, 10, 11, 12]

df = None

for path, distance in zip(datas_path, distances):
    data12 = np.load(f"{path}/1-2.npz")
    data13 = np.load(f"{path}/1-3.npz")
    data23 = np.load(f"{path}/2-3.npz")

    inter_est12 = data12["inter_est"]
    inter_est13 = data13["inter_est"]
    inter_est23 = data23["inter_est"]

    outliers12 = outliers(np.abs(inter_est12))
    outliers13 = outliers(np.abs(inter_est13))
    outliers23 = outliers(np.abs(inter_est23))

    inter_est12_filtered = np.delete(inter_est12, outliers12)
    inter_est13_filtered = np.delete(inter_est13, outliers13)
    inter_est23_filtered = np.delete(inter_est23, outliers23)

    df_tmp = pd.DataFrame(
        {
            "Inter-channel magnitude": np.hstack(
                (
                    np.abs(inter_est12_filtered),
                    np.abs(inter_est13_filtered),
                    np.abs(inter_est23_filtered),
                )
            ),
            "Inter-channel phase": np.hstack(
                (
                    np.angle(inter_est12_filtered),
                    np.angle(inter_est13_filtered),
                    np.angle(inter_est23_filtered),
                )
            ),
            "Channel": ["Tag1-Tag2"] * len(inter_est12_filtered)
            + ["Tag1-Tag3"] * len(inter_est13_filtered)
            + ["Tag2-Tag3"] * len(inter_est23_filtered),
            "Distance": [f"{distance}cm"]
            * (
                len(inter_est12_filtered)
                + len(inter_est13_filtered)
                + len(inter_est23_filtered)
            ),
        }
    )

    df = pd.concat([df, df_tmp])

plt.figure()
sns.boxplot(
    x="Distance",
    y="Inter-channel magnitude",
    hue="Channel",
    data=df,
)
plt.show(block=False)

plt.figure()
sns.boxplot(
    x="Distance",
    y="Inter-channel phase",
    hue="Channel",
    data=df,
)
plt.show()
