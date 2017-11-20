import pandas as pd
import json


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

    def run(self):
        self.process_init()
        while len(self.process) > 0:
            current = self.process[0]
            if current['type'] == 'input':
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
                print "Process Module: " + current['name']
                if len(current['shared_input_resource']) == 2:
                    left = self.shared_resource[current['shared_input_resource'][0]]['data']
                    right = self.shared_resource[current['shared_input_resource'][1]]['data']
                    df = left.append(right)
                    count = 1
                    if len(current['link']) > 0:
                        count = len(current['link'])
                    self.shared_resource[self.id] = {
                        'data': df,
                        'count': count
                    }
                    self.generate_next_bfs(current)
                    self.shared_resource[current['shared_input_resource'][0]]['count'] -= 1
                    self.shared_resource[current['shared_input_resource'][1]]['count'] -= 1

                    if self.shared_resource[current['shared_input_resource'][0]]['count'] <= 0:
                        del self.shared_resource[current['shared_input_resource'][0]]
                    if self.shared_resource[current['shared_input_resource'][1]]['count'] <= 0:
                        del self.shared_resource[current['shared_input_resource'][1]]
                    self.id += 1
                else:
                    self.process.append(current)
            elif current['type'] == 'process:join':
                print "Process Module: " + current['name']
                if len(current['shared_input_resource']) == 2:
                    left = self.shared_resource[current['shared_input_resource'][0]]['data']
                    right = self.shared_resource[current['shared_input_resource'][1]]['data']
                    df = left.merge(right, left_on=current['metadata']['left'], right_on=current['metadata']['right'],
                                    how=current['metadata']['how'])
                    count = 1
                    if len(current['link']) > 0:
                        count = len(current['link'])
                    self.shared_resource[self.id] = {
                        'data': df,
                        'count': count
                    }
                    self.generate_next_bfs(current)
                    self.id += 1

                    self.shared_resource[current['shared_input_resource'][0]]['count'] -= 1
                    self.shared_resource[current['shared_input_resource'][1]]['count'] -= 1

                    if self.shared_resource[current['shared_input_resource'][0]]['count'] <= 0:
                        del self.shared_resource[current['shared_input_resource'][0]]
                    if self.shared_resource[current['shared_input_resource'][1]]['count'] <= 0:
                        del self.shared_resource[current['shared_input_resource'][1]]
                else:
                    self.process.append(current)
            elif current['type'] == 'process:cfilter':
                print "Process Module: " + current['name']
                input = self.shared_resource[current['shared_input_resource'][0]]['data']
                self.shared_resource[current['shared_input_resource'][0]]['count'] -= 1
                if self.shared_resource[current['shared_input_resource'][0]]['count'] <= 0:
                    del self.shared_resource[current['shared_input_resource'][0]]
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
            self.process.pop(0)

    def get_current_data(self):
        return self.shared_resource


fp = FlowProcess()
with open('Metadata/hr.json') as data_file:
    metadata = json.load(data_file)
fp.set_metadata(metadata)
fp.run()
print fp.get_current_data()
