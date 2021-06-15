# python motion_visualize.py coordinates_file description_file true/false  (true/false is to save or not)

from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation
import mpl_toolkits.mplot3d.axes3d as p3
from sys import argv
from matplotlib import colors as mcolors
import random


def animate_scatters(i, refined_data, scatters):
    j = 0
    NUM_MARKER = num_marker_per_timestamp[timestamp_unique[i]]
    try:
        for j in range(NUM_MARKER):
            scatters[j]._offsets3d = (refined_data[i][j][1:2], refined_data[i][j][2:3], refined_data[i][j][3:])
        return scatters
    except Exception:
        print("Error with timestamp ", i, "and marker number ", j)


def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


# Read data
data = pd.read_csv(argv[1])  # coordinates_file
des = pd.read_csv(argv[2]).sort_values(by=['body part'])  # description_file sorted by body parts

# Classify data into categories
timestamp = data["time"]
timestamp_unique = unique(timestamp)
id = data["id"]
num_iter = len(set(timestamp))
x = data["x"]
y = data["y"]
z = data["z"]

# id to body part dictionary:
id_to_body = {des['id'][i]: des['body part'][i] for i in range(len(des))}

num_marker_per_timestamp = Counter(timestamp)

# Cluster it by timestamp, debug and check the inner structure, it's easy.
# Timestamp x marker x coordinates
refine_data = []

i = 0  # pointer to each duplicated timestamp

while i < len(timestamp):
    num_marker = num_marker_per_timestamp[timestamp[i]]
    refine_data.append([[id[i + j], x[i + j], y[i + j], z[i + j]] for j in range(num_marker)])
    i += num_marker

fig = plt.figure()
ax = p3.Axes3D(fig)

# Setting the axes properties
ax.set_xlim3d([-max(abs(x.min()), abs(x.max())), max(abs(x.min()), abs(x.max()))])
ax.set_xlabel('X')

ax.set_ylim3d([-max(abs(y.min()), abs(y.max())), max(abs(y.min()), abs(y.max()))])
ax.set_ylabel('Y')

# ax.set_zlim3d([0, max(abs(z.min()), abs(z.max()))])
ax.set_zlim3d([0, max(abs(z.min()), 1.5*abs(z.max()))])
ax.set_zlabel('Z')

ax.set_title('3D visualization')

# Provide starting angle for the view.
ax.view_init(0, -40)

# index to name of body parts:
ind_to_name = {1: "right leg", 2: "left leg", 3: "right arm", 4: "left arm", 5: "body"}

if __name__ == '__main__':

    # save setting:
    assert argv[3].lower() == "true" or argv[3].lower() == "false"
    if argv[3].lower() == "true":
        save = True
    else:
        save = False

    # Initialize random color for body parts:
    colors = random.sample(list(mcolors.TABLEAU_COLORS), len(des) // 2)
    body_to_color = {des['body part'].values[i]: colors[i // 2] for i in range(len(des))}

    # Initialize scatters
    scatters = [
        ax.scatter(x[i].reshape(1, 1), y[i].reshape(1, 1), z[i].reshape(1, 1), c=body_to_color[id_to_body[id[i]]], s=5,
                   marker='o', label=str(ind_to_name[id_to_body[id[i]] // 10]) + "_" + str(id_to_body[id[i]] % 10)) for i
        in
        range(num_marker_per_timestamp[timestamp[0]])]

    ani = animation.FuncAnimation(fig, animate_scatters, num_iter, fargs=(refine_data, scatters),
                                  interval=0.01, blit=False, repeat=False)

    if save:
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=40, metadata=dict(artist='Me'), bitrate=6000, extra_args=['-vcodec', 'libx264'])
        ani.save('3d-scatted-animated.mp4', writer=writer)

    ax.legend()
    ax.autoscale_view()
    plt.show()
