#!/usr/bin/python3

from databases import *

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

