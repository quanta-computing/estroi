"""
Estroi server

"""
import yaml

from flask import Flask, Blueprint
from flask import jsonify

from .errors import register_error_handlers
from .bucket import Bucket
from .key import Key
from .views import RootView, StatsView


class EstroiServer:
    """Main objet to store various stuff about the server"""

    def __init__(self):
        self.config = {}
        self.keys = {}
        self.buckets = []

    def auth(self, key, token):
        if key not in self.keys:
            return False
        return self.keys[key].auth(token)

    def load_config(self, config_file):
        """Load configuration from yaml file `config_file`"""
        with open(config_file) as fh:
            self.config = yaml.safe_load(fh)

    def register_buckets(self, app):
        """
        Read config dict and create appropriate buckets.
        They are the registerd to app
        """
        for name, bucket_config in self.config['buckets'].items():
            bucket = Bucket(name, bucket_config)
            bucket.register(app, self)
            self.buckets.append(bucket)

    def register_keys(self, app):
        for name, key_config in self.config['keys'].items():
            self.keys[name] = Key(name, key_config)

    def register_base_views(self, app):
        root = Blueprint('root', __name__)
        stats = Blueprint('stats', __name__)
        StatsView.register(stats, self)
        RootView.register(root, self)
        app.register_blueprint(root, url_prefix='/')
        app.register_blueprint(stats, url_prefix='/stats')

    @classmethod
    def setup(klass, config_file='/etc/estroi/estroi.yml'):
        app = Flask('estroi')
        register_error_handlers(app)
        estroi = klass()
        estroi.load_config(config_file)
        estroi.register_buckets(app)
        estroi.register_keys(app)
        estroi.register_base_views(app)
        app.estroi = estroi
        return app
