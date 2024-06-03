import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import sys

sns.set_theme()

rn16_frames = np.load(sys.argv[1])["frames"]
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
    x = current_frame.real
    y = current_frame.imag
    scat.set_offsets(np.c_[x, y])
    title.set_text(f"RN16 #{i}")
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
