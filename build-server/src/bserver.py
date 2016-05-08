#!/usr/bin/python3

import os,base64,sqlite3

from flask import Flask,g,url_for,send_from_directory,request,Response,jsonify,render_template
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['zip','tar.xz'])

# Create an instance of Flask
app = Flask(__name__,static_folder='../static',template_folder='../templates');
app.config.from_object(__name__);

app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024;

BINARY_DIR = os.path.join(app.root_path,'../bin')

PROJECT_TITLE = "Coffee"

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, '../db/error_reports.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
));
app.config.from_envvar('FLASKR_SETTINGS', silent=True);

def connect_to_database():
    return sqlite3.connect(app.config['DATABASE']);

def open_db():
    db = getattr(g,'_database',None);
    if db == None:
        db = g._database = connect_to_database();
    db.row_factory = sqlite3.Row;
    return db;

def init_db():
    with app.app_context():
        db = open_db();
        with app.open_resource('../db/schema.sql',mode='r') as f:
            db.cursor().executescript(f.read());
        db.commit();

def query_db(query,args=(),one=False):
    with open_db() as db:
        cur = db.execute(query,args);
        rd = cur.fetchall();
        cur.close();
        db.commit();
        return (rd[0] if rd else None) if one else rd;

def enter_report(obj):
    query_db("INSERT INTO BUILDREPORTS VALUES(NULL,?,?,?,?,?);",args=(obj['host'],obj['commit'],obj['platform'],obj['status'],obj['log']));
    return;

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g,'_database',None);
    if db != None:
        db.close();

# Present a nice screen when someone is lost
@app.route("/")
def default_route():
    elements = query_db("SELECT * FROM BUILDREPORTS;");
    return render_template('tables.html',name='index',entries=elements,title="CoffeeCutie Build Status",project=PROJECT_TITLE);

# For servers, get their logs and put them in the database
@app.route("/logger/data/<arch>",methods=['POST'])
def build_log_data(arch):
    if request.mimetype != 'application/json':
        return Response("Are you lost?",mimetype='text/plain');
    obj = request.get_json();
    logdata = ''
    try:
        # Truncate log if too long
        obj['log'] = obj['log'][len(obj['log'])-1000000:len(obj['log'])]
        obj['platform'] = arch;
        enter_report(obj);
    except KeyError:
        return jsonify({'status':1,'error': 'Malformed request!'});
    
    return jsonify({'status':0});

@app.route("/logs/<int:bid>",methods=['GET'])
def get_build_log(bid):
    query = query_db("SELECT ERROR_OUTPUT FROM BUILDREPORTS AS B WHERE B.REPORT_ID = ?;",args=(bid,),one=True);
    if query:
        try:
            return base64.b64decode(query[0]).replace('\n','</br>');
        except TypeError:
            pass;
    return "[THERE IS NOTHING TO SEE HERE]";

@app.route("/bin/<int:bid>",methods=['GET'])
def get_binary_release(bid):
    data = query_db("SELECT BUILD_HASH,PLATFORM_ID,SERVERID FROM BUILDREPORTS AS B WHERE B.REPORT_ID = ?;",args=(bid,),one=True);
    print("Looking for file: "+'%s_%s_%s.zip' % (data[2],data[0],data[1]));
    return send_from_directory(BINARY_DIR, '%s.zip' % (bid,),
        as_attachment=True,attachment_filename="%s-%s_(%s).zip" % (PROJECT_TITLE,data[0],data[1]));

@app.route("/bin/upload/data/<arch>/<int:bid>",methods=['POST'])
def push_binary_release(arch,bid):
    if len(request.data) > app.config['MAX_CONTENT_LENGTH']:
        return "Too big, senpai";
    data = query_db("SELECT PLATFORM_ID FROM BUILDREPORTS AS B WHERE B.REPORT_ID = ?;",args=(bid,),one=True);
    tmp_name = '%s.zip' % (bid,);
    if not data or data[0] != arch:
        return "Data mismatch";
    if os.path.isfile(BINARY_DIR+"/"+tmp_name):
        return "File exists!";
    file_data = base64.b64decode(request.data);
    file = open(BINARY_DIR+"/"+tmp_name,"wb");
    file.write(file_data);
    file.close();
    return "Absolute organ failure";

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True);
