# python visualize.py true/false to save video or not

from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation
import mpl_toolkits.mplot3d.axes3d as p3
from sys import argv


def animate_scatters(i, refine_data, scatters):
    j = 0
    try:
        for j in range(num_marker_per_timestamp[timestamp_unique[i]]):
            scatters[j]._offsets3d = (refine_data[i][j][0:1], refine_data[i][j][1:2], refine_data[i][j][2:])
        return scatters
    except Exception:
        print("Error with i= ", i, "and j= ", j)


def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


# Read data
data = pd.read_csv('Thursday.csv')

# Classify data into categories
timestamp = data["time"]
timestamp_unique = unique(timestamp)
id = data["id"]
num_marker = len(set(id))
num_iter = len(timestamp_unique)
x = data["x"]
y = data["y"]
z = data["z"]

num_marker_per_timestamp = Counter(timestamp)

# Cluster it by timestamp, debug and check the inner structure, it's easy.
# Timestamp x marker x coordinates
refine_data = [0 for _ in range(len(timestamp_unique))]

k = 0
i = 0

while i < len(timestamp):
    refine_data[k] = [[x[i + j], y[i + j], z[i + j]] for j in range(num_marker_per_timestamp[timestamp_unique[k]])]
    i += len(refine_data[k])
    k += 1

fig = plt.figure()
ax = p3.Axes3D(fig)

# Setting the axes properties
ax.set_xlim3d([-2, 2])
ax.set_xlabel('X')

ax.set_ylim3d([-2, 2])
ax.set_ylabel('Y')

ax.set_zlim3d([-2, 2])
ax.set_zlabel('Z')

ax.set_title('3D visualization')

# Provide starting angle for the view.
ax.view_init(25, 10)

if __name__ == '__main__':
    assert argv[1].lower() == "true" or argv[1].lower() == "false"
    if argv[1].lower() == "true":
        save = True
    else:
        save = False
    # Initialize scatters
    scatters = [ax.scatter(x[i].reshape(1, 1), y[i].reshape(1, 1), z[i].reshape(1, 1)) for i in
                range(num_marker_per_timestamp[timestamp_unique[0]])]

    ani = animation.FuncAnimation(fig, animate_scatters, num_iter, fargs=(refine_data, scatters),
                                  interval=1, blit=False, repeat=True)

    if save:
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=30, metadata=dict(artist='Me'), bitrate=1800, extra_args=['-vcodec', 'libx264'])
        ani.save('3d-scatted-animated.mp4', writer=writer)

    plt.show()
