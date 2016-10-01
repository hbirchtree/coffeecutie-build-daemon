#!/usr/bin/python3

from server_base import *
from databases import *
from app_base import *

from rest_api import *
from binary_api import *
from test_api import *
from log_api import *


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
        title=app.config['PAGE_TITLE'],
        project=app.config['PROJECT_TITLE']);


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True);
