#!/usr/bin/python3

from databases import *

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
    return '{"status": 1, "bid": %s}' % ();

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
