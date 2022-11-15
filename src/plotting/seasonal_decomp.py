from pandas import read_csv
from matplotlib import pyplot as plt
import matplotlib
import statsmodels.api as sm

# TODO: Command line args go here
# Args needed: file_to_plot, event_type -> (on, off, combined), num_rows
#              skip_rows, period, save_dir


if __name__ == "__main__":
    # get_args()
    csv_file = "test.csv"   # TODO: get csv_file from command line arg

    matplotlib.use("Qt5Agg")

    # TODO: only read what we need. Use the "usecols" kwarg in use_cols to select columns
    df = read_csv(csv_file, nrows=901)  # TODO: arg for how many rows to read

    # Arg for which column to plot, same as what is passed to use_cols
    on_count = df["On Count"]
    off_count = df["Off Count"]
    combined_count = df[" Combined Count"]
    # ------------------▲▲ The space here is stupid, I know

    # Auto generate plot title from csv_filename
    plot_title = "Seasonal_Decomposition-500us-sine-40deg-1Threshold"

    # Decomposition.plot() is weird. The name of the dataframe is used as the plot title
    on_count.name = plot_title

    # Arg for how many rows to skip--------------------▼▼▼
    decomposition = sm.tsa.seasonal_decompose(on_count[300:], period=100)
    # Arg for period-------------------------------------------------▲▲▲

    # TODO: The above code is also going to be used to clean data so it needs to be made into its own func
    #           * Cleaning data will consist of reading in the ON and OFF columns, performing seasonal decomp
    #             and then writing the seasonal data (decomposition.seasonal) to a new csv
    #           * Seasonal decomp will need to be performed for ON and OFF columns seperately
    #           * The new "Combined Count" column will be Seasonal ON + Seasonal OFF
    #           * This function will be put into plotting_utils once everything is done

    # Prototype for seasonal decomp function
    # def seasonal_decomp(csv_file: str, columns: List[str], row_skip: int, period: int) -> DecomposeResult:

    # All standard stuff below here. Format plot and save it
    decomposition.plot()

    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(16, 10)

    plt.tight_layout(pad=1.10)

    plt.savefig(f"{plot_title}.png")
    plt.clf()
