import tools
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
from pandas.plotting import *


class ChartTools(tools.Tools):

    def corr_matrix_chart(self, title):
        plt.matshow(self.df.corr())
        plt.title(title)

        return self.convert_base64(plt)

    def scatter_plot(self, x, y):
        df_fig = self.df.plot.scatter(x=x, y=y)
        fig = df_fig.get_figure()
        return self.convert_base64(fig)

    def scatter_matrix(self, target):
        scatter_matrix(self.df[target], alpha=0.2, figsize=(6, 6), diagonal='kde')
        return self.convert_base64(plt)

    def hist(self, column):
        df_fig = self.df[column].hist()
        fig = df_fig.get_figure()
        return self.convert_base64(fig)

    def box_plot(self, target):
        df_fig = self.df[target].plot.box()
        fig = df_fig.get_figure()
        plt.title("Box Plot")
        plt.show()
        return self.convert_base64(fig)

    def convert_base64(self, fig):
        figfile = BytesIO()
        fig.savefig(figfile, format='png')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue())
        return "data:image/png;base64," + figdata_png.decode('utf8')


