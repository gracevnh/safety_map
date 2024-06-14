import psycopg2
from config import Config

def init_db():
    conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS routes (
            id SERIAL PRIMARY KEY,
            start VARCHAR(128) NOT NULL,
            "end" VARCHAR(128) NOT NULL,
            safety_rating FLOAT
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

def main():
    init_db()

main()