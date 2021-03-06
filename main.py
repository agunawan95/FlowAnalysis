from flask import Flask, render_template, request, session, redirect, url_for, make_response, jsonify, abort, send_file
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import pandas as pd
from flask_cors import CORS, cross_origin
import json
import base64
import io

import tools.FlowProcess as fp

# --------------------------------------------------------------------------------------
# ===================================== Helper Class ===================================
# --------------------------------------------------------------------------------------

import user
import files as fl
import enterprise
import log
import project

# ======================================================================================


# --------------------------------------------------------------------------------------
# ==================================== Configuration ===================================
# --------------------------------------------------------------------------------------

UPLOAD_FOLDER = '/upload'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "bluebutterfly"

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


@app.context_processor
def utility_processor():
    def file_size(file_path):
        """
        this function will return the file size
        """
        if os.path.isfile(file_path):
            file_info = os.stat(file_path)
            return convert_bytes(file_info.st_size)
    return dict(filesize=file_size)

# ======================================================================================

# --------------------------------------------------------------------------------------
# ===================================== Error Pages ====================================
# --------------------------------------------------------------------------------------


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

# ======================================================================================


# --------------------------------------------------------------------------------------
# ================================== View Controller ===================================
# --------------------------------------------------------------------------------------

# --Utility

@app.route("/")
def main():
    if session.get("login") is None:
        return redirect("/login")
    session['page'] = 'home'
    user_helper = user.User()
    user_helper.load_user(session['id'])
    usr = user_helper.get_data()
    do_intro = False
    if usr['first_login'] == 0:
        do_intro = True
        user_helper.update_intro(session['id'])
    return render_template("main.html", do_intro=do_intro)


@app.route("/login", methods=['GET', 'POST'])
def login():
    user_helper = user.User()
    err = False
    msg = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if user_helper.login(username, password):
            u = user_helper.get_data()
            session['login'] = True
            session['username'] = request.form["username"]
            session['id'] = u['id']
            session['auth'] = u['auth']
            return redirect("/")
        else:
            err = True
            msg = user_helper.err_msg()
    return render_template("login.html", err=err, msg=msg)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -- Users


@app.route('/users/', defaults={'page': 1})
@app.route('/users/page/<int:page>')
def users(page):
    if session.get("login") is None:
        return redirect("/login")

    user_helper = user.User()

    all_user = None
    if session['auth'] == 'root':
        all_user = user_helper.get_all_admin()
    elif session['auth'] == 'admin':
        all_user = user_helper.get_enterprise_user(session['id'])
    session['page'] = 'users'
    return render_template("users.html", users=all_user, page_count=int(user_helper.get_page_count()), page=page)


@app.route('/users/s/<query>')
def users_search(query=None):
    err = 0
    msg = ''

    if session.get("login") is None:
        return redirect("/login")

    user_helper = user.User()

    users = None
    if session['auth'] == 'root':
        users = user_helper.search_admin(query)
    elif session['auth'] == 'admin':
        users = user_helper.search_user(query, session['id'])
    session['page'] = 'users'
    return render_template("users.html", users=users, page_count=0, page=0)


@app.route('/users/s/')
def redirect_user():
    return redirect("/users")

# -- Files

@app.route('/files/', defaults={'page': 1})
@app.route('/files/page/<int:page>')
def files(page):
    session['page'] = 'files'

    user_helper = user.User()
    file_helper = fl.Files()

    if session.get("login") is None:
        return redirect("/login")

    user_file = file_helper.user_file(session['id'])

    return render_template("files.html", files=user_file)

@app.route('/files/s/<query>')
def files_search(query=None):
    err = 0
    msg = ''

    if session.get("login") is None:
        return redirect("/login")

    file_helper = fl.Files()

    files = file_helper.search_file(session['id'], query)
    return render_template("files.html", files=files)


@app.route('/files/s/')
def redirect_files():
    return redirect("/files")


@app.route('/shared/', defaults={'page': 1})
@app.route('/shared/page/<int:page>')
def shared_page(page):
    session['page'] = 'files'

    user_helper = user.User()
    file_helper = fl.Files()

    if session.get("login") is None:
        return redirect("/login")

    user_file = file_helper.get_shared_file(session['id'])

    return render_template("shared_files.html", files=user_file)

