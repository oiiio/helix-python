
_DEFAULT_CONFIG = {
    'HELIX_STAGING': False,
    'HELIX_AUTH_GRANT_TYPE': None,
    'HELIX_IDENTITY_CLIENT_ID': None,
    'HELIX_IDENTITY_SECRET': None,
    'HELIX_GENOMIC_CLIENT_ID': None,
    'HELIX_GENOMIC_SECRET': None
}


class Helix:
    def __init__(self, app=None, **kwargs):  # noqa: D102
        self.app = None
        self.helix = None

        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        """
        Initialize the helix api for the given app.

        This should be used for a deferred initialization, supporting
        the Flask factory pattern.

        Args:
            app (flask.Flask): The Flask app to apply this extension to.

        """
        self.app = app

        for key, value in _DEFAULT_CONFIG.items():
            app.config.setdefault(key, value)

        for key, value in kwargs.items():
            app.config[key] = value

        self.helix = Helix(
            staging=app.config.get('HELIX_STAGING'),
            grant_type=app.config.get('HELIX_AUTH_GRANT_TYPE'),
            client_id=app.config.get('HELIX_IDENTITY_CLIENT_ID'),
            client_secret=app.config.get('HELIX_IDENTITY_SECRET'),
            genomic_client_id=app.config.get('HELIX_GENOMIC_CLIENT_ID'),
            genomic_client_secret=app.config.get('HELIX_GENOMIC_SECRET'),
        )
