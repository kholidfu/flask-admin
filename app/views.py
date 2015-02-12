from flask import render_template, request, redirect, send_from_directory, session, flash, url_for
from flask import make_response # untuk sitemap
from app import app
# untuk find_one based on data id => db.freewaredata.find_one({'_id': ObjectId(file_id)})
# atom feed
from werkzeug.contrib.atom import AtomFeed
from bson.objectid import ObjectId 
from filters import slugify, splitter, onlychars, get_first_part, get_last_part, formattime, cleanurl
from functools import wraps
from forms import AdminLoginForm, UserLoginForm, UserRegisterForm
import datetime
import pymongo
from flask.ext.mail import Message, Mail


# setup database mongo
c = pymongo.Connection()
dbentity = c["entities"]  # nanti ada dbentity.user, dbentity.admin, dll


@app.template_filter()
def slug(s):
    """ 
    transform words into slug 
    usage: {{ string|slug }}
    """
    return slugify(s)

@app.template_filter("humanize")
def jinja2_filter_humanize(date):
    """
    convert datetime object into human readable
    usage humanize(dateobject) or if in template
    {{ dateobject|humanize }}
    """
    import humanize
    secs = datetime.datetime.now() - date
    secs = int(secs.total_seconds())
    date = humanize.naturaltime(datetime.datetime.now() - datetime.timedelta(seconds=secs))  # 10 seconds ago
    return date


# handle robots.txt file
@app.route("/robots.txt")
def robots():
    # point to robots.txt files
    return send_from_directory(app.static_folder, request.path[1:])


def user_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is not None:
            return f(*args, **kwargs)
        else:
            flash("Please log in first...", "error")
            next_url = request.url
            login_url = "%s?next=%s" % (url_for("users_login"), next_url)
            return redirect(login_url)
    return decorated_function

@app.route("/")
def index():
    return render_template("index.html")

# @app.route("/admin")
# @admin_login_required
# def admin():
#     return render_template("admin/index.html")

# @app.route("/admin/login", methods=["GET", "POST"])
# def admin_login():
#     form = AdminLoginForm()

#     # if "admin" in session:
#     #     return redirect(url_for("admin"))

#     if request.method == "POST":
#         if form.validate() == False:
#             flash("invalid credentials")
#             return render_template("admin/login.html", form=form)
#         else:
#             session["admin"] = form.email.data
#             flash("Anda sudah berhasil masuk, selamat!", category="info")
#             return redirect(request.args.get("next") or url_for("admin"))
#     elif request.method == "GET":
#         return render_template("/admin/login.html", form=form)

# @app.route("/admin/logout")
# def admin_logout():
#     if "admin" not in session:
#         return redirect(url_for("admin_login"))
#     session.pop("admin", None)
#     return redirect(url_for("index"))

# @app.route("/users/login", methods=["GET", "POST"])
# def users_login():
#     form = UserLoginForm()
#     error = None

#     if "username" in session:
#         return redirect(url_for("users"))

#     if request.method == "POST":
#         # if username not exist in dbase, failed
#         if not dbentity.users.find_one({"username": form.username.data}):
#             error = "Username is not registered."
#             return render_template("/users/login.html", form=form, error=error)
#         # if password mismatch with dbase, failed
#         elif dbentity.users.find_one({"username": form.username.data})["password"] != form.password.data:
#             error = "Password mismatch!"
#             return render_template("/users/login.html", form=form, error=error)
#         # true semua
#         else:
#             session["username"] = form.username.data
#             return redirect(request.args.get("next") or url_for("users"))
#     return render_template("/users/login.html", form=form)

# @app.route("/users/<username>/profile", methods=["GET", "POST"])
# @user_login_required
# def users_profile(username):
#     # pakenya tetep db.user, biar ngumpul jadi satu
#     data = db.user.find_one({"username": session.get("username")})
#     return render_template("users/profile.html", data=data)


# @app.route("/users/<username>")
# def users_public_view(username):
#     """ this is for public view
#     contains:
#     all the picture uploaded.
#     """
#     return render_template("users_public_view.html")


# @app.route("/users/logout")
# def users_logout():
#     if "username" not in session:
#         return redirect(url_for("users_login"))
#     session.pop("username", None)
#     return redirect(url_for("index"))

# @app.route("/users")
# @user_login_required
# def users():
#     user = session["username"]
#     # if username == admin: redirect to admin page
#     return render_template("/users/index.html", user=user)

# @app.route("/users/register", methods=["GET", "POST"])
# def users_register():
#     form = UserRegisterForm()
#     mail = Mail(app)
#     error = None

#     if request.method == "POST":
#         # if username is blank
#         if not form.username.data:
#             error = "Username can't be empty!"
#             return render_template("/users/register.html", form=form, error=error)
#         # elif email is blank
#         elif not form.email.data:
#             error = "Email can't be empty!"
#             return render_template("/users/register.html", form=form, error=error)
#         # elif no password
#         elif not form.password.data:
#             error = "Please supply a password!"
#             return render_template("/users/register.html", form=form, error=error)
#         # is email already exists, failed
#         elif form.username.data in ["admin", "banteng"]:
#             error = "You can't use this username, try something else."
#             return render_template("/users/register.html", form=form, error=error)
#         elif dbentity.users.find_one({"email": form.email.data}):
#             error = "Email is already taken, please choose another."
#             return render_template("/users/register.html", form=form, error=error)
#         elif dbentity.users.find_one({"username": form.username.data}):
#             error = "Username is already taken, please choose another."
#             return render_template("/users/register.html", form=form, error=error)
#         elif "@" in form.username.data:
#             error = "Don't use email as username. Pick another one!"
#             return render_template("/users/register.html", form=form, error=error)
#         else:
#             # simpan session username
#             session["username"] = form.username.data
#             # simpan data
#             dbentity.users.insert({
#                                  "username": form.username.data,
#                                  "password": form.password.data,
#                                  "email": form.email.data,
#                                  "collections": [],
#                                  "friends": [],
#                                  "uploaded_picture": [],
#                                  "joined_at": datetime.datetime.now(),
#                                  "favorited": [],  # isinya oid
#                                  "voted": [],  # isinya oid
#                                  })
#             # send email
#             emailstring = """
#             Thank you for registering with example.com.

#             Here is your credential info, please keep it secret:

#             username: %s
#             password: %s

#             Regards,

#             wallgigs.com
#             """ % (form.username.data, form.password.data)
#             msg = Message("Welcome to example.com", sender="info@example.com", recipients=[form.email.data])
#             msg.body = emailstring
#             mail.send(msg)
#             # return redirect(request.args.get("next") or url_for("users"))
#             return redirect(request.args.get("next") or url_for("index"))
#     return render_template("/users/register.html", form=form)

@app.route("/sitemap.xml")
def sitemap():
    # data = db.freewaredata.find()
    # sitemap_xml = render_template("sitemap.xml", data=data)
    # response = make_response(sitemap_xml)
    # response.headers['Content-Type'] = 'application/xml'

    # return response
    pass

@app.route('/recent.atom')
def recent_feed():
    # http://werkzeug.pocoo.org/docs/contrib/atom/ 
    # wajibun: id(link) dan updated
    # feed = AtomFeed('Recent Articles',
    #                feed_url = request.url, url=request.url_root)
    # data = datas
    # for d in data:
    #    feed.add(d['nama'], content_type='html', id=d['id'], updated=datetime.datetime.now())
    # return feed.get_response()
    pass
