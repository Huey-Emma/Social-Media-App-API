from psycopg_pool import ConnectionPool

from src.config import conf

conninfo = f'dbname={conf.dbname} user={conf.db_user} password={conf.db_password} host={conf.db_host}'
pool = ConnectionPool(conninfo, open=False)
