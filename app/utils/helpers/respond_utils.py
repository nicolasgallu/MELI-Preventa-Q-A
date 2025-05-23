from flask import jsonify

def build_response(status, message=None, http_code=None):
    response = {"status": status}
    if message:
        response["message"] = message
    return jsonify(response), http_code
