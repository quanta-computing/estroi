"""
Stats server

"""
from flask.views import MethodView
from flask import jsonify


class StatsView(MethodView):
    """A view to serve stats and a list of buckets"""
    def __init__(self, estroi):
        self.estroi = estroi

    def get(self):
        return jsonify({
            bucket.name: bucket.stats()
            for bucket in self.estroi.buckets
        })

    @classmethod
    def register(klass, app, estroi):
        app.add_url_rule('/', view_func=klass.as_view('stats', estroi), methods=['GET'])
