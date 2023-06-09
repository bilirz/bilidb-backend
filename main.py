# import logging

from flask import Flask
from flask_cors import CORS

from handler import user
import config

app = Flask(__name__)

CORS(app, resources=r'/*', supports_credentials=True)

app.register_blueprint(user.bp)

app.config.from_object(config)


# logging.basicConfig(level=logging.DEBUG, filename="./app.log")


if __name__ == '__main__':
    app.run()
