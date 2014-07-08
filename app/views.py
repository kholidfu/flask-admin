# author: @sopier

from flask import render_template, request, redirect, send_from_directory
from flask import make_response # untuk sitemap
from app import app
# untuk find_one based on data id => db.freewaredata.find_one({'_id': ObjectId(file_id)})
# atom feed
from werkzeug.contrib.atom import AtomFeed
from bson.objectid import ObjectId 
from filters import slugify, splitter, onlychars, get_first_part, get_last_part, formattime, cleanurl

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

@app.route("/")
def index():
    return render_template("index.html")

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
