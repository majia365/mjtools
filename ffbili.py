#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 使用ffmpeg处理bilibili客户端缓存视频文件
#输入参数1: 源文件目录（缓存文件所在文件夹），缺省当前目录
#输入参数2: 输出目录，缺省当前目录
#输入参数3: 临时目录，缺省当前目录

import json
import os
import re
import sys
from collections import namedtuple
from configparser import ConfigParser
from datetime import date
from glob import glob
from optparse import OptionGroup, OptionParser

# 调试信息输出
def debug_print(*args, **kwargs):
  #print(*args, **kwargs)
  pass

# 获取绝对路径
def abspath(path):
  return os.path.abspath(os.path.expanduser(path))

# 获取绝对目录名
def dirname(path):
  dirname = abspath(path)
  if os.path.isdir(dirname):
    return dirname
  else:
    return os.path.dirname(dirname)

# 获取运行时变量
def _get_runtime():
  rt = {'pid'    : os.getpid(),  # 操作系统进程号
        'program': os.path.abspath(os.path.expanduser(sys.argv[0])),  # 包含绝对路径的程序名
        'prog'   : os.path.split(sys.argv[0])[1],  # 不包含路径的程序名
        'homedir': os.path.dirname(os.path.abspath(os.path.expanduser(sys.argv[0]))),  # 程序所在目录
        'appname': os.path.splitext(os.path.split(sys.argv[0])[1])[0],  # 不包含后缀的程序名
        'curpath': os.getcwd(),  # 当前路径
        'curdate': date.today().strftime("%Y%m%d"),  # 当前日期
  }
  rt['logident'] = "%(appname)s#%(pid)s" % rt
  RunTimeTuple = namedtuple("RunTime", rt)
  return RunTimeTuple(**rt)

# 执行时参数解析（结合命令行参数及配置文件）
def _get_exec_config(conftype='ini', runtime=None):
  if runtime is None:
    runtime = _get_runtime()
  BILI_PATH = os.path.join(os.environ['HOME'], "Movies", "bilibili")
  # 设置参数缺省值
  defaults = {'srcpath' : BILI_PATH,
              'destpath': ".",
              'tmppath' : ".",
              'confile': "%(homedir)s/%(appname)s.conf" % runtime._asdict(),
  }
  # 内部方法：命令行参数提取
  def _get_cmd_args():
    usageinfo = "%prog [<source-dir> <dest-dir>] [temp-dir] [--conf=confile]"
    versions  = "%prog v0.1"
    parser = OptionParser(usage=usageinfo, version=versions, conflict_handler="resolve")
    # parser set_defaults
    parser.set_defaults(debugmode   = False)
    parser.set_defaults(verbosemode = False)
    # parser config option
    parser.add_option('', '--conf', dest='confile', help='[optional] config file', metavar='FILE')
    # parser debug option
    group = OptionGroup(parser, "Debug Options")
    group.add_option('', '--debug', dest='debugmode', action='store_true', help='print debug information')
    group.add_option('', '--verbose', dest='verbosemode', action='store_true', help='more debug information')
    parser.add_option_group(group)
    # parse command args
    (options, args) = parser.parse_args(args=sys.argv[1:])
    debug_print(options)  # Values object不可增加修改，使用其内部对象__dict__
    debug_print(args)
    retvars = {}
    # 位置参数处理
    if len(args)==0:  # 不提供位置参数
      pass
    elif len(args)==2:  # 提供两个位置参数（源目录，目标目录）
      options.__dict__['srcpath'] = args[0]
      options.__dict__['destpath'] = args[1]
    elif len(args)==3:  # 提供三个位置参数（源目录，目标目录，临时目录）
      options.__dict__['srcpath'] = args[0]
      options.__dict__['destpath'] = args[1]
      options.__dict__['tmppath'] = args[2]
    else:  # 参数个数错误
      parser.error("error args")
    for key, value in options.__dict__.items():
      # 参数值为空，视为未配置
      if value is None:
        continue
      if value in ("", "None", "Null", "none", "null"):
        continue
      retvars[key] = value
    return retvars
  # 内部方法：配置文件参数提取
  def _get_config_args(conf, conftype, runtime):
    def _read_ini(conf, runtime):
      retvars = {}
      default_section = runtime.appname
      config = ConfigParser()
      config.read(confile, encoding='utf-8-sig')  #ignore utf8 BOM
      for section in config.sections():
        for key in config[section].keys():
          # 配置值为空，视为未配置
          if config.get(section, key) is None:
            continue
          if config.get(section, key) in ("", "None", "Null", "none", "null"):
            continue
          if section==default_section:
            retvars[key] = config.get(section, key)
          else:
            retvars[section+'.'+key] = config.get(section, key)
      return retvars
    if conftype=='json':
      return _read_json(conf, runtime)
    elif conftype=='xml':
      return _read_xml(conf, runtime)
    elif conftype=='yaml':
      return _read_yaml(conf, runtime)
    else:  # 缺省ini
      return _read_ini(conf, runtime)
  # 读取命令行参数
  cmd_vars = _get_cmd_args()
  debug_print(cmd_vars)
  # 读取配置文件参数
  confile = cmd_vars.get('confile') or defaults['confile']
  conf_vars = _get_config_args(conf=confile, conftype=conftype, runtime=runtime)
  debug_print(conf_vars)
  # 缺省值优先级最低，配置文件的参数优先级居中，命令行传入的参数优先级最高
  ec = {**defaults, **conf_vars, **cmd_vars}
  # 参数有效性检查
  assert os.path.isdir(abspath(ec['srcpath'])), "invalid source path. %s" % ec['srcpath']
  assert os.path.isdir(abspath(ec['destpath'])), "invalid dest path. %s" % ec['destpath']
  assert os.path.isdir(abspath(ec['tmppath'])), "invalid temp path. %s" % ec['tmppath']
  ec['srcpath']  = abspath(ec['srcpath'])
  ec['destpath'] = abspath(ec['destpath'])
  ec['tmppath']  = abspath(ec['tmppath'])
  ConfigTuple = namedtuple("Config", ec)
  debug_print(ec)
  return ConfigTuple(**ec)

