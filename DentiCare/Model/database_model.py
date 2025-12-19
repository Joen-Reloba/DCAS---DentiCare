
import pymysql

class DatabaseModel:
    def __init__(self):
        self.connection = None

    def connect(self):
        if self.connection is None:
            self.connection = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="dentalclinic",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit = True
            )
            print('connected to database')
        return self.connection



