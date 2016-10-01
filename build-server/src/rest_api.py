#!/usr/bin/python3

from databases import *

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
    
    # Viewing APIs
    helpme['v1'] = {};
    helpme['v1']['tests'] = {};
    helpme['v1']['tests']['<build_id>'] = "Retrieve test data";
    helpme['v1']['releases'] = "Retrieve data on binary releases";
    helpme['v1']['all'] = "Retrieve data on builds";
    
    # Submission/client APIs
    helpme['logs'] = {};
    helpme['logs']['upload'] = {'data': {'<arch>': "Upload build log data" }};
    helpme['logs']['<build_id>'] = "Get log for build";
    
    # Binary release APIs
    helpme['bin'] = {};
    helpme['bin']['upload'] = {'data':
            {'<arch>':
                {'<host>':
                    {'<commit>':
                        "Upload binary release"
                    }
                }
            }
        };
    
    # Test submission APIs
    helpme['tests'] = {};
    helpme['tests']['upload'] = {
            '<arch>': {
                '<host>': {
                    '<commit>': "Upload test data"
                }
            }
        };
    
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
  Interaction with data stored on server
   - Log data
   - Test data
   - Binary build releases
"""
