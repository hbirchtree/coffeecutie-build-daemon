#!/usr/bin/python3

import os,base64,sqlite3,time,datetime,md5

from flask import Flask,g,url_for,send_from_directory, request,Response, jsonify,render_template,redirect
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['zip'])

# Create an instance of Flask
app = Flask(__name__,static_folder='../static',template_folder='../templates');
app.config.from_object(__name__);

app.config['MAX_CONTENT_LENGTH'] = 100*1024*1024;

BINARY_DIR = os.path.join(app.root_path,'../bin')

# Displayed on web frontend, might be included in REST?
PROJECT_TITLE = "Coffee"

app.config['PROJECT_TITLE'] = PROJECT_TITLE;
app.config['UPLOAD_FOLDER'] = BINARY_DIR;

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, '../db/error_reports.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
));
app.config.from_envvar('FLASKR_SETTINGS', silent=True);

# Check if filename is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

"""
  Database functions, pretty stock
"""

# Connecting to database on start
def connect_to_database():
    return sqlite3.connect(app.config['DATABASE']);

# Opening the database at start of program or for a query
def open_db():
    db = getattr(g,'_database',None);
    if db == None:
        db = g._database = connect_to_database();
    db.row_factory = sqlite3.Row;
    return db;

# Initializing the database on first run
def init_db():
    with app.app_context():
        db = open_db();
        with app.open_resource('../db/schema.sql',mode='r') as f:
            db.cursor().executescript(f.read());
        db.commit();

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g,'_database',None);
    if db != None:
        db.close();

"""
  Custom database helper functions
"""

# General database query
def query_db(query,args=(),one=False):
    with app.app_context():
        with open_db() as db:
            cur = db.execute(query,args);
            rd = cur.fetchall();
            cur.close();
            db.commit();
            return (rd[0] if rd else None) if one else rd;

# General database query
def insert_into_db(query,args=(),one=False):
    with app.app_context():
        with open_db() as db:
            cur = db.execute(query,args);
            rd = cur.fetchall();
            key = cur.lastrowid;
            cur.close();
            db.commit();
            return key;

# Submitting a build report to the database
def enter_report(obj):
    print("Log size: %s" % (len(obj['log'])));
    query_db("""
             INSERT INTO BUILDREPORTS VALUES(NULL,?,?,?,?,?,?,?);
             """,
             args=(obj['host'],
                obj['commit'],obj['platform'],
                obj['status'],obj['log'],obj['time'],0)
             );
    return;

"""
  Miscellaneous helper functions
"""

# For binary uploads, MD5-hashes values for mapping build server+arch+commit to file
def gen_binary_filename(arch,host,commit):
    m = md5.new();
    m.update("%s%s%s" % (arch,host,commit[:10]));
    return m.hexdigest()+".zip";

# Check if a binary file exists in the filesystem
def verify_binary_filename(arch,host,commit):
    return os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'],
                                       gen_binary_filename(arch,
                                                           host,
                                                           commit)
                                       ));

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

"""
  Shorthand database retrievals, common across the board
"""

# Acquiring all the log data from builds, including failed ones
def get_log_data():
    elements = query_db("SELECT * FROM BUILDREPORTS;");
    cpy = [];
    for el in elements:
        ref = {};
        ref['bid'] = int(el[0]);
        ref['host'] = el[1];
        ref['commit'] = el[2];
        ref['platform'] = el[3];
        ref['status'] = int(el[4]);
        ref['log'] = el[5];
        ref['time'] = int(el[6]);
        ref['has_binary'] = verify_binary_filename(ref['platform'],
                                ref['host'],ref['commit']);
        cpy.append(ref);
    return cpy;

