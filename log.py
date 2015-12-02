#!/usr/bin/env python2.7
#coding=utf-8

"""logging module wrapper"""

__author__ = "Yingqi Jin (jinyingqi@luoha.com)"
__date__ = "Nov.14 2015"

__all__ = ['debug', 'info', 'warning', 'error', 'critical']

import logging
from singleton import Singleton


class Logger(Singleton):

    def __init__(self):
        self.__dir = '.' # log base path 
        self.__log_map = {} # name -> logging instance
        self.__level_map = {
            'debug' : logging.DEBUG,
            'info' : logging.INFO,
            'warning' : logging.WARNING,
            'error' : logging.ERROR,
            'critical' : logging.CRITICAL,
            }

    def set_dir(self, path):
        self.__dir = path

    def get(self, name='stdout', log='', level='debug', stream=False):
        """create new logging instance if not exists
        @arg1 : log name
        @arg2 : file name
        @arg3 : log level
        @arg4 : print on stdout
        @return : logging instance
        """
        if name not in self.__log_map:
            if not log:
                log = name + '.log'
            inst = logging.getLogger(name)
            inst.setLevel(logging.DEBUG)

            if level in self.__level_map:
                level = self.__level_map[level]
            else:
                level = logging.DEBUG

            formatter = logging.Formatter(
                '[%(asctime)s - %(process)-6d - %(threadName)-10s - %(levelname)-8s]\t%(message)s')

            # do not create log if when name is stdout
            if name != 'stdout':
                from os.path import join
                log = join(self.__dir, log)
                fh = logging.FileHandler(log, mode='w')
                fh.setLevel(level)
                fh.setFormatter(formatter)
                inst.addHandler(fh)

            if stream:
                sh = logging.StreamHandler()
                sh.setLevel(level)
                sh.setFormatter(formatter)
                inst.addHandler(sh)

            self.__log_map[name] = inst 
    
        return self.__log_map[name]


__logger = Logger()

def set_dir(path):
    __logger.set_dir(path)

def debug(msg, name='debug', log='', stream=False):
    __logger.get(name, log, 'debug', stream).debug(msg)

def info(msg, name='info', log='', stream=True):
    __logger.get(name, log, 'info', stream).info(msg)

def warning(msg, name='warning', log='', stream=False):
    __logger.get(name, log, 'warning', stream).warning(msg)

def error(msg, name='error', log='', stream=False):
    __logger.get(name, log, 'error', stream).error(msg)

def critical(msg, name='critical', log='', stream=False):
    __logger.get(name, log, 'critical', stream).critical(msg)


if __name__ == "__main__":
    
    set_dir('./')

    debug('hello world')

    info('info')
    
    warning('warning')


