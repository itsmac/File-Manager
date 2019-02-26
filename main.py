from flask import Flask, request, redirect, url_for, render_template, jsonify
#from google.cloud import storage
from google.appengine.api import app_identity
from google.appengine.ext import ndb
import logging
import os
from uuid import uuid4
import cloudstorage as gcs
import json
import subprocess

app = Flask(__name__,template_folder="Templates")

class ToDo(ndb.Model):
	unique_name = ndb.StringProperty(indexed=False)


#bucket_name = "my-project-15670.appspot.com"
bucket_name =os.environ.get('BUCKET_NAME',
    app_identity.get_default_gcs_bucket_name()
  )

@app.route('/')
def home():
    return render_template('form.html')


@app.route('/get',methods =['GET'])
def get_list():
    content_list = []
    stats = gcs.listbucket("/" + bucket_name + '/',delimiter = '/')
    for i in stats:
        name = os.path.basename(i.filename)
        content_list.append(name)
    return ",".join(content_list)
    #return str(content_list)

@app.route('/add-directory',methods = ['POST'])
def add_directory():
    folder_name = request.json["folderName"]
    dir_ = "/"+bucket_name+"/"+folder_name + "/"
    f = gcs.open(dir_,'w')
    #f.write()
    f.close
    # if not os.path.exists(dir_):
    #         os.makedirs(dir_)
    return jsonify({"success":True})


@app.route('/upload',methods = ['POST'])
def upload():
    upload_file = request.files.get('fileUpload',None)
    logging.debug(upload_file)
    if not upload_file:
        return 'No file uploaded.', 400
    file_name = upload_file.filename
    data = upload_file.stream.read()
    filepath = "/{}/{}".format(bucket_name,file_name)
    try:
        f = gcs.open(filepath, 'w')
        f.write(data)
        f.close()
    except Exception as e:
        return jsonify({'error': 'Could not process'}), 500

    return jsonify({"success":True})
        #return redirect(url_for('home'))
    



@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return "An internal error occurred", 500