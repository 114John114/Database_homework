import psycopg2
from psycopg2.pool import SimpleConnectionPool
from config import DB_CONFIG

class Database:
    _pool = None

    @classmethod
    def initialize(cls):
        if cls._pool is None:
            try:
                cls._pool = SimpleConnectionPool(1, 20, **DB_CONFIG)
            except Exception as e:
                print(f"数据库连接失败: {e}")
                raise

    @classmethod
    def get_connection(cls):
        if cls._pool is None:
            cls.initialize()
        return cls._pool.getconn()

    @classmethod
    def return_connection(cls, conn):
        if cls._pool is not None:
            cls._pool.putconn(conn)

    @classmethod
    def execute_query(cls, query, params=None):
        conn = cls.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if 'RETURNING' in query.upper() or query.strip().upper().startswith('SELECT'):
                    result = cur.fetchall()
                else:
                    result = None
                conn.commit()
                return result
        except Exception as e:
            conn.rollback()
            print(f"查询执行失败: {e}")
            raise
        finally:
            cls.return_connection(conn) 