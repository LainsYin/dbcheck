#!/usr/bin/env python2.7
# -*-coding:utf-8 -*-
__author__ = 'yin'
import json
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import logging
from optparse import OptionParser
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class DbCheck:
    def __init__(self, session, log_name, json_file):
        self.session = session
        self.log_name = log_name
        self.json = json.load(file(json_file))
        self.database_list = {}
        self.db_check_list = []

        self.check_init()
        self.check_database()

    def check_init(self):
        for db_list in self.json:
            db_name = db_list.get('database')
            tables = db_list.get('table')

            table_list = []
            for table in tables:
                field_list = {}
                table_name = table.get('table')
                field_list[table_name] = table.get('field')
                table_list.append(field_list)

            self.database_list[db_name] = table_list

    def check_database(self):
        for lists in self.execute_sql("SHOW  DATABASES;"):
            self.db_check_list.append(lists[0])

        for db_name in self.database_list.keys():
            logging.info('检测{}数据库...'.format(db_name))
            if db_name not in self.db_check_list:
                logging.debug('数据库不存在:{}'.format(db_name))
            else:
                self.execute_sql('USE {};'.format(db_name))
                self.check_table(self.database_list.get(db_name))

    def check_table(self, tables_list):
        tables = []
        for lists in self.execute_sql('SHOW TABLES;'):
            tables.append(lists[0])

        table_field = {}
        for table in tables_list:
            table_name = table.keys()[0]
            field_list = table.get(table_name)
            table_field[table_name] = field_list

        for name in table_field.keys():
            if name not in tables:
                logging.debug('不存在表:{}'.format(name))
            else:
                self.check_field(name, table_field.get(name))

    def check_field(self, table_name, filed_list):
        structures = self.execute_sql('DESC {};'.format(table_name))
        fields = []
        for structure in structures:
            str_val = [structure[0], structure[1]]
            fields.append(str_val)

        for field in filed_list:
            if field not in fields:
                logging.debug('表{}缺少字段:{}'.format(table_name, field))

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
        level=logging.DEBUG,
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
                      help='specify standard db host. default 127.0.0.1 ')
    parser.add_option('-t', '--port', dest='port', type='int', default=3306,
                      help='specify standard db port. default 3306')
    parser.add_option('-u', '--user', dest='user', default='yqc',
                      help='specify standard db user. default yqc')
    parser.add_option('-p', '--pwd', dest='password', default='yqc2014',
                      help='specify standard db pwd. default yqc2014')
    parser.add_option('-l', '--log', dest='log_name', default='dbcheck.log',
                      help='log file name. default dbcheck.log')
    parser.add_option('-j', '--json', dest='json', default='export.sql',
                      help='read file. default export.sql')

    (options, args) = parser.parse_args()
    return options


def main():
    opt = res_option()
    init_log(opt.log_name)
    db_connect = 'mysql+mysqldb://%s:%s@%s:%s/yiqiding_ktv?charset=utf8' % \
                 (opt.user, opt.password, opt.host, opt.port)

    engine = create_engine(db_connect)
    session = sessionmaker(bind=engine)
    DbCheck(session(), opt.log_name, opt.json)


if __name__ == '__main__':
    main()

