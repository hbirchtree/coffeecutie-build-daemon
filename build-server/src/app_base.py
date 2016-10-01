#!/usr/bin/python3

import server_keys
from server_base import *

# Create an instance of Flask
app = Flask(__name__,static_folder='../static',template_folder='../templates');
app.config.from_object(__name__);

# Find the binary directory
STORAGE_BASE_PATH = os.path.join(app.root_path,server_keys.STORAGE_PATH)
BINARY_DIR = os.path.join(STORAGE_BASE_PATH,'releases')

app.config['MAX_CONTENT_LENGTH'] = server_keys.MAX_UPLOAD_SIZE;

app.config['PROJECT_TITLE'] = server_keys.PROJECT_TITLE;
app.config['PAGE_TITLE'] = server_keys.PAGE_TITLE
app.config['UPLOAD_FOLDER'] = BINARY_DIR;

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE_PATH=os.path.join(STORAGE_BASE_PATH, 'db'),
    DATABASE_SCHEMA=os.path.join(app.root_path, '../db/schema.sql'),
    DATABASE=os.path.join(STORAGE_BASE_PATH, 'db/error_reports.db'),
    SECRET_KEY=server_keys.SERVER_SECRET_KEY,
    USERNAME=server_keys.SERVER_USER_NAME,
    PASSWORD=server_keys.SERVER_USER_PASS
));
app.config.from_envvar('FLASKR_SETTINGS', silent=True);

# Check if a binary file exists in the filesystem
def verify_binary_filename(arch,host,commit):
    return os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'],
                                       gen_binary_filename(arch,
                                                           host,
                                                           commit)
                                       ));
