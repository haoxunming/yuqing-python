# -*- coding:UTF-8 -*-
#
# 返回数据库配置
#
# Charles 吴波, 2021-08-31, copied from IHBH
#
import os
import json
import sys

sys.path.append('../')  # allow 'shared' to be imported below
import shared.common as c

_DB_CONFIG = None
_DB_CONFIG_FILE = os.path.join(os.path.dirname(__loader__.path), 'config.bin')


def _get(dbtype: str, profile: str, fields: str, set_fields: dict = None):
    global _DB_CONFIG

    if not _DB_CONFIG:
        try:
            with open(_DB_CONFIG_FILE, 'rt', encoding='utf-8') as jf:
                json_file = jf.read()
                _DB_CONFIG = c.EntityThrow(json.loads(json_file))
        except Exception as e:
            return None

    if dbtype not in _DB_CONFIG:
        return None

    cf_data = c.Entity(_DB_CONFIG[dbtype])
    config = c.Entity()

    if not profile:
        if not cf_data.hasdefault_profile:
            config.error = f'Default profile is not specified in source!'
            return config
        profile = cf_data.default_profile

    if not profile in cf_data:
        config.error = f'Profile {profile} does not exists!'
        config.list = ','.join([k for k in cf_data.keys() if not k.startswith('default')])
    else:
        p = cf_data[profile]
        for field in fields.split(','):
            def_field = 'default_' + field
            if set_fields and field in set_fields and set_fields[field]:
                config[field] = set_fields[field]
            elif field in p:
                config[field] = p[field]
            elif def_field in cf_data:  # look for default in this section first
                config[field] = cf_data[def_field]
            elif def_field in _DB_CONFIG:   # look for default in root
                config[field] = _DB_CONFIG[def_field]
            else:
                config.error = f'{field} is not specified and not default is found either!'
                break
    return config


def get_mysql_uri(db):
    return f"mysql+pymysql://{db.username}:{db.password}@{db.host}/{db.database}"


def get_mysql_config(profile, database=None):
    return _get('MySQL', profile, 'host,port,username,password,database', {'database': database})


def get_postgres_config(profile, database=None):
    return _get('postgres', profile, 'host,port,username,password,database', {'database': database})


def get_oracle_config(profile):
    return _get('Oracle', profile, 'username,password,dsn')


def get_mssql_config(profile, database=None):
    return _get('MSSQL', profile, 'host,port,username,password,database', {'database': database})


def get_mongodb_config(profile, database=None):
    conf = _get('mongodb', profile, 'host,port,username,password,database', {'database': database})
    if not conf or conf.haserror:
        return None, None, conf

    s1 = f'mongodb://{conf.username}:{conf.password}@{conf.host}:{conf.port}/{conf.database}'
    s2 = f'主机: {conf.host}:{conf.port}   用户: {conf.username}   数据库： {conf.database}'
    return s1, s2, conf