# Acquiring the latest binary release files
def get_release_data():
    elements = query_db(
        """
        SELECT PLATFORM_ID,
               SERVERID,
               REPORT_ID,
               MAX(BUILD_TIME),
               HAS_BINARY
            FROM BUILDREPORTS
            WHERE HAS_BINARY = 1
            GROUP BY PLATFORM_ID
            ORDER BY MAX(BUILD_TIME) DESC;
        """);
    cpy = [];
    for el in elements:
        ref = {};
        ref['platform'] = el[0];
        ref['host'] = el[1];
        ref['bid'] = int(el[2]);
        ref['time'] = int(el[3]);
        cpy.append(ref);
    return cpy;

# Acquiring unit test data
def get_unit_tests(build):
    test_data = query_db(
        """
	    SELECT RESULT
            FROM TEST_REPORT AS T,BUILDREPORTS AS B
            INNER JOIN TEST_BUILDREL AS R
                ON T.TEST_ID = R.TEST_ID AND B.REPORT_ID = R.REPORT_ID
            WHERE B.REPORT_ID = ?;
        """,
        args=(build,),one=True);
    if not test_data:
         return (None,None);
    elements = query_db(
        """
        SELECT U.RESULT,U.UNAME
            FROM TEST_REPORT AS T,UNIT_TEST AS U
            INNER JOIN UNIT_TESTREL AS R 
                ON T.TEST_ID = R.TEST_ID AND U.UNIT_ID = R.UNIT_ID
            INNER JOIN TEST_BUILDREL AS B
                ON B.TEST_ID = T.TEST_ID AND B.REPORT_ID = ?;
        """,
        args=(build,));
    cpy = [];
    for el in elements:
        ref = {};
        ref['result'] = int(el[0]);
        ref['testname'] = el[1];
        cpy.append(ref);
    return (int(test_data[0]),cpy);

def get_project_data():
    pinfo = {};
    pinfo['title'] = app.config['PROJECT_TITLE'];
    pinfo['max_binsize'] = app.config['MAX_CONTENT_LENGTH'];
    return pinfo;

"""
  REST interface for applications, pure query data mostly :)
"""

"""
  Showing help for those who are lost on the REST API
  We use versioning to keep consistency with older applications, creating new URLs for new APIs
"""
@app.route("/rest",methods=['GET'])
def restful_help():
    helpme = {};
    helpme['v1'] = {};
    helpme['v1']['tests'] = {};
    helpme['v1']['tests']['<build_id>'] = "Retrieve test data";
    helpme['v1']['releases'] = "Retrieve data on binary releases";
    helpme['v1']['all'] = "Retrieve data on builds";
    return jsonify(helpme);

# REST-ful interface to get log data links and etc.
@app.route("/rest/v1/all",methods=['GET'])
def restful_all_route():
    cpy = get_log_data();
    rst = [];
    for el in cpy:
        el.pop('log');
        rst.append(el);
    data = {};
    data['logs'] = rst;
    data['project'] = get_project_data();
    return jsonify(data);

@app.route("/rest/v1/tests/<int:build>",methods=['GET'])
def restful_test_route(build):
    data = {};
    data_tmp = get_unit_tests(build);
    if data_tmp[0] == None:
        return jsonify(data);
    data['id'] = data_tmp[0];
    data['data'] = data_tmp[1];
    return jsonify(data);

@app.route("/rest/v1/releases",methods=['GET'])
def restful_releases_route():
    data = {};
    data['releases'] = get_release_data();
    data['project'] = get_project_data();
    return jsonify(data);

"""
  Primary interface for most users
"""

# Present a nice overview of log data and etc.
@app.route("/",methods=['GET'])
def default_route():
    rcpy = get_release_data();
    cpy = get_log_data();
    rcpy = prettify_time_values(rcpy);
    cpy = prettify_time_values(cpy);
    return render_template('tables.html',
        name='index',entries=cpy,releases=rcpy,
        title="CoffeeCutie Build Status",
        project=app.config['PROJECT_TITLE']);


"""
  Interaction with data stored on server
   - Log data
   - Test data
   - Binary build releases
"""

