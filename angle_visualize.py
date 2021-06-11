from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from sys import argv
from matplotlib.animation import FuncAnimation
import random


def without_keys(d, keys):
    return [v for k, v in d.items() if k not in keys]


# Read data
data = pd.read_csv(argv[1])
refined_data = without_keys(data, 'time')

# num plots:
num_plot = len(data.keys()) - 1

# initialize subplots
fig, axs = plt.subplots(num_plot)

# choose random color:
colors = random.sample(list(mcolors.CSS4_COLORS), num_plot)

def animate(i):
    # plt.cla()
    for k in range(num_plot):
        axs[k].cla()
        axs[k].plot(data['time'][:i + 1], refined_data[k][:i + 1], color=colors[k], label=data.keys()[k+1])
        axs[k].set_xlabel('time')
        axs[k].set_ylabel('degree')
        axs[k].legend(loc='upper left')
    # for k in range(num_plot):
    #     axs[k].plot(data['time'], refined_data[k], label=str(refined_data[k]))
    #     scatters[k].set_offsets((data['time'][i:i + 1], refined_data[k:k+1][i:i + 1]))
    #     plt.tight_layout()
    #     return scatters


ani = FuncAnimation(plt.gcf(), animate, interval=(data['time'][1] - data['time'][0]) * 1000)
plt.tight_layout()
plt.show()
