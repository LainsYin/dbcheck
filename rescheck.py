#!/usr/bin/env python2.7
# -*-coding:utf-8 -*-
__author__='yin'
import os
import sys
import glob
import random
import json
import pdb

from optparse import OptionParser
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import logging
reload(sys)
sys.setdefaultencoding("utf-8")


class ResCheck:

    def __init__(self, host, user, pwd, port, db, filename, res_dir, logger, write_json=False):
        self.db_connect_str = 'mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8' % (user, pwd, host, port, db)
        self.engine = create_engine(self.db_connect_str)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.root_path = res_dir
        self.file_name = filename
        self.logger = logger
        self.write_json = write_json

    def write_to_file(self, err_lists, err_type):
        if self.write_json:
            json_list = []
            if err_type == 'fm' or err_type == 'actor':
                for line_err in err_lists:
                    json_list.append(line_err)
            else:
                for json_line in err_lists:
                    lines = []
                    for data in json_line:
                        lines.append(data)
                    json_list.append(lines)
                json_list.insert(0, err_type)
            logging.info(json.dumps(json_list, indent=4))
        else:
            if err_type == 'fm' or err_type == 'actor':
                for line_err in err_lists:
                    logging.info(line_err)
            else:
                for line_err in err_lists:
                    err_str = ''
                    for err in line_err:
                        err_str += str(err)
                        err_str += '   '
                    logging.info(err_str)

    def get_file_list(self, dir_path, file_type):
        dir_path = dir_path + '/*' + file_type
        file_list = glob.glob(dir_path)
        return file_list

    def check_mv_video(self, rand_count=0):
        path_list = ('01', '02', '03', '04', '05', '06', '07', '08')
        for disk_dir in path_list:
            path_num = '/' + disk_dir + '/'
            self.logger.debug("检测目录：%s " % path_num)
            query_str = 'SELECT  path, mid, serial_id, name FROM media WHERE path like ' + "\'" + path_num + '%' + "\'"
            mv_path = self.root_path + disk_dir
            try:
                query_re = self.session.execute(query_str).fetchall()
            except Exception, e:
                logging.info(e)
                return
            if len(query_re) < 1:
                return

            if rand_count > 0:
                lists = self.rand_list(query_re, rand_count)
            else:
                lists = query_re

            error_mv = []
            error_jpg = []
            mp4_files = self.get_file_list(mv_path, '.mp4')
            jpg_files = self.get_file_list(mv_path, '.jpg')
            self.logger.debug("     mp4文件数：%s " % len(mp4_files))
            self.logger.debug("     mp4图片文件数：%s " % len(jpg_files))
            for each_path in lists:
                each = each_path[0]
                mp4_name = each.strip(path_num)
                jpg_name = mp4_name.replace('.mp4', '_s.jpg')
                # print each
                if mp4_name not in mp4_files:
                    error_mv.append(each_path)

                if jpg_name not in jpg_files:
                    error_jpg.append(each_path)

            if len(error_mv) > 1:
                self.write_to_file(error_mv, 'mv  mp4')
            if len(error_jpg) > 1:
                self.write_to_file(error_jpg, 'mv jpg')

    def check_mv_lyric(self, rand_count=0):
        path_lyric = self.root_path + '/lyrics'
        self.logger.debug("mv歌词检测目录：%s " % path_lyric)
        query_str = 'SELECT  lyric, mid, serial_id, name FROM media WHERE lyric != \'NULL\''
        try:
            query_re = self.session.execute(query_str).fetchall()
        except Exception, e:
            logging.info(e)
            return
        if len(query_re) < 1:
            return

        if rand_count > 0:
            lists = self.rand_list(query_re, rand_count)
        else:
            lists = query_re

        err_lrc = []
        lyric_files = self.get_file_list(path_lyric, '.lrc')
        self.logger.debug("     mv歌词文件数：%s " % len(lyric_files))
        for each_lyric in lists:
            print 'lyric : %s   mid : %s  name : %s ' % (each_lyric[0], each_lyric[1], each_lyric[3])
            if each_lyric[0] not in lyric_files:
                err_lrc.append(each_lyric)

        if len(err_lrc) > 1:
            self.write_to_file(err_lrc, 'mv   lyric')

    def check_mp3_krc(self, rand_count=0):
        path_p3_lyric = self.root_path + '/lyrics'
        self.logger.debug("mp3歌词检测目录：%s " % path_p3_lyric)
        query_str = 'SELECT lyric, mmid, serial_id, name FROM media_music '
        try:
            query_re = self.session.execute(query_str).fetchall()
        except Exception, e:
            logging.info(e)
            return
        if len(query_re) < 1:
            return

        if rand_count > 0:
            lists = self.rand_list(query_re, rand_count)
        else:
            lists = query_re

        err_krc = []
        lyric_files = self.get_file_list(path_p3_lyric, '.krc')
        self.logger.debug("     mp3歌词文件数：%s " % len(lyric_files))
        for each_line in lists:
            print 'lyric : %s   mmid : %s  name : %s ' % (each_line[0], each_line[1], each_line[3])
            if each_line[0] not in lyric_files:
                err_krc.append(each_line)

        if len(err_krc) > 1:
            self.write_to_file(err_krc, 'mp3   lyric')

    def check_mp3_video(self, rand_count=0):
        path_p3_video = self.root_path + '/09'
        self.logger.debug("mp3视频检测目录：%s " % path_p3_video)
        query_str = 'SELECT path, mmid, serial_id, name FROM media_music '
        try:
            query_re = self.session.execute(query_str).fetchall()
        except Exception, e:
            logging.info(e)
            return
        if len(query_re) < 1:
            return

        if rand_count > 0:
            lists = self.rand_list(query_re, rand_count)
        else:
            lists = query_re

        err_video = []
        video_files = self.get_file_list(path_p3_video, '.mp4')
        self.logger.debug("     mp3视频歌词文件数：%s " % len(video_files))
        for each_line in lists:
            print 'path : %s   mmid : %s  name : %s ' % (each_line[0], each_line[1], each_line[3])
            if each_line[0] not in video_files:
                err_video.append(each_line)

        if len(err_video) > 1:
            self.write_to_file(err_video, 'mp3   mp4')

    def check_fm(self, rand_count=0):
        path_fm = self.root_path + '/fm'
        self.logger.debug("fm检测目录：%s " % path_fm)
        query_str = 'SELECT lid, serial_id, title FROM songlist;'
        try:
            query_re = self.session.execute(query_str).fetchall()
        except Exception, e:
            logging.info(e)
            return

        err_fm = self.check_picture(query_re, path_fm, 2, rand_count)
        if len(err_fm) > 1:
            # for err in err_fm:
            self.write_to_file(err_fm, 'fm')

    def check_actor(self, rand_count=0):
        path_actor = self.root_path + '/avatar'
        self.logger.debug("歌星头像检测目录：%s " % path_actor)
        query_str = 'SELECT sid, serial_id, name FROM actor;'
        try:
            query_re = self.session.execute(query_str).fetchall()
        except Exception, e:
            logging.info(e)
            return

        err_actor = self.check_picture(query_re, path_actor, 2, rand_count)
        if len(err_actor) > 1:
            # for err in err_actor:
            self.write_to_file(err_actor, 'actor')

    def check_picture(self, sql_list, d_path, n_index, rand_count=0):

        err_list = []
        if len(sql_list) > 0:
            files = self.get_file_list(d_path, '.jpg')
            self.logger.debug("     图片文件数：%d " % len(files))

            if rand_count > 0:
                lists = self.rand_list(sql_list, rand_count)
            else:
                lists = sql_list

            for each_line in lists:
                jpg_name = each_line[n_index]
                jpg_name += '.jpg'
                name = d_path + '/' + jpg_name
                print name
                if name not in files:
                    err_list.append(jpg_name)

        return err_list

    def rand_list(self, sql_list, rand_count):
        list_rv = []
        rand = []
        if len(sql_list) < rand_count:
            rand_count = len(sql_list)
        for i in range(rand_count):
            rand.append(random.randint(0, rand_count))

        for index in rand:
            list_rv.append(sql_list[index])
        return list_rv

    def mv(self, count):
        self.check_mv_video(count)
        self.check_mv_lyric(count)

    def picture(self, count):
        self.check_fm(count)
        self.check_actor(count)

    def video(self, count):
        self.check_mv_video(count)
        self.check_mp3_video(count)

    def lyric(self, count):
        self.check_mp3_krc(count)
        self.check_mv_lyric(count)

    def all(self):
        self.check_mv_lyric()
        self.check_mv_video()
        self.check_mp3_krc()
        self.check_mp3_video()
        self.check_fm()
        self.check_actor()


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
    parser.add_option("--host", dest="host", default="192.168.1.199", help="specify db host")
    parser.add_option("--port", dest="port", type="int", default=3306, help="specify db port")
    parser.add_option("--dir", dest="dir", default="/var/www", help="res directory")
    parser.add_option("-u", "--user", dest="user", default="root", help="specify db user")
    parser.add_option("-p", "--pwd", dest="password", default="lh", help="specify db user")
    parser.add_option("-d", "--db", dest="db", default="yiqiding_ktv", help="specify db database")
    parser.add_option("-l", "--log", dest="log_name", default="res.txt", help="log file name")
    parser.add_option("-j", "--json", dest="json",  default=False, help="output json  False/True")
    parser.add_option("-m", "--max", dest="max", default="0", help="spot-check max num")
    parser.add_option("-t", "--type", dest="type", default="all", help='''specify type, \n
                                                                       [mv]             check mv  video,picture,lyric\n
                                                                       [mv_video]       check mv  video,picture\n
                                                                       [mv_lyric]       check mv  lyric\n
                                                                       [mp3]            check mp3 video,lyric\n
                                                                       [mp3_video]      check mp3 video\n
                                                                       [mp3_lyric]      check mp3 lyric\n
                                                                       [fm_jpg]         check fm  picture\n
                                                                       [actor_jpg]      check singer picture\n
                                                                       [picture]        check fm and singer picture\n
                                                                       [video]          check mv and mp3 video\n
                                                                       [lyric]          check mv and mp3 lyric''')
    (options, args) = parser.parse_args()
    return options


