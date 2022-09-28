import numpy as np
from scipy.optimize import leastsq
import pylab as plt
import plotting_utils.get_plotting_data as get_plotting_data
from scipy.signal import savgol_filter


def optimize_func(x):
    return x[0] * np.sin(x[1] * t + x[2]) + x[3] - data


N = 1000  # number of data points

f = 1.15247  # Optional!! Advised not to use
# data = 3.0*np.sin(f*t+0.001) + 0.5 + np.random.randn(N) # create artificial data with noise

# FIXME: no longer works due to changes in getData (getData changed to read_aedat_csv)
on, off, all2, N, x = get_plotting_data.getData()
yhat = savgol_filter(off, 51, 3)
data = np.array(yhat)
t = np.linspace(0, 4 * np.pi, N)

guess_mean = np.mean(data)
guess_std = 3 * np.std(data) / (2**0.5) / (2**0.5)
guess_phase = 0
guess_freq = 12
guess_amp = 120

# we'll use this to plot our first estimate. This might already be good enough for you
data_first_guess = guess_std * np.sin(t + guess_phase) + guess_mean

# Define the function to optimize, in this case, we want to minimize the difference
# between the actual data and our "guessed" parameters

# FIXME: changed to a def because flake8 complained. Need to verify if the def statement works the same
# optimize_func = lambda x: x[0] * np.sin(x[1] * t + x[2]) + x[3] - data

est_amp, est_freq, est_phase, est_mean = leastsq(optimize_func, [guess_amp, guess_freq, guess_phase, guess_mean])[0]

# recreate the fitted curve using the optimized parameters
data_fit = est_amp * np.sin(est_freq * t + est_phase) + est_mean

# recreate the fitted curve using the optimized parameters

fine_t = np.arange(0, max(t), 0.1)
data_fit = est_amp * np.sin(est_freq * fine_t + est_phase) + est_mean

print(est_freq, est_freq / t[1])

# plt.plot(t, on, '.',c="green")
# plt.plot(t,off, '.',c="red")
# plt.plot(t, data_first_guess, label='first guess')
plt.plot(fine_t, data_fit, label="after fitting")
plt.plot(t, data, ".", c="red")
plt.legend()
plt.show()

plt.scatter(x, data)
plt.show()
