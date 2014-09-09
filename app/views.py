# author: @sopier

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

@app.template_filter()
def slug(s):
    """ 
    transform words into slug 
    usage: {{ string|slug }}
    """
    return slugify(s)

@app.template_filter()
def split(s):
    """ 
    split string s with delimiter '-' 
    return list object
    usage: {{ string|split }}
    """
    return splitter(s, '-')

@app.template_filter()
def getlast(text, delim=' '):
    """
    get last word from string with delimiter ' '
    usage: {{ string|getlast }}
    """
    return get_last_part(text, delim)

@app.template_filter()
def getfirst(text, delim=' '):
    """
    get first word from string with delimiter '-'
    usage: {{ string|getfirst }}
    """
    return get_first_part(text, delim)

@app.template_filter()
def getchars(text):
    """
    get characters and numbers only from string
    usage: {{ string|getchars }}
    """
    return onlychars(text)

@app.template_filter()
def sectomins(seconds):
    """
    convert seconds to hh:mm:ss
    usage: {{ seconds|sectomins }}
    """
    return formattime(seconds)

@app.template_filter()
def urlcleaner(text):
    """
    clean url from string
    """
    return cleanurl(text)

# handle robots.txt file
@app.route("/robots.txt")
def robots():
    # point to robots.txt files
    return send_from_directory(app.static_folder, request.path[1:])

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin") is not None:
            return f(*args, **kwargs)
        else:
            flash("Please log in first...", "error")
            next_url = request.url
            login_url = "%s?next=%s" % (url_for("admin_login"), next_url)
            return redirect(login_url)
    return decorated_function

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

@app.route("/admin")
@admin_login_required
def admin():
    return render_template("admin/index.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    form = AdminLoginForm()

    if "admin" in session:
        return redirect(url_for("admin"))

    if request.method == "POST":
        if form.validate() == False:
            flash("invalid credentials")
            return render_template("admin/login.html", form=form)
        else:
            session["admin"] = form.email.data
            flash("Anda sudah berhasil masuk, selamat!", category="info")
            return redirect(request.args.get("next"))
    elif request.method == "GET":
        return render_template("/admin/login.html", form=form)

@app.route("/admin/logout")
def admin_logout():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    session.pop("admin", None)
    return redirect(url_for("index"))

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
