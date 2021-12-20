import csv
from itertools import islice
import matplotlib.pyplot as plt

# FIXME: ▼▼▼▼▼▼ change all these variables to command line args
# The pixel to examine
pixel_x = 115
pixel_y = 45

area_size = 10
max_plot_points = 25

csv_filename = '5Hz_pol.csv'
# FIXME: ▲▲▲▲▲▲ change all these variables to command line args

last_pixel_state = None
redundancies = 0    # TODO: do redundancies for all pixels

change_timestamps = []  # The times when the pixel changed state
time_between = []       # The times between the state changes

with open(csv_filename) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')

    for row in islice(csv_reader, 1, None):     # Skip the header
        x_row = int(row[1])
        y_row = int(row[2])

        check_x = abs(x_row - pixel_x)
        check_y = abs(y_row - pixel_y)

        if check_x < area_size and check_y < area_size:
            pixel_state = (row[0] == 'True') or (row[0] == '1')

            if (pixel_state != last_pixel_state):
                reset_pixel = False
                last_pixel_state = pixel_state
                change_timestamps.append(int(row[3]))
                if len(change_timestamps) > max_plot_points:
                    break
            else:
                redundancies += 1

print(f"Redundancies: {redundancies}")

# Normalize timestamps & convert to mS
change_timestamps = [(x - change_timestamps[0]) / 1000 for x in change_timestamps]

# Get the time between timestamps
for i in range(len(change_timestamps) - 1):
    time_between.append(change_timestamps[i + 1] - change_timestamps[i])

# Add lines to plot
for stamp in change_timestamps:
    plt.plot([stamp, stamp], [0, 1], 'b')

plt.ylim(0, 1.2)
plt.yticks([])
plt.title('Temporal Resoltion')
plt.xlabel('Time(mS)')
plt.show()

if len(time_between) != 0:
    print(f"Average time between: {round(sum(time_between) / len(time_between), 2)}mS")
