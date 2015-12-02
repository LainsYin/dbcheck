# -*-coding:utf-8 -*-
__author__ = 'yin'


import os
import re
import sys
import glob
import random
import pdb
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date, SmallInteger, Text
reload(sys)
sys.setdefaultencoding("utf-8")

Base = declarative_base()


class MediaLyric(Base):
    """
    +-----------+------------------+------+-----+---------+----------------+
    | Field     | Type             | Null | Key | Default | Extra          |
    +-----------+------------------+------+-----+---------+----------------+
    | id        | int(11) unsigned | NO   | PRI | NULL    | auto_increment |
    | type      | int(8)           | NO   |     | NULL    |                |
    | serial_id | int(11)          | YES  |     | NULL    |                |
    | lyric     | text             | YES  |     | NULL    |                |
    +-----------+------------------+------+-----+---------+----------------+
    """
    __tablename__ = 'media_lyric'

    id = Column(Integer, primary_key=True)
    type = Column(Integer)
    serial_id = Column(Integer)
    lyric = Column(Text)

DB_CONNECT_STR = 'mysql+mysqldb://root:lh@127.0.0.1/yiqiding_ktv?charset=utf8'
ENGINE = create_engine(DB_CONNECT_STR)
Session = sessionmaker(bind=ENGINE)
session = Session()
ROOT_PATH = '/var/www/lyrics/'


def lyric():
    '''
    '''

    query_str = ['SELECT  lyric, mid, serial_id, name FROM media WHERE lyric != \'NULL\';',
                 'SELECT  lyric, mmid, serial_id, name FROM media_music;']
    type_index = 0
    for select_str in query_str:
        query_re = session.execute(select_str).fetchall()
        type_index += 1
        for each in query_re:
            file_path = ROOT_PATH + each[0]
            if os.path.isfile(file_path):
                print file_path
                try:
                    fp = file(file_path, 'r')
                    ''''
                    文本前去空行
                    '''
                    while True:
                        line_data = fp.readline()
                        line_data = re.sub('\[(.*?)\]', '', line_data)
                        line_data = re.sub('[\\r][\\n]', '', line_data)
                        line_data = re.sub('[\\n]', '', line_data)
                        if line_data in ['\xef\xbb\xbf', '']:
                            continue
                        else:
                            data_all = fp.read()
                            ly_text = line_data + os.linesep
                            ly_text += data_all
                            ly_text = re.sub('\[(.*?)\]', '', ly_text)
                            ly_text = re.sub('\<(.*?)\>', '', ly_text)
                            print ly_text
                            break
                    ml = MediaLyric()
                    ml.serial_id = each[2]
                    ml.type = type_index
                    ml.lyric = ly_text
                    session.add(ml)
                finally:
                    fp.close()
        session.flush()
        session.commit()

if __name__ == '__main__':
    lyric()