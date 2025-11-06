import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_database():
    # 连接到默认的postgres数据库
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='postgres',
        host='localhost',
        port='5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # 创建数据库
    try:
        cur.execute('CREATE DATABASE lewis')
        print("Database created successfully")
    except psycopg2.Error as e:
        print(f"Database already exists or error: {e}")
    
    cur.close()
    conn.close()

    # 连接到新创建的数据库并初始化pgvector扩展
    conn = psycopg2.connect(
        dbname='lewis',
        user='postgres',
        password='postgres',
        host='localhost',
        port='5432'
    )
    cur = conn.cursor()
    
    try:
        cur.execute('CREATE EXTENSION IF NOT EXISTS vector')
        print("Vector extension created successfully")
    except psycopg2.Error as e:
        print(f"Error creating vector extension: {e}")
    
    cur.close()
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()