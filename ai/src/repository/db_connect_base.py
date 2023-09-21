from repository.base_db import get_db


class DbConnectBase:
    _conn = None

    def _execute(self, sql, args=None):
        """Below is a wrapper for the normal psycopg2 execute
        to fix the issue when psycopg2 unable to handle connection
        disconnected by the server by timeout or other unknown causes:
        - First check the current connection success.
        - If not close it and open new connection.
        - Then proceed to execute the query.
        """
        try:
            if self._conn is None:
                self._conn = get_db()

            with self._conn.cursor() as cursor:
                # Atempt to connect
                cursor.execute("SELECT 1 + 1;")

        except Exception as e:
            if self._conn is not None:
                self._conn.close()

            self._conn = get_db()
            print("Reconnected db", e)
            pass

        with self._conn.cursor() as cursor:
            cursor.execute(sql, args)
            if cursor is not None and cursor.pgresult_ptr is not None:
                return cursor.fetchall()
