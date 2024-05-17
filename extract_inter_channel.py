import numpy as np
from dpc import DPC
import matplotlib.pyplot as plt
from scipy import signal
import sys


def extract_rn16_frames(sig, n_max_gap, n_t1, n_rn16):
    """
    Extracts RN16 frames from a given signal.

    Parameters:
    - sig (numpy.ndarray): Input signal.
    - n_max_gap (int): Maximum number of low-level continuous samples of the reader command signal.
    - n_t1 (int): Number of samples before the start of each frame.
    - n_rn16 (int): Number of RN16 samples in each frame.

    Returns:
    - frames (numpy.ndarray): Extracted RN16 frames.
    - frames_dc (numpy.ndarray): Estimated DC component of each frame.
    """
    idx = np.argwhere(np.abs(sig) < 0.05).reshape(-1)
    idx = idx[np.argwhere(np.diff(idx) > n_max_gap).reshape(-1)]
    bs_start = idx + n_t1
    bs_end = bs_start + n_rn16
    frames = []
    frames_dc = []
    for start, end in zip(bs_start, bs_end):
        if start >= len(sig) or end >= len(sig):
            continue
        pkt = sig[start:end]
        dc_est = np.mean(sig[start - 200 : start])
        frames.append(pkt)
        frames_dc.append(dc_est)
    frames = np.array(frames)
    frames_dc = np.array(frames_dc)
    return frames, frames_dc


def frame_sync(frame):
    preamble = np.repeat([1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1], 25) + 0j
    corr = np.abs(signal.correlate(frame[: len(preamble) + 100], preamble, "same"))
    frame_start = np.argmax(corr) - 6 * 25
    frame = frame[frame_start:]
    h_est = np.mean(frame[np.argwhere(preamble == 1)])
    return frame, h_est


def cluster_frame(frame: np.ndarray):
    dpc = DPC(n_clusters=4, filter_halo=True)
    labels = dpc.fit_predict(frame)
    centers = np.full(np.max(labels) + 1, np.nan, dtype=complex)
    for i in range(4):
        centers[i] = np.mean(frame[labels == i])
    return labels, centers


def calc_inter_channel(centers):
    centers_sorted = centers[np.argsort(np.abs(centers))]
    inter_channel = (
        centers_sorted[1]
        - centers_sorted[0]
        + centers_sorted[2]
        - centers_sorted[0]
        - centers_sorted[3]
    )
    return inter_channel


if __name__ == "__main__":
    sig_file = sys.argv[1]
    frame_index = sys.argv[2]
    sig = np.fromfile(sig_file, dtype=np.complex64)
    rn16_frames, rn16_frames_dc = extract_rn16_frames(
        sig, n_max_gap=440, n_t1=470, n_rn16=1250
    )

    frame = rn16_frames[int(frame_index)]
    frame -= rn16_frames_dc[int(frame_index)]
    frame, h_est = frame_sync(frame)
    frame /= h_est

    labels, centers = cluster_frame(frame)
    inter_channel = calc_inter_channel(centers)
    centers_sorted = centers[np.argsort(np.abs(centers))]
    center_expected = centers_sorted[3] + inter_channel

    print(np.abs(inter_channel * np.abs(h_est)))
    print(np.angle(inter_channel))

    plt.figure()
    plt.gca().set_aspect("equal", adjustable="box")
    plt.scatter(
        frame[labels == -1].real, frame[labels == -1].imag, color="gray", alpha=0.2
    )
    for i in range(4):
        plt.scatter(frame[labels == i].real, frame[labels == i].imag, alpha=0.2)
    plt.scatter(centers.real, centers.imag, color="blue")
    plt.scatter(center_expected.real, center_expected.imag, color="red")
    plt.show()
