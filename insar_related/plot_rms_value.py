## plot the RMS value
from mintpy.timeseries_rms import plot_rms_bar
import numpy as np
import matplotlib.pyplot as plt
txtContent = np.loadtxt('./rms_timeseriesResidual_ramp.txt', dtype=bytes).astype(str)
rms_list = [float(i) for i in txtContent[:, 1]]
date_list = [i for i in txtContent[:, 0]]
fig, ax = plt.subplots(figsize=[10, 4])
ax = plot_rms_bar(ax, date_list, rms_list)
#plt.show()
plt.savefig('rms_timeseriesResidual_ramp.png',bbox_inches='tight')
