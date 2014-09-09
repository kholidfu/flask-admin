from flask import render_template, redirect, request, session, flash, url_for
from flask import Blueprint
from functools import wraps

admin = Blueprint('admin', __name__, url_prefix="/admin")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is not None:
            return f(*args, **kwargs)
        else:
            flash("Please log in first...", "error")
            next_url = request.url
            login_url = "%s?next=%s" % (url_for("admin_login"), next_url)
            return redirect(login_url)
    return decorated_function

@admin.route("/admin")
@login_required
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
