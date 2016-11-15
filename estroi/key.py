class Key:
    """Represents a key and provides few helper methods for authentication"""

    def __init__(self, name, config):
        self.name = name
        self.config = config

    @property
    def token(self):
        return self.config['token']

    def auth(self, token):
        return token == self.token
