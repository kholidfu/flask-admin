from flask import Blueprint

admin = Blueprint('admin', __name__, static_folder="/admin/static",
                  template_folder="templates")