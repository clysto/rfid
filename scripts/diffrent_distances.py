import numpy as np
from tqdm import tqdm
from utils import extract_rn16_frames
import matplotlib.pyplot as plt
import seaborn as sns

from extract_inter_channel import process_one_frame

files = [
    "data/2024-05-23/50cm-8cm.cf32",
    "data/2024-05-23/50cm-9cm.cf32",
    "data/2024-05-23/50cm-10cm.cf32",
]

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



plt.figure()
for h in h_all:
    plt.plot(h)
plt.show()

plt.figure()
for h in h_all:
    sns.kdeplot(h)
plt.show()
