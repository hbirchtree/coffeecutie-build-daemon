#!/usr/bin/python3

# Run this on first start to create the database!

from databases import init_db,app
import os

if __name__ == "__main__":
    try:
        print("Creating %s" % app.config['DATABASE_PATH'])
        os.makedirs(app.config['DATABASE_PATH'])
    except OSError:
        pass
    init_db();
