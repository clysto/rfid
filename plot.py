import numpy as np
import matplotlib.pyplot as plt
from extract_inter_channel import (
    extract_rn16_frames,
    frame_sync,
    cluster_frame,
    calc_inter_channel,
)

GAINS = [74, 77, 80]
DISTANCES = [5, 8]
REPEAT = 4

if __name__ == "__main__":
    inter_channels = dict()
    for gain in GAINS:
        inter_channels[gain] = dict()
        for distance in DISTANCES:
            inter_channels[gain][distance] = list()
            for i in range(REPEAT):
                inter_channels[gain][distance].append(list())
                sig = np.fromfile(
                    f"data/{gain}_{distance}cm_{i}.cf32", dtype=np.complex64
                )
                rn16_frames = extract_rn16_frames(
                    sig, n_max_gap=440, n_t1=470, n_rn16=1250
                )
                for frame in rn16_frames:
                    try:
                        frame, h_est = frame_sync(frame)
                        frame /= h_est
                        clusters, centers = cluster_frame(frame)
                    except Exception as e:
                        print(e)
                        continue
                    centers_sorted = centers[np.argsort(np.abs(centers))]
                    symbols = frame[clusters >= 0]
                    inter_channel = calc_inter_channel(centers)
                    center_expected = centers_sorted[3] + inter_channel
                    inter_channels[gain][distance][i].append(inter_channel)

    for gain in GAINS:
        plt.figure()
        color_cycle = 0
        plt.title(f"Inter-channel magnitude for gain {gain}dB")
        plt.grid()
        for distance in DISTANCES:
            for i in range(REPEAT):
                inter_channel = inter_channels[gain][distance][i]
                kargs = {"color": f"C{color_cycle}"}
                if i == 0:
                    kargs["label"] = f"{distance}cm"
                plt.plot(np.abs(inter_channel), **kargs)
            color_cycle += 1
        plt.legend()
        plt.xlabel("#RN16 Frames")
        plt.ylabel("Inter-channel magnitude")
        plt.savefig(f"figs/inter_channel_magnitude_{gain}dB.svg")
        plt.show(block=False)

        plt.figure()
        color_cycle = 0
        plt.title(f"Inter-channel phase for gain {gain}dB")
        plt.grid()
        for distance in DISTANCES:
            for i in range(REPEAT):
                inter_channel = inter_channels[gain][distance][i]
                kargs = {"color": f"C{color_cycle}"}
                if i == 0:
                    kargs["label"] = f"{distance}cm"
                plt.plot(np.unwrap(np.angle(inter_channel)), **kargs)
            color_cycle += 1
        plt.legend()
        plt.xlabel("#RN16 Frames")
        plt.ylabel("Inter-channel phase")
        plt.savefig(f"figs/inter_channel_phase_{gain}dB.svg")
        plt.show(block=False)

    plt.show()
