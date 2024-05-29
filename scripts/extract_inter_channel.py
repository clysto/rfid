import sys

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import signal
from scipy.stats import multivariate_normal
from rich.progress import track


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
        frames.append(pkt)
        frames_dc.append(sig[start - 200 : start])
    frames = np.array(frames)
    frames_dc = np.array(frames_dc)
    return frames, frames_dc


def frame_sync(frame):
    preamble = np.repeat([1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1], 25) + 0j
    corr = np.abs(signal.correlate(frame[: len(preamble) + 100], preamble, "same"))
    frame_start = max(0, np.argmax(corr) - 6 * 25)
    h_est = np.mean(frame[frame_start:][np.argwhere(preamble == 1)])
    return frame_start, h_est


def estimate_dc(dists):
    n = np.shape(dists)[0]
    tt = np.reshape(dists, n * n)
    position = int(n * (n - 1) * 0.02)
    dc = np.sort(tt)[position + n]
    return dc


def cluster_frame(frame: np.ndarray, cov: np.ndarray, plot=False):
    N = frame.shape[0]

    frame_mag_phase = np.array([np.abs(frame), np.angle(frame)]).T
    dists = np.abs(frame_mag_phase[:, np.newaxis] - frame_mag_phase)
    scale = cov[0, 0] / cov[1, 1]
    dists = np.sqrt(dists[:, :, 0] ** 2 + dists[:, :, 1] ** 2 * scale)

    # cutoff distance
    dc = estimate_dc(dists)

    rhos = np.sum(np.exp(-((dists / dc) ** 2)), axis=1) - 1
    deltas = np.zeros(N)

    ordrho = np.argsort(-rhos)
    for i, index in enumerate(ordrho):
        if i == 0:
            continue
        index_higher_rho = ordrho[:i]
        deltas[index] = np.min(dists[index, index_higher_rho])
        deltas[ordrho[0]] = np.max(deltas)

    idx1 = np.argsort(-rhos * deltas)
    idx2 = idx1[np.argwhere(rhos[idx1] > 10).flatten()]
    index_centers = idx2[:4]

    centers = frame[index_centers]

    if plot:
        plt.figure()
        plt.scatter(rhos, deltas, color="gray")
        plt.scatter(
            rhos[index_centers],
            deltas[index_centers],
            c=[4, 3, 2, 1],
            cmap="Oranges",
            vmin=-1,
            s=60,
        )
        plt.xlabel("$\\rho$")
        plt.ylabel("$\\delta$")
        plt.show(block=False)

    rvs = []
    for i in range(len(centers)):
        rvs.append(multivariate_normal([np.abs(centers[i]), np.angle(centers[i])], cov))

    labels = np.full(N, -1, dtype=np.intp)
    for i in range(len(frame)):
        pdf = [rvs[j].pdf([np.abs(frame[i]), np.angle(frame[i])]) for j in range(4)]
        if np.max(pdf) > 1:
            labels[i] = np.argmax(pdf)

    return labels, index_centers


def sort_centers(centers, dc_mean, h_est):
    idx = np.arange(0, 4)
    index_ll = np.argmin(np.abs(centers - dc_mean))
    index_hh = np.argmin(np.abs(centers - h_est))
    idx = np.delete(idx, [index_ll, index_hh])
    idx = np.hstack(([index_ll], idx, [index_hh]))
    return centers[idx]


def calc_inter_channel(centers):
    inter_channel = (
        centers[1] - centers[0] + centers[2] - centers[0] - (centers[3] - centers[0])
    )
    return inter_channel


def process_one_frame(frame, dc, plot=False):
    dc_mean = np.mean(dc)
    mag_var = np.var(np.abs(dc))
    phase_var = np.var(np.angle(dc))
    cov = np.array([[mag_var, 0], [0, phase_var]])

    frame_start, h_est = frame_sync(frame - dc_mean)
    h_est += dc_mean
    # frame = frame[frame_start:]

    labels, _ = cluster_frame(frame, cov, plot)
    centers = np.zeros(4, dtype=np.complex64)
    for i in range(4):
        centers[i] = np.mean(frame[labels == i])

    centers_sorted = sort_centers(centers, dc_mean, h_est)
    inter_channel = calc_inter_channel(centers_sorted)
    center_expected = centers_sorted[3] + inter_channel

    if plot:
        plt.figure()
        plt.xlabel("In-phase")
        plt.ylabel("Quadrature")
        plt.scatter(
            frame[labels == -1].real,
            frame[labels == -1].imag,
            color="gray",
            marker=".",
            alpha=0.2,
        )
        for i in range(4):
            plt.scatter(
                frame[labels == i].real,
                frame[labels == i].imag,
                marker=".",
                alpha=0.2,
            )
        plt.scatter(centers_sorted.real, centers_sorted.imag, color="blue")
        plt.scatter(center_expected.real, center_expected.imag, color="red")
        plt.show()

    return inter_channel


if __name__ == "__main__":
    if len(sys.argv) == 3:
        sig_file = sys.argv[1]
        frame_index = sys.argv[2]
        sig = np.fromfile(sig_file, dtype=np.complex64)
        rn16_frames, rn16_frames_dc = extract_rn16_frames(
            sig, n_max_gap=440, n_t1=470, n_rn16=1250
        )
        frame = rn16_frames[int(frame_index)]
        dc = rn16_frames_dc[int(frame_index)]
        inter_channel = process_one_frame(frame, dc, plot=True)
        print("mag", np.abs(inter_channel))
        print("phase", np.angle(inter_channel))
    elif len(sys.argv) == 2:
        sig_file = sys.argv[1]
        sig = np.fromfile(sig_file, dtype=np.complex64)
        rn16_frames, rn16_frames_dc = extract_rn16_frames(
            sig, n_max_gap=440, n_t1=470, n_rn16=1250
        )
        inter_channels = []
        for i in track(range(len(rn16_frames))):
            frame = rn16_frames[i]
            dc = rn16_frames_dc[i]
            inter_channel = process_one_frame(frame, dc)
            inter_channels.append(inter_channel)

        plt.figure()
        plt.xlabel("Inter-channel amplitude")
        sns.kdeplot(np.abs(inter_channels), fill=True)
        plt.show(block=False)

        plt.figure()
        plt.xlabel("Inter-channel phase")
        sns.kdeplot(np.angle(inter_channels), fill=True)
        plt.show()

        np.save("inter_channel.npy", np.array(inter_channels))
