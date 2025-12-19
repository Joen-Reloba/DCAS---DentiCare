import pymysql
from .database_model import DatabaseModel


class PatientModel:
    """MODEL - Handles data and database operations only"""

    def __init__(self):
        db = DatabaseModel()
        self.connection = db.connect()

    def add_patient(self, fname, mname, lname, sex, bday, contact):
        """Add a new patient to the database (PatientID auto-increments)"""
        cursor = self.connection.cursor()

        try:
            # PatientID now auto-increments, so we don't include it
            sql = """
                  INSERT INTO patient
                  (PatientFname, PatientMname, PatientLname, Sex, Birthday, ContactNumber)
                  VALUES (%s, %s, %s, %s, %s, %s) 
                  """
            cursor.execute(sql, (fname, mname, lname, sex, bday, contact))
            self.connection.commit()

        except pymysql.Error as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def getAllPatient(self):
        """Get all patients from database"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            sql = "SELECT * FROM patient ORDER BY PatientID DESC"
            cursor.execute(sql)
            results = cursor.fetchall()
            return results

        except pymysql.Error as e:
            raise e
        finally:
            cursor.close()

    def getPatientByID(self, patientID):
        """Get a specific patient by ID"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            sql = "SELECT * FROM patient WHERE PatientID = %s"
            cursor.execute(sql, (int(patientID),))  # Ensure it's an integer
            result = cursor.fetchone()
            return result

        except pymysql.Error as e:
            raise e
        finally:
            cursor.close()

    def updatePatient(self, patientID, fname, mname, lname, sex, birthday, contact):
        """Update an existing patient"""
        cursor = self.connection.cursor()

        try:
            sql = """
                  UPDATE patient
                  SET PatientFname  = %s,
                      PatientMname  = %s,
                      PatientLname  = %s,
                      Sex           = %s,
                      Birthday      = %s,
                      ContactNumber = %s
                  WHERE PatientID = %s 
                  """
            cursor.execute(sql, (fname, mname, lname, sex, birthday, contact, int(patientID)))
            self.connection.commit()

        except pymysql.Error as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def deletePatient(self, patientID):
        """Delete patient - only if no existing transactions"""
        # First check for transactions
        if self.hasExistingTransactions(patientID):
            raise ValueError(
                "Cannot delete patient.\n\n"
                "This patient has existing transactions.\n\n"
                "Patients with transaction history cannot be deleted."
            )

        cursor = self.connection.cursor()

        try:
            sql = "DELETE FROM patient WHERE PatientID = %s"
            cursor.execute(sql, (int(patientID),))
            self.connection.commit()

        except pymysql.IntegrityError:
            self.connection.rollback()
            raise ValueError(
                "Cannot delete patient.\n\n"
                "This patient has existing records in the system."
            )
        except pymysql.Error as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def hasExistingTransactions(self, patientID):
        """Check if patient has any existing transactions"""
        cursor = self.connection.cursor()

        try:
            sql = """
                  SELECT 1
                  FROM transactions
                  WHERE PatientID = %s LIMIT 1 
                  """
            cursor.execute(sql, (int(patientID),))
            result = cursor.fetchone()
            return result is not None

        except pymysql.Error as e:
            raise e
        finally:
            cursor.close()

    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()

    def searchPatientByName(self, search_name):
        """Search for patients by name (supports first, middle, or last name)"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Clean up the search value
            search_name = search_name.strip()
            like_pattern = f"%{search_name}%"

            sql = """
                  SELECT * \
                  FROM patient
                  WHERE PatientFname LIKE %s
                     OR PatientMname LIKE %s
                     OR PatientLname LIKE %s
                     OR CONCAT(PatientFname, ' ', PatientLname) LIKE %s
                     OR CONCAT(PatientFname, ' ', IFNULL(PatientMname, ''), ' ', PatientLname) LIKE %s
                     OR CONCAT(PatientLname, ', ', PatientFname) LIKE %s
                     OR CONCAT(PatientLname, ', ', PatientFname, ' ', IFNULL(PatientMname, '')) LIKE %s
                  ORDER BY PatientID DESC
                  """

            cursor.execute(sql, (
                like_pattern,  # First name
                like_pattern,  # Middle name
                like_pattern,  # Last name
                like_pattern,  # "First Last"
                like_pattern,  # "First Middle Last"
                like_pattern,  # "Last, First"
                like_pattern  # "Last, First Middle"
            ))

            results = cursor.fetchall()
            return results

        except pymysql.Error as e:
            raise e
        finally:
            cursor.close()