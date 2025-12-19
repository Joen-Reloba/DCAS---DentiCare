import pymysql
from .database_model import DatabaseModel


class TransactionModel:
    """MODEL - Handles transaction and transaction details data operations with VAT"""

    def __init__(self):
        db = DatabaseModel()
        self.connection = db.connect()

    def createTransaction(self, dentist_id, staff_id, patient_id, total_amount,
                          transaction_date, service_details, notes=None):
        """Create new transaction with VAT information"""
        cursor = self.connection.cursor()

        try:
            # Start transaction
            self.connection.begin()

            # Insert into transactions table
            transaction_sql = """
                INSERT INTO transactions
                    (DentistID, StaffID, PatientID, TotalAmount, TransactionDate, Notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(transaction_sql,
                           (dentist_id, staff_id, patient_id, total_amount,
                            transaction_date, notes))

            # Get the auto-generated TransactionID
            transaction_id = cursor.lastrowid

            # Insert transaction details
            for service in service_details:
                service_id = service['service_id']
                quantity = service['quantity']

                # Get service details including VAT information
                price_sql = """
                    SELECT 
                        BasePrice,
                        IsVATApplicable,
                        VATRate,
                        CASE 
                            WHEN IsVATApplicable = TRUE THEN BasePrice * (1 + VATRate/100)
                            ELSE BasePrice
                        END AS FinalPrice,
                        CASE 
                            WHEN IsVATApplicable = TRUE THEN BasePrice * (VATRate/100)
                            ELSE 0
                        END AS VATAmount
                    FROM services 
                    WHERE ServiceID = %s
                """
                cursor.execute(price_sql, (service_id,))
                price_result = cursor.fetchone()

                if not price_result:
                    raise ValueError(f"Service ID {service_id} not found")

                base_price = price_result['BasePrice']
                final_price = price_result['FinalPrice']
                vat_amount = price_result['VATAmount']
                is_vat_applicable = price_result['IsVATApplicable']
                vat_rate = price_result['VATRate']

                # Insert transaction detail with VAT information
                detail_sql = """
                    INSERT INTO transactiondetails
                        (TransactionID, ServiceID, PriceAtTransaction, Quantity, 
                         BasePrice, VATAmount, VATRate, IsVATApplicable)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(detail_sql, (
                    transaction_id, service_id, final_price, quantity,
                    base_price, vat_amount, vat_rate, is_vat_applicable
                ))

            # Commit transaction
            self.connection.commit()
            return transaction_id

        except (pymysql.Error, ValueError) as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def getAllServices(self):
        """Get all available services with VAT calculations"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            sql = """
                SELECT 
                    ServiceID, 
                    ServiceName, 
                    BasePrice,
                    IsVATApplicable,
                    VATRate,
                    CASE 
                        WHEN IsVATApplicable = TRUE THEN BasePrice * (1 + VATRate/100)
                        ELSE BasePrice
                    END AS Price,
                    CASE 
                        WHEN IsVATApplicable = TRUE THEN BasePrice * (VATRate/100)
                        ELSE 0
                    END AS VATAmount
                FROM services 
                ORDER BY ServiceName
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            return results

        except pymysql.Error as e:
            raise e
        finally:
            cursor.close()

    def getAllDentists(self):
        """Get all dentists"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            sql = """
                SELECT d.StaffID,
                       CONCAT('Dr. ',s.StaffLname, ', ', s.StaffFname, ' ', IFNULL(s.StaffMname, '')) AS DentistName,
                       d.LicenseNum
                FROM dentist d
                         INNER JOIN staff s ON d.StaffID = s.StaffID
                ORDER BY s.StaffLname, s.StaffFname
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            return results

        except pymysql.Error as e:
            raise e
        finally:
            cursor.close()

    def searchPatient(self, search_value):
        """Search patient by name or ID"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            sql = """
                SELECT PatientID,
                       PatientFname,
                       PatientMname,
                       PatientLname,
                       Sex,
                       Birthday,
                       ContactNumber
                FROM patient
                WHERE PatientID = %s
                   OR CONCAT(PatientFname, ' ', IFNULL(PatientMname, ''), ' ', PatientLname) LIKE %s
            """
            cursor.execute(sql, (search_value, f'%{search_value}%'))
            results = cursor.fetchall()
            return results

        except pymysql.Error as e:
            raise e
        finally:
            cursor.close()

    def getAllTransactionRecords(self):
        """Get all transaction records with VAT breakdown - safe version"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # First, check if VAT columns exist
            cursor.execute("SHOW COLUMNS FROM transactiondetails LIKE 'BasePrice'")
            has_vat_columns = cursor.fetchone() is not None

            if has_vat_columns:
                # Query WITH VAT columns
                sql = """
                      SELECT t.TransactionID,
                             CONCAT(s.StaffLname, ', ', s.StaffFname, ' ', IFNULL(s.StaffMname, '')) AS ProcessedBy,
                             p.PatientID,
                             CONCAT(p.PatientLname, ', ', p.PatientFname, ' ',
                                    IFNULL(p.PatientMname, ''))                                      AS PatientName,
                             CONCAT('Dr. ', d_staff.StaffLname, ', ', d_staff.StaffFname, ' ',
                                    IFNULL(d_staff.StaffMname, ''))                                  AS DentistName,
                             svc.ServiceName                                                         AS Service,
                             td.BasePrice,
                             td.VATAmount,
                             td.PriceAtTransaction,
                             td.Quantity,
                             t.TotalAmount                                                           AS Total,
                             t.TransactionDate
                      FROM transactions t
                               INNER JOIN staff s ON t.StaffID = s.StaffID
                               INNER JOIN patient p ON t.PatientID = p.PatientID
                               INNER JOIN dentist d ON t.DentistID = d.StaffID
                               INNER JOIN staff d_staff ON d.StaffID = d_staff.StaffID
                               INNER JOIN transactiondetails td ON t.TransactionID = td.TransactionID
                               INNER JOIN services svc ON td.ServiceID = svc.ServiceID
                      ORDER BY t.TransactionDate DESC, t.TransactionID DESC \
                      """
            else:
                # Query WITHOUT VAT columns (fallback for unmigrated databases)
                print("WARNING: VAT columns not found in transactiondetails table")
                sql = """
                      SELECT t.TransactionID,
                             CONCAT(s.StaffLname, ', ', s.StaffFname, ' ', IFNULL(s.StaffMname, '')) AS ProcessedBy,
                             p.PatientID,
                             CONCAT(p.PatientLname, ', ', p.PatientFname, ' ',
                                    IFNULL(p.PatientMname, ''))                                      AS PatientName,
                             CONCAT('Dr. ', d_staff.StaffLname, ', ', d_staff.StaffFname, ' ',
                                    IFNULL(d_staff.StaffMname, ''))                                  AS DentistName,
                             svc.ServiceName                                                         AS Service,
                                                                                                    AS BasePrice,
                             0                                                                       AS VATAmount,
                             td.PriceAtTransaction,
                             td.Quantity,
                             t.TotalAmount                                                           AS Total,
                             t.TransactionDate
                      FROM transactions t
                               INNER JOIN staff s ON t.StaffID = s.StaffID
                               INNER JOIN patient p ON t.PatientID = p.PatientID
                               INNER JOIN dentist d ON t.DentistID = d.StaffID
                               INNER JOIN staff d_staff ON d.StaffID = d_staff.StaffID
                               INNER JOIN transactiondetails td ON t.TransactionID = td.TransactionID
                               INNER JOIN services svc ON td.ServiceID = svc.ServiceID
                      ORDER BY t.TransactionDate DESC, t.TransactionID DESC \
                      """

            cursor.execute(sql)
            result = cursor.fetchall()
            return result

        except pymysql.Error as e:
            print(f"ERROR in getAllTransactionRecords: {e}")
            raise e
        finally:
            cursor.close()

    def searchTransactionRecordsByPatientID(self, patient_id):
        """Search records by Patient ID with VAT breakdown"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            sql = """
                SELECT t.TransactionID,
                       CONCAT(s.StaffLname, ', ', s.StaffFname, ' ', IFNULL(s.StaffMname, '')) AS ProcessedBy,
                       p.PatientID,
                       CONCAT(p.PatientLname, ', ', p.PatientFname, ' ', 
                              IFNULL(p.PatientMname, '')) AS PatientName,
                       CONCAT('Dr. ',d_staff.StaffLname, ', ', d_staff.StaffFname, ' ', 
                              IFNULL(d_staff.StaffMname, '')) AS DentistName,
                       svc.ServiceName AS Service,
                       td.BasePrice,
                       td.VATAmount,
                       td.PriceAtTransaction,
                       td.Quantity,
                       t.TotalAmount AS Total,
                       t.TransactionDate
                FROM transactions t
                         INNER JOIN staff s ON t.StaffID = s.StaffID
                         INNER JOIN patient p ON t.PatientID = p.PatientID
                         INNER JOIN dentist d ON t.DentistID = d.StaffID
                         INNER JOIN staff d_staff ON d.StaffID = d_staff.StaffID
                         INNER JOIN transactiondetails td ON t.TransactionID = td.TransactionID
                         INNER JOIN services svc ON td.ServiceID = svc.ServiceID
                WHERE p.PatientID = %s
                ORDER BY t.TransactionDate DESC, t.TransactionID DESC
            """

            cursor.execute(sql, (patient_id,))
            result = cursor.fetchall()
            return result

        except pymysql.Error as e:
            raise e
        finally:
            cursor.close()

    def getTransactionRecordsForExport(self, patient_id):
        """Get transaction records INCLUDING notes and VAT for PDF export"""
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            query = """
                SELECT t.TransactionID,
                       CONCAT(s.StaffLname, ', ', s.StaffFname, ' ', IFNULL(s.StaffMname, '')) AS ProcessedBy,
                       t.PatientID,
                       CONCAT(p.PatientLname, ', ', p.PatientFname, ' ', IFNULL(p.PatientMname, '')) AS PatientName,
                       CONCAT(d.StaffLname, ', ', d.StaffFname, ' ', IFNULL(d.StaffMname, '')) AS DentistName,
                       srv.ServiceName AS Service,
                       td.BasePrice,
                       td.VATAmount,
                       td.VATRate,
                       td.IsVATApplicable,
                       td.PriceAtTransaction,
                       td.Quantity,
                       (td.PriceAtTransaction * td.Quantity) AS Total,
                       t.TransactionDate,
                       t.Notes
                FROM transactions t
                         JOIN staff s ON t.StaffID = s.StaffID
                         JOIN patient p ON t.PatientID = p.PatientID
                         JOIN staff d ON t.DentistID = d.StaffID
                         JOIN transactiondetails td ON t.TransactionID = td.TransactionID
                         JOIN services srv ON td.ServiceID = srv.ServiceID
                WHERE t.PatientID = %s
                ORDER BY t.TransactionDate DESC, t.TransactionID DESC
            """
            cursor.execute(query, (patient_id,))
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Failed to retrieve transaction records for export: {e}")

    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()