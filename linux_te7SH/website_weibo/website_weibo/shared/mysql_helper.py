# -*- coding:UTF-8 -*-
#
# MySQL helper
#
# Charles 吴波, 2022-09-19 copied from common.py
#
import sys
import contextlib
import time
import concurrent.futures
import binascii

sys.path.append('../')  # allow 'shared' to be imported below
import shared.common as c
from shared.dbhelper import MyDBHelper
from threading import Thread, Lock
import pymysql


def _get_mysql_client_with_param(prompt, host, username, password, database, port, cursor_class=None, log_file=None, to_console=False, show_err=True, read_timeout=None, write_timeout=None):
    connection = None
    with c.use_text_color(c.GREEN):
        if prompt:
            c.write_log(log_file, prompt % (host, username, database), to_console=to_console)

    try:
        connection = pymysql.connect(host=host, user=username, password=password, database=database, port=port, charset='utf8', init_command='select 1',
                                     cursorclass=cursor_class if cursor_class else pymysql.cursors.DictCursor, read_timeout=read_timeout, write_timeout=write_timeout, connect_timeout=160)
        if prompt:
            connection.ping()
            c.write_log(log_file, f'连接成功到 {host}, 数据库 {database}, 用户名: {username}.', to_console=to_console)

        return connection
    except Exception as error:
        if show_err:
            c.print_red(error)
    return None


def auto_retry(prompt, host, username, password, database, port, cursor_class=None, log_file=None, to_console=False, show_err=True, read_timeout=None, write_timeout=None):
    retry_interval = 5  # 重试间隔时间（秒）
    max_retry_times = 3  # 最大重试次数
    retry_count = 0  # 已重试次数

    while retry_count < max_retry_times:
        # print("正在第{}次尝试连接MySQL数据库".format(retry_count + 1))
        cnx = _get_mysql_client_with_param(prompt, host, username, password, database, port, cursor_class, log_file, to_console, show_err, read_timeout, write_timeout)  # 连接MySQL数据库

        if cnx:
            # print("成功连接MySQL数据库")
            return cnx  # 连接成功，返回连接对象

        print("连接MySQL数据库失败，将在{}秒后进行第{}次重试".format(retry_interval, retry_count + 2))
        time.sleep(retry_interval)
        retry_count += 1

    print("已达最大重试次数，连接MySQL数据库失败")
    return None


def get_mysql_client(prompt, config, log_file=None, to_console=True, show_err=True, cursor_class=None, read_timeout=None, write_timeout=None):
    if not config or 'error' in config:
        c.write_log(log_file, 'ERROR: ' + (config.error if config else "<n/a>"), text_color=c.RED, to_console=to_console)
        return None

    return auto_retry(prompt, config.host, config.username, config.password, config.database, config.port, cursor_class, log_file, to_console, show_err, read_timeout, write_timeout)


