#!/usr/bin/env python2.7
# -*-coding:utf-8 -*-
__author__ = 'yin'

import json
import glob
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import logging
from optparse import OptionParser
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def get_file_list(dir_path, file_type):
    dir_path = dir_path + '/*' + file_type
    file_list = glob.glob(dir_path)
    return file_list


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
    parser.add_option("--host", dest="host", default="192.168.1.199", help="specify standard db host. default 192.168.1.199 ")
    parser.add_option("--port", dest="port", type="int", default=3306, help="specify standard db port. default 3306")
    parser.add_option("--user", dest="user", default="root", help="specify standard db user. default yqc")
    parser.add_option("--pwd", dest="password", default="lh", help="specify standard db pwd. default yqc2014")

    (options, args) = parser.parse_args()
    return options


def main():
    opt = res_option()
    db_connect = 'mysql+mysqldb://%s:%s@%s:%s/yiqiding_ktv?charset=utf8' % \
                 (opt.user, opt.password, opt.host, opt.port)
    engine = create_engine(db_connect)
    session = sessionmaker(bind=engine)
    sess = session()

    lyric_files = get_file_list("/var/www/lyrics", ".krc")
    video_files = get_file_list("/var/www/09", ".mp4")
    sess.execute("USE yiqiding_ktv;")
    index = 0
    try:
        for lists in sess.execute("SELECT mmid, lyric, has_lyric FROM media_music ;").fetchall():
            index += 1
            status = 0
            cur_path = "/var/www/lyrics/"
            cur_path += lists[1]
            if cur_path in lyric_files:
                status = 1

            str1 = "UPDATE media_music SET has_lyric = %d WHERE mmid = %d;" % (status, int(lists[0]))
            sess.execute(str1)
            error_lyr = "%d     %s" % (index, str1)
            logging.info(error_lyr)

        logging.info("检测的歌词sql语句数 %d " % index)

        index = 0
        for lists in sess.execute("SELECT mmid, path, enabled, has_lyric FROM media_music ;").fetchall():
            index += 1
            video = lists[1].split("/")[-1]
            print index, "   ", video, "  ", lists
            v_path = "/var/www/09/"
            v_path += video
            if v_path in video_files and lists[3] is 1:
                status = 1
            else:
                status = 0
            str2 = "UPDATE media_music SET enabled = %d WHERE mmid = %d;" % (status, int(lists[0]))
            sess.execute(str2)
            error_mv = "%d   %s" % (index, str2)
            logging.info(error_mv)

        logging.info("检测的歌曲sql语句数 %d " % index)
    except Exception, e:
        print e

if __name__ == '__main__':
    main()
