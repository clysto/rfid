import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from utils import extract_rn16_frames, frame_sync

from extract_inter_channel_cxx import extract_inter_channel

sig = np.fromfile("data/rx.cf32", dtype=np.complex64)

rn16_frames, rn16_frames_dc = extract_rn16_frames(
    sig, n_max_gap=440, n_t1=470, n_rn16=1250
)

s_int_all = []

for frame, dc in zip(rn16_frames, rn16_frames_dc):
    dc_est = np.mean(rn16_frames_dc)
    frame_start, h_est = frame_sync(frame - np.mean(dc))
    h_est += np.mean(dc)
    frame = frame[frame_start : frame_start + 1150]
    assert len(frame) == 1150
    s_int = extract_inter_channel(frame, dc, dc_est, h_est)
    s_int_all.append(s_int)


plt.figure()
sns.kdeplot(np.abs(s_int_all))
plt.xlabel("Inter-channel amplitude")
plt.show()
