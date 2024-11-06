# -*- coding:UTF-8 -*-
#
# MyDBHelper
#
# Charles 吴波, 2022-09-16 copied from common_r
#
import os, sys, json
from shared.excel_workbook import ExcelWorkbook

sys.path.append('../')  # allow 'shared' to be imported below
import shared.common as c


class MyDBHelper:
    def __init__(self, cursor):
        self.cursor = cursor

    def commit(self):
        try:
            self.cursor.connection.commit()
        except Exception as e:
            return e
        return None

    def run_file(self, file_path, show_stmt=False, pbar=None):
        if not os.path.exists(file_path):
            return f'Error: {file_path} does not exists'

        try:
            data = open(file_path, 'rt', encoding='utf-8').readlines()
            DELIMITER, stmt = ';', ''
            for lineno, line in enumerate(data):
                if not line.strip() or line.startswith('--'):
                    continue

                if 'DELIMITER' in line:
                    DELIMITER = line.split()[1]
                    continue

                if (DELIMITER not in line):
                    stmt += line.replace(DELIMITER, ';').replace('\n', ' ')
                    continue

                if stmt:
                    stmt += line
                    stmt = stmt.strip()

                    if show_stmt:
                        print(stmt)
                        
                    self.cursor.execute(stmt)
                    if pbar:
                        pbar.update(pbar.currval + 1)
                    stmt = ''
                else:
                    line = line.strip()
                    if show_stmt:
                        print(line)
                    self.cursor.execute(line)
                    if pbar:
                        pbar.update(pbar.currval + 1)
            
            self.cursor.connection.commit()
        except Exception as e:
            c.show_ex(e)
            return f'Error on exception: {repr(e)}'

        return None


    def save_db_info(self, dbinfo, xls_filename, json_filename, sep_owner=False):
        if xls_filename:
            xls_book = ExcelWorkbook()
            xls_book.set_title('表定义')
            col_defs = [['数据库', 30], ['数据表', 30]] if sep_owner else [['数据表', 30]]
            xls_book.set_columns(col_defs + [['字段数量', 10], ['状态', 10], ['记录数量', 15], ['备注', 40], ['主键', 40], ['字段', 200]])

            def _parse_tbl_name():
                if sep_owner:
                    fs = list(tbl_name.split('.'))
                    if len(fs) == 1:
                        fs = ['', fs[0]]
                else:
                    fs = [tbl_name]
                return fs
                
            for tbl_name, dbi in dbinfo.items():
                xls_book.add_row(_parse_tbl_name() + [len(dbi.cols), dbi.status, dbi.num_rows, dbi.comments, ','.join(dbi.pkey) if dbi.pkey else None, ','.join(dbi.cols.keys())])
                
            xls_book.create_worksheet('字段定义')
            xls_book.set_columns(col_defs + [['字段名', 20], ['类型', 10], ['长度', 10], ['位数', 10], ['精度', 10], ['可空', 10], ['备注', 40]])
            
            for tbl_name, dbi in dbinfo.items():
                for col_name, info in dbi.cols.items():
                    xls_book.add_row(_parse_tbl_name() + [col_name] + [info[k] if k in info else None for k in 'type,length,scale,precision,nullable,comments'.split(',')])
            xls_book.save(xls_filename, False)

        if json_filename:
            with open(json_filename, 'wt', encoding='utf-8') as outf:
                json.dump(dbinfo, outf, indent=4, ensure_ascii=False)

