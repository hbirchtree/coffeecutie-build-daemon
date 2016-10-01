#!/usr/bin/python3

from databases import *

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
