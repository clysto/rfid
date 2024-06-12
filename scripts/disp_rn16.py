import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.animation as animation
import seaborn as sns
import sys


colors = ["gray"] + [plt.get_cmap("tab10")(i) for i in range(0, 4)]
custom_cmap = mcolors.ListedColormap(colors)


sns.set_theme()

data = np.load(sys.argv[1])
rn16_frames = data["frames"]
rn16_labels = data["labels"]
rn16_inter_channels = data["inter_est"]
print("Frames:", len(rn16_frames))


fig, ax = plt.subplots()
ax.set_aspect("equal", adjustable="box")
ax.set_xlabel("In-phase")
ax.set_ylabel("Quadrature")
scat = ax.scatter([], [])
title = ax.set_title("")

margin = 0.1
x_min, x_max = np.min(rn16_frames.flatten().real), np.max(rn16_frames.flatten().real)
y_min, y_max = np.min(rn16_frames.flatten().imag), np.max(rn16_frames.flatten().imag)
x_margin = (x_max - x_min) * margin
y_margin = (y_max - y_min) * margin
ax.set_xlim(x_min - x_margin, x_max + x_margin)
ax.set_ylim(y_min - y_margin, y_max + y_margin)


def animate(i):
    current_frame = rn16_frames[i]
    labels = rn16_labels[i]
    idx = np.argsort(labels)
    labels = labels[idx]
    current_frame = current_frame[idx]
    x = current_frame.real
    y = current_frame.imag
    scat.set_offsets(np.c_[x, y])
    scat.set_array(labels)
    scat.set_cmap(custom_cmap)
    scat.set_clim(-1, 3)
    title.set_text(f"RN16 #{i} {np.abs(rn16_inter_channels[i])}")
    return (scat, title)


ani = animation.FuncAnimation(
    fig,
    animate,
    repeat=True,
    frames=len(rn16_frames),
    interval=200,
)

# ani.save("rn16.mp4", dpi=600)

plt.show()
