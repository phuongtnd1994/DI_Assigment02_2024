import psycopg2
from config import config
import traceback

class PGSQLConnect():
    def __init__(self) -> None:
        self._config = config
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(host=f"{self._config.get('PGSQL','HOST')}",
                port = self._config.get("PGSQL","PORT"),
                database= self._config.get("PGSQL","DATABSE"), 
                user = self._config.get("PGSQL","USERNAME"),
                password= self._config.get("PGSQL","PASSWORD"))
            return self.conn
        except:
            traceback.print_exc()
    