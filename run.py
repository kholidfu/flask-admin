#!/usr/bin/env python
# http://blog.yeradis.com/2012/11/standalone-flask-wsgi-running-under.html
from app import app
# print 'Twisted on port 5000...'
# from twisted.internet import reactor
# from twisted.web.server import Site
# from twisted.web.wsgi import WSGIResource

# resource = WSGIResource(reactor, reactor.getThreadPool(), app)
# site = Site(resource)

# reactor.listenTCP(5000, site, interface="0.0.0.0")
# reactor.run()

print 'Tornado on port 5000...'
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(5000)
IOLoop.instance().start()

# app.run(debug=True)