# 读取哔哩哔哩缓存信息json文件
def _get_video_info(jsonfile="videoInfo.json"):
  with open(jsonfile, encoding='utf-8') as jf:
    info = json.load(jf)
    # 检查常用key
    bvid   = info['bvid']
    p      = info['p']
    title  = info['title']
    status = info['status']    # completed
    text = json.dumps(info, ensure_ascii=False)
    debug_print(text)
  return info

# 读取原m4s文件，写入临时文件
def _writeMediaStream(mediafile, fileno=0, tmppath="."):
  # 常量 哔哩哔哩本地缓存媒体文件头
  M4S_HEADER = b"000000000"
  chuck_size = 8*1024*1024
  with open(mediafile, "rb") as rf:
    header = rf.read(len(M4S_HEADER))
    # 检查是否9个0开头，如果是，移除并将其后文件内容写入临时文件
    if header == M4S_HEADER:
      # 避免同时执行时写入冲突的临时文件，写入前先检查临时文件是否已经存在
      tmpfile = os.path.join(tmppath, "media%03d.tmp"%fileno)
      while os.path.exists(tmpfile):
        fileno += 1
        tmpfile = os.path.join(tmppath, "media%03d.tmp"%fileno)
      # 写入临时文件
      with open(tmpfile, "wb") as tf:
        cnt = 0
        while dat := rf.read(chuck_size):
          cnt += 1
          tf.write(dat)
          if cnt%10 == 0:
            tf.flush()
      return tmpfile
    else: # 如果否，直接使用原文件
      print("warn: missed m4s header. %s" % mediafile)
      return mediafile

# 处理缓存目录
def _doFfmpeg(srcpath=".", destpath=".", tmppath="."):
  # 哔哩哔哩本地缓存视频信息文件名
  BILI_VideoInfo = "videoInfo.json"
  # 检查m4s与json文件
  m4slist = glob("%s/*.m4s" % srcpath)
  infofile = os.path.join(srcpath, BILI_VideoInfo)
  print(m4slist)
  debug_print(infofile)
  # 检查info文件
  if not os.path.isfile(infofile):
    print("error: not found videoInfo.json")
    return(-1)
  # 检查是否完成缓存
  info = _get_video_info(infofile)
  if info['status'] != 'completed':
    print("error: status %s" % info['status'])
    return(-1)
  # 生成临时文件
  tmplist = []
  for idx, m4sfile in enumerate(m4slist):
    tmplist.append(_writeMediaStream(m4sfile, idx, tmppath))
  # 目标文件名 合集视频文件名包含合集名称
  if info['title'] == info['groupTitle']:
    outfile = "%(title)s.p%(p)d.%(bvid)s.mp4" % info
  else:
    outfile = "%(groupTitle)s.p%(p)d.%(title)s.%(bvid)s.mp4" % info
  # 移除输出文件名中的特殊字符
  #comp = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]") # 匹配不是中文、大小写、数字的其他字符
  #outfile = comp.sub('-', outfile)
  # debug: title include char "/"
  outfile = outfile.replace(os.sep, '-').replace(' ', '')
  debug_print(outfile)
  # 执行ffmpeg
  # debug: 增加 -loglevel error 命令行参数，减少输出提示信息
  # debug: 增加 -y 命令行参数，忽略存在覆盖提示
  cmdline = "ffmpeg -loglevel error -i \"%s\" -i \"%s\" -c copy -y \"%s/%s\"" % (tmplist[0], tmplist[1], destpath, outfile)
  print(cmdline)
  os.system(cmdline)
  # 移除临时文件
  # debug: 避免同时执行时删除其他任务的临时文件
  #os.system("rm %s/media*.tmp" % tmppath)
  for tmpfile in tmplist:
    os.system("rm %s" % tmpfile)

# 是否哔哩哔哩缓存主目录
def _isBiliDir(path):
  # 哔哩哔哩本地缓存日志文件名
  BILI_LogFile = "load_log"
  # 检查是否存在哔哩哔哩本地缓存日志文件，简单判断是否为哔哩哔哩缓存主目录
  bililog = os.path.join(path, BILI_LogFile)
  return os.path.isfile(bililog)

# 主过程
def main():
  # 获取运行环境及参数配置
  rt = _get_runtime()
  ec = _get_exec_config()
  srcpath  = abspath(ec.srcpath)
  destpath = abspath(ec.destpath)
  tmppath  = abspath(ec.tmppath)
  # 如果是哔哩哔哩缓存主目录，循环取其中的缓存目录进行批量处理
  if _isBiliDir(srcpath):
    subdirs = os.listdir(srcpath)
    # 循环处理缓存子目录
    for subdir in subdirs:
      # 不处理操作系统隐藏目录，如.DS_Store
      if subdir.startswith("."):
        continue
      subpath = os.path.join(srcpath, subdir)
      if os.path.isdir(subpath):
        _doFfmpeg(subpath, destpath, tmppath)
  else:  # 如果不是哔哩哔哩缓存主目录，则仅对当前目录做单个处理
    _doFfmpeg(srcpath, destpath, tmppath)


if __name__ == "__main__":
  main()

