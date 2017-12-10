from tools import chart_tools as ct
import pandas as pd

tools = ct.ChartTools()
df = pd.read_csv("dummy/hr-2.csv")
df = df.groupby(['salary'])['satisfaction_level'].mean().reset_index()
tools.set_dataset(df.copy())
print tools.bar_chart('salary', 'satisfaction_level')