import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure()
plt.xlabel("Inter-channel amplitude")
for i in range(6):
    inter_channels = np.load(f"data/inter_channel{i+1}.npy")
    sns.kdeplot(np.abs(inter_channels), fill=True)
plt.show()

