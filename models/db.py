import mysql.connector


class Database:

    @staticmethod
    def get_connection():

        return mysql.connector.connect(
            host="10.24.10.72",
            user="granel_fel",
            password="FEL.2019",
            database="zetatanques",
            use_pure=True   # 🔥 ESTA ES LA CLAVE
        )