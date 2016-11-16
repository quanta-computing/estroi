"""
Represents a bucket

"""
import os
import uuid

from flask import Blueprint
from flask import send_from_directory
from .views import BucketView


class BucketStats:
    """
    Stats for a bucket

    """
    def __init__(self, bucket):
        self.bucket = bucket
        self.creations = 0
        self.deletions = 0

    @property
    def files_count(self):
        return 0

    def as_json(self):
        return {
            'creations': self.creations,
            'deletions': self.deletions,
        }


class Bucket:
    """
    Represents a bucket which store files

    """
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self._blueprint = Blueprint('bucket_{}'.format(self.name), __name__)
        self._stats = BucketStats(self)
        self.estroi = None

    @property
    def path(self):
        return self.config['path']

    @property
    def allowed(self):
        return self.config.get('allow', None)

    def is_key_allowed(self, key):
        return self.allowed == 'all' or key in self.allowed

    def filepath(self, name):
        return '{}/{}'.format(self.path, name)

    def register(self, app, estroi):
        self.estroi = estroi
        os.makedirs(self.path, exist_ok=True)
        BucketView.register(self, self._blueprint)
        app.register_blueprint(self._blueprint, url_prefix='/bucket/{}'.format(self.name))

    def generate_uuid(self):
        return uuid.uuid4()

    def create(self, content):
        name = self.generate_uuid()
        with open(self.filepath(name), 'wb') as f:
            f.write(content)
            self._stats.creations += 1
        return {'name': name}

    def delete(self, name):
        os.unlink(self.filepath(name))
        self._stats.deletions += 1
        return {'deleted': name}

    def auth(self, key, token):
        return self.is_key_allowed(key) and self.estroi.auth(key, token)

    def stats(self):
        return self._stats.as_json()