# For servers, get their logs and put them in the database
@app.route("/logger/data/<arch>",methods=['POST'])
def build_log_data(arch):
    if request.mimetype != 'application/json':
        return Response("Are you lost?",mimetype='text/plain');
    obj = request.get_json();
    logdata = ''
    try:
        # Truncate log if too long
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
    query = query_db("""
                     SELECT ERROR_OUTPUT FROM BUILDREPORTS AS B
                        WHERE B.REPORT_ID = ?;
                     """,
                     args=(bid,),one=True);
    if query:
        try:
            # Decoding b64 data, live!
            return base64.b64decode(query[0]).replace('\n','</br>');
        except TypeError:
            pass;
    return "[THERE IS NOTHING TO SEE HERE]";

# For servers, publishing binary releases, no magic type checking (yet, python-magic exists)
@app.route("/bin/upload/data/<arch>/<host>/<commit>",methods=['POST'])
def push_binary_release(arch,host,commit):
    commit = commit[:10];
    commit_s = "%s%%" % (commit,);

    data = query_db("""
                    SELECT BUILD_STATUS,REPORT_ID FROM BUILDREPORTS
                        WHERE PLATFORM_ID = ? AND
                        SERVERID = ? AND
                        BUILD_HASH LIKE ?;
                    """,
                    args=(arch,host,commit_s),one=True);

    if not data or data[0] != 0:
        return '{"status": 1}';

    query_db("""
             UPDATE BUILDREPORTS
                SET HAS_BINARY = 1
                WHERE REPORT_ID = ?;
             """,
             args=(data[1],));

    binname = gen_binary_filename(arch,host,commit);

    file = request.files['file'];
    if file and allowed_file(file.filename):
        filename = secure_filename("%s" % (binname,));
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename));
        return '{"status": 0}';
    return '{"status": 1}';

# For clients, retrieving binary releases
@app.route("/bin/<int:bid>",methods=['GET'])
def get_binary_release(bid):
    data = query_db("""
                    SELECT PLATFORM_ID,SERVERID,BUILD_HASH FROM BUILDREPORTS
                        WHERE REPORT_ID = ?;
                    """,
                    args=(bid,),one=True);

    if not data:
        return "[THERE IS NOTHING TO SEE HERE]";

    binname = gen_binary_filename(data[0],data[1],data[2]);

    print("Looking for file: "+'%s.zip' % (binname,));

    return send_from_directory(BINARY_DIR,
            secure_filename('%s' % (binname,)),
            as_attachment=True,
            attachment_filename="%s-%s_(%s).zip" % (PROJECT_TITLE,data[0],data[1]));

@app.route("/tests/upload/<arch>/<host>/<commit>",methods=['POST'])
def push_test_data(arch,host,commit):
    if request.mimetype != 'application/json':
        return Response("Are you lost?",mimetype='text/plain');
    obj = request.get_json();
    data = query_db("""
                    SELECT REPORT_ID FROM BUILDREPORTS
                        WHERE
                            PLATFORM_ID = ? AND
                            SERVERID = ? AND
                            BUILD_HASH = ?;
                    """,
                    args=(arch,host,commit));
                    
    if len(data) == 0 or obj['tests'] == None or len(obj['tests']) == 0:
        return '{"status": 1}';
    
    test_id = insert_into_db("INSERT INTO TEST_REPORT VALUES(NULL,?,?);",
                    args=(obj['test:status'],time.time()));
    
    for b in data:
        query_db("""
                 INSERT INTO TEST_BUILDREL VALUES(?,?);
                 """,
            args=(b[0],test_id));
    
    for u in obj['tests']:
        unit_id = insert_into_db("INSERT INTO UNIT_TEST VALUES(NULL,?,?);",
                    args=(u['result'],u['name']));
        query_db("INSERT INTO UNIT_TESTREL VALUES(?,?);",
            args=(test_id,unit_id));
    
    return '{"status": 0}';

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True);