@app.route('/shared/s/<query>')
def shared_search(query=None):
    err = 0
    msg = ''

    if session.get("login") is None:
        return redirect("/login")

    file_helper = fl.Files()

    files = file_helper.search_shared_file(session['id'], query)
    return render_template("shared_files.html", files=files)


@app.route('/shared/s/')
def redirect_shared():
    return redirect("/shared")


@app.route("/recycle")
def recycle():
    if session.get("login") is None:
        return redirect("/login")
    if session.get("auth") is "user":
        return redirect("/")

    file_helper = fl.Files()
    files = file_helper.get_recycle_bin(session['id'])

    return render_template("recycle.html", files=files)

@app.route('/recycle/s/<query>')
def recycle_search(query=None):
    err = 0
    msg = ''

    if session.get("login") is None:
        return redirect("/login")

    file_helper = fl.Files()

    files = file_helper.search_recycle(session['id'], query)
    return render_template("recycle.html", files=files)


@app.route('/recycle/s/')
def redirect_recycle():
    return redirect("/recycle")


# -- Projects
@app.route("/projects")
def projects():
    if session.get("login") is None:
        return redirect("/login")
    project_helper = project.Project()
    all_project = {}
    all_project = project_helper.get_user_project(session['id'])
    return render_template("projects.html", projects=all_project)


