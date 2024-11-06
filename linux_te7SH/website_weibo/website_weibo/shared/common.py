# -*- coding:UTF-8 -*-
#
# Banting Common utilities for Linux, for Eurekahai Data Processing
#
# Charles 吴波, July 12th, 2021, copied from lmfu.py
#
import os
import sys
import traceback
import pdb
import contextlib
import sys
import random
import re
import base64
import hashlib
import mmap
import optparse
import time
import socket
import getpass
import inspect

import dateutil
import psutil
import json
import uuid
import copy
import queue
import pickle
import gzip
import concurrent.futures
import unicodedata
import functools
from termcolor import cprint
from decimal import Decimal
from datetime import datetime, date
from dateutil import parser
from cryptography.fernet import Fernet
from threading import Thread, Lock

import progressbar
from progressbar import ProgressBar, SimpleProgress, Percentage, ETA, RotatingMarker, Bar

if sys.platform != 'win32':
    import subprocess


def _CPRINT_OUT(s): return s


_CPRINT_LOGF = None
_CPRINT_ENABLED = True


def print_green(s): return (_CPRINT_OUT(s), cprint(s, 'green', None, ['bold'])) if _CPRINT_ENABLED else (s,)


def print_yellow(s): return (_CPRINT_OUT(s), cprint(s, 'yellow', None, ['bold'])) if _CPRINT_ENABLED else (s,)
def print_white(s): return (_CPRINT_OUT(s), cprint(s, 'white', None, ['bold'])) if _CPRINT_ENABLED else (s,)
def print_red(s): return (_CPRINT_OUT(s), cprint(s, 'red', None, ['bold'])) if _CPRINT_ENABLED else (s,)
def print_cyan(s): return (_CPRINT_OUT(s), cprint(s, 'cyan', None, ['bold'])) if _CPRINT_ENABLED else (s,)


def print_purple(s): return (_CPRINT_OUT(s), cprint(s, 'magenta', None, ['bold'])) if _CPRINT_ENABLED else (s,)
def print_grey(s): return (_CPRINT_OUT(s), cprint(s, 'grey', None, ['bold'])) if _CPRINT_ENABLED else (s,)
def print_blue(s): return (_CPRINT_OUT(s), cprint(s, 'blue', None, ['bold'])) if _CPRINT_ENABLED else (s,)
def print_color(s, clr): return (_CPRINT_OUT(s), cprint(s, clr, None, ['bold'])) if _CPRINT_ENABLED else (s,)


@contextlib.contextmanager
def cprint_set_log(log_file):
    global _CPRINT_LOGF, _CPRINT_OUT
    if log_file:
        _CPRINT_LOGF = open(log_file, 'wt', encoding='utf-8')
        def _CPRINT_OUT(s): return (_CPRINT_LOGF.write(str(s) + '\n'), _CPRINT_LOGF.flush())
        print(f'**** 日志全部输出到 {log_file} ****')

    try:
        yield
    except Exception as e:
        traceback.print_exc(file=_CPRINT_LOGF if _CPRINT_LOGF else sys.stdout)

    if log_file:
        def _CPRINT_OUT(s): return s
        _CPRINT_LOGF.close()
        _CPRINT_LOGF = None
        print_white('**** 日志文件: ' + file_info_str(log_file) + ' ****')


GREY = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
PURPLE = 5
CYAN = 6
WHITE = 7

KEY_START = 0
KEY_END = 1
KEY_ADD = 2
KEY_COUNT = 3
KEY_SAVE = 4
KEY_STEP = 5
KEY_SET_COLUMNS = 6
KEY_LAST = 7
KEY_CHECK = 8
KEY_GET_PAGE_FIELD = 9
KEY_DONE_GPF = 10
KEY_READ_PAGE = 11
KEY_ERROR = -1


# ==========================================
def erase_prev_line() -> None:  # go up to prev line and erase to end
    print('\x1b[1A\r\x1b[2K', end='')


def erase_screen() -> None:  # erase full screen
    print('\x1b[100A\r\x1b[2J', end='')


def move_up_screen(lines: int) -> None:  # move up lines on screen
    if lines > 0:
        print(f'\x1b[{lines}A\r', end='')


def move_down_screen(lines: int) -> None:  # move up lines on screen
    if lines > 0:
        print(f'\x1b[{lines}B\r', end='')


def get_text_color(fore_color, back_color=None, light=True, bold=False, underline=False, reverse=False, use_code=False):
    cmd = ''
    if bold:
        cmd += '\x1b[1m'
    if underline:
        cmd += '\x1b[4m'
    if reverse:
        cmd += '\x1b[7m'

    if use_code:
        if not fore_color is None:
            cmd += f'\x1b[38;5;{fore_color}m'
        if not back_color is None:
            cmd += f'\x1b[48;5;{back_color}m'
    else:
        if not fore_color is None:
            cmd += f'\x1b[{30 + fore_color}{";1" if light else ""}m'
        if not back_color is None:
            cmd += f'\x1b[{40 + back_color}{";1" if light else ""}m'
    return cmd


def get_text_with_color_code(text):  # eg. 'Hello #c3 my #C world'
    if '#c' not in text:
        return text

    while True:
        m = re.search('#c\d+', text)
        if not m:
            break
        try:
            text = re.sub('#c\d+', get_text_color(int(m.group(0)[2:])), text, 1)
        except:
            return text

    while True:
        m = re.search('#C', text)
        if not m:
            break
        try:
            text = re.sub('#C', '\x1b[0m', text, 1)
        except:
            return text

    return text


def set_text_color(fore_color, back_color=None, light=True, bold=False, underline=False, reverse=False, use_code=False):
    print(get_text_color(fore_color, back_color, light, bold, underline, reverse, use_code), end='')


def reset_text_color():
    print('\x1b[0m', end='')


def startfile(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])

# choose an element random based on distribution. eg.  ['A', 70, 'B', 30]  will choose 70% A and 30% B


def choice_random(pattern):
    slots = []
    for ix in range(0, len(pattern) // 2 * 2, 2):
        data, repeat = pattern[ix], pattern[ix + 1]
        if isinstance(data, str):
            add = [data] * repeat
        elif isinstance(data, range):
            add = [random.choice(list(data)) for _ in range(repeat)]
        else:
            raise Exception(f'Unsupported data type: {type(data)}: {data}')
        slots += add
    return random.choice(slots)


# binary search, taken from python 3.10 and modified
def bisect(a, x, lo=0, hi=None, *, key=None):
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)

    while lo < hi:
        mid = (lo + hi) // 2
        if x == (v := (a[mid] if key is None else key(a[mid]))):
            break

        if x < v:
            hi = mid
        else:
            lo = mid + 1
    return lo


def convert_to_csv_field(v):
    if v is None:
        return ''

    if type(v) is str:
        v = v.replace('"', '""').replace('\n', ' ').replace('\r', ' ')
        return '"' + v + '"' if ',' in v or '"' in v else v

    if type(v) is datetime:
        return v.strftime("%Y-%m-%d %H:%M:%S")

    if type(v) is int or type(v) is float or type(v) is bool:
        return str(v)

    if type(v) is bytes:
        return base64.standard_b64encode(v).decode('ascii')

    # any other type, use json
    return json.dumps(v)


def get_host_user():
    try:
        host = socket.gethostname()
    except:
        try:
            host = os.environ['COMPUTERNAME']
        except:
            try:
                host = os.environ['HOST']
            except:
                host = ''

    try:
        user = getpass.getlogin()
    except:
        try:
            user = os.getlogin()
        except:
            try:
                user = os.environ['USERNAME']
            except:
                try:
                    user = os.environ['USER']
                except:
                    user = ''

    return host, user


def has_chinese(text):
    for ch in text:
        if 'CJK' in unicodedata.name(ch):
            return True
    return False


