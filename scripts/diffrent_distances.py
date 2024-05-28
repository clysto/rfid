# %%
import numpy as np
from utils import extract_rn16_frames
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from pathlib import Path
from scipy.stats import iqr

from extract_inter_channel import process_one_frame

sns.set_theme(font_scale=1.4)

files = []

for i in range(8, 13):
    files.append(Path(__file__).parent.parent / f"data/2024-05-27/{i}cm.cf32")

# %%
h_all = []

for file in files:
    sig = np.fromfile(file, dtype=np.complex64)
    rn16_frames, rn16_frames_dc = extract_rn16_frames(
        sig, n_max_gap=440, n_t1=470, n_rn16=1250
    )
    h = []
    for i in tqdm(range(len(rn16_frames))):
        frame = rn16_frames[i]
        dc = rn16_frames_dc[i]
        inter_channel = process_one_frame(frame, dc)
        h.append(inter_channel)
    h_all.append(h)

# %%


def remove_outliers(data, m=2):
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr_ = iqr(data)
    mask = (data > q1 - m * iqr_) & (data < q3 + m * iqr_)
    return data[mask]


h_all_filtered = [remove_outliers(np.abs(h)) for h in h_all]

plt.figure(figsize=(5.5, 3.6))
plt.xlabel("Tag distance")
plt.ylabel("Inter-channel amplitude")
for i, h in enumerate(h_all_filtered):
    sns.boxplot(x=[i] * len(h), y=h, showfliers=True)
plt.xticks(range(5), ["8cm", "9cm", "10cm", "11cm", "12cm"])
# plt.savefig("/Users/maoyachen/Documents/typst/RFID形变感知/figs/inter_channel_amplitude_vs_distance2.svg", bbox_inches="tight")
plt.show()

plt.figure(figsize=(5.5, 3.6))
plt.xlabel("Inter-channel amplitude")
for h in h_all_filtered:
    sns.kdeplot(h)
plt.legend(["8cm", "9cm", "10cm", "11cm", "12cm"])
# plt.savefig("/Users/maoyachen/Documents/typst/RFID形变感知/figs/inter_channel_amplitude_distribution2.svg", bbox_inches="tight")
plt.show()
