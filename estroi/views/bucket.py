"""
Bucket API view to handle object creation (POST), deletion (DELETE)
and a stats route (GET)

"""
from flask.views import MethodView
from flask import jsonify, abort
from flask import request


def authenticate(f, *args1, **kwargs1):
    def _auth(*args, **kwargs):
        print(args1)
        print(kwargs1)
        print(args)
        print(kwargs)
        bucket_view = args[0]
        print(request.username)
        if bucket_view.bucket.auth(request.username, request.password):
            return f(bucket_view, *args, **kwargs)
        else:
            abort(401)
    return _auth


class BucketView(MethodView):
    """
    API View representing a bucket

    """
    decorators = [authenticate]

    def __init__(self, bucket):
        self.bucket = bucket

    def post(self):
        """Handles POST / with file content as request body"""
        return jsonify(self.bucket.create(request.data))

    def delete(self, name):
        """Handles DELETE /{name}"""
        return jsonify(self.bucket.delete(name))

    def get(self):
        """Returns bucket stats"""
        return jsonify(self.bucket.stats())

    @classmethod
    def register(klass, bucket, app):
        view = klass.as_view(bucket.name, bucket)
        app.add_url_rule('/', view_func=view, methods=['GET', 'POST'])
        app.add_url_rule('/<name>', view_func=view, methods=['DELETE'])
