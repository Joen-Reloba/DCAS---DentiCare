import pymysql
from .database_model import DatabaseModel

class ServiceModel:
    def __init__(self):
        db = DatabaseModel()
        self.connection = db.connect()

    def add_service(self, serviceName, basePrice, isVATApplicable=True, vatRate=12.00):
        """Add a new service with VAT information"""
        cursor = self.connection.cursor()
        sql = """
            INSERT INTO services (ServiceName, BasePrice, IsVATApplicable, VATRate) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (serviceName, basePrice, isVATApplicable, vatRate))
        self.connection.commit()
        cursor.close()

    def getAllService(self):
        """Get all services with calculated final price"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
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
                END AS FinalPrice,
                CASE 
                    WHEN IsVATApplicable = TRUE THEN BasePrice * (VATRate/100)
                    ELSE 0
                END AS VATAmount,
                created_at,
                updated_at
            FROM services
            ORDER BY ServiceName
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        return results

    def getServiceByID(self, serviceID):
        """Get service details by ID with VAT calculations"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
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
                END AS FinalPrice,
                CASE 
                    WHEN IsVATApplicable = TRUE THEN BasePrice * (VATRate/100)
                    ELSE 0
                END AS VATAmount
            FROM services 
            WHERE ServiceID = %s
        """
        cursor.execute(sql, (serviceID,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def updateService(self, serviceID, serviceName, basePrice, isVATApplicable=True, vatRate=12.00):
        """Update service with VAT information"""
        cursor = self.connection.cursor()
        sql = """
            UPDATE services
            SET ServiceName = %s, 
                BasePrice = %s, 
                IsVATApplicable = %s,
                VATRate = %s
            WHERE ServiceID = %s
        """
        cursor.execute(sql, (serviceName, basePrice, isVATApplicable, vatRate, serviceID))
        self.connection.commit()
        cursor.close()

    def deleteService(self, serviceID):
        """Delete a service"""
        cursor = self.connection.cursor()
        try:
            sql = "DELETE FROM services WHERE ServiceID = %s"
            cursor.execute(sql, (serviceID,))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()