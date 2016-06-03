#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import numpy as np
import json


class status():
    """docstring for status"""
    def __init__(self, item):
        self.run_id = item[0]
        self.username = item[1]
        self.problem_id = item[2]
        self.result = item[3]
        self.memory = item[4]
        self.time_run = item[5]
        self.language = item[6]
        self.code_len = item[7]
        self.time = item[8]


class problem():
    """docstring for problem"""
    def __init__(self):
        self.vec = []
        self.rating = 1500


class rmd(object):
    def __init__(self, MySQL_info):
        self.sqlcon = MySQLdb.connect(
            host=MySQL_info["host"],
            user=MySQL_info["user"],
            passwd=MySQL_info["passwd"],
            db=MySQL_info["db"],
            charset=MySQL_info["charset"]
        )
        self.PROBLEM_MAP = {}
        self.MYSQLCUR = self.sqlcon.cursor()
        sql = "select * from OJ_data.problem_info where repo = 'Pku'"
        self.MYSQLCUR.execute(sql)
        for record in self.MYSQLCUR.fetchall():
            problem_ins = problem()
            problem_ins.vec = map(float, json.loads(record[3]))
            problem_ins.rating = float(record[2])
            self.PROBLEM_MAP[record[1]] = problem_ins

    def get_prating(self, pid):
        return self.PROBLEM_MAP[pid].rating

    def get_prating_all(self):
        prating_ret = []
        for k in self.PROBLEM_MAP:
            prating_ret.append({
                'ID': k,
                'level': int(self.PROBLEM_MAP[k].rating)
            })
        return prating_ret

    def cal_elo(self, ra, rb, res):
        EA = 1 / (1 + 10 ** ((rb - ra) / 400.0))
        EB = 1 / (1 + 10 ** ((ra - rb) / 400.0))
        KA = KB = SA = SB = 0
        if ra > 2400:
            KA = 3
        elif ra > 1800:
            KA = 6
        else:
            KA = 9
        if rb > 2400 or rb < 600:
            KB = 10
        elif rb > 1900 or rb < 1100:
            KB = 15
        else:
            KB = 30
        if res:
            SA = 1
            SB = 0
            factor = 1
        else:
            SA = 0
            SB = 1
            factor = 0.05
        RA = ra + KA * (SA - EA) * factor
        RB = rb + KB * (SB - EB)
        return RA, RB

    def get_elo(self, username):
        sql = "select * from poj_data where User = '%s' and Result != 'Compile Error'"
        self.MYSQLCUR.execute(sql % username)
        rating = 1500.0
        black_hole = 1500
        ac_arr = []
        for item in self.MYSQLCUR.fetchall():
            sta = status(item)
            if sta.result == 'Accepted' and sta.problem_id not in ac_arr:
                ac_arr.append(sta.problem_id)
                rating, black_hole = self.cal_elo(
                    rating,
                    self.PROBLEM_MAP[sta.problem_id].rating,
                    True
                )
            elif sta.result != 'Accepted' and sta.problem_id not in ac_arr:
                rating, black_hole = self.cal_elo(
                    rating,
                    self.PROBLEM_MAP[sta.problem_id].rating,
                    False
                )
        return rating, ac_arr

    def get_user_info(self, username):
        sql = "select * from poj_data where User = '%s' and Result != 'Compile Error'"
        self.MYSQLCUR.execute(sql % username)
        rating = 1500.0
        black_hole = 1500
        ac_arr = []
        rating_arr = []
        for item in self.MYSQLCUR.fetchall():
            sta = status(item)
            rating_flag = False
            if sta.result == 'Accepted' and sta.problem_id not in ac_arr:
                ac_arr.append(sta.problem_id)
                rating, black_hole = self.cal_elo(
                    rating,
                    self.PROBLEM_MAP[sta.problem_id].rating,
                    True
                )
                rating_flag = True
            elif sta.result != 'Accepted' and sta.problem_id not in ac_arr:
                rating, black_hole = self.cal_elo(
                    rating,
                    self.PROBLEM_MAP[sta.problem_id].rating,
                    False
                )
                rating_flag = True
            if rating_flag:
                rating_arr.append({
                    'Rating': rating,
                    'date': str(sta.time)
                })
        ac_rating_arr = []
        for item in ac_arr:
            ac_rating_arr.append([item, self.PROBLEM_MAP[item].rating])
        return rating, ac_rating_arr, rating_arr

    def get_user_info_group(self, group):
        ret_data = []
        for item in group:
            rating, ac_arr, rating_arr = self.get_user_info(item[1])
            ret_data.append({
                'name': item[0],
                'values': rating_arr
            })
        return ret_data

    def cal_cosin(self, veca, vecb):
        x = np.array(veca)
        y = np.array(vecb)
        lx = np.sqrt(x.dot(x))
        ly = np.sqrt(y.dot(y))
        return float(x.dot(y) / (lx * ly))

    def rmd_by_problem(self, problem_id):
        if len(self.PROBLEM_MAP[problem_id].vec) != 200:
            return []
        ans = []
        for key in self.PROBLEM_MAP:
            if key != problem_id and len(self.PROBLEM_MAP[key].vec) == 200:
                cos_dis = self.cal_cosin(
                    self.PROBLEM_MAP[problem_id].vec,
                    self.PROBLEM_MAP[key].vec
                )
                ans.append((key, cos_dis))
        ans = sorted(ans, cmp=lambda x, y: cmp(y[1], x[1]))
        return ans

    def rmd_by_user(self, username):
        ac_sql = "select * from poj_data where User = '%s' \
            order by RunId desc limit 10"
        self.MYSQLCUR.execute(ac_sql % username)
        problem_set = set()
        for item in self.MYSQLCUR.fetchall():
            sta = status(item)
            problem_set.add(sta.problem_id)
        ans_set = set()
        for item in problem_set:
            rmd_res = self.rmd_by_problem(item)
            for items in rmd_res:
                ans_set.add(items)
        # print ans_set
        ans = []
        user_elo, ac_arr = self.get_elo(username)
        for item in ans_set:
            if item[0] not in ac_arr:
                rl_err = 1 - abs(user_elo - self.PROBLEM_MAP[item[0]].rating) / user_elo
                ans.append((item[0], item[1] * rl_err))
        ans = sorted(
            ans,
            cmp=lambda x, y: cmp(y[1], x[1])
        )
        return ans

    def close_con(self):
        self.sqlcon.close()

if __name__ == '__main__':
    rmd_sys = rmd(
        MySQL_info={
            "host": "localhost",
            "user": "root",
            "passwd": "199528",
            "db": "OJ_data",
            "charset": "utf8"
        },
    )
    print rmd_sys.get_prating_all()
