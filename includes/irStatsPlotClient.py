from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import os

# https://matplotlib.org/stable/gallery/index.html

class irStatsPlotClient():

    def __init__(self, _hive_root=None):
        self.hive_root = _hive_root

    def plot_distribution(self, filename, datacol, binwidth):

        # Prep plot
        plt.figure(figsize=[10, 8])

        plt.ylabel('Frequency', fontsize=15)
        plt.title('iRating Distribution', fontsize=15)
        plt.legend(title='iR', fontsize=15)

        # Prep data
        bins = range(min(datacol), max(datacol) + binwidth, binwidth)

        plt.hist(datacol, bins)

        # Save plot
        export_path = os.path.join(self.hive_root, "media/plots", filename)
        plt.savefig(export_path)

