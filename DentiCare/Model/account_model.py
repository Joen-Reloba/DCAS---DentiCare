import pymysql
from .database_model import DatabaseModel


class AccountModel:
    def __init__(self):
        db = DatabaseModel()
        self.connection = db.connect()

    def add_account(self, staffID, username, password):
        #add new account
        cursor = self.connection.cursor()

        sql = "INSERT INTO staffcred (staffID, username, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (staffID, username, password))
        self.connection.commit()
        cursor.close()

    def accountExists(self, staffID):
       #check if an account already exist for a staff ID
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        sql = "SELECT staffID FROM staffcred WHERE staffID = %s"
        cursor.execute(sql, (staffID,))
        result = cursor.fetchone()
        cursor.close()

        return result is not None #return True if exist

    def usernameExists(self, username):
        #check if username exist
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        sql = "SELECT username FROM staffcred WHERE username = %s"
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        cursor.close()

        return result is not None  #return True if exist

    def getAllAccounts(self):
        #get all accounts with info
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        sql = """
              SELECT a.StaffID, 
                     a.Username,
                     s.StaffFname, 
                     s.StaffMname, 
                     s.StaffLname, 
                     a.Username,
                     a.Password, 
                     s.Role,
                  a.created_at,
                  a.updated_at
              FROM staffcred a
                       JOIN staff s ON a.StaffID = s.StaffID 
              """
        cursor.execute(sql)
        results = cursor.fetchall() #return all rows
        cursor.close()

        return results

    def getAccountByStaffID(self, staffID):
        #get account by a staff ID
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        sql = """
              SELECT a.staffID, 
                     a.username,
                     s.StaffFname, 
                     s.StaffMname, 
                     s.StaffLname, 
                     a.Username,
                     a.Password, 
                     s.Role
              FROM staffcred a
                       JOIN staff s ON a.staffID = s.StaffID
              WHERE a.staffID = %s 
              """
        cursor.execute(sql, (staffID,))
        result = cursor.fetchone()
        cursor.close()

        return result

    def updateAccount(self, staffID, username, password):
        #update existing account
        cursor = self.connection.cursor()

        sql = """
              UPDATE staffcred
              SET username = %s, 
                  password = %s
              WHERE staffID = %s 
              """
        cursor.execute(sql, (username, password, staffID))
        self.connection.commit()
        cursor.close()

    def deleteAccount(self, staffID):
        #delete an account
        cursor = self.connection.cursor()

        try:
            sql = "DELETE FROM staffcred WHERE staffID = %s"
            cursor.execute(sql, (staffID,))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            self.connection.rollback()
            cursor.close()
            raise e