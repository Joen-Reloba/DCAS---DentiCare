import pymysql
from .database_model import DatabaseModel


class ReportModel:
    """MODEL - Handles report-related data operations"""

    def __init__(self):
        db = DatabaseModel()
        self.connection = db.connect()

    def getTransactionsByMonthYear(self, month, year):
        """Get all transactions for a specific month and year with details"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            sql = """
                  SELECT t.TransactionID,
                         CONCAT(s.StaffLname, ', ', s.StaffFname, ' ', IFNULL(s.StaffMname, '')) AS ProcessedBy,
                         CONCAT(p.PatientLname, ', ', p.PatientFname, ' ', IFNULL(p.PatientMname, '')) AS PatientName,
                         CONCAT(d_staff.StaffLname, ', ', d_staff.StaffFname, ' ', IFNULL(d_staff.StaffMname, '')) AS DentistName,
                         svc.ServiceName AS Service,
                         td.Quantity,
                         t.TotalAmount,
                         t.TransactionDate
                  FROM transactions t
                           INNER JOIN staff s ON t.StaffID = s.StaffID
                           INNER JOIN patient p ON t.PatientID = p.PatientID
                           INNER JOIN dentist d ON t.DentistID = d.StaffID
                           INNER JOIN staff d_staff ON d.StaffID = d_staff.StaffID
                           INNER JOIN transactiondetails td ON t.TransactionID = td.TransactionID
                           INNER JOIN services svc ON td.ServiceID = svc.ServiceID
                  WHERE MONTH(t.TransactionDate) = %s 
                    AND YEAR(t.TransactionDate) = %s
                  ORDER BY t.TransactionDate DESC, t.TransactionID DESC
                  """

            cursor.execute(sql, (month, year))
            results = cursor.fetchall()
            return results

        except pymysql.Error as e:
            raise e
        finally:
            cursor.close()

    def getRevenueByServiceForMonth(self, month, year):
        """Get revenue breakdown by service for a specific month/year"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            sql = """
                  SELECT svc.ServiceName,
                         SUM(td.Quantity) AS TotalQuantity,
                         SUM(td.PriceAtTransaction * td.Quantity) AS TotalRevenue
                  FROM transactions t
                           INNER JOIN transactiondetails td ON t.TransactionID = td.TransactionID
                           INNER JOIN services svc ON td.ServiceID = svc.ServiceID
                  WHERE MONTH(t.TransactionDate) = %s 
                    AND YEAR(t.TransactionDate) = %s
                  GROUP BY svc.ServiceID, svc.ServiceName
                  ORDER BY TotalRevenue DESC
                  """

            cursor.execute(sql, (month, year))
            results = cursor.fetchall()
            return results

        except pymysql.Error as e:
            raise e
        finally:
            cursor.close()

    def getTotalRevenueForMonth(self, month, year):
        """Get total revenue for a specific month/year"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            sql = """
                  SELECT SUM(t.TotalAmount) AS TotalRevenue,
                         COUNT(DISTINCT t.TransactionID) AS TransactionCount
                  FROM transactions t
                  WHERE MONTH(t.TransactionDate) = %s 
                    AND YEAR(t.TransactionDate) = %s
                  """

            cursor.execute(sql, (month, year))
            result = cursor.fetchone()
            return result

        except pymysql.Error as e:
            raise e
        finally:
            cursor.close()

    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()