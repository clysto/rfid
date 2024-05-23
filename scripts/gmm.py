from sklearn.mixture import GaussianMixture
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# 创建一些模拟数据
# np.random.seed(0)
# data1 = np.random.normal(loc=-2, scale=1, size=(300, 2))
# data2 = np.random.normal(loc=2, scale=1.5, size=(700, 2))
# data = np.vstack([data1, data2])

sig = np.fromfile("data/nothing.cf32", dtype=np.complex64)
data = np.array([sig.real, sig.imag]).T

# 创建并训练GMM模型
gmm = GaussianMixture(n_components=1, random_state=0)
gmm.fit(data)

# 生成网格数据
x = np.linspace(-1, 1, 500)
y = np.linspace(-1, 1, 500)
X, Y = np.meshgrid(x, y)
XX = np.array([X.ravel(), Y.ravel()]).T

# 计算网格上的对数概率密度
log_prob = gmm.score_samples(XX)
Z = np.exp(log_prob).reshape(X.shape)


# 绘制概率密度图
plt.contourf(X, Y, Z, levels=100, cmap="viridis")
plt.colorbar()
plt.scatter(data[:, 0], data[:, 1], c="gray", alpha=0.1)
plt.title("Gaussian Mixture Probability Density")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.show()
