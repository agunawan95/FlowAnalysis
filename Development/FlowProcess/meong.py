import pandas as pd
import re

def update(df, formulas):
    for k, v in formulas.items():
        df[k] = pd.eval(v)


df = pd.read_csv('Data/hr-1.csv')
formulas = {'meong': '(df["number_project"] + df["time_spend_company"])/2'}

update(df, formulas)

print df[['number_project', 'time_spend_company', 'meong']].head(10)

res = df.groupby(['department_id', 'salary'])['time_spend_company'].max().reset_index()
res = res.rename(columns={'time_spend_company': 'avg_time_spend_company'})
print res

str = "meong"
regex = re.compile("([-()+*/])")
if regex.search(str):
    print "Match"
else:
    print "Not Match"
