#!/usr/bin/python3

import os,base64,sqlite3,time,datetime
import hashlib as md5

from flask import Flask,g,url_for,send_from_directory, request,Response, jsonify,render_template,redirect
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['zip'])

# Displayed on web frontend, might be included in REST?
PROJECT_TITLE = "Coffee"


# Check if filename is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


"""
  Miscellaneous helper functions
"""

# For binary uploads, MD5-hashes values for mapping build server+arch+commit to file
def gen_binary_filename(arch,host,commit):
    m = md5.md5();
    m.update(("%s%s%s" % (arch,host,commit[:10])).encode());
    return m.hexdigest()+".zip";

"""
  Printing a UNIX timestamp in standard format YYYY-mm-DDTHH:MM:SS
"""
def prettify_time_values(arr):
    for rw in arr:
        if rw['time'] != 0:
            rw['time'] = datetime.datetime.fromtimestamp(rw['time']).strftime("%Y-%m-%dT%H:%M:%S");
        else:
            rw['time'] = "N/A";
    return arr;
