#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import datetime
import time
import json
from tornado.ioloop import PeriodicCallback
from recommendation import rmd
from POJ_fetch_mysql import POJ_fetcher as pspider

MySQL_info = {
    "host": "localhost",
    "user": "root",
    "passwd": "199528",
    "db": "OJ_data",
    "charset": "utf8"
}


def logging(msg, lv):
    ISOTIMEFORMAT = "%Y-%m-%d %X"
    logtime = time.strftime(ISOTIMEFORMAT, time.localtime())
    lvstr = ["MASSAGE", "WARNING", "ERROR  "]
    print lvstr[lv], logtime, ":", msg


class RmdByUserHandler(tornado.web.RequestHandler):
    def get(self, username):
        rmd_sys = rmd(MySQL_info)
        self.write(json.dumps(rmd_sys.rmd_by_user(username)[:10]))
        rmd_sys.close_con()


class RmdByProHandler(tornado.web.RequestHandler):
    def get(self, pid):
        rmd_sys = rmd(MySQL_info)
        self.write(json.dumps(rmd_sys.rmd_by_problem(int(pid))[:10]))
        rmd_sys.close_con()


class UserRatingHandler(tornado.web.RequestHandler):
    def get(self, username):
        rmd_sys = rmd(MySQL_info)
        self.write(json.dumps(rmd_sys.get_elo(username)[0]))
        rmd_sys.close_con()


class ProRatingHandler(tornado.web.RequestHandler):
    def get(self, pid):
        rmd_sys = rmd(MySQL_info)
        self.write(json.dumps(rmd_sys.get_prating(int(pid))))
        rmd_sys.close_con()

    def post(self):
        rmd_sys = rmd(MySQL_info)
        self.write(json.dumps(rmd_sys.get_prating_all()))
        rmd_sys.close_con()


class ProRatingAllHandler(tornado.web.RequestHandler):
    def get(self):
        rmd_sys = rmd(MySQL_info)
        self.write(json.dumps(rmd_sys.get_prating_all()))
        rmd_sys.close_con()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class UserInfoHandler(tornado.web.RequestHandler):
    def get(self, username):
        rmd_sys = rmd(MySQL_info)
        self.write(json.dumps(rmd_sys.get_user_info(username)))
        rmd_sys.close_con()

    def post(self):
        rmd_sys = rmd(MySQL_info)
        print self.get_argument('group')
        group = json.loads(self.get_argument('group'))
        self.write(json.dumps(rmd_sys.get_user_info_group(group)))
        rmd_sys.close_con()


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/Recommendation/user/(.*)/", RmdByUserHandler),
    (r"/Recommendation/problem/Pku/(.*)/", RmdByProHandler),
    (r"/UserRating/(.*)/", UserRatingHandler),
    (r"/ProblemRating/(.*)/", ProRatingHandler),
    (r"/ProblemRatingAll/", ProRatingAllHandler),
    (r"/UserInfo/(.*)/", UserInfoHandler),
    (r"/UserInfo/", UserInfoHandler),
])


def fetch():
    fetcher = pspider(
        MySQL_info={
            "host": "localhost",
            "user": "root",
            "passwd": "199528",
            "db": "OJ_data",
            "charset": "utf8"
        },
        quiet=True
    )
    logging("Poj spider Start!", 0)
    fetcher.main(None, None, datetime.datetime.today())
    logging("Poj spider End!", 0)


if __name__ == "__main__":
    application.listen(8888)
    pc = PeriodicCallback(fetch, 1000 * 60 * 60)
    pc.start()
    tornado.ioloop.IOLoop.instance().start()
