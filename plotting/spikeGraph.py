"""
Spike graphs are a record of the acivity of a single pixel or a group of pixels.
Y Axis: ON events correspond to +1 and OFF events correspond to -1
X Axis: Time

CSV Format: on/off,x,y,timestamp
"""
import csv
from itertools import islice
import matplotlib.pyplot as plt

# The pixel to examine
pixel_x = 50
pixel_y = 50

area_size = 4

max_plot_points = 25

csv_filename = 'plotting/test.csv'

activity_timestamps = []  # The times when the pixel changed state
time_between = []       # The times between the state changes

y_values = []

with open(csv_filename) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')

    for row in islice(csv_reader, 1, None):     # Skip the header
        x_row = int(row[1])
        y_row = int(row[2])

        check_x = abs(x_row - pixel_x)
        check_y = abs(y_row - pixel_y)

        # Check if this event is inside the specified area
        if check_x < area_size and check_y < area_size:

            activity_timestamps.append(int(row[3]))
            if row[0] == "True":
                y_values.append(1)
            else:
                y_values.append(-1)



# Get the time between timestamps
for i in range(len(activity_timestamps) - 1):
    time_between.append(activity_timestamps[i + 1] - activity_timestamps[i])

# Add lines to plot
for i, stamp in enumerate(activity_timestamps):
    plt.plot([stamp, stamp], [0, y_values[i]], 'b') # Add to points at the same X value to make vertical lines

plt.ylim(-1.1, 1.1)
plt.title('Spike Graph')
plt.xlabel('Time(mS)')
plt.show()

if len(time_between) != 0:
    print(f"Average time between: {round(sum(time_between) / len(time_between), 2)}mS")
