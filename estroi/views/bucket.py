"""
Bucket API view to handle object creation (POST), deletion (DELETE)
and a stats route (GET)

"""
from flask.views import MethodView
from flask import jsonify, abort
from flask import request


class BucketView(MethodView):
    """
    API View representing a bucket

    """
    def __init__(self, bucket):
        self.bucket = bucket

    def post(self):
        """Handles POST / with file content as request body"""
        return jsonify(self.bucket.create(request.data))

    def delete(self, name):
        """Handles DELETE /{name}"""
        try:
            return jsonify(self.bucket.delete(name))
        except FileNotFoundError:
            abort(404)

    def stats(self):
        """Returns bucket stats"""
        return jsonify(self.bucket.stats())

    def file(self, name):
        """Returns the file from the bucket"""
        try:
            with self.bucket.fileobj_for_send(name) as f:
                return (f.read(), {'Content-type': 'application/octet-stream'})
        except FileNotFoundError:
            abort(404)

    def get(self, name=None):
        """Returns stats if name is None or file from bucket"""
        if name is None:
            return self.stats()
        else:
            return self.file(name)

    def _bucket_auth(self, auth):
        """Authenticate against the bucket using authorization dict"""
        return self.bucket.auth(auth['username'], auth['password'])

    def _authenticate_request(self):
        """Authenticate the request"""
        if request.authorization is None:
            abort(401)
        elif not self._bucket_auth(request.authorization):
            abort(403)

    def dispatch_request(self, *args, **kwargs):
        self._authenticate_request()
        return super().dispatch_request(*args, **kwargs)

    @classmethod
    def register(klass, bucket, app):
        view = klass.as_view(bucket.name, bucket)
        app.add_url_rule('/', view_func=view, methods=['GET', 'POST'])
        app.add_url_rule('/<name>', view_func=view, methods=['GET', 'DELETE'])
