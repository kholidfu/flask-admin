from flask import Flask
from app.admin import admin

app = Flask(__name__, 
        static_folder="static", # match with your static folder
        static_url_path="/static" # you can change this to anything other than static, its your URL
      )

from app import views

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
