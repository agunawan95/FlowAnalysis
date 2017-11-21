import pandas as pd
import json
import query_tools as qt


class FlowProcess:
    metadata = None
    # process
    process = []
    memo = []
    shared_resource = {}

    # id
    id = 0

    # Result
    chart = []
    model = []

    def __init__(self):
        self.id = 0

    def set_metadata(self, metadata):
        '''
        Set JSON Metadata From Workspace (in Dict Format)
        :param metadata: Dict
        :return: None
        '''
        self.metadata = metadata

    def process_init(self):
        '''
        Initialization of Process
        :return:
        '''
        for key, data in self.metadata.iteritems():
            if data['type'] == 'input':
                self.process.append(data)

    def generate_next_bfs(self, current):
        for link in current['link']:
            if link not in self.memo:
                new_data = self.metadata[link]
                new_data['shared_input_resource'] = []
                new_data['shared_input_resource'].append(self.id)
                self.memo.append(link)
                self.process.append(new_data)
            else:
                for key, cur in enumerate(self.process):
                    if cur['id_operation'] == link:
                        self.process[key]['shared_input_resource'].append(self.id)
                        break

    def extract_input(self, current, mode):
        if mode == 1:
            input = self.shared_resource[current['shared_input_resource'][0]]['data']
            self.shared_resource[current['shared_input_resource'][0]]['count'] -= 1
            if self.shared_resource[current['shared_input_resource'][0]]['count'] <= 0:
                del self.shared_resource[current['shared_input_resource'][0]]
            return input
        elif mode == 2:
            left = self.shared_resource[current['shared_input_resource'][0]]['data']
            right = self.shared_resource[current['shared_input_resource'][1]]['data']

            self.shared_resource[current['shared_input_resource'][0]]['count'] -= 1
            self.shared_resource[current['shared_input_resource'][1]]['count'] -= 1

            if self.shared_resource[current['shared_input_resource'][0]]['count'] <= 0:
                del self.shared_resource[current['shared_input_resource'][0]]
            if self.shared_resource[current['shared_input_resource'][1]]['count'] <= 0:
                del self.shared_resource[current['shared_input_resource'][1]]
            return left, right
        else:
            return None

    def run(self):
        self.process_init()
        while len(self.process) > 0:
            current = self.process[0]
            if current['type'] == 'input':
                # Todo Change Input Condition
                df = pd.read_csv("Data/" + str(current['name']))
                count = 1
                if len(current['link']) > 0:
                    count = len(current['link'])
                tmp = {
                    'data': df,
                    'count': count
                }
                self.shared_resource[self.id] = tmp
                self.generate_next_bfs(current)
                self.id += 1
            elif current['type'] == 'process:append':
                if len(current['shared_input_resource']) == 2:
                    left, right = self.extract_input(current, 2)
                    df = left.append(right)
                    count = 1
                    if len(current['link']) > 0:
                        count = len(current['link'])
                    self.shared_resource[self.id] = {
                        'data': df,
                        'count': count
                    }
                    self.generate_next_bfs(current)
                    self.id += 1
                else:
                    self.process.append(current)
            elif current['type'] == 'process:join':
                if len(current['shared_input_resource']) == 2:
                    left, right = self.extract_input(current, 2)

                    df = left.merge(right, left_on=current['metadata']['left'], right_on=current['metadata']['right'], how=current['metadata']['how'])
                    count = 1
                    if len(current['link']) > 0:
                        count = len(current['link'])
                    self.shared_resource[self.id] = {
                        'data': df,
                        'count': count
                    }
                    self.generate_next_bfs(current)
                    self.id += 1
                else:
                    self.process.append(current)
            elif current['type'] == 'process:cfilter':
                input = self.extract_input(current, 1)
                desired_column = []
                for key in current['shape']:
                    desired_column.append(key)
                df = input[desired_column]
                count = 1
                if len(current['link']) > 0:
                    count = len(current['link'])
                self.shared_resource[self.id] = {
                    'data': df,
                    'count': count
                }
                self.generate_next_bfs(current)
                self.id += 1
            elif current['type'] == 'process:filter':
                tools = qt.QueryTools()
                input = self.extract_input(current, 1)
                tools.set_dataset(input.copy())
                tools.set_condition(current['query'])
                df = tools.get_filter()
                count = 1
                if len(current['link']) > 0:
                    count = len(current['link'])
                self.shared_resource[self.id] = {
                    'data': df,
                    'count': count
                }
                self.generate_next_bfs(current)
                self.id += 1
            elif current['type'] == 'process:update-value':
                tools = qt.QueryTools()
                input = self.extract_input(current, 1)
                tools.set_dataset(input.copy())
                tools.set_condition(current['query'])
                into = current['into']
                if input[current['target']].dtype == 'int64':
                    into = int(into)
                elif input[current['target']].dtype == 'float64':
                    into = float(into)
                elif input[current['target']].dtype == 'object':
                    into = str(into)
                tools.update(current['target'], into)
                df = tools.data_frame()
                count = 1
                if len(current['link']) > 0:
                    count = len(current['link'])
                self.shared_resource[self.id] = {
                    'data': df,
                    'count': count
                }
                self.generate_next_bfs(current)
                self.id += 1
            elif current['type'] == 'process:update-column':
                tools = qt.QueryTools()
                input = self.extract_input(current, 1)
                tools.set_dataset(input.copy())
                tools.set_condition(current['query'])
                into = input[current['into']]
                tools.update(current['target'], into)
                df = tools.data_frame()
                count = 1
                if len(current['link']) > 0:
                    count = len(current['link'])
                self.shared_resource[self.id] = {
                    'data': df,
                    'count': count
                }
                self.generate_next_bfs(current)
                self.id += 1
            elif current['type'] == 'process:delete':
                tools = qt.QueryTools()
                input = self.extract_input(current, 1)
                tools.set_dataset(input.copy())
                tools.set_condition(current['query'])
                tools.delete()
                df = tools.data_frame()
                count = 1
                if len(current['link']) > 0:
                    count = len(current['link'])
                self.shared_resource[self.id] = {
                    'data': df,
                    'count': count
                }
                self.generate_next_bfs(current)
                self.id += 1
            elif current['type'] == 'process:aggregate':
                tools = qt.QueryTools()
                input = self.extract_input(current, 1)
                tools.set_dataset(input.copy())
                gb = []
                if ',' in str(current['group_by']).strip():
                    gb = str(current['group_by']).strip().split(',')
                else:
                    gb.append(str(current['group_by']))
                df = tools.get_aggregate(gb, current['function'], current['target'])
                count = 1
                if len(current['link']) > 0:
                    count = len(current['link'])
                self.shared_resource[self.id] = {
                    'data': df,
                    'count': count
                }
                self.generate_next_bfs(current)
                self.id += 1
            elif current['type'] == 'process:formula':
                tools = qt.QueryTools()
                input = self.extract_input(current, 1)
                tools.set_dataset(input.copy())
                tools.execute_formula(current['formula'], current['new_name'])
                df = tools.data_frame()
                count = 1
                if len(current['link']) > 0:
                    count = len(current['link'])
                self.shared_resource[self.id] = {
                    'data': df,
                    'count': count
                }
                self.generate_next_bfs(current)
                self.id += 1
            elif current['type'] == 'process:factorize':
                input = self.extract_input(current, 1)
                df = input.copy()
                df[current['target']] = pd.factorize(input[current['target']])[0]
                count = 1
                if len(current['link']) > 0:
                    count = len(current['link'])
                self.shared_resource[self.id] = {
                    'data': df,
                    'count': count
                }
                self.generate_next_bfs(current)
                self.id += 1
            elif current['type'] == 'process:fillna-aggregate':
                input = self.extract_input(current, 1)
                f = current['function']
                df = pd.DataFrame()
                if f == 'sum':
                    df = input.fillna(input[current['target']].sum())
                elif f == 'avg':
                    df = input.fillna(input[current['target']].mean())
                elif f == 'count':
                    df = input.fillna(input[current['target']].count())
                elif f == 'std':
                    df = input.fillna(input[current['target']].std())
                elif f == 'max':
                    df = input.fillna(input[current['target']].max())
                elif f == 'min':
                    df = input.fillna(input[current['target']].min())
                count = 1
                if len(current['link']) > 0:
                    count = len(current['link'])
                self.shared_resource[self.id] = {
                    'data': df,
                    'count': count
                }
                self.generate_next_bfs(current)
                self.id += 1
            elif current['type'] == 'process:fillna-oc':
                input = self.extract_input(current, 1)
                df = input.copy()
                df[current['target']].fillna(df[current['other']])
                count = 1
                if len(current['link']) > 0:
                    count = len(current['link'])
                self.shared_resource[self.id] = {
                    'data': df,
                    'count': count
                }
                self.generate_next_bfs(current)
                self.id += 1
            elif current['type'] == 'process:fillna-value':
                input = self.extract_input(current, 1)
                df = input.copy()
                into = df[current['value']]
                if input.dtype[current['target']] == 'int64':
                    into = int(into)
                elif input.dtype[current['target']] == 'float64':
                    into = float(into)
                elif input.dtype[current['target']] == 'object':
                    into = str(into)
                df[current['target']].fillna(into)
                count = 1
                if len(current['link']) > 0:
                    count = len(current['link'])
                self.shared_resource[self.id] = {
                    'data': df,
                    'count': count
                }
                self.generate_next_bfs(current)
                self.id += 1
            self.process.pop(0)

    def get_current_data(self):
        return self.shared_resource


fp = FlowProcess()
with open('Metadata/hr-test.json') as data_file:
    metadata = json.load(data_file)
fp.set_metadata(metadata)
fp.run()
tmp = fp.get_current_data()[5]['data']
tmp.to_csv("meong.csv")
