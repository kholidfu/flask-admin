from flask import Flask
from app.admin import admin
from flask.ext.mail import Mail


app = Flask(__name__,
        static_folder="static", # match with your static folder
        static_url_path="/static" # you can change this to anything other than static, its your URL
      )

# mail config start

mail = Mail(app)

app.config.update(
                    MAIL_SERVER='smtp.gmail.com',
                    MAIL_PORT=465,
                    MAIL_USE_SSL=True,
                    MAIL_USERNAME = 'email@gmail.com',
                    MAIL_PASSWORD = 'yourcurrentpasswordis'
                  )
# mail config end

from app import views


# global domain name config
# calling from jinja => {{ config["domain_name"] }}
app.config["DOMAIN_NAME"] = "example"
app.config["DOMAIN_URL"] = "example.com"

# important! needed for login things >> joss
app.secret_key = "vertigo"

# adding admin blueprint
from app.admin.views import admin
app.register_blueprint(admin)

# logging tools
# author: https://gist.github.com/mitsuhiko/5659670
# monitor uwsgi access / error :: output di nohup.out

import sys
from logging import Formatter, StreamHandler
handler = StreamHandler(sys.stderr)
handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(handler)
