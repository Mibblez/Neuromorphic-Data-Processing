from sklearn.cluster import SpectralClustering
import numpy as np
import plotting_utils.get_plotting_data as get_plotting_data
from plotting_utils.get_plotting_data import DataStorage
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # TODO: Make the variables below into command line args
    file_to_plot = "eventChunkData/bean/31Hz-2sl-40deg-m1Threshold-BackLight-2s.csv"
    max_time = 0.00125  # Take in as microseconds then convert to seconds
    num_clusters = 6

    data = get_plotting_data.SpatialCsvData.from_csv(file_to_plot, DataStorage.NONE, max_time)

    # Transform X and Y positions into the correct format for this plot -> [[X,Y], [X,Y], ...]
    plot_points = np.asarray(list(zip(data.x_positions, data.y_positions)))

    model = SpectralClustering(
        n_clusters=num_clusters, assign_labels="cluster_qr", affinity="rbf", eigen_solver="lobpcg"
    )

    labels = model.fit_predict(plot_points)

    plt.scatter(plot_points[:, 0], plot_points[:, 1], c=labels, s=10, cmap="viridis")
    # TODO: save to disk instead of showing
    plt.show()
