
from .database_model import DatabaseModel #connection from db to system


class AuthenticationModel:
    def __init__(self):
        db = DatabaseModel()
        self.connection = db.connect()

    def authenticate(self, username, password):
       #collects data from db base on username
        try:
            cursor = self.connection.cursor()
            sql = """
                  SELECT sc.StaffID, s.Role
                  FROM StaffCred sc
                           JOIN Staff s ON sc.StaffID = s.StaffID
                  WHERE sc.Username = %s \
                    AND sc.Password = %s \
                  """
            cursor.execute(sql, (username, password))
            result = cursor.fetchone() #fetch the first row result
            cursor.close()
            return result
        except Exception as e:
            print(f"Database error during authentication: {e}")
            return None



