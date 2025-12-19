from .database_model import DatabaseModel
import pandas as pd

class DashboardModel:
    def __init__(self):
        db = DatabaseModel()
        self.connection = db.connect()

    def getTotalPatients(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) AS TotalPatients FROM patient;")
        result = cursor.fetchone()
        cursor.close()
        return result["TotalPatients"]

    def getTotalStaff(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) AS TotalStaff FROM staff;")
        result = cursor.fetchone()
        cursor.close()
        return result["TotalStaff"]

    def getTotalRevenue(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT SUM(TotalAmount) AS TotalRevenue FROM transactions;")
        result = cursor.fetchone()
        cursor.close()
        return result["TotalRevenue"] if result["TotalRevenue"] is not None else 0

    def getMonthlySalesData(self):
        """Get monthly sales data for the current year"""
        cursor = self.connection.cursor()
        # FIXED: Removed ALL spaces between function names and parentheses
        query = """
                SELECT
                MONTH(TransactionDate) AS Month, YEAR(TransactionDate) AS Year, SUM(TotalAmount) AS TotalSales
                FROM transactions
                WHERE YEAR (TransactionDate) = YEAR(CURDATE())
                GROUP BY YEAR (TransactionDate), MONTH(TransactionDate)
                ORDER BY Month; 
                """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        # Convert to pandas DataFrame
        df = pd.DataFrame(results)

        if df.empty:
            # Return empty dataframe with proper columns if no data
            return pd.DataFrame(columns=['Month', 'Year', 'TotalSales'])

        # IMPORTANT: Convert data types to numeric
        df['Month'] = pd.to_numeric(df['Month'], errors='coerce')
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['TotalSales'] = pd.to_numeric(df['TotalSales'], errors='coerce')

        # Fill any NaN values with 0
        df = df.fillna(0)

        return df
