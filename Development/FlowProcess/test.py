import pandas as pd
import json

with open('Metadata/hr.json') as data_file:
    metadata = json.load(data_file)

# process
process = []
memo = []
shared_resource = {}

# id
id = 0

# Result
chart = []
model = []

# init
for key, data in metadata.iteritems():
    if data['type'] == 'input':
        process.append(data)

while len(process) > 0:
    current = process[0]
    if current['type'] == 'input':
        print "Input Module: " + current['name']
        df = pd.read_csv("Data/" + str(current['name']))
        count = 1
        if len(current['link']) > 0:
            count = len(current['link'])
        tmp = {
            'data': df,
            'count': count
        }
        shared_resource[id] = tmp
        print "-- Added New Resource ID: " + str(id)
        for link in current['link']:
            if link not in memo:
                new_data = metadata[link]
                new_data['shared_input_resource'] = []
                new_data['shared_input_resource'].append(id)
                memo.append(link)
                process.append(new_data)
            else:
                for key, cur in enumerate(process):
                    if cur['id_operation'] == link:
                        process[key]['shared_input_resource'].append(id)
                        break
        id += 1
    elif current['type'] == 'process:append':
        print "Process Module: " + current['name']
        if len(current['shared_input_resource']) == 2:
            left = shared_resource[current['shared_input_resource'][0]]['data']
            right = shared_resource[current['shared_input_resource'][1]]['data']
            df = left.append(right)
            count = 1
            if len(current['link']) > 0:
                count = len(current['link'])
            shared_resource[id] = {
                'data': df,
                'count': count
            }
            print "-- Added New Resource ID: " + str(id)
            for link in current['link']:
                if link not in memo:
                    new_data = metadata[link]
                    new_data['shared_input_resource'] = []
                    new_data['shared_input_resource'].append(id)
                    memo.append(link)
                    process.append(new_data)
                else:
                    for key, cur in enumerate(process):
                        if cur['id_operation'] == link:
                            process[key]['shared_input_resource'].append(id)
                            break

            shared_resource[current['shared_input_resource'][0]]['count'] -= 1
            shared_resource[current['shared_input_resource'][1]]['count'] -= 1

            if shared_resource[current['shared_input_resource'][0]]['count'] <= 0:
                del shared_resource[current['shared_input_resource'][0]]
            if shared_resource[current['shared_input_resource'][1]]['count'] <= 0:
                del shared_resource[current['shared_input_resource'][1]]
            id += 1
        else:
            process.append(current)
    elif current['type'] == 'process:join':
        print "Process Module: " + current['name']
        if len(current['shared_input_resource']) == 2:
            left = shared_resource[current['shared_input_resource'][0]]['data']
            right = shared_resource[current['shared_input_resource'][1]]['data']
            df = left.merge(right, left_on=current['metadata']['left'], right_on=current['metadata']['right'], how=current['metadata']['how'])
            count = 1
            if len(current['link']) > 0:
                count = len(current['link'])
            shared_resource[id] = {
                'data': df,
                'count': count
            }
            print "-- Added New Resource ID: " + str(id)
            for link in current['link']:
                if link not in memo:
                    new_data = metadata[link]
                    new_data['shared_input_resource'] = []
                    new_data['shared_input_resource'].append(id)
                    memo.append(link)
                    process.append(new_data)
                else:
                    for key, cur in enumerate(process):
                        if cur['id_operation'] == link:
                            process[key]['shared_input_resource'].append(id)
                            break
            id += 1
            shared_resource[current['shared_input_resource'][0]]['count'] -= 1
            shared_resource[current['shared_input_resource'][1]]['count'] -= 1

            if shared_resource[current['shared_input_resource'][0]]['count'] <= 0:
                del shared_resource[current['shared_input_resource'][0]]
            if shared_resource[current['shared_input_resource'][1]]['count'] <= 0:
                del shared_resource[current['shared_input_resource'][1]]
        else:
            process.append(current)
    elif current['type'] == 'process:cfilter':
        print "Process Module: " + current['name']
        input = shared_resource[current['shared_input_resource'][0]]['data']
        shared_resource[current['shared_input_resource'][0]]['count'] -= 1
        if shared_resource[current['shared_input_resource'][0]]['count'] <= 0:
            del shared_resource[current['shared_input_resource'][0]]
        desired_column = []
        for key in current['shape']:
            desired_column.append(key)
        df = input[desired_column]
        count = 1
        if len(current['link']) > 0:
            count = len(current['link'])
        shared_resource[id] = {
            'data': df,
            'count': count
        }
        print "-- Added New Resource ID: " + str(id)
        for link in current['link']:
            if link not in memo:
                new_data = metadata[link]
                new_data['shared_input_resource'] = []
                new_data['shared_input_resource'].append(id)
                memo.append(link)
                process.append(new_data)
            else:
                for key, cur in enumerate(process):
                    if cur['id_operation'] == link:
                        process[key]['shared_input_resource'].append(id)
                        break
        id += 1
    process.pop(0)
final_data = shared_resource[id - 1]['data']
print final_data.sort_values(['department', 'satisfaction_level'])[['department', 'satisfaction_level']].head(10)

print("------------------")

hr1 = pd.read_csv("Data/hr-1.csv")
hr2 = pd.read_csv("Data/hr-2.csv")
df = hr1.append(hr2)
departments = pd.read_csv("Data/hr-departments.csv")
df = df.merge(departments, left_on="department_id", right_on="department_id", how="inner")
df.drop('salary', axis=1, inplace=True)
print df.sort_values(['department', 'satisfaction_level'])[['department', 'satisfaction_level']].head(10)