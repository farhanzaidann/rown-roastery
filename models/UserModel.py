from models.db import get_db_connection

class UserModel:
    def __init__(self):
        pass

    def find_by_username(self, username):
        """
        Mencari pengguna berdasarkan username dari database.
        Nama tabel diasumsikan 'tabel_user' sesuai permintaan.
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM `tabel_user` WHERE username = %s"
                cursor.execute(sql, (username,))
                return cursor.fetchone()
        finally:
            connection.close()