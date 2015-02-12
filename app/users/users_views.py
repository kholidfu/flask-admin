from flask import render_template, redirect, request, session, flash, url_for
from flask import Blueprint
from functools import wraps
from app.forms import AdminLoginForm, UserLoginForm, UserRegisterForm
import pymongo


# setup database mongo
c = pymongo.Connection()
dbusers = c["users"]  # nanti ada dbusers.user, dbusers.admin, dll


users = Blueprint('users', __name__, url_prefix="/users")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is not None:
            return f(*args, **kwargs)
        else:
            flash("Please log in first...", "error")
            next_url = request.url
            login_url = "%s?next=%s" % (url_for("users.users_login"), next_url)
            return redirect(login_url)
    return decorated_function


@users.route("/register", methods=["GET", "POST"])
def users_register():
    form = UserRegisterForm()
    mail = Mail(app)
    error = None

    if request.method == "POST":
        # if username is blank
        if not form.username.data:
            error = "Username can't be empty!"
            return render_template("/users/register.html", form=form, error=error)
        # elif email is blank
        elif not form.email.data:
            error = "Email can't be empty!"
            return render_template("/users/register.html", form=form, error=error)
        # elif no password
        elif not form.password.data:
            error = "Please supply a password!"
            return render_template("/users/register.html", form=form, error=error)
        # is email already exists, failed
        elif form.username.data in ["admin", "banteng"]:
            error = "You can't use this username, try something else."
            return render_template("/users/register.html", form=form, error=error)
        elif dbusers.user.find_one({"email": form.email.data}):
            error = "Email is already taken, please choose another."
            return render_template("/users/register.html", form=form, error=error)
        elif dbusers.user.find_one({"username": form.username.data}):
            error = "Username is already taken, please choose another."
            return render_template("/users/register.html", form=form, error=error)
        elif "@" in form.username.data:
            error = "Don't use email as username. Pick another one!"
            return render_template("/users/register.html", form=form, error=error)
        else:
            # simpan session username
            session["username"] = form.username.data
            # simpan data
            dbusers.user.insert({
                                 "username": form.username.data,
                                 "password": form.password.data,
                                 "email": form.email.data,
                                 "collections": [],
                                 "friends": [],
                                 "uploaded_picture": [],
                                 "joined_at": datetime.datetime.now(),
                                 "favorited": [],  # isinya oid
                                 "voted": [],  # isinya oid
                                 })
            # send email
            emailstring = """
            Thank you for registering with example.com.

            Here is your credential info, please keep it secret:

            username: %s
            password: %s

            Regards,

            wallgigs.com
            """ % (form.username.data, form.password.data)
            msg = Message("Welcome to example.com", sender="info@example.com", recipients=[form.email.data])
            msg.body = emailstring
            mail.send(msg)
            # return redirect(request.args.get("next") or url_for("users"))
            return redirect(request.args.get("next") or url_for("index"))
    return render_template("/users/register.html", form=form)


@users.route("/")
@login_required
def users_index():
    user = session["username"]
    # if username == admin: redirect to admin page
    return render_template("/users/index.html", user=user)


@users.route("/login", methods=["GET", "POST"])
def users_login():
    form = UserLoginForm()
    error = None

    # if "username" in session:
    #     return redirect(url_for("users"))

    if request.method == "POST":
        # if username not exist in dbase, failed
        if not dbusers.user.find_one({"username": form.username.data}):
            error = "Username is not registered."
            return render_template("/users/login.html", form=form, error=error)
        # if password mismatch with dbase, failed
        elif dbusers.user.find_one({"username": form.username.data})["password"] != form.password.data:
            error = "Password mismatch!"
            return render_template("/users/login.html", form=form, error=error)
        # true semua
        else:
            session["username"] = form.username.data
            return redirect(request.args.get("next") or url_for("users.users_index"))
    return render_template("/users/login.html", form=form)

@users.route("/profile/<username>")
@login_required
def users_profile(username):
    # pakenya tetep db.user, biar ngumpul jadi satu
    data = dbusers.user.find_one({"username": session.get("username")})
    print session.get("username")
    if not data:
        return redirect("/")
    return render_template("users/profile.html", data=data)


@users.route("/logout")
def users_logout():
    if "username" not in session:
        return redirect(url_for("users_login"))
    session.pop("username", None)
    print "popped out!"  # fixed
    return redirect(url_for("index"))



