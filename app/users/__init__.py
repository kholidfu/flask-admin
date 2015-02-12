from flask import Blueprint

users = Blueprint('users', __name__, static_folder="/users/static",
                  template_folder="templates")
