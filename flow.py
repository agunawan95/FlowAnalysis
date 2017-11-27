from flask import Flask, render_template, request, session, redirect, url_for, make_response, jsonify, abort, send_file
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import pandas as pd
import json
import base64

import tools.FlowProcess as fp

app = Flask(__name__)


@app.route("/")
def main():
    return render_template("flow.html")


@app.route("/project")
def project():
    return render_template("project_dashboard.html")


@app.route("/api/file/metadata/<id>")
def file_metadata(id=None):
    df = None
    id = int(id)
    if id == 1:
        df = pd.read_csv('dummy/hr-1.csv')
    elif id == 2:
        df = pd.read_csv('dummy/hr-2.csv')
    elif id == 3:
        df = pd.read_csv('dummy/west_nile.csv')
    elif id == 4:
        df = pd.read_csv('dummy/west_nile_weather.csv')
    elif id == 5:
        df = pd.read_csv('dummy/hr-departments.csv')
    return jsonify(df.dtypes.apply(lambda x: x.name).to_dict())


@app.route("/api/file/query/metadata/<id>")
def file_query_metadata(id=None):
    df = pd.read_csv('dummy/hr-1.csv')
    res = []
    for key, value in df.dtypes.apply(lambda x: x.name).to_dict().iteritems():
        tmp = {}
        if "int" in value:
            tmp = {
                'id': key,
                'label': key,
                'type': 'integer'
            }
        elif "float" in value or 'double' in value:
            tmp = {
                'id': key,
                'label': key,
                'type': 'double'
            }
        elif "object" in value:
            tmp = {
                'id': key,
                'label': key,
                'type': 'string'
            }
        res.append(tmp)
    return jsonify(res)


@app.route("/api/query/metadata", methods=['POST'])
def generate_query_metadata():
    res = []
    if request.method == 'POST':
        data = request.json['data']
        for key, value in data.iteritems():
            tmp = {}
            if "int" in value:
                tmp = {
                    'id': key,
                    'label': key,
                    'type': 'integer'
                }
            elif "float" in value or 'double' in value:
                tmp = {
                    'id': key,
                    'label': key,
                    'type': 'double'
                }
            elif "object" in value:
                tmp = {
                    'id': key,
                    'label': key,
                    'type': 'string'
                }
            res.append(tmp)
    return jsonify(res)


@app.route("/report", methods=['POST'])
def report():
    metadata = str(request.form['metadata']).encode('utf8')
    return render_template("report.html", metadata=metadata)


@app.route("/api/run", methods=['POST'])
def run():
    metadata = json.loads(request.form['metadata'])
    tools = fp.FlowProcess()
    tools.set_metadata(metadata)
    tools.run()
    data = tools.get_current_data()
    chart = tools.get_chart()
    model = tools.get_model()
    data_tables = []
    co = 1
    for key, value in data.iteritems():
        descat = ''
        desnum = ''
        if len(value['data'][value['data'].columns[value['data'].dtypes == "object"]].columns) > 0:
            descat = value['data'][value['data'].columns[value['data'].dtypes == "object"]].describe().to_html(classes='table table-hover table-bordered')
        if len(value['data'][value['data'].columns[value['data'].dtypes == "int64"]].columns) > 0 or len(value['data'][value['data'].columns[value['data'].dtypes == "float64"]].columns) > 0:
            desnum = value['data'].describe().to_html(classes='table table-hover table-bordered')
        data_tables.append({
            'count': co,
            'table': value['data'].head(10).to_html(classes='table table-hover table-bordered'),
            'describe_numeric': desnum,
            'describe_categorical': descat
        })
        co += 1
    model_html = []
    for val in model:
        model_html.append(render_template("report/classifier.html", data=val))
    return jsonify({
        'data_html': render_template('report/data_list.html', data=data_tables),
        'chart': chart,
        'model': model,
        'model_html': model_html
    })


@app.route('/api/downloadbase64', methods=['POST'])
def downloadbase64():
    data = request.form['img']
    data = data.replace('data:image/png;base64,', '')
    img = base64.b64decode(data)
    response = make_response(img)
    response.headers['Content-Type'] = 'image/jpeg'
    response.headers['Content-Disposition'] = 'attachment; filename=img.jpg'
    return response


if __name__ == '__main__':
    app.run(debug=True)
