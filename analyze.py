import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 加载信号
sig = np.fromfile("rx_B.cf32", dtype=np.complex64)

# 计算幅值和相位
magnitude = np.abs(sig)
phase = np.angle(sig)

# 将相位从弧度转换为度数
phase_degrees = np.degrees(phase)


# 创建一个图形框架
plt.figure(figsize=(12, 6))

# 绘制幅值的分布曲线
plt.subplot(1, 2, 1)
sns.kdeplot(magnitude, color="C0", fill=True)
plt.title("Magnitude Distribution")
plt.xlabel("Magnitude")
plt.ylabel("Density")

# 绘制相位的分布曲线
plt.subplot(1, 2, 2)
sns.kdeplot(phase_degrees, color="C1", fill=True)
plt.title("Phase Distribution")
plt.xlabel("Phase (degrees)")
plt.ylabel("Density")

plt.tight_layout()
plt.show()
