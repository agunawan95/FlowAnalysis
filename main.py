from flask import Flask, render_template, request, session, redirect, url_for, make_response, jsonify, abort, send_file
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)


@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == '__main__':
    app.run(debug=True)