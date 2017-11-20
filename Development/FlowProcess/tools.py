import pandas as pd


class Tools:

    df = None
    file_location = ""

    def __init__(self):
        self.df = None
        self.file_location = ""

    def set_file(self, file_location):
        """
        Set File at Certain Location to Object DataFrame
        :param file_location: Location of File
        :return: None
        """
        self.file_location = file_location
        self.df = pd.read_csv(self.file_location)

    def set_dataset(self, df):
        self.df = df

    def commit_change(self):
        """
        Create a CSV File Based on DataFrame
        :return: None
        """
        self.df.to_csv(self.file_location)

    def data_frame(self):
        """
        Return Current DataFrame
        :return:
        """
        return self.df

    def corr_table(self):
        return self.df.corr()

    def describe_numeric(self):
        return self.df.describe()