class MySQLHelper(MyDBHelper):
    def get_count2(self, db, field='*', where=None):
        if ' ' not in db and '`' not in db and '.' not in db:   # put table name in `` to suport all table names, such as procedure
            db = f'`{db}`'
        field = f'COUNT({field})'
        sql = f'SELECT {field} FROM {db}'
        if where:
            sql += ' WHERE ' + where
        self.cursor.execute(sql)
        return self.cursor.fetchall()[0][0]

    def get_count(self, db, field='*', where=None):
        try:
            return None, self.get_count2(db, field, where)
        except Exception as e:
            return (e, None)

    def get_last_insert_id(self):
        return self.cursor.connection.insert_id()

    def rollback(self):
        self.cursor.connection.rollback()

    def delete(self, db, where, reset_auto_inc=False) -> bool:
        try:
            if ' ' not in db and '`' not in db:   # put table name in `` to suport all table names, such as procedure
                db = f'`{db}`'
            sql = f'DELETE FROM {db}'
            if where:
                sql += ' WHERE ' + where
            self.cursor.execute(sql)

            if reset_auto_inc:
                self.cursor.execute(f'ALTER TABLE {db} AUTO_INCREMENT=1')
        except Exception as e:
            c.show_ex(e)
            return False
        return True

    def truncate_table(self, tbl, reset_auto_inc=True, no_fk_check=True) -> bool:
        try:
            if no_fk_check:
                self.cursor.execute('SET FOREIGN_KEY_CHECKS=0')

            if ' ' not in tbl and '`' not in tbl:   # put table name in `` to suport all table names, such as procedure
                tbl = f'`{tbl}`'
            self.cursor.execute(f'TRUNCATE TABLE {tbl}')

            if no_fk_check:
                self.cursor.execute('SET FOREIGN_KEY_CHECKS=1')

            if reset_auto_inc:
                self.cursor.execute(f'ALTER TABLE {tbl} AUTO_INCREMENT=1')
        except Exception as e:
            c.show_ex(e)
            return False
        return True

    def create_table_from_src(self, curs, db_name, tbl_name, skip_fields=None):
        if isinstance(skip_fields, (list, tuple)):
            skip_fields = set([f.lower() for f in skip_fields])

        try:
            # get column definition from source
            stmt = f"select column_name,data_type,character_maximum_length,numeric_scale,numeric_precision,is_nullable,column_comment from information_schema.columns where table_schema='{db_name}' and table_name='{tbl_name}' order by ordinal_position"
            curs.execute(stmt)
            r = curs.fetchall()
            if not r:
                return Exception(f'Failed to find information about {db_name}.{tbl_name}')

            fields = ','.join([f"{fn.lower()} " +
                               (ft if len is None else (f'{ft}({len})' if digits is None else (f'{ft}({digits})' if ps is None else f'{ft}({digits},{int(ps)})'))) + ' ' +
                               (f"{'NOT NULL' if null == 'N' else 'NULL'} ") +
                               (("COMMENT '" + cmt.replace("'", "''") + "'") if cmt else "") for fn, ft, len, digits, ps, null, cmt in r if not skip_fields or fn not in skip_fields])

            self.cursor.execute(f'DROP TABLE IF EXISTS {tbl_name}')
            stmt = f"CREATE TABLE `{tbl_name}` ({fields})"  # ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=Dynamic

            curs.execute(f"SELECT TABLE_COMMENT FROM information_schema.TABLES WHERE TABLE_TYPE LIKE 'BASE_TABLE' and table_schema='{db_name}' and table_name='{tbl_name}'")
            r = curs.fetchall()
            if r:
                stmt += " COMMENT = '" + r[0][0].replace("'", "''") + "'"
            self.cursor.execute(stmt)
        except Exception as e:
            return e

        return None

    def _make_select(self, db, fields=None, where=None, orderby=None, groupby=None, limit=None) -> str:
        if ' ' not in db and '`' not in db:   # put table name in `` to suport all table names, such as procedure
            db = f'`{db}`'
        sql = f'SELECT {fields if fields else "*"} FROM {db}'
        if where:
            sql += f' WHERE {where}'
        if orderby:
            sql += f' ORDER BY {orderby}'
        if groupby:
            sql += f' GROUP BY {groupby}'
        if limit:
            sql += f' LIMIT {limit}'
        return sql

    def get_top_row(self, db, fields=None, where=None, orderby=None, groupby=None, limit=None):
        try:
            sql = self._make_select(db, fields, where, orderby, groupby, limit)
            self.cursor.execute(sql)
            return None, self.cursor.fetchone()
        except Exception as e:
            return e, None

    def get_row(self, db, fields=None, where=None, orderby=None, groupby=None, limit=None):
        try:
            sql = self._make_select(db, fields, where, orderby, groupby, limit)
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            if not result:
                yield None, None
            else:
                for r in result:
                    yield None, r
        except Exception as e:
            yield e, None

    def get_all_rows(self, db, fields=None, where=None, orderby=None, groupby=None, limit=None):
        try:
            sql = self._make_select(db, fields, where, orderby, groupby, limit)
            self.cursor.execute(sql)
            return None, self.cursor.fetchall()
        except Exception as e:
            return e, None

    @staticmethod
    def _check_sql_value(v, vals: list):    # 0: mysql  1: oracle  2: sqlite
        if v is None or isinstance(v, str) and len(v) == 0:
            return 'NULL'

        if isinstance(v, (int, float)):
            return f'{v}'

        if isinstance(v, bytes):
            vs = binascii.hexlify(v).decode('ascii')
            return f"X'{vs}'"
        vals.append(v)
        return "%s"

    def _process_values(self, values):
        syms, vals = '(', []
        for v in values:
            syms += self._check_sql_value(v, vals) + ','
        syms = syms[:-1] + ')'
        return syms, vals

    def insert(self, db, fields: list, values: list, get_last_id=False):
        try:
            assert len(fields), 'SQLHelper::insert: Please specify fields'
            if len(fields) != len(values):
                assert False, f'SQLHelper::insert: fields size is {len(fields)} is different than value size of {len(values)}'

            f = ','.join([f'`{f}`' for f in fields])
            syms, vals = self._process_values(values)

            if ' ' not in db and '`' not in db:   # put table name in `` to suport all table names, such as procedure
                db = f'`{db}`'
            sql = f'INSERT INTO {db} ({f}) VALUES {syms}'
            self.cursor.execute(sql, vals)

            result = self.cursor.fetchone()
            return (self.get_last_insert_id() if get_last_id else None, result)
        except Exception as e:
            return (e, None)

    def update(self, db, fields: list, values: list, where=None):
        try:
            assert len(fields), 'SQLHelper::update: Please specify fields'
            if len(fields) != len(values):
                assert False, f'SQLHelper::update: fields size is {len(fields)} is different than value size of {len(values)}'

            stmt, vals = '', []
            for ix in range(len(fields)):
                f, v = fields[ix], values[ix]
                if v is None or type(v) is str and len(v) == 0:
                    stmt = f'`{f}`=NULL, '
                elif type(v) is int or type(v) is float:
                    stmt += f'`{f}`={v},'
                else:
                    stmt += f'`{f}`=%s,'
                    vals.append(v)
            stmt = stmt[:-1]

            if ' ' not in db and '`' not in db:   # put table name in `` to suport all table names, such as procedure
                db = f'`{db}`'
            sql = f'UPDATE {db} SET {stmt}'
            if where:
                sql += f' WHERE {where}'
            self.cursor.execute(sql, vals)

            result = self.cursor.fetchone()
            return (None, result)
        except Exception as e:
            return (e, None)

    def insertmany(self, db, fields: list, values_list: list, ignore_key_errors=False, commit_now=False):
        try:
            assert len(fields), 'SQLHelper::insert: Please specify fields'
            for values in values_list:
                if len(fields) != len(values):
                    assert False, f'SQLHelper::insert: fields size is {len(fields)} is different than value size of {len(values)}'

            f = ','.join([f'`{f}`' for f in fields])

            syms, vals = '', []
            for values in values_list:
                s, v = self._process_values(values)
                syms += s + ', '
                vals += v
            syms = syms[:-2]

            if ' ' not in db and '`' not in db:   # put table name in `` to suport all table names, such as procedure
                db = f'`{db}`'
            ignore = 'IGNORE' if ignore_key_errors else ''
            sql = f'INSERT {ignore} INTO {db} ({f}) VALUES {syms}'
            self.cursor.execute(sql, vals)

            result = self.cursor.fetchone()

            if commit_now:
                self.cursor.connection.commit()
            return (None, result)
        except Exception as e:
            return (e, None)

    def get_random_rows(self, table_name, field_name, limit=1):
        err, value = self.get_all_rows(table_name, field_name, orderby='RAND()', limit=limit)
        if err:
            c.print_red(f'Error: {repr(err)}')
            return None

        result = []
        for row in value:
            result.append(list(row.items())[0][1])
        return result

    def insert_batch(self, table_name: str, fields, batch: list, log_file=None, keep_rows=False, commit_now=False, ignore=True, clear_on_err=True, print_err_msg=True):
        if not batch:
            return None
        if isinstance(fields, str):
            fields = fields.split(',')
        err, _ = self.insertmany(table_name, fields, batch, ignore_key_errors=ignore, commit_now=commit_now)
        if err:
            msg = f'Error inserting into {table_name}: {repr(err)}'
            if log_file:
                c.write_log(log_file, msg, to_console=True)
            elif print_err_msg:
                c.print_red(msg)
            if clear_on_err and not keep_rows:
                batch.clear()
            return msg

        if ignore:
            self.cursor.execute('show warnings')
            for _, _, msg in self.cursor.fetchall():
                c.print_purple(msg)

        if not keep_rows:
            batch.clear()
        return None

    def insert_batch2(self, table_name: str, fields: list, batch: list, p: c.Entity = None) -> bool:
        '''insert many records into the given table
        p has the following input parameters:
            log_file: log file
            commit_now: commit after this insert statment
            keep_rows: true if don't need to clear input batch data
            clear: true if want to clear the data on error
            print_err_msg: true if want to display error message
            ignore: ignore insert errors
        return True on success
        also on return:
            p.result: result from insert
        '''
        if batch:
            ignore = p.ignore if p and p.hasignore else False
            commit_now = p.commit_now if p and p.hascommit_now else False
            log_file = p.log_file if p and p.haslog_file else None
            print_err_msg = p.print_err_msg if p and p.hasprint_err_msg else True
            clear_on_err = p.clear_on_err if p and p.hasclear_on_err else True
            keep_rows = p.keep_rows if p and p.haskeep_rows else False

            err, p.result = self.insertmany(table_name, fields, batch, ignore_key_errors=ignore, commit_now=commit_now)
            if err:
                p.err = f'Error inserting into {table_name}: {repr(err)}'
                # special processing for key error

                if log_file:
                    c.write_log(log_file, p.err, to_console=True)
                elif print_err_msg:
                    c.print_red(p.err)
                if clear_on_err and not keep_rows:
                    batch.clear()
                return False

            if ignore:
                self.cursor.execute('show warnings')
                p.warnings = self.cursor.fetchall()

            if not keep_rows:
                batch.clear()
        return True

    def get_key_from_1062(self, msg):
        if msg:
            ix = msg.find(m1 := "Duplicate entry '")
            jx = msg.find("' for key '")
            if ix >= 0 and jx > ix + len(m1):
                return msg[ix + len(m1):jx]
        return None

    def _make_sub_clause(self, key_fields: str, key: str, vals: list):
        kfl = key_fields.split(',')
        assert len(kfl) == 1, 'only support one primary key for now'
        vals.append(key)
        return f'`{kfl[0]}`=%s'

    def make_del_stmt(self, tbl_name, key_fields, keys):
        vals = []
        return f'DELETE FROM {tbl_name} WHERE ({" OR ".join(self._make_sub_clause(key_fields, k, vals) for k in keys)})' if keys else None, vals

    def update_batch(self, tbl_name: str, fields: list, batch: list, pkey_count=1):
        '''
        update multiple records using "update xxx set val_field=case when key_field=yyy then zzz end
        '''
        try:
            if isinstance(fields, str):
                fields = fields.split(',')
            key_field = fields[0]

            if batch:
                for val_ix, val_field in enumerate(fields[1:]):
                    vals = []
                    qch = "'"
                    # construct a update set case when end statement to update each value field at once
                    sql = f'UPDATE `{tbl_name}` SET `{val_field}`= CASE ' + \
                        ' '.join(f'WHEN {key_field}={v[0] if isinstance(v[0], (int, float)) else (qch + str(v[0]) + qch)} THEN {self._check_sql_value(v[val_ix + 1], vals)}' for v in batch) + \
                        ' END WHERE ' + c.make_clause(key_field, [v[0] for v in batch])
                    # c.print_blue(sql)
                    self.cursor.execute(sql, vals)
                batch.clear()
        except Exception as e:
            c.print_purple(f'  was not removed: {e!r}')


    def flexible_update_batch(self, tbl_name: str, fields: list, batch: list, k_field: str):
        '''
        update multiple records using "update xxx set val_field=case when key_field=yyy then zzz end
        '''
        if isinstance(fields, str):
            fields = fields.split(',')

        if batch:
            qch = "'"
            for val_field in fields:
                # construct a update set case when end statement to update each value field at once
                sql = f'UPDATE `{tbl_name}` SET `{val_field}`= CASE '
                field_batch = [v for v in batch if val_field in v and v[val_field]]
                if not field_batch:
                    continue
                sql += ''.join(f' WHEN `{k_field}`={v[k_field]} THEN {qch + v[val_field] + qch}' for v in field_batch)
                sql += ' END WHERE ' + c.make_clause(k_field, [v[k_field] for v in field_batch])
                c.print_blue(sql)
                self.cursor.execute(sql, [])

            batch.clear()

    def delete_batch_not_data(self, tbl_name: str, key_name: str, key_values):
        page_size = 1000
        for start in range(0, len(key_values), page_size):
            stmt = f'delete from {tbl_name} where ' + c.make_clause(key_name, key_values[start: start + page_size], use_not=True)
            self.cursor.execute(stmt)

    def delete_batch(self, tbl_name: str, key_name: str, key_values):
        page_size = 1000
        for start in range(0, len(key_values), page_size):
            stmt = f'delete from {tbl_name} where ' + c.make_clause(key_name, key_values[start: start + page_size])
            self.cursor.execute(stmt)

    def save_database_info(self, xls_filename=None, json_filename=None, want_dbs=None):
        '''
        read current MySQL database, writes all table info to an Excel or JSON file, will return as json,
        want_dbs is a list of comma delimeted db_names to search
        '''
        dbinfo = c.EntityThrow()

        db_clause = (' AND ' + c.make_clause('table_schema', want_dbs.lower().split(','))) if want_dbs else ''
        stmt = f"SELECT TABLE_SCHEMA,TABLE_NAME,TABLE_ROWS,TABLE_COMMENT FROM information_schema.TABLES WHERE TABLE_TYPE LIKE 'BASE_TABLE'" + db_clause

        self.cursor.execute(stmt)
        for db_name, table_name, num_rows, table_comment in self.cursor.fetchall():
            if db_name.lower() not in 'sys,mysql,information_schema,performance_schema'.split(','):
                tbl_name = f'{db_name}.{table_name}'
                dbinfo[tbl_name] = c.EntityThrow({'num_rows': num_rows, 'cols': c.Entity(), 'indices': c.Entity(), 'pkey': []})
                if table_comment:
                    dbinfo[tbl_name].comment = table_comment

        # get column definition
        stmt = "select table_schema,table_name,column_name,ordinal_position,column_default,data_type,character_maximum_length,numeric_precision,numeric_scale,is_nullable,column_comment from information_schema.columns order by table_schema,table_name,column_name,ordinal_position" + db_clause
        self.cursor.execute(stmt)
        for db_name, table_name, column_name, ordinal_position, default, data_type, length, precision, scale, is_nullable, comment in self.cursor.fetchall():
            tbl_name = f'{db_name}.{table_name}'
            if tbl_name in dbinfo:
                tbi = dbinfo[tbl_name]
                v = c.EntityThrow({'id': ordinal_position, 'type': data_type, 'nullable': is_nullable})
                for fn in 'default,length,precision,scale,comment'.split(','):
                    if locals()[fn]:
                        v[fn] = locals()[fn]
                tbi.cols[column_name] = v

        # get primary key and indices
        stmt = "select table_schema,table_name,column_name,index_name,collation from information_schema.statistics order by table_schema,table_name,index_name,seq_in_index" + db_clause
        self.cursor.execute(stmt)
        for db_name, table_name, column_name, index_name, collation in self.cursor.fetchall():
            tbl_name = f'{db_name}.{table_name}'
            if tbl_name in dbinfo:
                tbi = dbinfo[tbl_name]
                if index_name.lower() == 'primary':
                    dbinfo[tbl_name].pkey.append(column_name)
                else:
                    if index_name not in tbi.indices:
                        tbi.indices[index_name] = c.EntityThrow()
                    tbi.indices[index_name][column_name] = (collation == 'D')   # true if D (decending)

        self.save_db_info(dbinfo, xls_filename, json_filename)
        return dbinfo

    def get_cursor_desc(self):
        wp = c.EntityThrow()
        wp.cols = []
        for name, col_type, _, len, numeric_precision, numeric_scale, null_ok in self.cursor.description:
            wp.cols.append(c.Entity({'name': name, 'col_type': col_type, 'len': len, 'numeric_precision': numeric_precision, 'numeric_scale': numeric_scale, 'null_ok': null_ok}))
        wp.fields = [v.name.lower() for v in wp.cols]
        wp.date_fields = [v.name.lower() for v in wp.cols if v.col_type in (pymysql.constants.FIELD_TYPE.DATETIME, pymysql.constants.FIELD_TYPE.DATE)]
        wp.text_fields = [v.name.lower() for v in wp.cols if v.col_type in (pymysql.constants.FIELD_TYPE.CHAR, pymysql.constants.FIELD_TYPE.STRING, pymysql.constants.FIELD_TYPE.VARCHAR)]
        return wp

    def run_stmt(self, stmt, clr='yellow'):
        with c.time_it() as tm:
            self.cursor.execute(stmt)
        if len(stmt) < 60:
            c.print_color(f'完成 {stmt}. 耗时: {tm.time_used_str()}', clr)
        else:
            c.print_color(f'完成 {stmt[:25]} ... {stmt[-25:]}. 耗时: {tm.time_used_str()}', clr)

    def remove_fk_constraints(self, database):
        '''
        remove all foreign key constraints to speed up
        '''
        stmt = f"select table_name, constraint_name from information_schema.key_column_usage where table_schema='{database}' and referenced_table_name is not null"
        self.cursor.execute(stmt)
        rows = list(self.cursor)
        if rows:
            if not input(f'Found {len(rows):,} constraints. Press ENTER to remove them all: '):
                for tbl_name, fk_name in rows:
                    try:
                        self.cursor.execute(f'alter table `{database}`.`{tbl_name}` drop constraint `{fk_name}`')
                        c.print_yellow(f'   {fk_name} in {database}.{tbl_name} removed')
                    except Exception as e:
                        c.print_purple(f'   {fk_name} in {database}.{tbl_name} was not removed: {e!r}')
        else:
            c.print_green(f'No FK constraint was found in {database}')

    def optimize_tables(self, profile, database, show_large=500):
        '''
        optimize tables when free_space is > 100MB or more than 30% of free space, show_large: show information for table with used space > 500 MB
        '''
        cur = self.cursor

        stmt = f"select table_name, data_length, data_free from information_schema.tables where table_schema='{database}' and data_length != 0"
        cur.execute(stmt)
        tbls = sorted([(tbl_name, used, wasted) for tbl_name, used, wasted in cur], key=lambda r: r[1], reverse=True)
        total = sum([r[1] for r in tbls])
        free = sum([r[2] for r in tbls])
        c.print_white(f'\nConnection profile: {profile}\n{"="*18}\nFor database {database}, {len(tbls):,} tables found with {c.to_size_text(total)} of data and {c.to_size_text(free)} of wasted space.')
        if show_large:
            c.print_green(f'\t{"Table Name":<30}\tUsed\tWasted (%)')
            for tbl_name, used, wasted in tbls:
                if used >= 500 * 1024 * 1024:
                    c.print_green(f'\t{tbl_name:<30}\t{c.to_size_text(used):^5}\t{c.to_size_text(wasted):^5}  {wasted/(used+wasted):.0%}')

        to_op = [(tbl_name, used, wasted) for tbl_name, used, wasted in tbls if wasted * 100 / (used + wasted) >= 30 or wasted > 100 * 1024 * 1024]
        if to_op:
            c.print_yellow(f'Found {len(to_op):,} tables with wasted more than 30% or more than 100 MB that can be optimized.')
            c.print_cyan(f'\t{"Table Name":<30}\tUsed\tWasted (%)')
            for tbl_name, used, wasted in to_op:
                c.print_cyan(f'\t{tbl_name:<30}\t{c.to_size_text(used):^5}\t{c.to_size_text(wasted):^5}  {wasted/(used+wasted):.0%}')
            always = None
            if not input('    Press ENTER to start: '):
                for tbl_name, used, wasted in to_op:
                    a = always or input(f'   About to optimize {tbl_name}, used: {c.to_size_text(used)}, wasted: {c.to_size_text(wasted)} [{wasted/(used + wasted):.0%}].  Press ENTER to continue (a: do not ask again  s: skip):  ')
                    if a == 'a':
                        always = 'a'
                    if not a or a == 'a':
                        with c.time_it() as tm:
                            cur.execute(f'optimize table {database}.{tbl_name}')
                        msgs = cur.fetchall()
                        if msgs:
                            c.print_yellow('\n'.join(f'{r[2]}: {r[3]}' for r in msgs))
                        c.print_green(f'Completed optimizing {database}.{tbl_name} in {tm.time_used_str(want_hour=True)}')

                        # stmt = f"select data_length, data_free from information_schema.tables where table_schema='{database}' and table_name='{tbl_name}' and data_length != 0"
                        # cur.execute(stmt)
                        # row = cur.fetchall()[0]
        else:
            c.print_green('Found no table with wasted space > 100 MB')

    # read first 10,000 rows to select a page field

    def get_page_field(self, db_name, tbl_name, page_field=None, dbinfo=None, tbi=None, rows_to_read=10000):
        if not tbi:
            if not dbinfo:
                dbinfo = self.save_database_info(want_dbs=db_name)
            if not (tbi := dbinfo.get(db_name + '.' + tbl_name)):
                raise Exception(f'Table {tbl_name} is not found in given database')

        # select first existing field in 'page_field
        if page_field:
            if isinstance(page_field, str):
                page_field = page_field.split(',')
            for f in page_field:
                if f.lower() in tbi.cols:
                    page_field = f
                    break
            else:
                page_field = None

        if not page_field and len(tbi.pkey) == 1:
            page_field = tbi.pkey[0]

        if page_field:
            return page_field, 0, tbi

        # select page field from primary key first
        sel_fields = ','.join(tbi.pkey)
        if not sel_fields:
            sel_fields = '*'

        # select first 5000 rows and count distinct value of each column and use the largest one as the page field
        self.cursor.execute(f'select {sel_fields} from {tbl_name} limit {rows_to_read}')
        cts = None
        rc = 0
        for r in self.cursor:
            rc += 1
            if not cts:
                fields = [d[0] for d in self.cursor.description]
                cts = {f: set() for f in fields}
            if isinstance(r, (list, tuple)):  # unbuffered cursor
                for ix in range(len(r)):
                    cts[fields[ix]].add(r[ix])
            else:
                for f in fields:
                    cts[f.lower()].add(r[f])

        if not rc:
            return None, 0, tbi

        pfrc = 0
        for f in fields:
            cdv = len(cts[f])
            if cdv >= min(rc // 33, 300) and cdv <= rc * 9 // 10 and cdv > pfrc:    # don't use fields where unique values is the same as number of rows or outside of 3% to 90% range (eg. GUID)
                page_field, pfrc = f, cdv
        return page_field, pfrc * 100 // rc, tbi


@ contextlib.contextmanager
def use_mysql(prompt: str, db_config: c.Entity, unbuff_cur=True, read_timeout=None, commit=False, err: c.Entity = None, time_it=False, stmt=None, data=None, no_fk_check=False, want_helper=False):
    db = cur = None
    yielded = False
    start_time = time.time() if time_it else None
    try:
        if db_config.haserror:
            raise Exception(db_config.error)
        db = get_mysql_client(prompt, db_config, cursor_class=pymysql.cursors.SSCursor if unbuff_cur else None, read_timeout=read_timeout)
        if db:
            cur = db.cursor()

            if no_fk_check:
                cur.execute('SET FOREIGN_KEY_CHECKS=0')
        else:
            raise Exception(f'Failed to connect to {db_config.host} as {db_config.username} on {db_config.database} pass:{db_config.password}')

        if stmt:
            cur.execute(stmt)
            if isinstance(data, c.Entity):
                data.rows = cur.fetchall()

        yielded = True
        yield MySQLHelper(cur) if want_helper else cur

        if no_fk_check:
            cur.execute('SET FOREIGN_KEY_CHECKS=1')
    except Exception as e:
        commit = False  # don't commit on exception

        if isinstance(err, c.Entity) or isinstance(data, c.Entity):
            if not isinstance(err, c.Entity):
                err = data
            err.ex = e
            err.error = repr(e)
        else:
            c.show_ex(e)

        if not yielded:
            yield MySQLHelper(cur) if want_helper else cur
    finally:
        c.close_db_cur(db, cur, commit)
        if err is not None and time_it:
            err[time_it if isinstance(time_it, str) else 'time_used'] = time.time() - start_time


def run_statements(stmt_list, params: c.Entity, reporter=None, page_size=100, max_workers=10):
    if max_workers <= 0 or not stmt_list:
        return

    def _execute_stmts(stmts):
        ti = c.Entity()
        page_size = 1000    # run at most 1000 statements at once to avoid locking transaction for too long
        for start in range(0, len(stmts), page_size):
            with use_mysql(None, params.config.get_mysql_config(params.profile, database=params.database), err=ti, no_fk_check=True, commit=True) as cur:
                if not ti.hasex:
                    for sv in stmts[start: start + page_size]:
                        try:
                            if isinstance(sv, (tuple, list)):
                                if sv[1] is not None:
                                    cur.execute(sv[0], sv[1])
                                else:
                                    cur.execute(sv[0])
                            elif isinstance(sv, str):
                                cur.execute(sv)
                            else:
                                raise ValueError(f'invalid value type: {repr(sv)}, {type(sv)}')

                            ti.count += 1
                        except Exception as e:
                            if not ti.errors:
                                ti.errors = []
                            ti.errors.append((sv, e))
                    cur.fetchall()

            if ti.hasex:
                c.show_ex(ti.ex)
        return ti

    if reporter:
        reporter(c.KEY_START, None)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        if isinstance(stmt_list, dict):
            futures = [executor.submit(_execute_stmts, stmts=sl) for sl in stmt_list.values()]
        else:
            futures = [executor.submit(_execute_stmts, stmts=stmt_list[start:start + page_size]) for start in range(0, len(stmt_list), page_size)]

        for future in concurrent.futures.as_completed(futures):
            ti = future.result()
            if ti.errors:
                c.show_err(ti.errors)
                if reporter:
                    reporter(c.KEY_ERROR, ti)
            else:
                params.count += ti.count
                if reporter:
                    reporter(c.KEY_CHECK, params)

    if reporter:
        reporter(c.KEY_END, None)


def read_whole_table_by_page(cursor, tbl_name, page_field, get_fields, page_size, ids_to_read=None, reporter=None, where=None, page_tbl_name=None, orderby=None,
                             config=None, profile=None, host=None, db_name=None, num_threads=None):
    if reporter:
        reporter(0, 0, None)

    all_rows = []
    try:
        ids = ids_to_read
        if not ids:
            cursor.execute(f'select distinct {page_field} from {page_tbl_name if page_tbl_name else tbl_name}')
            ids = cursor.fetchall()
        if reporter:
            reporter(0, len(ids), None)

        threads = [c.Entity() for _ in range(num_threads)] if num_threads else []

        def _read_source(ti):
            err = c.Entity()
            with use_mysql(None, config.get_mysql_config(profile, database=db_name), err=err, stmt=ti.stmt) as cur:
                if not err.hasex:
                    ti.rows = cur.fetchall()

        def _get_rows():
            for ti in threads:
                if ti.hasthrd and not ti.thrd.is_alive():
                    if ti.haserr:
                        raise Exception(ti.err)
                    if ti.hasrows:
                        rows = ti.rows
                        del ti.rows
                        return rows
            return None

        count = 0
        while 1:
            if ids:
                ids_to_read = [p[page_field] for p in ids[:page_size]]
                if type(ids_to_read[0]) is str:
                    clause = f'{page_field} in (' + ','.join("'" + p + "'" for p in ids_to_read) + ')'
                else:
                    clause = f'{page_field} in (' + ','.join(str(p) for p in ids_to_read) + ')'
                count += len(ids_to_read)
                ids = ids[page_size:]

                if where:
                    clause = f'({where}) and {clause}'

                stmt = f"select {get_fields} from {tbl_name} where {clause}"
                if orderby:
                    stmt += ' order by ' + orderby

                if num_threads:
                    done, rows = False, None
                    while not done:
                        for ti in threads:
                            if not ti.hasthrd or not ti.thrd.is_alive():
                                if ti.haserr:
                                    raise Exception(ti.err)
                                if ti.hasrows:
                                    rows = ti.rows
                                    del ti.rows
                                ti.thrd = Thread(target=_read_source, args=(ti,))
                                ti.stmt = stmt
                                ti.thrd.start()
                                done = True
                                break

                        # wait for a thread to become available
                        while not done and not [ti for ti in threads if not ti.thrd.is_alive()]:
                            time.sleep(0.1)

                    # if any thread has done, take the rows
                    if not rows:
                        rows = _get_rows()

                    if not rows:
                        continue
                else:
                    cursor.execute(stmt)
                    rows = cursor.fetchall()
            else:
                # ids is empty
                if not num_threads:
                    break   # we are done in single thread case

                # check if any thread has done its work
                rows = _get_rows()
                if not rows:
                    # all threads are done?
                    if not [ti for ti in threads if ti.hasthrd and ti.thrd.is_alive()]:
                        break   # we are done when all threads are done
                    time.sleep(0.1)
                    continue

            if reporter:
                reporter(1, count, rows)

            all_rows += rows
    except Exception as e:
        c.show_ex(e)
        return None

    if reporter:
        reporter(2, 0, None)
    return all_rows


def count_one_table(config, db_name, tbl_name, page_field=None, dbinfo=None, tbi=None, jfn=None, msg_lock=None):
    '''
    read every field and every record from the given table by paging on key fields
    '''
    if msg_lock:
        msg_lock.acquire()
    c.print_white(f'{c.time_str()}{db_name}.{tbl_name}  count_one_table starts, {page_field=} {tbi.num_rows=:,}')
    if msg_lock:
        msg_lock.release()

    with use_mysql(None, config, err=(err := c.EntityThrow()), want_helper=True) as helper:
        if not err.hasex:
            page_field, tbi = helper.get_page_field(db_name, tbl_name, page_field)
    if err.hasex:
        raise err.ex

    cols = tbi.cols

    if isinstance(count_distinct_fields, str):
        count_distinct_fields = count_distinct_fields.spilt(',')
    if count_distinct_fields:
        count_distinct_fields = set(count_distinct_fields)

    if msg_lock:
        msg_lock.acquire()
    c.print_cyan(f'    {db_name}.{tbl_name}    page_field is set as {page_field}')
    if msg_lock:
        msg_lock.release()

    with use_mysql(None, config, err=(err := c.EntityThrow())) as cur:
        if not err.hasex:
            cur.execute(f'select {page_field} from {tbl_name} group by {page_field}')
            ids = [r[0] for r in cur if r is not None]  # we need to deal with NULL value differently

            if msg_lock:
                msg_lock.acquire()
            c.print_yellow(f'{c.time_str()}    {len(ids):,} distinct values found for {page_field} in {db_name}.{tbl_name}')
            if msg_lock:
                msg_lock.release()

            def _check(name, value):
                if value:
                    cols[name].value_count += 1
                    if not cols[name].min or value < cols[name].min:
                        tbi.cols[name].min = value
                    if not cols[name].max or value > cols[name].max:
                        tbi.cols[name].max = value

            for v in cols.values():
                v.min = v.max = None
                v.value_count = 0

            def _proc():
                for r in cur:
                    sp.num_rows += 1
                    if not sp.fields:
                        sp.fields = [d[0] for d in cur.description]

                    if isinstance(r, (list, tuple)):  # unbuffered cursor
                        for ix in range(len(r)):
                            _check(sp.fields[ix], r[ix])
                    else:
                        for f in sp.fields:
                            _check(f.lower(), r[f])

                if time.time() - sp.check_time > 300:
                    sp.check_time = time.time()

                    if msg_lock:
                        msg_lock.acquire()
                    c.print_grey(f'        {db_name}.{tbl_name}    {sp.num_rows:,} records read so far, {c.to_percent_text(sp.num_rows, tbi.num_rows)}...')
                    if msg_lock:
                        msg_lock.release()

            sp = c.EntityThrow({'num_rows': 0, 'check_time': time.time(), 'fields': None})
            for batch in c.page_list(ids, 1000):
                cur.execute(f'select * from {tbl_name} where ' + c.make_clause(page_field, batch, parameterized=True), batch)
                _proc()
            cur.execute(f'select * from {tbl_name} where {page_field} is NULL')
            _proc()

            if msg_lock:
                msg_lock.acquire()
            msg = f'{c.time_str()}{db_name}.{tbl_name}    {sp.num_rows:,} records were read.'
            if sp.num_rows != tbi.num_rows:
                msg += f' Difference of {sp.num_rows - tbi.num_rows:,} to saved number'
            c.print_green(msg)
            if msg_lock:
                msg_lock.release()

            tbi.num_rows = sp.num_rows

            if jfn and dbinfo:
                c.save_data_to_json(dbinfo, jfn)
    if err.hasex:
        raise err.ex
    return dbinfo


def count_tables(config, db_name, page_field=None, dbinfo=None, jfn=None):
    if not dbinfo:
        with use_mysql(None, config, err=(err := c.EntityThrow()), want_helper=True) as helper:
            if not err.hasex:
                dbinfo = helper.save_database_info(want_dbs=db_name)
        if err.hasex:
            raise err.ex

    msg_lock = Lock()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        concurrent.futures.wait([executor.submit(count_one_table, config=config, db_name=db_name, tbl_name=tbl_name.split('.')[1], page_field=page_field, tbi=tbi, msg_lock=msg_lock) for tbl_name, tbi in dbinfo.items()])

    if jfn:
        c.save_data_to_json(dbinfo, jfn)
    return dbinfo
