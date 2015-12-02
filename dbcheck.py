#!/usr/bin/env python2.7
# -*-coding:utf-8 -*-
__author__ = 'yin'
import json
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import logging
from optparse import OptionParser
from log import set_dir, debug, info, warning
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


logger = logging.getLogger("log")
log = logging.getLogger("db")


class DbCheck:
    def __init__(self, session_check, session, db, log_name="info", is_json=False):
        self.session_check = session_check
        self.session = session
        self.db = db
        self.log_name = log_name
        self.is_json = is_json

    def compare_field(self, table, db):
        try:
            field_check = self.session_check.execute('show columns from `%s`' % table).fetchall()
            field = self.session.execute('show columns from `%s`' % table).fetchall()
        except Exception, e:
            err_str = ' %s : %s ' % table, e
            self.write_file(db_name=db, err_str=err_str)
            return

        for fil in field:
            # self.logger.debug("         field : %s" % fil)
            debug("         field : %s" % fil)
            if len(fil) >= 1:
                if fil not in field_check:
                    self.write_file(db_name=db, table_name=table, field_name=fil[0], err_str=" Missing field ")
                else:
                    field_check.remove(fil)

        if len(field_check) > 1:
            for fn in field:
                self.write_file(db_name=db, table_name=table, field_name=fn[0], err_str="More than a field")

    def compare_tables(self, db):
        try:
            self.session_check.execute('use %s' % db)
            self.session.execute('use %s' % db)
            list_check = self.session_check.execute('show tables').fetchall()
            list_dst = self.session.execute('show tables').fetchall()
        except Exception, e:
            err_str = ' %s %s ' % list_dst[0], e
            self.write_file(db_name=db, err_str=err_str)
            return

        for tables in list_dst:
            # self.logger.debug("     table : %s" % tables)
            debug("     table : %s" % tables)
            if tables in list_check:
                self.compare_field(tables[0], db)
                list_check.remove(tables)
            else:
                self.write_file(db_name=db, table_name=tables[0], err_str=" Missing table ")
        if len(list_check) > 1:
            for tn in list_check:
                self.write_file(db_name=db, table_name=tn[0], err_str="More than a table")

    def compare_db(self):
        lists_check = []
        database_list = []
        try:
            if self.db is not None:
                lists_check.append(self.db)
                database_list.append(self.db)
            else:
                database_list = ['yiqiding', 'yiqiding_ktv', 'yiqiding_info', 'yqcchaindb', 'yqcdb']
                for lists in self.session_check.execute("SHOW  DATABASES;").fetchall():
                    lists_check.append(lists[0])
        except Exception, e:
            err_str = ' %s ' % e
            self.write_file(err_str=err_str)
            return

        for data in database_list:
            debug("database : %s" % data)
            if data not in lists_check:
                self.write_file(db_name=data, err_str=" Missing db ")
            else:
                self.compare_tables(data)

    def write_file(self, db_name=None, table_name=None, field_name=None, err_str=None):
        w_str = {}
        if err_str is not None:
            w_str["err"] = err_str
        if db_name is not None:
            w_str["db"] = db_name
        if table_name is not None:
            w_str["table"] = table_name
        if field_name is not None:
            w_str["field"] = field_name

        if self.is_json:
            info(name=self.log_name, msg=json.dumps(w_str, indent=4))
        else:
            info(name=self.log_name, msg=w_str)


def init_log(log_name):
    logging.basicConfig(
        level=logging.INFO,
        filename=log_name,
        filemode='w')

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    logging.getLogger('').addHandler(sh)


def res_option():
    parser = OptionParser()
    parser.add_option("--host", dest="host", default="192.168.1.233", help="specify standard db host. default 192.168.1.233 ")
    parser.add_option("--port", dest="port", type="int", default=3306, help="specify standard db port. default 3306")
    parser.add_option("--user", dest="user", default="yqc", help="specify standard db user. default yqc")
    parser.add_option("--pwd", dest="password", default="yqc2014", help="specify standard db pwd. default yqc2014")

    parser.add_option("--chost", dest="chost", default="127.0.0.1", help="specify check db host. default 127.0.0.1")
    parser.add_option("--cport", dest="cport", type="int", default=3306, help="specify check db port. default 3306")
    parser.add_option("--cuser", dest="cuser", default="yqc", help="specify check db user. default value yqc")
    parser.add_option("--cpwd", dest="cpassword", default="yqc2014", help="specify check db pwd. default value yqc2014")

    parser.add_option("-d", "--db", dest="db", default=None, help="specify check db. default check all")
    parser.add_option("-l", "--log", dest="log_name", default="dbinfo", help="log file name. default db.txt")
    parser.add_option("-j", "--json", dest="json", default=False, help="output json. default False")

    (options, args) = parser.parse_args()
    return options


def main():
    opt = res_option()
    db_connect_check = 'mysql+mysqldb://%s:%s@%s:%s/yiqiding_ktv?charset=utf8' % \
                       (opt.cuser, opt.cpassword, opt.chost, opt.cport)
    db_connect = 'mysql+mysqldb://%s:%s@%s:%s/yiqiding_ktv?charset=utf8' % \
                 (opt.user, opt.password, opt.host, opt.port)

    engine_check = create_engine(db_connect_check)
    engine_des = create_engine(db_connect)
    session_check = sessionmaker(bind=engine_check)
    session = sessionmaker(bind=engine_des)
    db = DbCheck(session_check(), session(), opt.db, opt.log_name, opt.json)
    db.compare_db()


if __name__ == '__main__':
    main()

