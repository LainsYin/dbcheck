#!/usr/bin/env python2.7
# -*-coding:utf-8 -*-
__author__ = 'yin'
import json
import os.path
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import logging
from optparse import OptionParser
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class DbExport():
    def __init__(self, session, db, log_name, json_name):
        self.session = session
        self.db = db
        self.log_name = log_name
        self.json_name = json_name

        databases = []
        for database in db:
            dbs = {
                'database': database,
                'table': self.export_tables(database)
            }
            databases.append(dbs)

        file_object = open(json_name, 'w')
        file_object.write(json.dumps(databases, indent=4, ensure_ascii=False))
        file_object.close()
        print os.path.abspath(json_name)

    def export_tables(self, db_name):
        self.execute_sql('USE {}'.format(db_name))
        table = self.execute_sql('SHOW TABLES;')
        tables = []
        for lists in table:
            fields = {
                'table': lists[0],
                'field': self.export_structure(lists[0])
            }
            tables.append(fields)
        return tables

    def export_structure(self, table_name):
        structures = self.execute_sql('DESC {};'.format(table_name))
        field = []
        for structure in structures:
            str_val = [structure[0], structure[1]]
            field.append(str_val)
        return field

    def execute_sql(self, sql_str):
        try:
            if not sql_str.find('USE') == -1:
                self.session.execute(sql_str)
                return []
            else:
                return self.session.execute(sql_str).fetchall()
        except Exception, e:
            logging.error(e)


def init_log(log_name):
    logging.basicConfig(
        level=logging.INFO,
        filename=log_name,
        format='[%(asctime)s - %(levelname)-8s] %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filemode='w')

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    logging.getLogger('').addHandler(sh)


def res_option():
    parser = OptionParser()
    parser.add_option('-i', '--host', dest='host', default='127.0.0.1',
                      help='specify standard db host. default 127.0.0.1')
    parser.add_option('-t', '--port', dest='port', type='int', default=3306,
                      help='specify standard db port. default 3306')
    parser.add_option('-u', '--user', dest='user', default='yqc',
                      help='specify standard db user. default yqc')
    parser.add_option('-p', '--pwd', dest='password', default='yqc2014',
                      help='specify standard db pwd. default yqc2014')

    parser.add_option('-d', '--db', dest='db', default='yiqiding_info,yiqiding_ktv',
                      help='specify export db. eg: -d yiqiding_info,yiqiding_ktv')
    parser.add_option('-l', '--log', dest='log_name', default='dbexport.log',
                      help='log file name. default dbexport.log')
    parser.add_option('-j', '--json', dest='json', default='export.sql',
                      help='output json. default export.sql')

    (options, args) = parser.parse_args()
    return options


def main():
    opt = res_option()
    init_log(opt.log_name)
    db_connect = 'mysql+mysqldb://%s:%s@%s:%s/yiqiding_ktv?charset=utf8' % \
                 (opt.user, opt.password, opt.host, opt.port)

    engine = create_engine(db_connect)
    session = sessionmaker(bind=engine)
    db_list = str(opt.db).split(',')
    if db_list is None:
        print '未指定数据库'
    else:
        DbExport(session(), db_list, opt.log_name, opt.json)


if __name__ == '__main__':
    main()

