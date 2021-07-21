from gunicorn.app.base import BaseApplication

from OptchainBackend.wsgi import application


class StandaloneApplication(BaseApplication):
    """Our Gunicorn application."""

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':
    gunicorn_options = {
        'bind': '0.0.0.0:8000',
        'workers': 1,
        'preload':True,
    }

    StandaloneApplication(application, gunicorn_options).run()
