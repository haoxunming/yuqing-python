import sys
sys.path += ['./', '../']  # allow 'shared' to be imported below
import shared.common as c
import shared.config as config
from shared.mysql_helper import use_mysql

def collection_mysql():
    with use_mysql(None, config.get_mysql_config(profile='wesite_collection', database='public_sentiment'), unbuff_cur=False, err=(err := c.EntityThrow())) as cur:
        if not err.hasex:
            stmt = f'select * from t_programme'
            cur.execute(stmt)
            for r in cur:
                r = c.EntityThrow(r)
                print(r)

if __name__ == '__main__':
    collection_mysql()


