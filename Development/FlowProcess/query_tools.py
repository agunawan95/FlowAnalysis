import tools
import json
import pandas as pd
import re


def update(df, formulas):
    for k, v in formulas.items():
        df[k] = pd.eval(v)


class QueryTools(tools.Tools):

    mask = None

    def __init__(self):
        tools.Tools.__init__(self)
        self.mask = None

    def compare(self, operator, df, column, value):
        """
        Function Helping Masking Function
        :param operator: Operator for DataFrame Operation Like Less Than, Greater Than
        :param df: DataFrame Targer of Operation
        :param column: Target Column of DataFrame
        :param value: Value for Compare
        :type operator: string
        :type df: DataFrame
        :type column: string
        :type value: Depend on DataFrame Column Type
        :return: Mask
        """
        if operator == "equal":
            return df[column].astype(str) == value
        elif operator == "less":
            return df[column] < int(value)
        elif operator == "less_or_equal":
            return df[column] <= int(value)
        elif operator == "greater":
            return df[column] > int(value)
        elif operator == "greater_or_equal":
            return df[column] >= int(value)
        elif operator == "not_equal":
            return df[column] != value
        elif operator == "greater_or_equal":
            return df[column] >= int(value)
        elif operator == "greater_or_equal":
            return df[column] >= value
        elif operator == 'begin_with':
            return df[column].str.startswith(value)
        elif operator == 'not_begin_with':
            return ~(df[column].str.startswith(value))
        elif operator == 'contains':
            return df[column].str.match(value)
        elif operator == 'not_contains':
            return ~(df[column].str.match(value))

    def masking(self, df, condition):
        """
        Function to Produce Mask of Certain Operation on DataFrame
        :param df: DataFrame Target Operation
        :param condition: Dictionary of Condition to be Applied
        :return: Mask
        """
        mask = None
        start = True
        for con in condition['rules']:
            tmp = None
            if "condition" in con:
                tmp = self.masking(df.copy(), con)
            else:
                tmp = self.compare(con['operator'], df.copy(), con['field'], con['value'])
            if start:
                start = False
                mask = tmp
            else:
                if condition['condition'] == 'OR':
                    mask = mask | tmp
                elif condition['condition'] == 'AND':
                    mask = mask & tmp
        return mask

    def set_condition(self, condition):
        """
        Set a Condition and save it as Mask
        :param condition: String containing JSON Data format of Condition
        :return: None
        """
        data = json.loads(condition)
        self.mask = self.masking(self.df.copy(), data)

    def update(self, column, value):
        """
        Update Certain Data on DataFrame Based on Mask
        :param column: What Column to Update
        :param value: Update to What Value
        :return: None
        """
        self.df.loc[self.mask, column] = value

    def update_with_other_column(self, column, into):
        """
        Update Certain Data With Other Dataset Column on DataFrame Based on Mask
        :param column: What Column to Update
        :param value: Update to What Value
        :return: None
        """
        self.df.loc[self.mask, column] = self.df[into]

    def delete(self):
        """
        Delete All Record Based on Mask
        :return:
        """
        self.df = self.df[~self.mask]

    def add_record(self, arr):
        """
        Add 1 Record to Dataframe with same structure
        :param arr: Sequence / Record
        :type arr: Array
        :return: No Return
        :rtype: void
        """
        header = list(self.df)
        tmp = pd.DataFrame(columns=header)
        for key, value in enumerate(arr, start=0):
            tmp[header[key]] = [value]
        self.df = pd.concat([self.df, tmp]).reset_index(drop=True)

    def get_aggregate(self, groupby, f, target):
        res = None
        if f == 'sum':
            res = self.df.groupby(groupby)[target].sum().reset_index()
            res = res.rename(columns={target: 'sum_' + target})
        elif f == 'avg':
            res = self.df.groupby(groupby)[target].mean().reset_index()
            res = res.rename(columns={target: 'avg_' + target})
        elif f == 'count':
            res = self.df.groupby(groupby)[target].count().reset_index()
            res = res.rename(columns={target: 'count_' + target})
        elif f == 'std':
            res = self.df.groupby(groupby)[target].std().reset_index()
            res = res.rename(columns={target: 'standard_deviation_' + target})
        elif f == 'max':
            res = self.df.groupby(groupby)[target].max().reset_index()
            res = res.rename(columns={target: 'max_' + target})
        elif f == 'min':
            res = self.df.groupby(groupby)[target].min().reset_index()
            res = res.rename(columns={target: 'min_' + target})
        return res

    def execute_formula(self, formula, new_column):
        tmp = re.split("([-()+*/])", formula)
        regex = re.compile("([-()+*/])")
        res = ""
        for value in tmp:
            value = str(value).strip()
            if not regex.search(value) and value in list(self.df):
                res += "df['" + value + "']"
            else:
                res += value
        formulas = {new_column: res}
        update(self.df, formulas)

    def get_filter(self):
        """
        Get Data Based on Mask
        :return: DataFrame
        """
        return self.df[self.mask].copy()

    def apply_filter(self):
        """
        Apply Masking to Current DataFrame
        :return: None
        """
        self.df = self.df[self.mask]
