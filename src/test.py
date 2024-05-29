import numpy as np
import matplotlib.pyplot as plt
from extract_inter_channel import extract_rn16_frames, process_one_frame

sig_file = "../data/rx.cf32"
sig = np.fromfile(sig_file, dtype=np.complex64)
frame = sig[10859:12009]

# labels = np.array(labels)
# print(len(frame))
# print(len(labels))

plt.figure()
plt.plot(frame.real)
plt.plot(frame.imag)
plt.show()

# plt.figure()
# plt.scatter(frame[labels == -1].real, frame[labels == -1].imag, color="gray")
# plt.scatter(frame[labels != -1].real, frame[labels != -1].imag, c=labels[labels != -1])
# plt.show()
