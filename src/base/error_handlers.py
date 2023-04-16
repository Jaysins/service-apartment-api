from werkzeug.exceptions import HTTPException

from src import app
from flask import jsonify


@app.errorhandler(HTTPException)
def handle_exception(response):
    status_code = response.code if isinstance(response, HTTPException) else 500

    print("hrrrr")
    return jsonify(response), status_code
