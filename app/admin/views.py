from flask import render_template
from flask import Blueprint

admin = Blueprint('admin', __name__, url_prefix="/admin")

@admin.route("/")
def index():
	return render_template("admin/index.html")

@admin.route("/flot")
def flot():
	return render_template("admin/flot.html")

@admin.route("/morris")
def morris():
	return render_template("admin/morris.html")

@admin.route("/tables")
def tables():
	return render_template("admin/tables.html")

@admin.route("/forms")
def forms():
	return render_template("admin/forms.html")

@admin.route("/panels-wells")
def panels_wells():
	return render_template("admin/panels-wells.html")

@admin.route("/buttons")
def buttons():
	return render_template("admin/buttons.html")

@admin.route("/notifications")
def notifications():
	return render_template("admin/notifications.html")

@admin.route("/typography")
def typography():
	return render_template("admin/typography.html")

@admin.route("/grid")
def grid():
	return render_template("admin/grid.html")

@admin.route("/blank")
def blank():
	return render_template("admin/blank.html")

@admin.route("/login")
def login():
	return render_template("admin/login.html")