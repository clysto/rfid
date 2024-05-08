import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


def extract_rn16_frames(sig, n_max_gap, n_t1, n_rn16, frame_cv_threshoud=0.04):
    """
    Extracts RN16 frames from a given signal.

    Parameters:
    - sig (numpy.ndarray): Input signal.
    - n_max_gap (int): Maximum number of low-level continuous samples of the reader command signal.
    - n_t1 (int): Number of samples before the start of each frame.
    - n_rn16 (int): Number of RN16 samples in each frame.
    - frame_cv_threshoud (float): Threshold for coefficient of variation (CV) to filter frames.

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
        pkt = sig[start:end]
        frames.append(pkt)
    frames = np.array(frames)
    cv = np.std(np.abs(frames), axis=-1) / np.mean(np.abs(frames), axis=-1)
    idx = np.argwhere(cv >= frame_cv_threshoud).reshape(-1)
    frames = frames[idx, :]
    return frames


def symbol_samples(frame):
    frame_diff = np.abs(np.diff(np.abs(frame)))
    q1 = np.percentile(frame_diff, 25)
    q3 = np.percentile(frame_diff, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    condition = (frame_diff >= lower_bound) & (frame_diff <= upper_bound)
    return frame[np.argwhere(condition).reshape(-1)]


def cluster_samples(samples: np.ndarray):
    data = np.array([samples.real, samples.imag]).T
    kmeans = KMeans(n_clusters=4)
    kmeans.fit(data)
    labels = kmeans.labels_
    clustering_centers = kmeans.cluster_centers_
    sorted_centers = np.argsort(np.linalg.norm(clustering_centers, axis=-1))
    ll_label = sorted_centers[0]
    lh_label = sorted_centers[1]
    hl_label = sorted_centers[2]
    hh_label = sorted_centers[3]
    data_ll = data[labels == ll_label]
    data_lh = data[labels == lh_label]
    data_hl = data[labels == hl_label]
    data_hh = data[labels == hh_label]
    return {
        "ll_center": clustering_centers[ll_label][0]
        + clustering_centers[ll_label][1] * 1j,
        "lh_center": clustering_centers[lh_label][0]
        + clustering_centers[lh_label][1] * 1j,
        "hl_center": clustering_centers[hl_label][0]
        + clustering_centers[hl_label][1] * 1j,
        "hh_center": clustering_centers[hh_label][0]
        + clustering_centers[hh_label][1] * 1j,
        "ll": data_ll[:, 0] + data_ll[:, 1] * 1j,
        "lh": data_lh[:, 0] + data_lh[:, 1] * 1j,
        "hl": data_hl[:, 0] + data_hl[:, 1] * 1j,
        "hh": data_hh[:, 0] + data_hh[:, 1] * 1j,
    }


def plot_result(result, expected_center):
    plt.figure()
    plt.scatter(result["ll"].real, result["ll"].imag, marker=".")
    plt.scatter(result["lh"].real, result["lh"].imag, marker=".")
    plt.scatter(result["hl"].real, result["hl"].imag, marker=".")
    plt.scatter(result["hh"].real, result["hh"].imag, marker=".")
    plt.scatter(expected_center.real, expected_center.imag, marker="x", c="b")
    plt.scatter(result["hh_center"].real, result["hh_center"].imag, marker="x", c="b")
    plt.show()


if __name__ == "__main__":
    sig = np.fromfile("static.cf32", dtype=np.complex64)
    rn16_frames = extract_rn16_frames(sig, n_max_gap=440, n_t1=470, n_rn16=1250)
    inter_channels = []
    for i in range(0, len(rn16_frames), 16):
        samples = symbol_samples(rn16_frames[i : i + 16].reshape(-1))
        result = cluster_samples(samples)
        bs_1 = result["lh_center"] - result["ll_center"]
        bs_2 = result["hl_center"] - result["ll_center"]
        expected_center = (bs_1 + bs_2) + result["ll_center"]
        inter_channels.append(expected_center - result["hh_center"])
        print("")
        print("  mag:", np.abs(expected_center - result["hh_center"]))
        print("phase:", np.angle(expected_center - result["hh_center"]))
    fig, ax1 = plt.subplots()
    ax1.plot(np.abs(inter_channels), color="C0")
    ax1.set_ylabel("Magnitude", color="C0")
    ax2 = ax1.twinx() 
    ax2.plot(np.unwrap(np.angle(inter_channels)), color="C1")
    ax2.set_ylabel("Phase", color="C1")
    plt.show()
