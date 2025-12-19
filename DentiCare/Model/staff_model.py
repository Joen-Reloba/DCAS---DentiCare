import pymysql
from .database_model import DatabaseModel


class StaffModel:
    def __init__(self):
        db = DatabaseModel()
        self.connection = db.connect()

    def addStaff(self, fn, mn, ln, sex, bday, contact, barangay, city, province, zipcode, role, datehired,
                 licenseNum=None):
        """
        Add new staff member
        created_at and updated_at are automatically set by MySQL
        """
        cursor = self.connection.cursor()

        # Insert staff - timestamps are automatically set
        sql = (
            "INSERT INTO staff (StaffFname, StaffMname, StaffLname, Sex, Birthday, ContactNumber, "
            "Barangay, City, Province, Zipcode, Role, DateHired) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        cursor.execute(sql, (fn, mn, ln, sex, bday, contact, barangay, city, province, zipcode, role, datehired))

        # Get the generated StaffID
        new_staff_id = cursor.lastrowid

        # Insert into Dentist if needed
        if role.lower() == "dentist" and licenseNum:
            sql_dentist = "INSERT INTO dentist (StaffID, LicenseNum) VALUES (%s, %s)"
            cursor.execute(sql_dentist, (new_staff_id, licenseNum))

        self.connection.commit()
        cursor.close()

        return new_staff_id

    def getAllStaff(self):
        """
        Get all staff with timestamps included
        """
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        sql = """
            SELECT s.*, d.LicenseNum
            FROM staff s
            LEFT JOIN dentist d ON s.StaffID = d.StaffID 
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        return results

    def getStaffByID(self, staff_id):
        """
        Get staff by ID with timestamps
        """
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        sql = """
            SELECT s.*, d.LicenseNum
            FROM staff s
            LEFT JOIN dentist d ON s.StaffID = d.StaffID
            WHERE s.StaffID = %s 
        """
        cursor.execute(sql, (staff_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def updateStaff(self, staff_id, fn, mn, ln, sex, bday, contact, barangay, city, province, zipcode, role, datehired,
                    licenseNum):
        """
        Update staff member
        updated_at is automatically updated by MySQL
        """
        cursor = self.connection.cursor()

        sql_staff = """
            UPDATE staff
            SET StaffFname=%s, 
                StaffMname=%s, 
                StaffLname=%s, 
                Sex=%s, 
                Birthday=%s,
                ContactNumber=%s, 
                Barangay=%s, 
                City=%s, 
                Province=%s, 
                Zipcode=%s,
                Role=%s, 
                DateHired=%s
            WHERE StaffID = %s 
        """
        cursor.execute(sql_staff,
                       (fn, mn, ln, sex, bday, contact, barangay, city, province, zipcode,
                        role, datehired, staff_id))

        if role == "dentist":
            sql_dentist = """
                INSERT INTO dentist (StaffID, LicenseNum)
                VALUES (%s, %s) ON DUPLICATE KEY 
                UPDATE LicenseNum=%s 
            """
            cursor.execute(sql_dentist, (staff_id, licenseNum, licenseNum))
        else:
            sql_delete = "DELETE FROM dentist WHERE StaffID=%s"
            cursor.execute(sql_delete, (staff_id,))

        self.connection.commit()
        cursor.close()

    def deleteStaff(self, staff_id):
        cursor = self.connection.cursor()

        try:
            # First delete from dentist table if exists
            sql_delete_dentist = "DELETE FROM dentist WHERE StaffID=%s"
            cursor.execute(sql_delete_dentist, (staff_id,))

            # Then delete from staff table
            sql_delete_staff = "DELETE FROM staff WHERE StaffID=%s"
            cursor.execute(sql_delete_staff, (staff_id,))

            self.connection.commit()
            cursor.close()

        except Exception as e:
            self.connection.rollback()
            cursor.close()
            raise e