def put_text_by_width(text, width, justify=-1):  # justify < 0: left     == 0: middle    > 0 right
    # try to adjust width based on # of unicode char
    width -= 1  # leave a space on right
    for ix, ch in enumerate(text):
        width -= 1 if unicodedata.east_asian_width(ch) != 'W' and unicodedata.east_asian_width(ch) != 'F' else 2
        if width <= 0:
            text = text[:ix + 1 if width == 0 else ix]
            break

    if width < 0:
        width = 1
    return text + ' ' * (width + 1) if justify < 0 else ((' ' * (width + 1) + text) if justify > 0 else (' ' * (width // 2) + text + ' ' * (width // 2 + 1 + ((width % 2) != 0))))


@contextlib.contextmanager
def use_text_color(fore_color, back_color=None, light=True, bold=False, underline=False, reverse=False, use_code=False):
    if fore_color is not None:
        set_text_color(fore_color, back_color, light, bold, underline, reverse, use_code)
    yield
    if fore_color is not None:
        reset_text_color()


def print_with_color(color, msg, end=None):
    with use_text_color(color):
        print(msg, end=end)


def convert_value(val, get_float=True, suffix=None):
    if suffix and isinstance(val, str) and val.lower().endswith(suffix.lower()):
        val = val[:-len(suffix)]

    try:
        return float(val)
    except Exception as e:
        for n, dch in enumerate('０１２３４５６７８９'):
            val = val.replace(dch, str(n))
        val = val.replace('．', '.').replace('．', ',')

        try:
            return float(val)
        except Exception:
            pass
    return 0


def common_pbar_fields(main_t1='读取了', main_t2='条记录.', dual=False):
    chnTimer = progressbar.Timer()
    chnTimer.format_string = '   耗时: %s    '
    pmem = SimpleProgress()
    pmem.update = lambda _: ' ' + avail_mem_str() + ' '
    p1 = SimpleProgress()
    if dual:
        p1.update = lambda pbar: f'{main_t1} {pbar.currval:,}/{pbar.maxval:,} {main_t2} '
    else:
        p1.update = lambda pbar: f'{main_t1} {pbar.currval:,} {main_t2} '
    p2 = SimpleProgress()
    p2.sep = ''
    p2.update = lambda x: p2.sep
    return p1, p2, pmem, chnTimer


def common_pbar(maxval=None, main_t1='读取了', main_t2='条记录.', dual=False):
    p1, p2, pmem, chnTimer = common_pbar_fields(main_t1, main_t2, dual)
    return ProgressBar(maxval=maxval if maxval else 10**10, widgets=[p1, p2, pmem, chnTimer], term_width=80, fd=sys.stdout)


def common_pbar2(maxval=None, main_t1='读取了', main_t2='条记录.', eta=True, dual=None, width=80, want_bar=None, no_mem=False, no_time=False):
    if dual is None:
        dual = maxval != None
    if want_bar is None:
        want_bar = maxval != None
    p1, p2, pmem, chnTimer = common_pbar_fields(main_t1, main_t2, dual)
    widgets = [p1, p2] + (['  ', Percentage()] if maxval else []) + (['  ', Bar(marker=RotatingMarker())] if maxval and want_bar else []) + (['  ', ETA()] if maxval and eta else [])
    if not no_mem:
        widgets += [pmem]
    if not no_time:
        widgets += [chnTimer]
    return ProgressBar(maxval=maxval if maxval else 10**10, widgets=widgets, term_width=width, fd=sys.stdout), p2


def show_ex(ex, prompt='ERROR', msg=None, color=RED, post_mortem=False, log_file=None):
    traceback.print_tb(sys.exc_info()[2], limit=3, file=log_file if log_file else sys.stdout)
    # traceback.print_exc(file=log_file if log_file else sys.stdout)

    with use_text_color(color):
        print(f'{prompt}: {repr(ex)}')
        if msg:
            print(msg)

    if post_mortem:
        pdb.post_mortem()


def get_exinfo(ex, title='Exception: '):
    return title + (ex := repr(ex)) + '\n' + '=' * (len(ex) + len(title)) + '\n' + '\n'.join(traceback.format_tb(sys.exc_info()[2], limit=5))


def show_err(err_msg, prompt=True):
    print_red(f'错误: {err_msg}')
    # traceback.print_tb(sys.exc_info()[2], limit=3, file=sys.stdout)
    traceback.print_exc()
    # if prompt:
    #     input('按 ENTER 键继续... ')


class Entity(dict):
    def __init__(self, data=None, more_data=None, str_def=None, deep_copy=False, copy_fields=None) -> None:
        if data is not None:
            if copy_fields:
                if isinstance(copy_fields, str):
                    copy_fields = copy_fields.split(',')
                for f in copy_fields:
                    self[f] = data.get(f, None)
            else:
                self.update(copy.deepcopy(data) if deep_copy else data)  # copy everything from given data
        if more_data:
            self.update(copy.deepcopy(more_data) if deep_copy else more_data)

        if str_def:  # eg. key1=valu1;key2=value2a,value2b
            for kv in str_def.split(';'):
                try:
                    k, v = kv.split('=')
                    try:
                        self[k] = int(v)
                    except:
                        self[k] = v.split(',') if ',' in v else v
                except:
                    pass    # ignore error for now

    def __getattr__(self, name):
        if name[:2] == '__' and name not in self:
            raise AttributeError(name)

        if len(name) > 4 and name.startswith('has'):    # hash is ok, len(name) needs to be 5 or above
            return name[3:] in self
        return self[name] if name in self else 0

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]

    def json(self):
        return json.dumps(self, ensure_ascii=False)

    def pops(self, keys):
        for key in keys.split(','):
            if key in self:
                self.pop(key)
        return self

    def format(self, spec: dict):
        out = {}
        for k, v in self.items():
            out[k] = v

        for keys, spec in spec.items():
            for k in keys.split(','):
                k = k.strip()
                if k in out:
                    v = out[k]
                    if spec == 'number':
                        v = f'{v:,}'
                    elif spec == 'size':
                        v = to_size_text(v)
                    out[k] = v
        return out


# same as Entity except this throws an exception if key is not found
class EntityThrow(Entity):
    def __getattr__(self, name) -> None:
        if name[:2] == '__' and name not in self:
            raise AttributeError(name)

        if len(name) > 4 and name.startswith('has'):    # hash is ok, len(name) needs to be 5 or above
            return name[3:] in self

        if name in self:
            return self[name]
        raise AttributeError(name)


@contextlib.contextmanager
def open_mmap_file_to_read(file_name, offset=0, length=0):
    with open(file_name, 'rb') as inf:
        with mmap.mmap(inf.fileno(), length, offset=offset, access=mmap.ACCESS_READ) as data:
            try:
                yield data
            except Exception as e:
                show_ex(e)


@contextlib.contextmanager
def open_mmap_file_to_write(file_name, offset=0, length=0):
    with open(file_name, 'a+b') as outf:
        with mmap.mmap(outf.fileno(), length, offset=offset, access=mmap.ACCESS_WRITE) as data:
            try:
                yield data
            except Exception as e:
                show_ex(e)


def get_random_name(size):
    name = ''
    for _ in range(size):
        c = random.randint(0, 35)
        name += chr(ord('A') + c) if c < 26 else chr(ord('0') + c - 26)
    return name


def err_msg(msg, number=0, log_file=None, color=RED, timestamp=False):
    write_log(log_file, "ERROR" + ('' if number == 0 else ' ' + str(number)) + ': ' + msg, True, timestamp=timestamp, text_color=color, light_fore=False)


def info_msg(msg, number=0, log_file=None, color=GREEN, timestamp=False):
    write_log(log_file, "INFO" + ('' if number == 0 else ' ' + str(number)) + ': ' + msg, True, timestamp=timestamp, text_color=color, light_fore=False)


def warn_msg(msg, number=0, log_file=None, color=PURPLE, timestamp=False):
    write_log(log_file, "WARNING" + ('' if number == 0 else ' ' + str(number)) + ': ' + msg, True, timestamp=timestamp, text_color=color, light_fore=False)


def to_time_text(seconds, want_hour=False):
    if isinstance(seconds, float) and seconds < 1:
        return '00:0%.3f' % seconds
    h, ms = divmod(seconds, 3600)
    m, s = divmod(ms, 60)
    return '%02d:%02d:%02d' % (h, m, s) if want_hour else '%02d:%02d' % (m, s)


# convert list of k=v into list of [k,v]
def convert_key_values(kvs):
    kvl = []
    if kvs:
        for s in kvs:
            fs = s.split('=')
            if len(fs) == 2:
                k, v = fs[0], fs[1].strip()
                if v.lower() in ['true', 'false']:
                    kvl.append([k, v.lower() == 'true'])
                else:
                    try:
                        kvl.append([k, int(v)])  # if it's int, store int
                    except:
                        kvl.append([k, v])
    return kvl


def check_and_replace(r: dict, keys: str, search_text: str) -> None:
    for key in keys.split(','):
        if key in r and r[key]:
            r[key] = r[key].replace(search_text, '*' * len(search_text)) if search_text else '*' * len(r[key])


def change_all_keys_lower(d):
    nd = [[k.lower(), v] for k, v in d.items()]
    d.clear()
    d.update(nd)
    return d


_RX_DATE = re.compile('\d\d\d\d(-|/)\d\d(-|/)\d\d')
_RX_DATE1 = re.compile('\d\d\d\d-\d\d-\d')
_RX_DATE2 = re.compile('\d\d\d\d-\d-\d\d')
_RX_TIME = re.compile('\d\d:\d\d:\d\d')
_RX_TIME2 = re.compile('\d\d:\d\d')


def parse_datetime(text, default_value=None, try_ymd=True):
    if not text:
        return default_value

    if isinstance(text, datetime):
        return text

    if isinstance(text, date):
        return datetime.fromordinal(text.toordinal())

    if isinstance(text, str):
        text = text.strip().replace('：', ':').replace('。', '.').replace('，', ',').replace(' :', ':')
        # quick check on invalid date str
        if not text or ord(text[0]) >= 255:
            return default_value

    # try YMD HMS. eg: 2022-02-10 15:11:00 血小板  or 2022-02-1015:11:00
    if try_ymd:
        try:
            if (sr := _RX_DATE.search(text)) or (sr := _RX_DATE1.search(text)) or (sr := _RX_DATE2.search(text)):
                dt = sr.group()
                if (sr := _RX_TIME.search(text)):
                    return datetime.strptime(dt + ' ' + sr.group(), '%Y-%m-%d %H:%M:%S')
                else:
                    return datetime.strptime(dt, '%Y-%m-%d')
        except:
            ...

    try:
        return parser.parse(text)
    except:
        return default_value


def take_date_from_title(title, default_date=None):
    if title:
        title = title.strip()
        if len(title) >= 10 and _RX_DATE.search(title[:10]):
            dstr, title, tstr = title[:4] + title[5:7] + title[8:10], title[10:], None
            if title and title[0] == ' ':
                title = title[1:]
            if len(title) >= 5:
                if _RX_TIME.search(title[:8]):
                    tstr, title = title[:8], title[8:]
                elif _RX_TIME2.search(title[:5]):
                    tstr, title = title[:5] + ':00', title[5:]

            return datetime.strptime(dstr + ' ' + tstr, '%Y%m%d %H:%M:%S') if tstr else datetime.strptime(dstr, '%Y%m%d'), title.strip()

        ix = title.find('[')
        if ix >= 0:
            jx = title.find(']', ix)
            new_title = title[:ix] + (title[jx + 1:] if jx > ix else '')
            return parse_datetime(title[ix + 1:jx], default_date) if jx > ix else default_date, new_title if new_title else None
    return default_date, title


def time_str(time=None, elapsed=None, want_date=True, want_time=True, want_hour=True, want_meminfo=False, as_file_name=False):
    if not time:
        time = datetime.now()
    elif isinstance(time, float):
        time = datetime.fromtimestamp(time)

    if as_file_name:
        return time.strftime('%Y%m%d-%H%M%S')

    dt = time.strftime('%Y-%m-%d ') if want_date else ''
    es = ' [' + to_time_text((time - elapsed).total_seconds(), True) + ']' if elapsed else ''
    tm = (time.strftime('%H:%M:%S ' if want_hour else '%M:%S ')) if want_time else ''
    return dt + tm + es + (avail_mem_str() if want_meminfo else '')


def day_str(time=None, elapsed=None, want_date=True, want_time=True, want_hour=True, want_meminfo=False, as_file_name=False):
    if not time:
        time = datetime.now()
    elif isinstance(time, float):
        time = datetime.fromtimestamp(time)

    if as_file_name:
        return time.strftime('%Y%m%d')

    dt = time.strftime('%Y-%m-%d ') if want_date else ''
    es = ' [' + to_time_text((time - elapsed).total_seconds(), True) + ']' if elapsed else ''
    tm = (time.strftime('%H:%M:%S ' if want_hour else '%M:%S ')) if want_time else ''
    return dt + tm + es + (avail_mem_str() if want_meminfo else '')


def now_str(want_date=True, want_hour=True):
    tm = datetime.now()
    dt = tm.strftime('%Y-%m-%d ') if want_date else ''
    return dt + time.strftime('%H:%M:%S' if want_hour else '%M:%S')


def avail_mem_str(prefix: str = '可用内存: ', suffix: str = '') -> str:
    return prefix + to_size_text(psutil.virtual_memory().available, rounding=2) + suffix


class Timer():
    def __init__(self):
        self.start_time = datetime.now()
        self.lap_start = self.start_time
        self.end_time = self.start_time

    def end(self):
        self.end_time = datetime.now()

    def lap_time(self, get_seconds=True, reset=False):
        delta = (datetime.now() - self.lap_start).total_seconds()
        if reset:
            self.lap_start = datetime.now()
        return int(delta) if get_seconds else delta

    def time_used_so_far(self, get_seconds=True):
        delta = (datetime.now() - self.start_time).total_seconds()
        return int(delta) if get_seconds else delta

    def time_used_so_far_str(self, want_hour=False):
        return to_time_text(self.time_used_so_far(True), want_hour=want_hour)

    def time_used(self, get_seconds=True):
        delta = (self.end_time - self.start_time).total_seconds()
        return int(delta) if get_seconds else delta

    def time_used_str(self, want_hour=False):
        return to_time_text(self.time_used(True), want_hour=want_hour)

    def tps(self, count):
        sec = self.time_used_so_far(False)
        return int(count // sec) if sec else 0

    def etime_str(self):    # show current time with elapsed seconds
        return time_str(None, self.start_time)


@contextlib.contextmanager
def time_it():
    t = Timer()
    yield t
    t.end()


# check if the given cache file, if exists, load as pickle data into p.data, if it doesn't, yield to caller, and upon return, save p.data into the given cache file
@contextlib.contextmanager
def data_cache(p, cache_fn, compress=False):
    loaded = False
    try:
        with open(cache_fn, 'rb') as inf:
            p.data = pickle.loads(gzip.decompress(inf.read())) if compress else pickle.load(inf)
        loaded = True
    except:
        ...

    # let the called fill up p.data if needed
    yield loaded

    if not loaded and p.hasdata and p.data:
        try:
            with open(cache_fn, 'wb') as outf:
                if compress:
                    outf.write(gzip.compress(pickle.dumps(p.data)))
                else:
                    pickle.dump(p.data, outf)
        except:
            ...


def pprint_dict(dict_obj, title='', ident=4, max_key_len=18, no_print=False, one_line=False):
    sep = '\t' if one_line else '\n'
    text = title + sep
    if dict_obj:
        for k in dict_obj.keys():
            v = dict_obj[k]
            if isinstance(v, str):
                if len(v) != 0:
                    text += ' ' * ident + ('{:%d}' % max_key_len).format(k) + '   ' + v + sep
            elif isinstance(v, int):
                if v != 0:
                    text += ' ' * ident + ('{:%d}' % max_key_len).format(k) + '   ' + str(v) + sep
            elif isinstance(v, bool):
                text += ' ' * ident + ('{:%d}' % max_key_len).format(k) + '   ' + str(v) + sep
            elif isinstance(v, datetime):
                text += ' ' * ident + ('{:%d}' % max_key_len).format(k) + '   ' + time_str(v) + sep
            else:
                text += ' ' * ident + ('{:%d}' % max_key_len).format(k) + '   ' + str(type(v)) + sep

        if not no_print:
            print(text)
            if one_line:
                print()
    return text


def pprint_rows(rows, field_def, title='', title_color=None):
    if title:
        if title_color:
            print_with_color(title_color, title)
        else:
            print(title)
    disp = DisplayByFields(field_def)
    disp.print_header()
    disp.print_data(rows)


class MultipleOption(optparse.Option):
    ACTIONS = optparse.Option.ACTIONS + ("extend",)
    STORE_ACTIONS = optparse.Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = optparse.Option.TYPED_ACTIONS + ("extend",)
    ALWAYS_TYPED_ACTIONS = optparse.Option.ALWAYS_TYPED_ACTIONS + ("extend",)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "extend":
            values.ensure_value(dest, []).append(value)
        else:
            optparse.Option.take_action(self, action, dest, opt, value, values, parser)


def execute(title, options, args, _CMDS, default_cmd=None, handler=None, handler_params=None):
    cmd = args[0] if len(args) >= 1 else default_cmd

    if handler_params:
        handler_params.cmd, handler_params.args, handler_params.options = cmd, args, options

    # _CMDS may be a function, use it directly
    if isinstance(_CMDS, type(execute)):
        if handler:
            handler(KEY_START, handler_params)
        _CMDS(args, options)
        if handler:
            handler(KEY_END, handler_params)
        return

    for cmd_data in _CMDS:
        if cmd == cmd_data[0]:
            if handler:
                handler(KEY_START, handler_params)
            cmd_data[2](args[1:], options)
            if handler:
                handler(KEY_END, handler_params)
            return

    if handler:
        handler(KEY_ERROR, handler_params)
    with use_text_color(YELLOW):
        print(title)
        print("=" * len(title))

    with use_text_color(GREEN):
        print("Please provide one of following commands:")
        for cmd in _CMDS:
            print("\t{:8}\t{}".format(cmd[0] if cmd[0] else 'None', cmd[1]))


def _xyz_dec(data): return Fernet(b'4zH3962TJPDI2wmmPscmIA6Cmvhp3i5I8wuLiI9Ki50=').decrypt(data)


def print_company_header(title, company_name='北京华数医汇科技有限公司', width=120, title_color=YELLOW, company_color=GREEN):
    print('=' * width)
    with use_text_color(title_color):
        print(title.center(width))
    print(f'-' * width)
    with use_text_color(company_color):
        print(company_name.center(width))
    print('=' * width)


def to_size_text(v, original=False, rounding=0):
    n = float(v)
    suffix = ["B", "KB", "MB", "GB", "TB", "PB"]

    r = 1
    for ix in range(len(suffix)):
        if v < (r << 10):
            n /= r
            return ('{:,}   '.format(v) if original else '') + ('{:,.%df} ' % (rounding if ix != 0 else 0)).format(n) + suffix[ix]
        r <<= 10
    return '<???>'


def file_size_text(src, rounding=0):
    return to_size_text(os.path.getsize(src), rounding=rounding) if os.path.exists(src) else '<N/A>'


def to_percent_text(a, b, rounding=0):
    if isinstance(a, (dict, set, tuple, list)):
        a = len(a)
    if isinstance(b, (dict, set, tuple, list)):
        b = len(b)
    try:
        return ('{:.%df}%%' % rounding).format(a * 100 / b)
    except:
        return ''


def to_speed_text(size, tm, rounding=1):
    if tm == 0:
        return '未知'
    return to_size_text(int(size / tm), rounding=rounding)


def file_info_str(filename: str, timestamp=False, filename_only=False):
    if os.path.isfile(filename):
        fn = os.path.split(filename)[1] if filename_only else filename
        s = f"{fn}, 大小: {to_size_text(os.path.getsize(filename), rounding=2)}"
        if timestamp:
            t1 = datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d %H:%M:%S')
            s += f" 修改日期: {t1}"
    else:
        s = filename
    return s


# partial = 100 means read all file, partial=5 means only read 5% of the file
def get_file_md5(file_name, partial=100, size=None, reporter=None, block_size=10 * 1024 * 1024):
    def _reporter(step, stats):
        if step == KEY_START:
            stats.pbar, stats.p2 = common_pbar2(maxval=stats.file_size // (1024 * 1024), main_t1='计算 MD5, 读取了', main_t2=' MB')
            stats.pbar.start()
        elif step == KEY_STEP:
            stats.p2.sep = '   目前 MD5 是 ' + stats.hash.hexdigest()
            stats.pbar.update(stats.pos // (1024 * 1024))
        elif step == KEY_END:
            stats.pbar.finish()

    try:
        stats = Entity()
        stats.file_name, stats.partial = file_name, partial
        stats.file_size = os.path.getsize(stats.file_name)
        stats.block_size = block_size

        if isinstance(reporter, int):
            reporter = _reporter if stats.file_size >= reporter else None

        if reporter:
            reporter(KEY_START, stats)

        stats.size_to_read = size if size else stats.file_size

        with open_mmap_file_to_read(file_name) as data:
            stats.partial = min(100, stats.partial)
            if stats.partial == 100 and not reporter:
                return hashlib.md5(data[:stats.size_to_read]).hexdigest()

            stats.hash = hashlib.md5()
            stats.pos = 0
            while stats.pos < stats.size_to_read:
                stats.size_to_check = min(stats.size_to_read - stats.pos, stats.block_size * stats.partial // 100)
                stats.sub = data[stats.pos: stats.pos + stats.size_to_check]
                stats.hash.update(stats.sub)

                if reporter:
                    reporter(KEY_STEP, stats)
                stats.pos += stats.block_size

            if reporter:
                reporter(KEY_LAST, stats)

            stats.h = stats.hash.hexdigest()
            if stats.partial != 100:
                stats.h = str(stats.partial) + ':' + stats.h

        if reporter:
            reporter(KEY_END, stats)
        return stats.h
    except Exception as e:
        stats.error = e
        if reporter:
            reporter(KEY_ERROR, stats)
        show_ex(e)
        return None


def process_file_name(file_name, source_dir=None, target_dir=None, tokens=[]):
    f = ''
    if file_name:
        f = file_name.strip().replace('%t', time_str(as_file_name=True))
        for t, v in tokens:
            f = f.replace(t, v if v else '')

        f = os.path.expanduser(f)

        if sys.platform == 'win32':
            if f.startswith('$s:\\') or f.startswith('$S:\\'):
                # replace with source dir drive
                r = os.getcwd()[:3] if source_dir[1] != ':' else source_dir[:3]
                return r + f[4:]

            if f.startswith('$t:\\') or f.startswith('$T:\\'):
                # replace with target dir drive
                r = os.getcwd()[:3] if target_dir[1] != ':' else target_dir[:3]
                return r + f[4:]

            if f.startswith('$s.\\') or f.startswith('$S.\\'):
                # replace with source dir drive
                r = source_dir + ('' if source_dir.endswith('\\') else '\\')
                return r + f[4:]

            if f.startswith('$t.\\') or f.startswith('$T.\\'):
                # replace with target dir drive
                r = target_dir + ('' if target_dir.endswith('\\') else '\\')
                return r + f[4:]
    return f


def create_log_file(log_file_name, options_dict=None, title='', mode='w', to_console=True):
    if len(log_file_name) == 0:
        return None

    log_file = open(log_file_name, mode, encoding='utf-8-sig')
    if to_console:
        info_msg("Log file is " + log_file_name)
    log_file.write(time_str() + '\n')
    if len(title) != 0:
        log_file.write(title + '\n')
    if options_dict:
        log_file.write(pprint_dict(options_dict, title='Linux Options are as follows:', max_key_len=18, no_print=True))
    return log_file

# handle  100mb, >5MB, <1GB, >10KB<5gb, returns min_size, max_size, err_msg
# or      100, <5, >200, etc.


def _process_range_option(text, _take_num_func):
    if len(text) == 0:
        return 0, 0, None

    ms = text.upper()
    if ms[0] == '>' or ms[0] == '》' or ms[0] == '.':
        ms, n, err = _take_num_func(ms[1:])
        if err:
            return 0, 0, err
        if len(ms) == 0:
            return n, 0, None

        min = n
        if ms[0] != '<' and ms[0] != '《' and ms != ',':
            return 0, 0, 'Maximum must be specified with a <, now at ' + ms
        ms, n, err = _take_num_func(ms[1:])
        if err:
            return 0, 0, err
        max = n
        if min > max:
            return 0, 0, 'Minimum is bigger than maximum.'
        return (min, max, None) if len(ms) == 0 else (0, 0, 'Unknown specification at end ' + ms)

    if ms[0] == '》' or ms[0] == '.':
        ms, n, err = _take_num_func(ms[1:])
        if err:
            return 0, 0, err
        return (n, 0, None) if len(ms) == 0 else (0, 0, 'Unknown specification at end ' + ms)

    ms, n, err = _take_num_func(ms)
    if err:
        return 0, 0, err
    return (n, n, None) if len(ms) == 0 else (0, 0, 'Unknown specification at end ' + ms)


# handle  100mb, >5MB, <1GB, >10KB<5gb, returns min_size, max_size
def process_size_option(size_text):
    def _take_num(text):
        n = 0
        while len(text) != 0:
            ch = text[0]
            text = text[1:]

            if ch < '0' or ch > '9':
                if ch == '<' or ch == '>' or ch == '》' or ch == '《':
                    text = ch + text
                    break

                if ch == 'B':
                    break
                # check byte unit
                if ch == 'K' and len(text) != 0 and text[0] == 'B':
                    n *= 1024
                    text = text[1:]
                    break

                if ch == 'M' and len(text) != 0 and text[0] == 'B':
                    n *= 1024 * 1024
                    text = text[1:]
                    break

                if ch == 'G' and len(text) != 0 and text[0] == 'B':
                    n *= 1024 * 1024 * 1024
                    text = text[1:]
                    break
                return text, 0, "Invalid character '" + ch + "': remaining text=" + text
            else:
                n = n * 10 + int(ch)

        return text, n, None

    return _process_range_option(size_text, _take_num)

# handle  100, >50, <150, >150<300   returns min, max


def process_number_option(number_text):
    def _take_num(text):
        n = 0
        while len(text) != 0:
            ch = text[0]
            text = text[1:]

            if ch < '0' or ch > '9':
                if ch == '<' or ch == '>' or ch == '》' or ch == '《':
                    text = ch + text
                    break
                return text, 0, "Invalid character '" + ch + "': remaining text=" + text
            else:
                n = n * 10 + int(ch)
        return text, n, None

    return _process_range_option(number_text, _take_num)


from io import TextIOWrapper


def write_log(log_file, msg, to_console=False, text_color=None, light_fore=False, timestamp=True, prompt=False, lock: Lock = None, flush=False):
    if msg:
        # print only the first line of a list (eg. returned from print_white)
        if isinstance(msg, (list, tuple)):
            msg = msg[0]

        if not log_file:
            print(msg)
            return

        if lock:
            lock.acquire()

        closing = False
        if isinstance(log_file, str):
            log_file = open(log_file, 'a+', encoding='utf-8')
            closing = True

        if isinstance(log_file, TextIOWrapper):
            log_file.write((time_str() if timestamp else '') + msg + '\n')
        elif log_file:   # assume log_file is like logger, with info method
            log_file.info(msg)

        if to_console:
            if timestamp:
                print(time_str(), end='')
            if text_color is not None:
                with use_text_color(text_color, light=light_fore):
                    print(msg)
            else:
                print(msg)
            if prompt:
                input('按 ENTER 键继续... ')

        if log_file:
            if flush:
                log_file.flush()
            if closing:
                log_file.close()

        if lock:
            lock.release()

# a simpler version of write_log without timestamp (as provied in msg already)


def wl(log_file, msg, flush=False):
    return write_log(log_file, msg, timestamp=False, flush=flush)


def commit_with_retry(db, close=False, log_file=None) -> None:
    if db:
        for ix in range(5):
            try:
                db.commit()
                if close:
                    db.close()
                return True
            except Exception as e:
                write_log(log_file, f'数据库 Commit 错误: {repr(e)}. 5秒再试第 {ix+2} 次', to_console=True, text_color=RED)
                time.sleep(5)

                # try reconnect
                try:
                    db.connect()
                except:
                    pass

        write_log(log_file, '******* 数据库 Commit 失败！*******', to_console=True, text_color=RED)
    return False


# wait till all futures are completed, keep=True: keep exited future in given list, interrupt=True: quit when any yield causes exception  idle_func: func to call on each pull loop
def futures_as_completed(futures: list, timeout=0, keep=False, interrupt=True, idle_func=None, interval=0.1, left_jobs=0):
    try:
        start = time.time()
        check_list = list(futures) if keep else futures
        while len(check_list) > left_jobs:
            if timeout and time.time() - start >= timeout:
                break

            time.sleep(interval)
            if idle_func:
                try:
                    if idle_func(check_list):
                        start = time.time()  # restart timeout counter
                except Exception as e:
                    show_ex(e)
                    if interrupt:
                        break

            ix = 0
            while ix < len(check_list):
                future = check_list[ix]
                if future.done():
                    start = time.time()  # restart timeout counter
                    try:
                        yield future
                    except Exception as e:
                        show_ex(e)
                        if interrupt:
                            check_list = None
                            break
                    finally:
                        del check_list[ix]
                        ix -= 1
                ix += 1
    except Exception as e:
        show_ex(e)


# return a set of rows of dict, where the given field is unqiue
def select_unique(rows, field_name):
    nr = []
    if rows:
        existing = set()
        for r in rows:
            if field_name in r and r[field_name] not in existing:
                nr.append(r)
                if field_name in r:
                    existing.add(r[field_name])
    return nr


# from numba import jit
# @jit(nopython=True)
def make_dict_rows(rows, col_desc, want_lower=True):
    return [EntityThrow(zip([d[0].lower() if want_lower else d[0] for d in col_desc], row)) for row in rows]


# @jit(nopython=True)
def get_col_from_rows(rows, field, exclude=None):
    return [r[field] for r in rows if not exclude or r[field] not in exclude]


def check_sql_value(v, vals: list, db_type=0):    # 0: mysql  1: oracle  2: sqlite
    if v is None or isinstance(v, str) and len(v) == 0:
        return 'NULL'

    if isinstance(v, (int, float)):
        return f'{v}'

    if db_type == 1 and isinstance(v, datetime):
        ts = v.strftime('%Y-%m-%d %H:%M:%S')
        return f"TIMESTAMP '{ts}'"

    if db_type == 1:
        return f"{v}"

    vals.append(v)
    return "%s" if db_type != 2 else '?'


def get_kv_dict(cursor, sql_stmt, fields=None, prompt=True):
    with time_it() as tm:
        cursor.execute(sql_stmt)
        rows = cursor.fetchall()
        key_field, value_field = fields.split('=')[0] if fields else 0, fields.split('=')[1] if fields else 1
        d = dict(zip([r[key_field] for r in rows], [r[value_field] for r in rows]))
    if prompt:
        print(f'读取了 {len(d):,} 个 {key_field}={value_field} 记录, 耗时: {tm.time_used_str()}')
    return d


def call_later(fn, args=(), delay=0.001):
    if isinstance(args, (list, tuple)):
        (thread := Thread(target=lambda: (time.sleep(delay), fn(*args)))).start()
    else:
        (thread := Thread(target=lambda: (time.sleep(delay), fn(**args)))).start()
    return thread


def write_data_to_file(bin_file, data, compress=False, err=None, clear_data=True):
    ''' write a piece of data into the bin file, return bytes saved due to compressiong'''
    cb_saved = 0
    if data is not None:
        try:
            bin_data = pickle.dumps(data)
            old_cb = len(bin_data)
            if compress:
                bin_data = gzip.compress(bin_data)
                cb_saved = old_cb - len(bin_data)
            cb = len(bin_data)

            to_close = False
            if isinstance(bin_file, str):
                bin_file = open(bin_file, 'wb')
                to_close = True

            bin_file.write(cb.to_bytes(4, 'big'))
            bin_file.write(bin_data)
            if to_close:
                bin_file.close()
                to_close = False
            else:
                bin_file.flush()
        except Exception as e:
            if err:
                err.ex = e
                err.error = f'无法写入数据到 {bin_file}: {repr(e)}'
        finally:
            if to_close:
                bin_file.close()

        if isinstance(data, list) and clear_data:
            data.clear()
    return cb_saved


def read_data_from_file(inf, compress=False, ignore_decompression_error=True, remove_file=False):
    ''' read a piece of data from file, return the instance read, or NOne if failed/EOF'''
    try:
        in_filename = None
        if isinstance(inf, str):
            if not os.path.isfile(inf):
                return None
            in_filename = inf
            inf = open(in_filename, 'rb')

        cbd = inf.read(4)
        if cbd is not None and len(cbd):
            cb = int.from_bytes(cbd, 'big')
            data = inf.read(cb)
            if compress:
                try:
                    data = gzip.decompress(data)
                except Exception as e:
                    if not ignore_decompression_error:
                        show_ex(e)
                        return None

            obj = pickle.loads(data)
            if remove_file and in_filename:
                inf.close()
                os.remove(in_filename)
                in_filename = None
            return obj
    except Exception as e:
        show_ex(e)
    finally:
        if in_filename:
            inf.close()
    return None


def close_db_cur(db, cur, commit=False):
    try:
        if cur:
            cur.close()
        if db:
            if commit:
                commit_with_retry(db, close=True)
            else:
                db.close()
    except Exception:
        pass


# make a conditional clause using a key name and a set of values
# common usage: use_in=True, use_not=False will return   id in (1,2,3)
# common usage: use_and=False, use_equal=True will return   id=1 or id=2 or id=3
def make_clause(key, ids, use_in=True, use_not=False, use_and=False, use_equal=True, key_no_quote=False, ids_no_quote=False, force_string=False, parameterized=False):
    if not ids:
        return ''

    if not isinstance(ids, (list, tuple)):
        ids = list(ids)

    key_quote = '' if key_no_quote else '`'
    ids_quote = '' if ids_no_quote else "'"

    if use_in:
        lop = ' not in ' if use_not else ' in '
        return f'({key_quote}{key}{key_quote}{lop}(' + ','.join((['%s'] * len(ids)) if parameterized else [(f"{ids_quote}{p}{ids_quote}" if force_string or isinstance(ids[0], str) else str(p)) for p in ids]) + '))'

    lop = ' AND ' if use_and else ' OR '
    nop = '=' if use_equal else '<>'

    return '(' + lop.join((['%s'] * len(ids)) if parameterized else [(f"{key_quote}{key}{key_quote}{nop}" + (f"{ids_quote}{p}{ids_quote}" if force_string or isinstance(ids[0], str) else str(p))) for p in ids]) + ')'

def make_clause_many_field(key1, key2, ids, use_and=False, use_equal=True, key_no_quote=True, ids_no_quote=False, force_string=False, parameterized=False):
    if not ids:
        return ''

    if not isinstance(ids, (dict)):
        ids = dict(ids)

    key_quote = '' if key_no_quote else '`'
    ids_quote = '' if ids_no_quote else "'"

    lop = ' AND ' if use_and else ' OR '
    nop = '=' if use_equal else '<>'
    noplike = 'LIKE'
    like_l = "'%"
    like_r = "%'"
    return lop.join((['%s'] * len(ids)) if parameterized else [(f"({key_quote}{key1}{key_quote}{nop}" + (f"{ids_quote}{empi}{ids_quote}" if force_string else str(empi)) + (f" AND {key_quote}{key2}{key_quote} {noplike} " + (f"{like_l}{p}{like_r})"))) for empi, p in ids.items()])

class DisplayByFields:
    # find and summerize field definiton from a list of rows
    def find_field_definition(self, rows):
        if not rows or type(rows) is not list:
            return None

        fds = [[k, k, len(k) + 1, len(k) + 1, ''] for k in rows[0].keys()]
        for r in rows:
            for ix in range(len(fds)):
                fd = fds[ix]
                _, kn, w, t = fd

                if kn in r:
                    v, dv = r[kn], ''
                    if v is None:
                        continue

                    if type(v) is int or type(v) is float:
                        if not t:
                            fd[4] = 'n'
                        dv = f'{v:,.3f}' if type(v) is float else f'{int(v):,}'
                    elif type(v) is date or type(v) is datetime:
                        dv = v.strftime('%Y-%m-%d %H:%M:%S') if type(v) is datetime else v.strftime('%Y-%m-%d')
                        if not t:
                            fd[4] = 'd'
                    elif type(v) is bytes:  # special case, treat binary types are all GB2312 text
                        try:
                            r[kn] = v = v.decode(encoding='GB2312', errors='ignore')
                        except:
                            v = f'<无法解码 {len(v)} 个字节>'
                    else:
                        fd[4] = 's'
                        dv = repr(v)

                    if len(dv) + 1 > w:
                        fd[2] = fd[3] = len(dv) + 1
        return fds

    def __init__(self, fields=None, rows=None, prefix='', first_line_prefix=None, for_print=False):
        self.fields = self.find_field_definition(rows) if rows else fields        # fields is a list of definition, each defintion has four elements: name to be displayed, key name, width for UTF8, width for ASCII, data type: n b d or s
        self.prefix = prefix
        self.first_line_prefix = first_line_prefix
        self.for_print = for_print  # if True, no color output

    def print_header(self, color=None, light=True):
        if not self.for_print and color is not None:
            set_text_color(color, light=light)

        print(self.first_line_prefix if self.first_line_prefix is not None else self.prefix, end='')
        for ft, _, w, t in self.fields:
            print(ft.ljust(w - len([c for c in ft if unicodedata.east_asian_width(c) == 'W' or unicodedata.east_asian_width(c) == 'F'])), end='')
        print()
        print(self.prefix, end='')
        for ft, _, w, t in self.fields:
            print('=' * (w - 1), end=' ')
        print()

        if not self.for_print and color is not None:
            reset_text_color()

    def print_data(self, data, color=None, light=True, alt_color=None, alt_light=None, before_row=None, after_row=None, show_total=None):
        if not data:
            return

        if not self.for_print and color is not None:
            set_text_color(color, light=light)

        if type(data) is not list:
            data = [data]

        sums = [0] * len(show_total) if show_total else None
        seq = 0
        for r in data:
            seq += 1
            if before_row:
                before_row(r)

            if alt_color is not None:
                set_text_color(alt_color if seq % 2 else color, light=alt_light if seq % 2 else light)

            def _convert_number(t, v):
                text = None
                if t == 'n':
                    text = f'{v:,.3f}' if type(v) is float else f'{int(v):,}'
                elif t == 'n.':
                    text = f'{v:.3f}' if type(v) is float else f'{int(v)}'

                if text and text.endswith('.000'):
                    return text[:-4]
                return text

            print(self.prefix, end='')
            for _, fn, w, t in self.fields:
                if fn == 'seq':
                    v = str(seq)
                    t = 's'
                elif fn in r:
                    v = r[fn]
                else:
                    v = f'<没有 {fn}>'
                    t = 's'

                if v is None:
                    v = ''
                else:
                    v1 = v
                    try:
                        if t[0] == 'n':
                            v1 = _convert_number(t, v)
                            if v1 and show_total and fn in show_total:
                                ix = show_total.index(fn)
                                sums[ix] += v
                        elif t == 'b':
                            v1 = 'Yes' if v else 'No'
                        elif t == 'd':
                            v1 = v.strftime('%Y-%m-%d')
                        elif t == 'c':  # count
                            v1 = _convert_number('n', len(v))
                        elif t == '$':
                            v1 = '￥' + _convert_number('n', v)
                    except:
                        v1 = '[数值错误]'
                    v = v1

                try:
                    print(put_text_by_width(v.replace('\n', ' | ').replace('\r', '').strip(), w), end='')
                except:
                    print('<ERROR>'.ljust(w - 1), end='')
            print()

            if after_row:
                after_row(r)

        # print totals
        if show_total:
            for line in range(2):
                print(self.prefix, end='')
                for _, fn, w, t in self.fields:
                    if line == 0:
                        print(('-' * (w - 1) + ' ') if fn in show_total else ' ' * w, end='')
                    elif fn in show_total:
                        v = _convert_number(t, sums[show_total.index(fn)])
                        print(v.ljust(w - 1), end=' ')
                    else:
                        print(' ' * w, end='')
                print()

        if not self.for_print and color is not None:
            reset_text_color()


from html.parser import HTMLParser
from html.entities import name2codepoint

# parse one and only one HTML tag, all sub-tags are ignored with text combined， embedded tag will overwrite previous contents


class MyHTMLParser(HTMLParser):
    def __init__(self, data: Entity, convert_charrefs: bool = False) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.current = data

    def handle_starttag(self, tag, attrs):
        if self.current.hasstart_tag:
            child = Entity()
            if not self.current.children:
                self.current.children = []
            self.current.children.append(child)
            child.parent = self.current
            self.current = child

        self.current.start_tag = tag
        self.current.attrs = {} if attrs else None
        for name, value in attrs:
            self.current.attrs[name] = value

    def handle_endtag(self, tag):
        self.current.end_tag = tag
        if tag == self.current.start_tag and self.current.hasparent:
            self.current = self.current.parent

    def handle_data(self, data):
        self.current.text = (self.current.text if self.current.hastext else '') + data

    def handle_comment(self, data):
        self.current.comment = data

    def handle_entityref(self, data):
        data = chr(name2codepoint[data])
        self.current.text = (self.current.text if self.current.hastext else '') + data

    def handle_charref(self, name):
        name = chr(int(name[1:], 16)) if name.startswith('x') else chr(int(name))
        self.current.text = (self.current.text if self.current.hastext else '') + name

    def handle_decl(self, data):
        self.current.decl = data


def get_object_size(obj, seen=None):
    """Recursively finds size of objects in bytes"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if hasattr(obj, '__dict__'):
        for cls in obj.__class__.__mro__:
            if '__dict__' in cls.__dict__:
                d = cls.__dict__['__dict__']
                if inspect.isgetsetdescriptor(d) or inspect.ismemberdescriptor(d):
                    size += get_object_size(obj.__dict__, seen)
                break
    if isinstance(obj, dict):
        size += sum((get_object_size(v, seen) for v in obj.values()))
        size += sum((get_object_size(k, seen) for k in obj.keys()))
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum((get_object_size(i, seen) for i in obj))

    if hasattr(obj, '__slots__'):  # can have __slots__ with __dict__
        size += sum(get_object_size(getattr(obj, s), seen) for s in obj.__slots__ if hasattr(obj, s))

    return size


def get_object_size_str(obj, seen=None, rounding=2):
    cb = get_object_size(obj)
    return to_size_text(cb, rounding=rounding)


def set_file_times(file_name, modified_timestamp, access_timestamp=None):
    mtime, atime = modified_timestamp, access_timestamp

    try:
        if mtime and type(mtime) is datetime:
            mtime = mtime.timestamp()
    except:
        mtime = None

    try:
        if atime and type(atime) is datetime:
            atime = atime.timestamp()
        else:
            atime = mtime
    except:
        atime = mtime

    if mtime:
        try:
            os.utime(file_name, (atime, mtime))
        except Exception as e:
            err_msg('Failed to set time on %s: %s' % (file_name, repr(e)))
            return False
    return True


def copy_file(src_file, target_file):
    try:
        with open_mmap_file_to_read(src_file) as data:
            dir = os.path.split(target_file)[0]
            if dir:
                os.makedirs(dir, exist_ok=True)
            with open(target_file, 'wb') as outf:
                outf.write(data)

        fst = os.stat(src_file)
        return set_file_times(target_file, fst.st_mtime, fst.st_atime)
    except Exception as e:
        show_ex(e)
    return False


class AtomicCounter:
    def __init__(self):
        self.counter = 0
        self.lock = Lock()

    def get(self):
        with self.lock:
            return self.counter

    def set(self, value):
        self.counter = value

    def increment(self):
        with self.lock:
            self.counter += 1
            return self.counter

    def decrement(self):
        with self.lock:
            self.counter -= 1
            return self.counter

    def add(self, value):
        with self.lock:
            self.counter += value
            return self.counter

    def delete(self, value):
        with self.lock:
            self.counter -= value
            return self.counter

    def is_zero(self):
        with self.lock:
            return self.counter == 0

    def check_zero(self, timeout=0, interval=0.2):
        while True:
            if self.is_zero():
                return True
            time.sleep(interval)
            if timeout != 0:
                if timeout < interval:
                    return False
                timeout -= interval


class SQLRunner:
    def _runner(self, tinfo: Entity()):
        while 1:
            try:
                stmt, val = tinfo.q.get(False)
                if stmt == self.quit:
                    break

                tinfo.cursor.execute(stmt, [val] if val else None)
            except queue.Empty:
                time.sleep(0.1)
            except Exception:
                try:
                    # retry again
                    tinfo.retry += 1
                    tinfo.cursor.execute(stmt, [val] if val else None)
                except Exception:
                    try:
                        # retry again
                        tinfo.retry += 1
                        tinfo.cursor.execute(stmt, [val] if val else None)
                    except Exception:
                        pass
        tinfo.close_func(tinfo.cursor)
        with tinfo.q.mutex:
            tinfo.q.queue.clear()

    def __init__(self, num_threads, make_cursor_func, close_func) -> None:
        self.num_threads = num_threads
        self.threads = [Entity() for _ in range(num_threads)]
        self.quit = '<<QUIT>>'
        self.lock = Lock()
        for tinfo in self.threads:
            tinfo.q = queue.Queue()
            tinfo.cursor = make_cursor_func()
            tinfo.close_func = close_func
            tinfo.retry_count = 0

            tinfo.thread = Thread(target=self._runner, args=(tinfo,))
            tinfo.thread.daemon = True

    def start(self):
        for tinfo in self.threads:
            tinfo.thread.start()

    def stop(self, reporter=None):
        for tinfo in self.threads:
            if tinfo.thread and tinfo.thread.is_alive():
                tinfo.q.put((self.quit, None))

        while [t for t in self.threads if t.thread and t.thread.is_alive()]:
            time.sleep(0.5)
            if reporter and reporter(self.threads):
                break

    def total_qsize(self):
        return sum([t.q.qsize() for t in self.threads if t.thread and t.thread.is_alive()])

    def total_retry(self):
        return sum([t.retry_count for t in self.threads if t.thread and t.thread.is_alive()])

    def put(self, stmt, val):
        tm = min(self.threads, key=lambda x: x.q.qsize())
        tm.q.put((stmt, val))


class BinFile:
    def __init__(self, file_name, to_read=False, as_mmap_file=True, append=False) -> None:
        self.file_name = file_name
        self.file_size = os.path.getsize(file_name) if os.path.isfile(file_name) and (to_read or append) else 0
        self.file = open(file_name, 'rb' if to_read else ('ab+' if append else 'wb+'))  # use + to allow both reading and writing
        self.data = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ) if as_mmap_file and to_read else None
        self.data_pos = 0
        self.EOF_byte = b'*'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        if self.data:
            self.data.close()
        self.file.close()

    def tell(self) -> int:
        return self.data_pos if self.data else self.file.tell()

    def seek(self, pos, whence=os.SEEK_SET) -> None:
        if self.data:
            if whence == os.SEEK_SET:
                self.data_pos = pos
            elif whence == os.SEEK_CUR:
                self.data_pos += pos
            else:
                self.data_pos = max(0, self.data.size() - pos)
        else:
            self.file.seek(pos, whence)

    def write_EOF_byte(self, eof_rec=None) -> None:
        self.file.write(self.EOF_byte)
        if not eof_rec:
            self.file.write(int(0).to_bytes(3, 'big'))
        else:
            data = pickle.dumps(eof_rec)
            self.file.write(len(data).to_bytes(3, 'big'))
            self.file.write(data)

    def read(self, num_bytes: int) -> bytes:
        if self.data:
            num_bytes = min(num_bytes, self.data.size() - self.data_pos)
            dr = self.data[self.data_pos:self.data_pos + num_bytes] if num_bytes else None
            self.data_pos += num_bytes
        else:
            dr = self.file.read(num_bytes)
        return dr

    def read_int(self, num_bytes: int = 4) -> int:
        dn = self.read(num_bytes)
        return int.from_bytes(dn, 'big') if dn else 0

    def read_eof_rec(self):
        cb = self.read_int(3)
        return pickle.loads(self.read(cb)) if cb else None

    def write_str(self, s: str) -> None:
        data = s.encode('utf-8')
        self.file.write(len(data).to_bytes(4, 'big'))
        self.file.write(data)

    def read_str(self, skip=False) -> str:
        cb = self.read_int()
        if not cb:
            return None  # EOF

        if skip:
            self.seek(cb, os.SEEK_CUR)
            return ''
        return self.read(cb).decode('utf-8')

    # compress = 0: no compress  1: always compress  -1: compress only if smaller
    def write_data(self, data: object, compress: int = 0) -> None:
        if data:
            data = pickle.dumps(data)

            cdata = gzip.compress(data) if compress else data
            cb = len(cdata)

            compressed = b'Y'
            if compress < 0 and cb >= len(data) - 1 or compress == 0:
                # compressed size is bigger than actual size? then no need to compress
                compressed = b'N'
                cb = len(data)
                cdata = data

            self.file.write(compressed)
            self.file.write(cb.to_bytes(4, 'big'))
            self.file.write(cdata)

    # compress = 0: no compress  1: always compress  -1: compress only if smaller
    def read_data(self, eof_rec=None, skip=False) -> None:
        lead_byte = self.read(1)
        if lead_byte == self.EOF_byte:
            er = self.read_eof_rec()
            if eof_rec:
                eof_rec['eof_rec'] = er
            return None

        cb = self.read_int()
        if not cb:
            return None

        if skip:
            self.seek(cb, os.SEEK_CUR)
            return cb

        data = self.read(cb)
        if lead_byte == b'Y':
            try:
                return pickle.loads(gzip.decompress(data))
            except:
                pass
        return pickle.loads(data)

    # write a zero to the file to signal an end of a stream
    def write_zero(self):
        self.file.write(b'\0' * 5)  # one lead byte, plus 4 bytes for zero int
        self.file.flush()

    # write compressed data to end, then add data length of 4 bytes to file end so the data can be read from fileend next time
    # this should be the last write to this binfile
    def write_data_to_end(self, data, compress=True):
        if data:
            ndata = pickle.dumps(data)
            cdata = gzip.compress(ndata) if compress else ndata
            cb = len(cdata)
            self.file.write(cdata)
        else:
            cb = 0
        self.file.write(b'Y' if compress else b'N')
        self.file.write(cb.to_bytes(4, 'big'))
        return cb

    # read the last four bytes of the file as size, then read the data before
    def read_data_from_end(self):
        if self.file_size <= 5:
            return None

        try:
            self.seek(self.file_size - 5)
            compressed = self.read(1)
            cb = self.read_int()
            self.seek(last_pos := self.tell() - cb - 5)
            cdata = self.read(cb)
            if compressed == b'Y':
                cdata = gzip.decompress(cdata)
            data = pickle.loads(cdata)
            self.seek(last_pos)  # move to end of read data (before last piece) to continue writting
            return data
        except Exception as e:
            show_ex(e)
        return None


class InserterBase(Thread):
    def __init__(self, filename, batch_limit=10000):
        Thread.__init__(self)
        self.daemon = True  # program will end without waiting for this thread to end
        self.filename = filename
        self.lock = Lock()
        self.vals_list = []
        self.quit = False
        self.insert_count = 0
        self.batch_count = 0
        self.batch_size = 0
        self.batch_limit = batch_limit
        self.batch = []

    def insert_data(self, vals_list):
        return

    def run(self):
        while True:
            vals_list = None
            with self.lock:
                if self.vals_list:
                    vals_list = self.vals_list
                    self.vals_list = []
                    self.batch_size = len(vals_list)
                    self.insert_count += 1

            if vals_list:
                self.insert_data(vals_list)
            else:
                if self.quit:
                    break
                time.sleep(0.1)

    def stop(self):
        if self.batch:
            self.add(self.batch)
        self.quit = True
        self.join()

    def add(self, vals):
        with self.lock:
            self.batch_count += 1
            self.vals_list.append(vals)

    def add_one(self, val):
        with self.lock:
            self.batch.append(val)
            if len(self.batch) >= self.batch_limit:
                self.vals_list.append(self.batch)
                self.batch = []


class BinFile_Inserter(InserterBase):
    def __init__(self, filename, batch_limit=10000):
        super().__init__(filename, batch_limit)
        self.total_data_size = 0
        self.saved_size = 0

    def insert_data(self, vals_list):
        with self.lock:
            vals = []
            for v in vals_list:
                vals += v
            if vals:
                with open(self.filename, 'ab+') as outf:
                    data = pickle.dumps(vals)
                    cb = len(data)
                    self.total_data_size += cb
                    data = gzip.compress(data)
                    self.saved_size += cb - (cb_now := len(data))
                    outf.write(cb_now.to_bytes(4, 'big'))
                    outf.write(data)


def make_one_line_center(m=None, border_ch='*', space_ch=' ', width=120, add_lf=True):
    if not m:
        m = ''
    lm = len(m)
    spaces = space_ch * ((width - 2 - lm) // 2)
    extra = space_ch * (lm % 2 != 0)
    msg = f'{border_ch}{spaces}{m}{spaces}{extra}{border_ch}'
    return (msg + '\n') if add_lf else msg


def _read_data_seg(seg):
    data_fn, pos, cb = seg
    ti = Entity()
    ti.rows = []
    try:
        with open(data_fn, 'rb') as inf:
            inf.seek(pos)
            data = inf.read(cb)

        ti.rows = pickle.loads(gzip.decompress(data))
    except Exception as e:
        ti.ex = e
    return ti


def read_bin_file(data_fn, worker_func, wp, reader_func=None, read_header_only=False, debug=False):
    wp.hdr = None
    print_green(f'Reading {data_fn} of size {to_size_text(os.path.getsize(data_fn), rounding=2)}...')

    data_segs = []
    with open(data_fn, 'rb') as inf:
        while (cbd := inf.read(4)):
            pos = inf.tell()
            cbd = int.from_bytes(cbd, 'big')
            if cbd > 0:
                data_segs.append((data_fn, pos, cbd))
                inf.seek(pos + cbd)
            else:   # size of the block can not be zero, it can only be negative at this time, which means following block is a header
                cbd = -cbd
                wp.hdr = pickle.loads(gzip.decompress(inf.read(cbd)))
                break

    if not read_header_only:
        wp.pbar, wp.p2 = common_pbar2(maxval=len(data_segs), dual=True, main_t2='数据段', width=140, want_bar=False)
        wp.pbar.start()

        max_workers = 1 if debug else 8
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) if debug else \
            concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
        for f in concurrent.futures.as_completed([executor.submit(reader_func if reader_func else _read_data_seg, seg=v) for v in data_segs]):
            try:
                ti = f.result()
                if ti.hasex:
                    show_ex(ti.ex)
                else:
                    worker_func(wp, ti)
                    wp.pbar.update(wp.pbar.currval + 1)
            except Exception as e:
                show_ex(e)
        executor.shutdown()

        wp.pbar.maxval = wp.pbar.currval
        wp.pbar.finish()
        del wp.pbar
        del wp.p2


def create_marker_file(filename):
    try:
        if not os.path.isfile(filename):
            with open(filename, 'wt') as outf:
                outf.write(time_str() + '\n')
    except:
        return False

    return os.path.isfile(filename)


def has_marker_file(filename, remove=False):
    if os.path.isfile(filename):
        if remove:
            try:
                os.remove(filename)
            except:
                ...
        return True
    return False


def remove_file(filename):
    return has_marker_file(filename, True)


def write_data(outf, data):
    data = gzip.compress(pickle.dumps(data))
    outf.write((cb := len(data)).to_bytes(4, 'big'))
    if cb:
        outf.write(data)
    return cb


def read_data(inf):
    try:
        return pickle.loads(gzip.decompress(inf.read(int.from_bytes(inf.read(4), 'big'))))
    except:
        pass    # ignore error, could be EOF
    return None


def stringify(v, new_type_func=None, p=None, date_as_str=False, int_as_float=False):
    ''' convert a value into string consistently for the purpose of calculate MD5'''
    if v is None:
        return ''
    if isinstance(v, datetime):
        try:
            return v.strftime('%Y-%m-%d %H:%M:%S') if date_as_str else str(int(v.timestamp() * 10 ** 6))
        except:
            # datetime could be invalid
            return v.strftime('%Y-%m-%d %H:%M:%S')

    if int_as_float and isinstance(v, int):
        v = float(v)

    if isinstance(v, date):
        return v.strftime('%Y-%m-%d') if date_as_str else str(v.toordinal())
    if isinstance(v, (float, Decimal)):
        return str(int(v * 10 ** 10))
    if isinstance(v, (list, tuple, set)):
        return '-'.join(sorted(stringify(x) for x in v))
    if isinstance(v, bytes):
        return '-'.join(str(b) for b in sorted(v))
    if isinstance(v, dict):
        return '-'.join(sorted(stringify(k) + ':' + stringify(x) for k, x in v.items()))
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, (int, uuid.UUID)):
        return str(v)

    return new_type_func(v, p) if new_type_func else str(v).strip()


def show_msg(wp: EntityThrow, msg: str) -> None:
    if not wp.hasmsg_count:
        wp.msg_count = 0
    write_log(wp.logf if wp.haslogf else None, print_color(time_str() + msg, 'yellow' if wp.msg_count % 2 else 'green'), timestamp=False, flush=True)
    wp.msg_count += 1


def tail_log(wp: EntityThrow, ti: EntityThrow, prefix: str, clr: str) -> bool:
    '''
    show unprinted lines in a log file. needs following params:
        ti.log_fn:          log file name
        ti.last_log_line:   last printed log line number (optional)
        wp.msg_count:       msg counter for color alternating (optional, will use ti if not given)
    '''
    if os.path.isfile(ti.log_fn):
        if not ti.haslast_log_line:
            ti.last_log_line = 0
        if not wp:
            wp = ti
        if not wp.hasmsg_count:
            wp.msg_count = 0

        if prefix[-1] != ' ':
            prefix += ' '

        with open(ti.log_fn, 'r', encoding='utf-8') as inf:
            lines = [l.strip() for l in inf]
        lines_to_show = lines[ti.last_log_line:]
        if lines_to_show:
            for l in lines_to_show:
                fs = clr.split(',')
                if len(fs) == 1:
                    print_color(prefix + l, clr)
                else:
                    print_color(prefix + l, fs[0] if wp.msg_count % 2 else fs[1])
                wp.msg_count += 1
            ti.last_log_line = len(lines)
            return True
        return False


@contextlib.contextmanager
def read_from_cache_or_else(cfn, wp, name=None, prompt=False, clear_data=False, no_cache=False):
    wp.data = None
    if not no_cache and os.path.isfile(cfn):
        if prompt:
            a = input(f'存在缓存文件 {file_info_str(cfn, timestamp=True)}. 按 ENTER 键使用: ')
            if not a:
                wp.data = read_data_from_file(cfn)
                yield None
            else:
                yield wp
                write_data_to_file(cfn, wp.data, clear_data=clear_data)
        else:
            print_white(f'使用缓存文件 {file_info_str(cfn, timestamp=True)}')
            wp.data = read_data_from_file(cfn)
            yield None
    else:
        yield wp    # caller should fill in wp.data
        write_data_to_file(cfn, wp.data, clear_data=clear_data)

# 从中国身份证号提取生日和性别


def get_dob_gender_from_chinese_id(cid):
    dob = sex = None
    try:
        if len(cid) == 18:
            dob = date(int(cid[6:10]), int(cid[10:12]), int(cid[12:14]))
            sex = 1 if int(cid[-2]) % 2 else 2
        elif len(cid) == 15:
            dob = date(1900 + int(cid[6:8]), int(cid[8:10]), int(cid[10:12]))
            sex = 1 if int(cid[-1]) % 2 else 2
    except:
        dob = sex = None
    return dob, sex


def GET_AGE(check_date, dob): return check_date.year - dob.year - (((check_date.month, check_date.day) < (dob.month, dob.day)))


def try_something(max_tries, timeout=10):
    '''
    a function decorator that would run the wrapped function at most max_tries
    '''
    def wrapper(func):
        # functools.wraps 可以将原函数对象的指定属性复制给包装函数对象,
        @functools.wraps(func)
        def __decorator(*args, **kwargs):
            for _ in range(max_tries):
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    show_ex(ex)
                time.sleep(timeout)
        return __decorator
    return wrapper


def is_same_date(dates1, dates2):
    dates1 = dates1 if isinstance(dates1, (list, tuple)) else (dates1,)
    dates2 = dates2 if isinstance(dates2, (list, tuple)) else (dates2,)
    for ix, dt1 in enumerate(dates1):
        dt2 = dates2[ix]
        if dt1 == dt2:
            continue
        if dt1 and not dt2 or not dt1 and dt2:
            return False
        if not isinstance(dt1, (datetime, date)):
            dt1 = parse_datetime(dt1)
        if not isinstance(dt2, (datetime, date)):
            dt2 = parse_datetime(dt1)
        if not dt1 or not dt2:
            return False  # some error in above converstion
        if (dt1.year, dt1.month, dt1.day) != (dt2.year, dt2.month, dt2.day):
            return False
    return True


def is_same_dict(d1, d2):
    if not d1:
        return not d2
    if not d2:
        return False
    if not isinstance(d1, dict) or not isinstance(d2, dict):
        return False

    return stringify(d1) == stringify(d2)


def page_list(data, page_size, want_offset=False):
    if data:
        if isinstance(data, str):
            data = data.split(',')
        else:
            data = list(data)

        for offset in range(0, len(data), page_size):
            if want_offset:
                yield data[offset:offset + page_size], offset, len(data[offset:offset + page_size])
            else:
                yield data[offset:offset + page_size]


def page_list2(data, data2, page_size, want_offset=False):
    if data:
        if isinstance(data, str):
            data = data.split(',')
        else:
            data = list(data)

        if isinstance(data2, str):
            data2 = data2.split(',')
        elif data2:
            data2 = list(data2)

        for offset in range(0, len(data), page_size):
            if want_offset:
                yield data[offset:offset + page_size], data2[offset:offset + page_size] if data2 else None, offset, len(data[offset:offset + page_size]), len(data2[offset:offset + page_size]) if data2 else 0
            else:
                yield data[offset:offset + page_size], data2[offset:offset + page_size] if data2 else None


def strip_tags(v):
    '''
    simply remove everything between <> and concatenate the rest today, striping white space and control characters
    '''
    bc = 0
    nv = ''
    for ch in v:
        if ch == '<':
            bc += 1
            continue

        if ch == '>' and bc > 0:
            bc -= 1
            continue

        if bc == 0 and ord(ch) >= 32:  # 32 is space
            nv += ch
    return nv.strip()


class JSONDateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, Decimal):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def save_data_to_json(obj, jfn):
    with open(jfn, 'wt', encoding='utf-8') as outf:
        json.dump(obj, outf, indent=4, ensure_ascii=False, cls=JSONDateTimeEncoder)

if __name__ == '__main__':
    with open('E:\\huashu\\binwj\\config.bin', 'rb') as outf:
        fgh = Fernet(b'4zH3962TJPDI2wmmPscmIA6Cmvhp3i5I8wuLiI9Ki50=').encrypt(outf.read())
        print(fgh)