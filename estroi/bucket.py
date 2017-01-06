"""
Represents a bucket

"""
import os
import uuid
import gzip

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
    DEFAULT_COMPRESS_LEVEL = 6

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

    @property
    def compression(self):
        compression = self.config.get('compress', 0)
        if compression is False:
            return 0
        elif compression is True:
            return self.DEFAULT_COMPRESS_LEVEL
        else:
            return compression

    def is_key_allowed(self, key):
        return self.allowed == 'all' or key in self.allowed

    def filepath(self, name):
        return '{}/{}'.format(self.path, name)

    def filepath_gz(self, name):
        return "{}.gz".format(self.filepath(name))

    def fileobj_for_send(self, name):
        name = os.path.basename(name)  # avoid directory traversal
        if os.path.isfile(self.filepath_gz(name)):
            return gzip.open(self.filepath_gz(name), 'rb')
        else:
            return open(self.filepath(name), 'rb')

    def register(self, app, estroi):
        self.estroi = estroi
        os.makedirs(self.path, exist_ok=True)
        BucketView.register(self, self._blueprint)
        app.register_blueprint(self._blueprint, url_prefix='/bucket/{}'.format(self.name))

    def generate_uuid(self):
        return uuid.uuid4()

    def _create_with_gz(self, path, content):
        with gzip.open(path, 'wb', self.compression) as f:
            f.write(content)

    def _create_without_gz(self, path, content):
        with open(path, 'wb') as f:
            f.write(content)

    def create(self, content):
        name = self.generate_uuid()
        if self.compression > 0:
            self._create_with_gz(self.filepath_gz(name), content)
        else:
            self._create_without_gz(self.filepath(name), content)
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
