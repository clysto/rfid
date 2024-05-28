import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure()
plt.xlabel("Inter-channel amplitude")
for i in range(2):
    inter_channels = np.load(f"inter_channel{i+1}.npy")
    sns.kdeplot(np.abs(inter_channels), fill=True)
plt.show()


# plt.figure()
# plt.xlabel("Inter-channel amplitude")
# for i in range(2):
#     inter_channels = np.load(f"inter_channel{i+1}.npy")
#     plt.plot(np.angle(inter_channels))
# plt.show()
