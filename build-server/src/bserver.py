#!/usr/bin/python3

import os,base64,sqlite3,time,datetime,md5

from flask import Flask,g,url_for,send_from_directory,request,Response,jsonify,render_template,redirect
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['zip'])

# Create an instance of Flask
app = Flask(__name__,static_folder='../static',template_folder='../templates');
app.config.from_object(__name__);

app.config['MAX_CONTENT_LENGTH'] = 50*1024*1024;

BINARY_DIR = os.path.join(app.root_path,'../bin')

PROJECT_TITLE = "Coffee"

app.config['UPLOAD_FOLDER'] = BINARY_DIR;

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, '../db/error_reports.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
));
app.config.from_envvar('FLASKR_SETTINGS', silent=True);

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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
    query_db("INSERT INTO BUILDREPORTS VALUES(NULL,?,?,?,?,?,?);",args=(obj['host'],obj['commit'],obj['platform'],obj['status'],obj['log'],obj['time']));
    return;

# For binary uploads, MD5-hashes values for mapping build server+arch+commit to file
def gen_binary_filename(arch,host,commit):
    m = md5.new();
    m.update("%s%s%s" % (arch,host,commit[:10]));
    return m.hexdigest()+".zip";

def get_log_data():
    elements = query_db("SELECT * FROM BUILDREPORTS;");
    cpy = [];
    for rw in elements:
        ref = [];
        for i in range(len(rw)):
            if i == 6 or i == 4 or i == 0:
                # Some arguments must be integers
                ref.append(int(rw[i]));
            else:
                ref.append(str(rw[i]));
        print(len(ref));
        ref.append(os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], gen_binary_filename(ref[3],ref[1],ref[2]) )));
        print(ref[7]);
        cpy.append(ref);
    return cpy;

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g,'_database',None);
    if db != None:
        db.close();

# REST-ful interface to get log data links and etc.
@app.route("/rest",methods=['GET'])
def restful_route():
    cpy = get_log_data();
    rst = [];
    for el in cpy:
        el.pop(5);
        el_d = {};
        el_d['bid'] = el[0];
        el_d['host'] = el[1];
        el_d['commit'] = el[2];
        el_d['platform'] = el[3];
        el_d['status'] = el[4];
        el_d['time'] = el[5];
        el_d['has_binary'] = el[7];
        rst.append(el_d);
    return jsonify({'logs':rst});

# Present a nice overview of log data and etc.
@app.route("/",methods=['GET'])
def default_route():
    cpy = get_log_data();
    for rw in cpy:
        if rw[6] != 0:
            rw[6] = datetime.datetime.fromtimestamp(int(rw[6])).strftime("%Y-%m-%dT%H:%M:%S");
        else:
            rw[6] = "N/A";
    return render_template('tables.html',name='index',entries=cpy,title="CoffeeCutie Build Status",project=PROJECT_TITLE);

# For servers, get their logs and put them in the database
@app.route("/logger/data/<arch>",methods=['POST'])
def build_log_data(arch):
    if request.mimetype != 'application/json':
        return Response("Are you lost?",mimetype='text/plain');
    obj = request.get_json();
    logdata = ''
    try:
        # Truncate log if too long
        obj['log'] = obj['log'][:-1000000]
        obj['platform'] = arch;
        # Imprint reporting time, useful to know when a build was released
        # Might include build duration as well
        obj['time'] = time.time();
        enter_report(obj);
    except KeyError:
        return jsonify({'status':1,'error': 'Malformed request!'});
    
    return jsonify({'status':0});

# For servers, slight modification to the URL, same function
@app.route("/logs/upload/data/<arch>",methods=['POST'])
def build_log_data2(arch):
    return build_log_data(arch);

# For clients, retrieving the log data
@app.route("/logs/<int:bid>",methods=['GET'])
def get_build_log(bid):
    query = query_db("SELECT ERROR_OUTPUT FROM BUILDREPORTS AS B WHERE B.REPORT_ID = ?;",args=(bid,),one=True);
    if query:
        try:
            # Decoding b64 data, live!
            return base64.b64decode(query[0]).replace('\n','</br>');
        except TypeError:
            pass;
    return "[THERE IS NOTHING TO SEE HERE]";

# For clients, retrieving binary releases
@app.route("/bin/<int:bid>",methods=['GET'])
def get_binary_release(bid):
    data = query_db("SELECT PLATFORM_ID,SERVERID,BUILD_HASH FROM BUILDREPORTS WHERE REPORT_ID = ?;",args=(bid,),one=True);

    if not data:
        return "[THERE IS NOTHING TO SEE HERE]";

    binname = gen_binary_filename(data[0],data[1],data[2]);

    print("Looking for file: "+'%s.zip' % (binname,));

    return send_from_directory(BINARY_DIR, secure_filename('%s' % (binname,)),
        as_attachment=True,attachment_filename="%s-%s_(%s).zip" % (PROJECT_TITLE,data[0],data[1]));

# For servers, publishing binary releases, no magic type checking (yet, python-magic exists)
@app.route("/bin/upload/data/<arch>/<host>/<commit>",methods=['POST'])
def push_binary_release(arch,host,commit):
    commit = commit[:10];
    commit_s = "%s%%" % (commit,);

    data = query_db("""
                    SELECT REPORT_ID FROM BUILDREPORTS
                    WHERE PLATFORM_ID = ? AND
                    SERVERID = ? AND
                    BUILD_HASH LIKE ?;
                    """,
                    args=(arch,host,commit_s),one=True);

    if not data:
        return '{"status": 1}';

    binname = gen_binary_filename(arch,host,commit);

    file = request.files['file'];
    if file and allowed_file(file.filename):
        filename = secure_filename("%s" % (binname,));
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename));
        return '{"status": 0}';
    return '{"status": 1}';

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True);
