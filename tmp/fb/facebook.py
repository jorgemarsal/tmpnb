import os
import uuid

import tornado.gen
import tornado.web
import tornado.httpserver
import tornado.auth
import tornado.ioloop
import tornado.options

import modules

class FacebookHandler(tornado.web.RequestHandler, tornado.auth.FacebookGraphMixin):
    @tornado.gen.coroutine
    def get(self):
        accessToken = self.get_secure_cookie('access_token')
        if not accessToken:
            self.redirect('/auth/login')
            return

        response = yield self.facebook_request(
            "/me/feed",
            access_token=accessToken)

        name = self.get_secure_cookie('user_name')
        self.render('home.html', feed=response['data'] if response else [], name=name)

    @tornado.gen.coroutine
    def post(self):
        accessToken = self.get_secure_cookie('access_token')
        if not accessToken:
            self.redirect('/auth/login')
            return

        userInput = self.get_argument('message')

        response = yield self.facebook_request(
            "/me/feed",
            post_args={'message': userInput},
            access_token=accessToken)

        self.redirect('/')


class LoginHandler(tornado.web.RequestHandler, tornado.auth.FacebookGraphMixin):
    @tornado.gen.coroutine
    def get(self):
        userID = self.get_secure_cookie('user_id')

        if self.get_argument('code', None):
            user = yield self.get_authenticated_user(
                redirect_uri='http://localhost:8011/auth/login',
                client_id=self.settings['facebook_api_key'],
                client_secret=self.settings['facebook_secret'],
                code=self.get_argument('code'))
            if not user:
                self.clear_all_cookies()
                raise tornado.web.HTTPError(500, 'Facebook authentication failed')

            self.set_secure_cookie('user_id', str(user['id']))
            self.set_secure_cookie('user_name', str(user['name']))
            self.set_secure_cookie('access_token', str(user['access_token']))
            self.redirect('/')

        elif self.get_secure_cookie('access_token'):
            self.redirect('/')

        self.authorize_redirect(
            redirect_uri='http://localhost:8011/auth/login',
            client_id=self.settings['facebook_api_key'],
            extra_params={'scope': 'email,publish_actions,user_posts'}
        )


class LogoutHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.clear_all_cookies()
        self.render('logout.html')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', FacebookHandler),
            (r'/auth/login', LoginHandler),
            (r'/auth/logout',  LogoutHandler)
        ]

        settings = {
            'facebook_api_key': os.environ['FB_APP_ID'],
            'facebook_secret': os.environ['FB_APP_SECRET'],
            'cookie_secret': 'MpoBYXlPKCIJqmiu2SdT28Uz5C+9kdWmE+haGSW4Lf3NFwsbedTUxTtDdnO9c0Xb1Mo=',
            'template_path': 'templates',
            'ui_modules': modules
        }

        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    tornado.options.parse_command_line()

    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(8011)
    tornado.ioloop.IOLoop.instance().start()
