#!/usr/bin/python3

from app_base import *

"""
  Database functions, pretty stock
"""

# Connecting to database on start
def connect_to_database():
    return sqlite3.connect(app.config['DATABASE']);

# Opening the database at start of program or for a query
def open_db():
    db = getattr(g,'_database',None);
    
    # Attempt to load database, if it fails, create it
    try:
        if db == None:
            db = g._database = connect_to_database();
    except sqlite3.OperationalError:
        os.makedirs(app.config['DATABASE_PATH'])
        init_db()
        db = g._database = connect_to_database();
        
    db.row_factory = sqlite3.Row;
    return db;

# Initializing the database on first run
def init_db():
    with app.app_context():
        db = open_db();
        with app.open_resource(app.config['DATABASE_SCHEMA'],mode='r') as f:
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
