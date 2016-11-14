"""
Contains the root view

"""
from flask.views import MethodView
from flask import jsonify


class RootView(MethodView):
    """Returns a list of buckets"""
    def __init__(self, estroi):
        self.estroi = estroi

    def get(self):
        return jsonify({
            'buckets': [
                bucket.name for bucket in self.estroi.buckets
            ]
        })

    @classmethod
    def register(klass, app, estroi):
        app.add_url_rule('/', view_func=klass.as_view('root', estroi), methods=['GET'])
