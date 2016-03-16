from flask import Flask,render_template,url_for,redirect,session,request

from flask.ext.bootstrap import Bootstrap

import os
import json
from swift_api import *
from keystone_api import get_token
from werkzeug import secure_filename
from flask import Response , stream_with_context
import requests
import threading
username = None
password = None
hostname = None
storage_url = None



app = Flask(__name__)

Bootstrap(app)

app.config.from_pyfile("config.py")
keystone_port = app.config['KEYSTONE_PORT']


@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    token = session.get('token')
    if token != None:
        list_containers = json.loads(get_info_account(token,storage_url))
        return render_template("index.html",list_containers= list_containers,container_info= None)
    else:
        return redirect(url_for('login'))
    
@app.route('/containers/<container_name>',methods=['GET','POST'])
def container_info(container_name):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    token = session.get('token')
    if token != None:
        list_containers = json.loads(get_info_account(token,storage_url))
        directory = request.args.get('dir')
        action = request.args.get('action')
        container_info = get_subdir(token,storage_url,container_name,directory)
        container_info = list_item_in_dir(container_info)
        if action == None:            
            return render_template("index.html",list_containers= list_containers,container_info = container_info,container_name = container_name,directory = directory)
        elif action== "delete_object":
            object_name = request.args.get("object_name")
            result = delete_object(token,storage_url,container_name,object_name)
            return redirect(url_for("container_info",dir = directory,container_name = container_name))
        elif action =="delete_container":
            result = delete_container(token,storage_url,container_name)
            return redirect(url_for("index"))
        elif action == "download":
            object_name = request.args.get("object_name")
            req = download_object(token,storage_url,container_name,object_name)
            print req.iter_content()
            return Response(stream_with_context(req),content_type=req.headers['content-type'],headers={"Content-Disposition": "attachment; filename=%s" % object_name})
        # elif action== "upload":

        if request.method =='POST':
            file = request.files['file']
            filename = secure_filename(file.filename)
            return redirect(url_for("upload_object",filename=filename,container_name = container_name, directory = directory))        

    else:
        return redirect(url_for('login'))

@app.route("/token",methods=['GET'])
def return_token():
    data = {"token":session.get('token'), "storage_url":storage_url}
    print data
    data = json.dumps(data)
    return   data
@app.route("/login", methods=['GET', 'POST'])
def login():
    global username
    global password
    global hostname
    global error
    global storage_url
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hostname = request.form['hostname']
        tenant_name = request.form['tenant_name']
        token = get_token(tenant_name, username, password, hostname, keystone_port)
        storage_url = get_storage_url(tenant_name, 'swift', username, password, hostname, keystone_port)
        session['logged_in'] = True
        session['token'] = token
        return redirect(url_for("index"))
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug= True,host='0.0.0.0',threaded=True)
