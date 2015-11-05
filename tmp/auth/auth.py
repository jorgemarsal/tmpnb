import tornado.httpserver
import tornado.web
from tornado import ioloop, gen
from tornado.options import define, options

import uuid

from werkzeug.security import generate_password_hash, \
     check_password_hash

class BaseHandler(tornado.web.RequestHandler):

    def get_login_url(self):
        return u"/login"

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if user_json:
            return tornado.escape.json_decode(user_json)
        else:
            return None

class IndexHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("templates/index.html")

class LoginHandler(BaseHandler):

    def authenticate(self, username, password):
        golden = generate_password_hash('123')
        return check_password_hash(golden, password) and username == 'jorgemarsal'

    def get(self):
        self.render("templates/login.html", next=self.get_argument("next","/"))

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        # The authenticate method should match a username and password
        # to a username and password hash in the database users table.
        # Implementation left as an exercise for the reader.

        auth = self.authenticate(username, password)

        if auth:
            self.set_current_user(username)
            next = self.get_argument("next", u"/")
            if not next:
                self.redirect('/')
            else:
                self.redirect(next)
        else:
            error_msg = u"?error=" + tornado.escape.url_escape("Login incorrect.")
            self.redirect(u"/login" + error_msg)

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")

class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie("user")
        self.redirect(u"/login")

define("port", default=8012, help="run on the given port", type=int)


if __name__ == "__main__":
    settings = dict(cookie_secret='fd3fa3ea-4c48-49ed-a4d4-bba588f106e0')
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler),
                                            (r"/login", LoginHandler),
                                            (r"/logout", LogoutHandler)],
                                  **settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


