"""
Provides a register_error_handlers function to replace flask error handlers with something which
returns JSON

"""
from flask import jsonify


def register_error_handlers(app):
    """
    Register custom error handlers to return errors in JSON format

    """
    from werkzeug.exceptions import default_exceptions, HTTPException

    def _json_error(e):
        if isinstance(e, HTTPException):
            code = e.code
        else:
            code = 500
        response = jsonify(error=str(e), code=code)
        response.status_code = code
        return response

    for code in default_exceptions:
        app.errorhandler(code)(_json_error)
