from flask import render_template, request, redirect
from flask import send_from_directory, session, flash, url_for
from flask import make_response  # sitemap
from flask import abort  # 404 page
from app import app
from werkzeug.contrib.atom import AtomFeed  # feed
from bson.objectid import ObjectId 
from filters import slugify
from functools import wraps
from forms import AdminLoginForm, UserLoginForm, UserRegisterForm
import datetime
import humanize
import pytz
import pymongo
from flask.ext.mail import Message, Mail


# setup database mongo
c = pymongo.Connection()
dbentity = c["entities"]  # db for dbentity.user, dbentity.admin, etc.


@app.errorhandler(404)
def page_not_found(e):
    """ handling 404 page
    ex: if something: abort(404)
    """
    return render_template("404.html"), 404


@app.errorhandler(500)
def exception_handler(e):
    return render_template("500.html"), 500


@app.template_filter()
def slug(s):
    """ 
    transform words into slug 
    usage: {{ string|slug }}
    """
    return slugify(s)


@app.template_filter("lastmod")
def jinja2_filter_lastmod(dt):
    """ make the date xml comply """
    return dt.replace(tzinfo=pytz.utc).isoformat()


@app.template_filter("humanize")
def jinja2_filter_humanize(date):
    """
    convert datetime object into human readable
    usage humanize(dateobject) or if in template
    {{ dateobject|humanize }}
    """
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


@app.route("/sitemap")
def sitemap():
    # data = db.freewaredata.find()
    # dummy data
    data = [{"title": "the title", "added": datetime.datetime.now()}]
    sitemap_xml = render_template("sitemap.xml", data=data)
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response


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
