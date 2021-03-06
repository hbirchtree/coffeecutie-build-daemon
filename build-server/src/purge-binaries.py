#!/usr/bin/python3

import bserver,os

def clean_binaries():
    entries = bserver.query_db(
        """
        SELECT PLATFORM_ID,SERVERID,BUILD_HASH,REPORT_ID FROM BUILDREPORTS;
        """);
    file_pool = os.listdir(bserver.BINARY_DIR);
    for ent in entries:
        fname = bserver.gen_binary_filename(ent[0],ent[1],ent[2]);
        try:
            file_pool.remove(fname);
        except ValueError:
            continue;
        bserver.query_db(
            """
            UPDATE BUILDREPORTS
            SET HAS_BINARY = 1
            WHERE REPORT_ID = ?;
            """,args=(ent[3],));
    print("Deleting: %s" % (file_pool,));
    for f in file_pool:
        os.remove(os.path.join(bserver.BINARY_DIR,f));

if __name__ == "__main__":
    clean_binaries();
