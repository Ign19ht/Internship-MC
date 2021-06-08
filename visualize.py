# python visualize.py filename true/false  (true/false is to save or not)

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
        print("Error with timestamp ", i, "and marker number ", j)


def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


# Read data
data = pd.read_csv(argv[1])

# Classify data into categories
timestamp = data["time"]
timestamp_unique = unique(timestamp)
id = data["id"]
num_iter = len(set(timestamp))
x = data["x"]
z = data["y"]
y = data["z"]

num_marker_per_timestamp = Counter(timestamp)

# Cluster it by timestamp, debug and check the inner structure, it's easy.
# Timestamp x marker x coordinates
refine_data = []

i = 0  # pointer to each duplicated timestamp

while i < len(timestamp):
    num_marker = num_marker_per_timestamp[timestamp[i]]
    refine_data.append([[x[i + j], y[i + j], z[i + j]] for j in range(num_marker)])
    i += num_marker

fig = plt.figure()
ax = p3.Axes3D(fig)

# Setting the axes properties
ax.set_xlim3d([-2*max(abs(x.min()), abs(x.max())), 2*max(abs(x.min()), abs(x.max()))])
ax.set_xlabel('X')

ax.set_ylim3d([-2*max(abs(y.min()), abs(y.max())), 2*max(abs(y.min()), abs(y.max()))])
ax.set_ylabel('Y')

# ax.set_zlim3d([0, max(abs(z.min()), abs(z.max()))])
ax.set_zlim3d([-2*max(abs(z.min()), abs(z.max())), 2*max(abs(z.min()), abs(z.max()))])
ax.set_zlabel('Z')

ax.set_title('3D visualization')

# Provide starting angle for the view.
ax.view_init(0, -40)

if __name__ == '__main__':

    # save setting:
    assert argv[2].lower() == "true" or argv[2].lower() == "false"
    if argv[2].lower() == "true":
        save = True
    else:
        save = False

    # Initialize scatters
    scatters = [ax.scatter(x[i].reshape(1, 1), y[i].reshape(1, 1), z[i].reshape(1, 1), c='black', s=1, marker='x') for i in
                range(num_marker_per_timestamp[timestamp[0]])]

    for i in range(num_marker_per_timestamp[timestamp[0]]):
        scatters[i].set

    ani = animation.FuncAnimation(fig, animate_scatters, num_iter, fargs=(refine_data, scatters),
                                  interval=-0.1, blit=False, repeat=True)

    if save:
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=30, metadata=dict(artist='Me'), bitrate=4000, extra_args=['-vcodec', 'libx264'])
        ani.save('3d-scatted-animated.mp4', writer=writer)

    # plt.show()
