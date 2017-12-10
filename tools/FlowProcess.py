import pandas as pd
import json
import time
import query_tools as qt
import chart_tools as ct
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
import sklearn.tree as tree
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn import svm
from sklearn.linear_model import LassoCV
import recommender.ClassifierRecommender as cr
import recommender.RegressorRecommender as rr

class FlowProcess:
    metadata = None
    # process
    process = []
    memo = []
    shared_resource = {}
    last_resource = None

    # id
    id = 0

    # Result
    chart = []
    model = []
    recommender = []

    def __init__(self):
        self.metadata = None
        self.process = []
        self.memo = []
        self.shared_resource = {}
        self.last_resource = None
        self.id = 0
        self.chart = []
        self.model = []
        recommender = []

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
                self.last_resource = self.shared_resource[current['shared_input_resource'][0]]
                del self.shared_resource[current['shared_input_resource'][0]]
            return input
        elif mode == 2:
            left = self.shared_resource[current['shared_input_resource'][0]]['data']
            right = self.shared_resource[current['shared_input_resource'][1]]['data']

            self.shared_resource[current['shared_input_resource'][0]]['count'] -= 1
            self.shared_resource[current['shared_input_resource'][1]]['count'] -= 1

            if self.shared_resource[current['shared_input_resource'][0]]['count'] <= 0:
                self.last_resource = self.shared_resource[current['shared_input_resource'][0]]
                del self.shared_resource[current['shared_input_resource'][0]]
            if self.shared_resource[current['shared_input_resource'][1]]['count'] <= 0:
                self.last_resource = self.shared_resource[current['shared_input_resource'][1]]
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
                df = pd.read_csv("dummy/" + str(current['name']))
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
            elif current['type'] == 'chart:cm':
                tools = ct.ChartTools()
                tools.clear_chart()
                input = self.extract_input(current, 1)
                tools.set_dataset(input.copy())
                title = "Correlation Matrix"
                img = tools.corr_matrix_chart(title)
                data = {
                    'title': title,
                    'img': img
                }
                self.chart.append(data)
            elif current['type'] == 'chart:scatter':
                tools = ct.ChartTools()
                tools.clear_chart()
                input = self.extract_input(current, 1)
                tools.set_dataset(input.copy())
                title = "Scatter Chart"
                img = tools.scatter_plot(current['x'], current['y'])
                data = {
                    'title': title,
                    'img': img
                }
                self.chart.append(data)
            elif current['type'] == 'chart:line':
                tools = ct.ChartTools()
                tools.clear_chart()
                input = self.extract_input(current, 1)
                tools.set_dataset(input.copy())
                title = "Line Chart"
                img = tools.line_plot(current['x'], current['y'])
                data = {
                    'title': title,
                    'img': img
                }
                self.chart.append(data)
            elif current['type'] == 'chart:bar':
                tools = ct.ChartTools()
                tools.clear_chart()
                input = self.extract_input(current, 1)
                tools.set_dataset(input.copy())
                title = "Bar Chart"
                img = tools.bar_chart(current['x'], current['y'])
                data = {
                    'title': title,
                    'img': img
                }
                self.chart.append(data)
            elif current['type'] == 'chart:pie':
                tools = ct.ChartTools()
                tools.clear_chart()
                input = self.extract_input(current, 1)
                tools.set_dataset(input.copy())
                title = "Pie Chart"
                img = tools.pie_plot(current['target'])
                data = {
                    'title': title,
                    'img': img
                }
                self.chart.append(data)
            elif current['type'] == 'chart:hist':
                tools = ct.ChartTools()
                tools.clear_chart()
                input = self.extract_input(current, 1)
                tools.set_dataset(input.copy())
                title = "Histogram"
                img = tools.hist(current['target'])
                data = {
                    'title': title,
                    'img': img
                }
                self.chart.append(data)
            elif current['type'] == 'chart:box':
                tools = ct.ChartTools()
                tools.clear_chart()
                input = self.extract_input(current, 1)
                tools.set_dataset(input.copy())
                title = "Boxplot Chart"
                img = tools.box_plot(current['target'])
                data = {
                    'title': title,
                    'img': img
                }
                self.chart.append(data)
            elif current['type'] == 'model:dt':
                input = self.extract_input(current, 1)
                clf = tree.DecisionTreeClassifier()
                x = input.drop(current['target'], axis=1)
                y = input[current['target']]
                x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
                summary = y_test.value_counts()
                support = {}
                total_data = 0
                for key, value in summary.iteritems():
                    support[key] = value
                    total_data += int(value)
                clf = tree.DecisionTreeClassifier()
                start = time.clock()
                dt = clf.fit(x_train, y_train)
                end = time.clock()
                score = dt.score(x_test, y_test)
                support_table = pd.DataFrame({"real": y_test, "predict": clf.predict(x_test)})
                support_table['correct'] = support_table['predict'] == support_table['real']
                support_table['correct'] = support_table['correct'].apply(int)
                support_metadata = {}
                for key, value in summary.iteritems():
                    tmp = support_table.groupby('real').sum()['correct'][key]
                    d = {
                        'count': float(value),
                        'conf': float(tmp),
                        'psupport': float(value) / total_data * 100, 
                        'pconf': float(tmp) / value * 100  
                    }
                    support_metadata[key] = d
                cv = cross_val_score(dt, x, y, cv=10)
                performance = cv
                objects = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                y_pos = np.arange(len(objects))
                plt.clf()
                plt.bar(y_pos, performance, align='center', alpha=0.5)
                plt.xticks(y_pos, objects)
                axes = plt.gca()
                axes.set_ylim([0, 1])
                plt.ylabel('Accuracy')
                plt.xlabel('Fold')
                plt.title('Decision Tree Cross Validation, 10 Fold')
                tools = ct.ChartTools()
                p = tools.convert_base64(plt)
                res = {
                    "name": "Decision Tree",
                    "type": "clf",
                    "cv": cv.tolist(),
                    "accuracy": float(cv.mean()),
                    "error": float(cv.std() * 2),
                    "time": end - start,
                    "support": support_metadata,
                    "score": score,
                    "cv_plot": p,
                    "total_test_data": int(total_data)
                }
                self.model.append(res)
            elif current['type'] == 'model:nb':
                input = self.extract_input(current, 1)
                clf = GaussianNB()
                x = input.drop(current['target'], axis=1)
                y = input[current['target']]
                x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
                summary = y_test.value_counts()
                support = {}
                total_data = 0
                for key, value in summary.iteritems():
                    support[key] = value
                    total_data += int(value)
                start = time.clock()
                nb = clf.fit(x_train, y_train)
                end = time.clock()
                score = nb.score(x_test, y_test)
                support_table = pd.DataFrame({"real": y_test, "predict": clf.predict(x_test)})
                support_table['correct'] = support_table['predict'] == support_table['real']
                support_table['correct'] = support_table['correct'].apply(int)
                support_metadata = {}
                for key, value in summary.iteritems():
                    tmp = support_table.groupby('real').sum()['correct'][key]
                    d = {
                        'count': float(value),
                        'conf': float(tmp),
                        'psupport': float(value) / total_data * 100, 
                        'pconf': float(tmp) / value * 100  
                    }
                    support_metadata[key] = d
                cv = cross_val_score(nb, x, y, cv=10)
                performance = cv
                objects = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                y_pos = np.arange(len(objects))
                plt.clf()
                plt.bar(y_pos, performance, align='center', alpha=0.5)
                plt.xticks(y_pos, objects)
                axes = plt.gca()
                axes.set_ylim([0, 1])
                plt.ylabel('Accuracy')
                plt.xlabel('Fold')
                plt.title('Naive Bayes Cross Validation, 10 Fold')
                tools = ct.ChartTools()
                p = tools.convert_base64(plt)
                res = {
                    "name": "Naive Bayes",
                    "type": "clf",
                    "cv": cv.tolist(),
                    "accuracy": float(cv.mean()),
                    "error": float(cv.std() * 2),
                    "time": end - start,
                    "support": support_metadata,
                    "score": score,
                    "cv_plot": p,
                    "total_test_data": int(total_data)
                }
                self.model.append(res)
            elif current['type'] == 'model:lr':
                input = self.extract_input(current, 1)
                clf = LogisticRegression()
                x = input.drop(current['target'], axis=1)
                y = input[current['target']]
                x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
                summary = y_test.value_counts()
                support = {}
                total_data = 0
                for key, value in summary.iteritems():
                    support[key] = value
                    total_data += int(value)
                start = time.clock()
                lr = clf.fit(x_train, y_train)
                end = time.clock()
                score = lr.score(x_test, y_test)
                support_table = pd.DataFrame({"real": y_test, "predict": clf.predict(x_test)})
                support_table['correct'] = support_table['predict'] == support_table['real']
                support_table['correct'] = support_table['correct'].apply(int)
                support_metadata = {}
                for key, value in summary.iteritems():
                    tmp = support_table.groupby('real').sum()['correct'][key]
                    d = {
                        'count': float(value),
                        'conf': float(tmp),
                        'psupport': float(value) / total_data * 100, 
                        'pconf': float(tmp) / value * 100  
                    }
                    support_metadata[key] = d
                cv = cross_val_score(lr, x, y, cv=10)
                performance = cv
                objects = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                y_pos = np.arange(len(objects))
                plt.clf()
                plt.bar(y_pos, performance, align='center', alpha=0.5)
                plt.xticks(y_pos, objects)
                axes = plt.gca()
                axes.set_ylim([0, 1])
                plt.ylabel('Accuracy')
                plt.xlabel('Fold')
                plt.title('Logistic Regression Cross Validation, 10 Fold')
                tools = ct.ChartTools()
                p = tools.convert_base64(plt)
                res = {
                    "name": "Logistic Regression",
                    "type": "clf",
                    "cv": cv.tolist(),
                    "accuracy": float(cv.mean()),
                    "error": float(cv.std() * 2),
                    "time": end - start,
                    "support": support_metadata,
                    "score": score,
                    "cv_plot": p,
                    "total_test_data": int(total_data)
                }
                self.model.append(res)
            elif current['type'] == 'model:rt':
                input = self.extract_input(current, 1)
                desc = input.describe()
                regressor = tree.DecisionTreeRegressor()
                x = input.drop(current['target'], axis=1)
                y = input[current['target']]
                regressor.fit(x, y)
                rmse= np.sqrt(-cross_val_score(regressor, x, y, scoring="neg_mean_squared_error", cv = 10))

                objects = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                y_pos = np.arange(len(objects))
                performance = rmse
                
                plt.clf()
                plt.bar(y_pos, performance, align='center', alpha=0.5)
                plt.xticks(y_pos, objects)
                plt.ylabel('RMSE')
                plt.xlabel('Fold')
                plt.title('Regression Tree Cross Validation, 10 Fold')
                
                tools = ct.ChartTools()
                p = tools.convert_base64(plt)
                res = {
                    'name': 'Regression Tree',
                    "type": "regressor",
                    'desc': desc.to_dict()[current['target']],
                    'accuracy': rmse.mean(),
                    'std_dev': rmse.std(),
                    'cv_plot': p,
                }
                self.model.append(res)
            elif current['type'] == 'model:svr':
                input = self.extract_input(current, 1)
                desc = input.describe()
                regressor = svm.SVR()
                x = input.drop(current['target'], axis=1)
                y = input[current['target']]
                regressor.fit(x, y)
                rmse= np.sqrt(-cross_val_score(regressor, x, y, scoring="neg_mean_squared_error", cv = 10))

                objects = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                y_pos = np.arange(len(objects))
                performance = rmse
                
                plt.clf()
                plt.bar(y_pos, performance, align='center', alpha=0.5)
                plt.xticks(y_pos, objects)
                plt.ylabel('RMSE')
                plt.xlabel('Fold')
                plt.title('Support Vector Regressor Cross Validation, 10 Fold')
                
                tools = ct.ChartTools()
                p = tools.convert_base64(plt)
                res = {
                    'name': 'Support Vector Regressor',
                    "type": "regressor",
                    'desc': desc.to_dict()[current['target']],
                    'accuracy': rmse.mean(),
                    'std_dev': rmse.std(),
                    'cv_plot': p,
                }
                self.model.append(res)
            elif current['type'] == 'model:lasso':
                input = self.extract_input(current, 1)
                desc = input.describe()
                x = input.drop(current['target'], axis=1)
                y = input[current['target']]
                regressor = LassoCV(alphas=[1, 0.1, 0.001, 0.0005]).fit(x, y)
                rmse= np.sqrt(-cross_val_score(regressor, x, y, scoring="neg_mean_squared_error", cv = 10))

                objects = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                y_pos = np.arange(len(objects))
                performance = rmse
                
                plt.clf()
                plt.bar(y_pos, performance, align='center', alpha=0.5)
                plt.xticks(y_pos, objects)
                plt.ylabel('RMSE')
                plt.xlabel('Fold')
                plt.title('Lasso Regression Cross Validation, 10 Fold')
                
                tools = ct.ChartTools()
                p = tools.convert_base64(plt)
                res = {
                    'name': 'Lasso Regression',
                    "type": "regressor",
                    'desc': desc.to_dict()[current['target']],
                    'accuracy': rmse.mean(),
                    'std_dev': rmse.std(),
                    'cv_plot': p,
                }
                self.model.append(res)
            elif current['type'] == 'recommender:regressor':
                input = self.extract_input(current, 1)

                row = input.shape[0]
                percent = float(current['sample_size']) / 100
                y = df[current['target']]

                if current['sample_type'] == 'random':
                    df = input.sample(int(row * percent))
                else:
                    bins = np.linspace(0, y.shape[0], 5)
                    y_binned = np.digitize(y, bins)
                    x_train, x_test, y_train, y_test = train_test_split(df, y, test_size=percent, stratify=y_binned)
                    df = x_test

                rec = rr.RegressorRecommender()
                rec.set_data(input.copy())
                rec.define_target(current['target'])
                rec.run()
                res = rec.sort('rmse')

                for key, value in enumerate(res):
                    objects = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                    y_pos = np.arange(len(objects))
                    performance = value['cv']
                    
                    plt.clf()
                    plt.bar(y_pos, performance, align='center', alpha=0.5)
                    plt.xticks(y_pos, objects)
                    plt.ylabel('RMSE')
                    plt.xlabel('Fold')
                    plt.title('Cross Validation, 10 Fold')
                    
                    tools = ct.ChartTools()
                    p = tools.convert_base64(plt)

                    res[key]['cv_plot'] = p
                    res[key]['type'] = 'regressor'

                self.recommender = res
            elif current['type'] == 'recommender:classifier':
                input = self.extract_input(current, 1)

                row = input.shape[0]
                percent = float(current['sample_size']) / 100
                y = df[current['target']]

                if current['sample_type'] == 'random':
                    df = input.sample(int(row * percent))
                else:
                    x_train, x_test, y_train, y_test = train_test_split(df, y, test_size=percent)
                    df = x_test

                rec = cr.ClassifierRecommender()
                rec.set_data(df.copy())
                rec.define_target(current['target'])
                rec.run()
                res = rec.sort('accuracy')

                for key, value in enumerate(res):
                    objects = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                    y_pos = np.arange(len(objects))
                    performance = value['cv']
                    
                    plt.clf()
                    plt.bar(y_pos, performance, align='center', alpha=0.5)
                    plt.xticks(y_pos, objects)
                    plt.ylabel('Accuracy')
                    plt.xlabel('Fold')
                    plt.title('Cross Validation, 10 Fold')
                    
                    tools = ct.ChartTools()
                    p = tools.convert_base64(plt)

                    res[key]['cv_plot'] = p
                    res[key]['type'] = 'classifier'
                self.recommender = res
            self.process.pop(0)
        if len(self.shared_resource) == 0:
            self.shared_resource[self.id] = self.last_resource
            self.id += 1

    def get_current_data(self):
        return self.shared_resource

    def get_chart(self):
        return self.chart

    def get_model(self):
        return self.model

    def get_recommender(self):
        return self.recommender
