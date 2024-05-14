import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from scipy import signal


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
    """
    idx = np.argwhere(np.abs(sig) < 0.05).reshape(-1)
    idx = idx[np.argwhere(np.diff(idx) > n_max_gap).reshape(-1)]
    bs_start = idx + n_t1
    bs_end = bs_start + n_rn16
    frames = []
    for start, end in zip(bs_start, bs_end):
        if start >= len(sig) or end >= len(sig):
            continue
        dc_est = np.mean(sig[start - 200 : start])
        pkt = sig[start:end] - dc_est
        frames.append(pkt)
    frames = np.array(frames)
    return frames


def frame_sync(frame):
    preamble = np.repeat([1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1], 25) + 0j
    corr = np.abs(signal.correlate(frame[: len(preamble) + 100], preamble, "same"))
    frame_start = np.argmax(corr) - 6 * 25
    frame = frame[frame_start:]
    h_est = np.mean(frame[np.argwhere(preamble == 1)])
    return frame, h_est


def cluster_frame(frame: np.ndarray, eps=0.02):
    dbscan = DBSCAN(eps, min_samples=50)
    centers = np.full(4, np.nan, dtype=complex)
    clusters = dbscan.fit_predict(np.array([frame.real, frame.imag]).T)
    if np.max(clusters) != 3:
        raise Exception("Expected 4 clusters, found {}".format(np.max(clusters) + 1))
    for i in range(4):
        centers[i] = np.mean(frame[clusters == i])
    return clusters, centers


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
    sig = np.fromfile("rx.cf32", dtype=np.complex64)
    rn16_frames = extract_rn16_frames(sig, n_max_gap=440, n_t1=470, n_rn16=1250)

    for frame in rn16_frames:
        frame, h_est = frame_sync(frame)
        frame /= h_est
        try:
            clusters, centers = cluster_frame(frame)
        except Exception as e:
            print(e)
            continue
        centers_sorted = centers[np.argsort(np.abs(centers))]
        symbols = frame[clusters >= 0]
        inter_channel = calc_inter_channel(centers)
        center_expected = centers_sorted[3] + inter_channel
        # print(np.abs(inter_channel * np.abs(h_est)))
        print(np.angle(inter_channel))

    plt.figure()
    plt.xlim(-1.2, 1.2)
    plt.ylim(-1.2, 1.2)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.scatter(symbols.real, symbols.imag, color="gray")
    plt.scatter(centers.real, centers.imag, c="red")
    plt.scatter(center_expected.real, center_expected.imag, c="blue")
    plt.show()
