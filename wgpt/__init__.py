from flask import Flask
from flask_restful import Api
from config import Config
from flask_sqlalchemy import SQLAlchemy
from wgpt.ssh_check import generate_keys

app = Flask(__name__, static_url_path='')
api = Api(app)
app.config.from_object(Config)
db = SQLAlchemy(app)

from wgpt import routes, models

with app.app_context():
    try:
        conf = models.ConfigOptions.query.all()
        if not conf:
            print('No ssh keys found, generating')
            priv, pub = generate_keys()
            new_conf = models.ConfigOptions(
                ssh_privkey = priv,
                ssh_pubkey = pub
            )
            db.session.add(new_conf)
            db.session.commit()
    except:
        print('Could not read ConfigOptions from database, does it exist?')
    