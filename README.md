# dbcheck

数据库和资源检测工具
dbcheck.py 数据库检测脚本
rescheck.py 资源检测脚本

使用说明：
运行-h 查看具体参数使用
数据库
    1.运行dbexport.py生成一份标准数据库的json文件
    2.运行dbcheck.py指定刚生成的json文件作为标准对比
资源检测
    1.运行rescheck.py默认检测所有资源，资源不存在会以log形式记录