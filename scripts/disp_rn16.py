import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

rn16_frames = np.load("frames.npy")
fig, ax = plt.subplots()
ax.set_aspect("equal", adjustable="box")
ax.set_title("RN16 #0")
scat = ax.scatter(rn16_frames[0].real, rn16_frames[0].imag)

margin = 0.1

print("Frames:", len(rn16_frames))


def animate(i):
    current_frame = rn16_frames[i + 1]
    x = current_frame.real
    y = current_frame.imag
    scat.set_offsets(np.c_[x, y])

    x_min, x_max = np.min(x), np.max(x)
    y_min, y_max = np.min(y), np.max(y)
    x_margin = (x_max - x_min) * margin
    y_margin = (y_max - y_min) * margin

    ax.set_xlim(x_min - x_margin, x_max + x_margin)
    ax.set_ylim(y_min - y_margin, y_max + y_margin)
    ax.set_title(f"RN16 #{i + 1}")

    return (scat,)


ani = animation.FuncAnimation(
    fig, animate, repeat=True, frames=len(rn16_frames) - 1, interval=200
)

plt.show()
