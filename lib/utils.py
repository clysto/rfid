import numpy as np
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
    """
    Synchronizes the frame by finding the start position and estimating the channel response.

    Parameters:
    - frame (ndarray): The input frame to be synchronized.

    Returns:
    - tuple: A tuple containing the frame start position and the estimated channel response.
    """
    preamble = np.repeat([1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1], 25) + 0j
    corr = np.abs(signal.correlate(frame[: len(preamble) + 100], preamble, "same"))
    frame_start = max(0, np.argmax(corr) - 6 * 25)
    h_est = np.mean(frame[frame_start:][np.argwhere(preamble == 1)])
    return frame_start, h_est