if __name__ == '__main__':

    opt = res_option()
    init_log(opt.log_name)

    logger = logging.getLogger("log")
    logger.setLevel(logging.DEBUG)
    fp = logging.FileHandler("check.log")
    logger.addHandler(fp)

    nums = opt.max.split(",")
    res = ResCheck(opt.host, opt.user, opt.password, opt.port, opt.db, opt.log_name, opt.dir, logger, opt.json)
    for obj in opt.type.split(","):
        if len(nums):
            check_num = int(nums[0])
            if opt.type != 'all':
                del nums[0]

        if obj == 'mv':
            res.mv(check_num)
        elif obj == 'mv_video':
            res.check_mv_video(check_num)
        elif obj == 'mv_lyric':
            res.check_mv_lyric(check_num)
        elif obj == 'mp3':
            res.check_mp3_video(check_num)
            res.check_mp3_krc(check_num)
        elif obj == 'mp3_video':
            res.check_mp3_video(check_num)
        elif obj == 'mp3_lyric':
            res.check_mp3_krc(check_num)
        elif obj == 'fm_jpg':
            res.check_fm(check_num)
        elif obj == 'actor_jpg':
            res.check_actor(check_num)
        elif obj == 'picture':
            res.picture(check_num)
        elif obj == 'video':
            res.video(check_num)
        elif obj == 'lyric':
            res.lyric(check_num)
        elif obj == 'all':
            res.all()
        check_num = 0