@app.route("/projects/<id>")
def project_dashboard(id):
    if session.get("login") is None:
        return redirect("/login")
    user_helper = user.User()
    user_helper.load_user(session['id'])
    home_folder = user_helper.get_data()['home_folder']
    project_helper = project.Project()
    all_data = project_helper.scan_project(home_folder, id)
    p = project_helper.get_project(id)
    charts = []
    for chart in all_data['charts']:
        target = "upload/" + home_folder + "/projects/" + p['name'] + "/charts/" + chart  
        with open(target, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            charts.append("data:image/png;base64," + encoded_string)
    return render_template("project_dashboard.html", charts=charts, data=p)

@app.route("/workspace/<id>")
def workspace(id):
    file_helper = fl.Files()
    user_file = file_helper.user_file(session['id'])
    
    user_helper = user.User()
    user_helper.load_user(session['id'])
    home_folder = user_helper.get_data()['home_folder']

    project_helper = project.Project()
    p = project_helper.get_project(id)

    load_project = 0
    metadata = {}
    schema = {}

    basedir = os.getcwd()
    if os.path.exists(basedir + app.config['UPLOAD_FOLDER'] + "/" + home_folder + "/projects/" + p['name'] + "/metadata.json"):
        if os.path.exists(basedir + app.config['UPLOAD_FOLDER'] + "/" + home_folder + "/projects/" + p['name'] + "/schema.json"):
            metadata = json.load(open(basedir + app.config['UPLOAD_FOLDER'] + "/" + home_folder + "/projects/" + p['name'] + "/metadata.json"))
            schema = json.load(open(basedir + app.config['UPLOAD_FOLDER'] + "/" + home_folder + "/projects/" + p['name'] + "/schema.json"))
            load_project = 1
    return render_template("flow.html", user_file=user_file, id=id, load_project=load_project, metadata=json.dumps(metadata), schema=json.dumps(schema))

@app.route("/api/save/workspace", methods=['POST'])
def save_workspace():
    metadata = request.form['metadata']
    schema = request.form['schema']
    id = request.form['id']

    user_helper = user.User()
    user_helper.load_user(session['id'])
    home_folder = user_helper.get_data()['home_folder']
    
    project_helper = project.Project()
    p = project_helper.get_project(id)
    
    target = 'upload/' + home_folder + "/projects/" + p['name'] + '/'

    with io.open(target + 'metadata.json', 'w', encoding='utf-8') as f:
        f.write(metadata)
    with io.open(target + 'schema.json', 'w', encoding='utf-8') as f:
        f.write(schema)
    return jsonify({
        "err": 0
    })
    

@app.route("/api/file/metadata/<id>")
def file_metadata(id=None):
    df = None
    id = int(id)
    file_helper = fl.Files()
    file_helper.load_file(id)
    target = file_helper.get_data()
    df = pd.read_csv("upload/" + target['location'])
    return jsonify(df.dtypes.apply(lambda x: x.name).to_dict())

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


@app.route("/recomend", methods=['POST'])
def recommender():
    metadata = str(request.form['metadata']).encode('utf8')
    return render_template("recomender.html", metadata=metadata)

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
            desnum = value['data'].describe().to_html(classes='table table-hover table-bordered desc-num')
        data_tables.append({
            'count': co,
            'table': value['data'].head(10).to_html(classes='table table-hover table-bordered data-finished'),
            'describe_numeric': desnum,
            'describe_categorical': descat
        })
        co += 1
    model_html = []
    for val in model:
        if val['type'] == 'clf':
            model_html.append(render_template("report/classifier.html", data=val))
        elif val['type'] == 'regressor':
            model_html.append(render_template("report/regressor.html", data=val))
    return jsonify({
        'data_html': render_template('report/data_list.html', data=data_tables),
        'chart': chart,
        'model': model,
        'model_html': model_html
    })

@app.route("/api/recommend", methods=['POST'])
def recommend():
    metadata = json.loads(request.form['metadata'])
    tools = fp.FlowProcess()
    tools.set_metadata(metadata)
    tools.run()
    res = tools.get_recommender()
    rank = []
    for key, value in enumerate(res):
        value['rank'] = key + 1
        value['report'] = ''
        
        rank.append(render_template('recommender/recomended.html', data=value))
    return jsonify({
        'rank_result': rank
    })

# ======================================================================================


# --------------------------------------------------------------------------------------
# ======================================== API =========================================
# --------------------------------------------------------------------------------------

@app.route("/api/users", methods=['POST'])
def add_user():
    user_helper = user.User()

    err = 0
    msg = ''

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        auth = ''
        admin = 0
        if session['auth'] == 'root':
            auth = 'admin'
        elif session['auth'] == 'admin':
            auth = 'user'
            admin = session['id']
        if confirm is not password:
            err = 1
            msg = "Confirm Password Incorrect"

        if user_helper.add_user(username, password, email, auth, admin):
            if auth == "admin":
                # Add Enterprise Data
                name = request.form['enterprise_name']
                address = request.form['enterprise_address']
                email = request.form['enterprise_email']
                phone = request.form['enterprise_phone']
                filesize = request.form['enterprise_filesize']
                user_limit = request.form['enterprise_user']
                enterprise_helper = enterprise.Enterprise()

                u = user_helper.get_by_username(username)

                if enterprise_helper.add_enterprise(name, address, email, phone, filesize, user_limit, u['id']):
                    err = 0
                    msg = "Success"
                else:
                    err = 1
                    msg = "Failed"
        else:
            err = 1
            msg = user_helper.err_msg()
    return jsonify({
        'err': err,
        'msg': msg
    })


@app.route("/api/users/<id>", methods=['GET'])
def get_user(id):
    user_helper = user.User()

    if session.get("login") is None:
        abort(403)

    id_session = session['id']
    user_helper.load_user(id_session)
    data = user_helper.get_data()

    if data['auth'] == 'user':
        abort(403)
    if id is not None:
        res = user_helper.load_user(id)
        if res is False:
            abort(404)
        if res['auth'] == 'root':
            abort(403)
        if res['auth'] == 'admin':
            enterprise_helper = enterprise.Enterprise()
            res['enterprise'] = enterprise_helper.get_enterprise_by_user(res['id'])
        return jsonify(res)
    else:
        return jsonify({"err": 1, "msg": "Must Have ID"})


@app.route("/api/users/<id>", methods=['DELETE'])
def delete_user(id):
    user_helper = user.User()

    if session.get("login") is None:
        abort(403)

    id_session = session['id']
    user_helper.load_user(id_session)
    data = user_helper.get_data()

    if data['auth'] == 'user':
        abort(403)

    user_helper.load_user(id)
    res = user_helper.get_data()
    if res['auth'] == 'user':
        f = fl.Files()
        f.transfer_protocol(id, res['admin'])

    if user_helper.delete_user(id):
        return jsonify({"err": 0, "msg": "Success"})
    else:
        return jsonify({"err": 1, "msg": user_helper.err_msg()})


@app.route("/api/users/<id>", methods=['PUT'])
def update_user(id):
    user_helper = user.User()

    password = request.form['password']
    confirm = request.form['confirm']

    if password != '':
        if password == confirm:
            if not user_helper.change_password(id, password):
                return jsonify({"err": 1, "msg": user_helper.err_msg()})
        else:
            return jsonify({"err": 1, "msg": "Detected Password Change but Wrong Confirmation Password"})

    user_helper.load_user(id)
    data = user_helper.get_data()

    if data['auth'] == 'admin':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        filesize = request.form['filesize']
        user_limit = request.form['user_limit']

        enterprise_helper = enterprise.Enterprise()
        if not enterprise_helper.update_enterprise(data['id'], name, address, email, phone, filesize, user_limit):
            return jsonify({"err": 1, "msg": enterprise_helper.error_msg()})

    return jsonify({"err": 0, "msg": "Success"})

# -- Files

@app.route("/api/upload", methods=['POST'])
def add_files():
    enterprise_helper = enterprise.Enterprise()
    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({
            "err": 1,
            "msg": "No File Part " + str(request.files)
        })
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        return jsonify({
            "err": 1,
            "msg": "No Selected File"
        })

    if file and allowed_file(file.filename):
        file_helper = fl.Files()
        user_helper = user.User()
        user_helper.load_user(session['id'])
        user_data = user_helper.get_data()
        filename = secure_filename(file.filename)
        basedir = os.getcwd()
        if not os.path.exists(basedir + app.config['UPLOAD_FOLDER'] + "/" + user_data['home_folder']):
            os.makedirs(basedir + app.config['UPLOAD_FOLDER'] + "/" + user_data['home_folder'])
        if not os.path.exists(basedir + app.config['UPLOAD_FOLDER'] + "/" + user_data['home_folder'] + "/files"):
            os.makedirs(basedir + app.config['UPLOAD_FOLDER'] + "/" + user_data['home_folder'] + "/files")
        if not os.path.exists(basedir + app.config['UPLOAD_FOLDER'] + "/" + user_data['home_folder'] + "/project"):
            os.makedirs(basedir + app.config['UPLOAD_FOLDER'] + "/" + user_data['home_folder'] + "/project")
        target = basedir + app.config['UPLOAD_FOLDER'] + "/" + user_data['home_folder'] + "/files"
        file.save(os.path.join(target, filename))
        file_helper.add_file(filename, session['id'], user_data['home_folder'] + "/files/" + filename)
        return jsonify({
            "err": 0,
            "msg": "Upload File Success",
            "filename": file.filename
        })
    else:
        return jsonify({
            "err": 1,
            "msg": "Extension not Allowed"
        })

@app.route("/api/download/<id>", methods=['GET'])
def download(id=None):
    if session.get("login") is None:
        return redirect("/login")
    if session.get("lock") is True:
        return redirect("/lock")

    file_helper = fl.Files()
    file_helper.load_file(id)
    data = file_helper.get_data()

    # Add Security File Owner
    if data['owner'] is not session['id']:
        # Check if File Shared
        if not file_helper.check_shared(session['id'], id):
            abort(403)

    basedir = os.getcwd()
    path = basedir + app.config['UPLOAD_FOLDER'] + "/" + data['location']
    return send_file(path, as_attachment=True)


@app.route("/api/recycle", methods=['POST'])
def recycle_file():
    if session.get("login") is None:
        return redirect("/login")
    if session.get("lock") is True:
        return redirect("/lock")

    id_file = request.form['id_file']
    id_admin = 0
    if session['auth'] == 'user':
        user_helper = user.User()
        user_helper.load_user(session['id'])
        user_data = user_helper.get_data()
        id_admin = user_data['admin']
    else:
        id_admin = session['id']

    file_helper = fl.Files()
    if file_helper.recycle_file(id_file, id_admin):
        return jsonify({"err": 0, "msg": "Success"})
    else:
        return jsonify({"err": 1, "msg": file_helper.err_msg()})


@app.route("/api/shareable/<id_file>")
def shareable_file(id_file=None):
    if session.get("login") is None:
        return redirect("/login")
    if session.get("lock") is True:
        return redirect("/lock")

    file_helper = fl.Files()

    file_helper.load_file(id_file)
    f = file_helper.get_data()
    if f['owner'] is not session['id']:
        abort(403)

    data = file_helper.search_shareable_user(session['id'], id_file)
    return jsonify(data)


@app.route("/api/share/detail/<id_file>")
def share_detail(id_file=None):
    if session.get("login") is None:
        return redirect("/login")
    if session.get("lock") is True:
        return redirect("/lock")

    file_helper = fl.Files()

    file_helper.load_file(id_file)
    f = file_helper.get_data()
    if f['owner'] is not session['id']:
        abort(403)

    data = file_helper.share_detail(id_file)
    return jsonify(data)

@app.route("/api/share", methods=['POST'])
def share():
    users = request.form['users']
    id = request.form['id_file']
    permission = request.form['permission']

    if session.get("login") is None:
        return redirect("/login")
    if session.get("lock") is True:
        return redirect("/lock")

    file_helper = fl.Files()

    file_helper.load_file(id)
    f = file_helper.get_data()
    if f['owner'] is not session['id']:
        abort(403)

    if file_helper.share_file(users, id, permission):
        return jsonify({"err": 0, "msg": "Success"})
    else:
        return jsonify({"err": 1, "msg": file_helper.err_msg()})

@app.route("/api/share/<id>", methods=['DELETE'])
def unshared(id=None):
    if session.get("login") is None:
        return redirect("/login")
    if session.get("lock") is True:
        return redirect("/lock")

    file_helper = fl.Files()

    if file_helper.unshare(id):
        return jsonify({"err": 0, "msg": "Success"})
    else:
        return jsonify({"err": 1, "msg": file_helper.err_msg()})

@app.route("/api/file/<id>", methods=['DELETE'])
def file_api(id=None):
    if session.get("login") is None:
        return redirect("/login")
    if session.get("lock") is True:
        return redirect("/lock")

    file_helper = fl.Files()
    if request.method == 'DELETE':
        file_helper.load_file(id)
        if file_helper.delete_file(app.config['UPLOAD_FOLDER']):
            return jsonify({"err": 0, "msg": "Success"})
        else:
            return jsonify({"err": 0, "msg": file_helper.err_msg()})

@app.route("/api/recycle/<id_recycle>", methods=['DELETE'])
def restore_file(id_recycle=None):
    if session.get("login") is None:
        return redirect("/login")
    if session.get("lock") is True:
        return redirect("/lock")
    if session.get("auth") is "user":
        return redirect("/")

    file_helper = fl.Files()
    if file_helper.restore_file(id_recycle):
        return jsonify({"err": 0, "msg": "Success"})
    else:
        return jsonify({"err": 1, "msg": file_helper.err_msg()})

@app.route("/api/project", methods=['POST'])
def add_project():
    if session.get("login") is None:
        return redirect("/login")

    name = request.form['name']
    user_helper = user.User()
    user_helper.load_user(session['id'])
    home_folder = user_helper.get_data()['home_folder']
    project_helper = project.Project()
    if project_helper.add_project(session['id'], name, app.config['UPLOAD_FOLDER'], home_folder):
        return jsonify({
            'status': 1
        })
    else:
        return jsonify({
            'status': 0,
            'msg': project_helper.get_error_msg()
        })

@app.route("/api/project/<id>", methods=['DELETE'])
def delete_project(id=None):
    if session.get("login") is None:
        return redirect("/login")
    
    user_helper = user.User()
    user_helper.load_user(session['id'])
    home_folder = user_helper.get_data()['home_folder']
    project_helper = project.Project()
    if project_helper.delete_project(app.config['UPLOAD_FOLDER'], home_folder, id):
        return jsonify({
            'err': 0
        })
    else:
        return jsonify({
            'err': 1,
            'msg': project_helper.get_error_msg()
        })

# ======================================================================================

if __name__ == '__main__':
    app.run(debug=True)
