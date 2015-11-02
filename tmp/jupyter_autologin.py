#!/usr/bin/env python
import requests
import urllib

import tornado.httpserver
import tornado.ioloop

from tornado import gen
from tornado.httpclient import HTTPRequest, HTTPResponse, HTTPError, AsyncHTTPClient
from tornado.httputil import HTTPHeaders
from tornado.options import define, options
from tornado.web import RequestHandler


class IndexHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        # if not 'username-localhost-8888' in self.cookies:
        #     http_client = AsyncHTTPClient()
        #     http_req = HTTPRequest(url='http://localhost:8888/login',method='POST',body=urllib.urlencode({'password':'123'}))
        #     http_rsp = yield http_client.fetch(http_req)
        #     tmp = http_rsp.buffer
        # self.redirect(url='http://localhost:8888/tree')

        if not 'username-localhost-8888' in self.cookies:
            r = requests.post("http://localhost:8888/login", allow_redirects=False,data = {"password":"123"})
            for c in r.cookies:
                if c.value[0] == '"' and c.value[-1] == '"': value = c.value[1:-1]
                else: value = c.value
                self.set_cookie(c.name, value, domain=None, expires=None, path=None)
        self.redirect(url='http://localhost:8888/tree')


define("port", default=8010, help="run on the given port", type=int)


if __name__ == "__main__":
	tornado.options.parse_command_line()
	app = tornado.web.Application(handlers=[(r"/", IndexHandler)])
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
