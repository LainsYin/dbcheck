# -*- coding:utf-8 -*-
__author__ = 'yin'

import MySQLdb
conn=MySQLdb.connect(
        host='192.168.1.233',
        port=3306,
        user='yqc',
        passwd='yqc2014',
        db='yiqiding_ktv',
        charset='utf8'
        )
cur = conn.cursor()
cur.execute("SELECT mid, serial_id, name, count FROM media;")
file_object = open("mediainfo.txt", 'w')
while (True):
    row = cur.fetchone()
    if row == None:
        break
    lineData = "%s, %s, %s, %s" % (row[0], row[1], row[2], row[3])
    # import pdb
    # pdb.set_trace()
    lineData += '\n'
    file_object.writelines(lineData.encode("utf8"))

file_object.close()


cur.close()
#conn.colse()
