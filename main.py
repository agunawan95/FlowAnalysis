from flask import Flask, render_template, request, session, redirect, url_for, make_response, jsonify, abort, send_file
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import pandas as pd
from flask_cors import CORS, cross_origin

# --------------------------------------------------------------------------------------
# ===================================== Helper Class ===================================
# --------------------------------------------------------------------------------------

import user
import files as fl
import enterprise

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
    return render_template("main.html")


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
# ======================================================================================


if __name__ == '__main__':
    app.run(debug=True)
