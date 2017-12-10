import tools
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
import numpy as np
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
        return self.convert_base64(fig)

    def convert_base64(self, fig):
        figfile = BytesIO()
        fig.savefig(figfile, format='png')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue())
        return "data:image/png;base64," + figdata_png.decode('utf8')

    def line_plot(self, date, target):
        ts = pd.Series(self.df[target], index=self.df[date])
        ts = ts.cumsum()
        df_fig = ts.plot()
        fig = df_fig.get_figure()
        plt.title("Box Plot")
        plt.show()
        return self.convert_base64(fig)

    def pie_plot(self, target):
        pie = self.df[target].value_counts()
        df_fig = pie.plot.pie(figsize=(6, 6))
        fig = df_fig.get_figure()
        plt.title("Pie Plot")
        return self.convert_base64(fig)

    def bar_chart(self, x, y):
        y_pos = np.arange(len(self.df[x]))
        plt.bar(y_pos, self.df[y], align='center', alpha=0.5)
        plt.xticks(y_pos, self.df[x])
        plt.ylabel(y)
        plt.xlabel(x)
        plt.title('Bar Chart')
        return self.convert_base64(plt)

    def clear_chart(self):
        plt.clf()
