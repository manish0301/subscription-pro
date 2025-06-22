import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

class Database:
    def __init__(self):
        self.connection_string = os.environ.get('DATABASE_URL', 'postgresql://localhost/subscriptionpro')
    
    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(self.connection_string)
        try:
            yield conn
        finally:
            conn.close()
    
    @contextmanager
    def get_cursor(self):
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor, conn
            finally:
                cursor.close()

db = Database()