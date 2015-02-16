#!/usr/bin/env python
import optparse
from app import app

"""
There are 3 python web server here:
- werkzeug => ./run.py --builtin
- twisted  => ./run.py --twisted
- tornado  => ./run.py --tornado

help: ./run.py -h

adapted from here:
http://blog.yeradis.com/2012/11/standalone-flask-wsgi-running-under.html
"""

def builtin(option, opt_str, value, parser):
    print "Built in development server..."
    app.run(debug=True)

def tornado(option, opt_str, value, parser):
    print 'Tornado on port 5000...'
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()


def twisted(option, opt_str, value, parser):
    print 'Twisted on port 5000...'
    from twisted.internet import reactor
    from twisted.web.server import Site
    from twisted.web.wsgi import WSGIResource

    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    site = Site(resource)

    reactor.listenTCP(5000, site, interface="0.0.0.0")
    reactor.run()


def main():
    parser = optparse.OptionParser(usage="%prog [options] or type %prog -h (--help)")
    parser.add_option('--builtin',
                      help="Builtin Flask dev server", 
                      action="callback",
                      callback=builtin)
    parser.add_option('--tornado',
                      help="Tornado dev server",
                      action="callback",
                      callback=tornado)
    parser.add_option('--twisted',
                      help="Twisted dev server",
                      action="callback",
                      callback=twisted)
    (options, args) = parser.parse_args()
    parser.print_help()


if __name__ == "__main__":
    main()
