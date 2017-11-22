from flask import Flask, render_template, request, session, redirect, url_for, make_response, jsonify, abort, send_file
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import pandas as pd
import json

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
    data_tables = []
    co = 1
    for key, value in data.iteritems():
        data_tables.append({
            'count': co,
            'table': value['data'].head(10).to_html(classes='table table-hover')
        })
        co += 1
    return jsonify({
        'data': data_tables,
        'chart': chart
    })


if __name__ == '__main__':
    app.run(debug=True)
