#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import json
from recommendation import rmd


class RmdByUserHandler(tornado.web.RequestHandler):
    def get(self, username):
        rmd_sys = rmd(
            MySQL_info={
                "host": "localhost",
                "user": "root",
                "passwd": "199528",
                "db": "OJ_data",
                "charset": "utf8"
            },
        )
        self.write(json.dumps(rmd_sys.rmd_by_user(username)[:10]))
        rmd_sys.close_con()


class RmdByProHandler(tornado.web.RequestHandler):
    def get(self, pid):
        rmd_sys = rmd(
            MySQL_info={
                "host": "localhost",
                "user": "root",
                "passwd": "199528",
                "db": "OJ_data",
                "charset": "utf8"
            },
        )
        self.write(json.dumps(rmd_sys.rmd_by_problem(int(pid))[:10]))
        rmd_sys.close_con()


class UserRatingHandler(tornado.web.RequestHandler):
    def get(self, username):
        rmd_sys = rmd(
            MySQL_info={
                "host": "localhost",
                "user": "root",
                "passwd": "199528",
                "db": "OJ_data",
                "charset": "utf8"
            },
        )
        self.write(json.dumps(rmd_sys.get_elo(username)[0]))
        rmd_sys.close_con()


class ProRatingHandler(tornado.web.RequestHandler):
    def get(self, pid):
        rmd_sys = rmd(
            MySQL_info={
                "host": "localhost",
                "user": "root",
                "passwd": "199528",
                "db": "OJ_data",
                "charset": "utf8"
            },
        )
        self.write(json.dumps(rmd_sys.get_prating(int(pid))))
        rmd_sys.close_con()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class UserInfoHandler(tornado.web.RequestHandler):
    def get(self, username):
        rmd_sys = rmd(
            MySQL_info={
                "host": "localhost",
                "user": "root",
                "passwd": "199528",
                "db": "OJ_data",
                "charset": "utf8"
            },
        )
        self.write(json.dumps(rmd_sys.get_user_info(username)))
        rmd_sys.close_con()


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/Recommendation/user/(.*)/", RmdByUserHandler),
    (r"/Recommendation/problem/Pku/(.*)/", RmdByProHandler),
    (r"/UserRating/(.*)/", UserRatingHandler),
    (r"/ProblemRating/(.*)/", ProRatingHandler),
    (r"/UserInfo/(.*)/", UserInfoHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()