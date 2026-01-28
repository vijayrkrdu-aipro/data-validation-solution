"""
SQL Server database connector.
"""

import pyodbc
from typing import Any, Dict, Optional
from .base_connector import BaseConnector
from ..utils.exceptions import ConnectionException, QueryExecutionException
from ..utils.logger import logger


class SQLServerConnector(BaseConnector):
    """Connector for Microsoft SQL Server databases."""

    def get_dialect(self) -> str:
        """Return SQL Server dialect name."""
        return "sqlserver"

    def connect(self) -> None:
        """Establish connection to SQL Server."""
        try:
            if self.config.get('connection_string'):
                conn_str = self.config['connection_string']
            else:
                driver = self.config.get('driver', '{ODBC Driver 17 for SQL Server}')
                host = self.config['host']
                port = self.config.get('port', 1433)
                database = self.config['database']
                username = self.config.get('username', '')
                password = self.config.get('password', '')

                if username and password:
                    conn_str = (
                        f"Driver={driver};"
                        f"Server={host},{port};"
                        f"Database={database};"
                        f"UID={username};"
                        f"PWD={password};"
                        f"TrustServerCertificate=yes;"
                    )
                else:
                    # Use Windows authentication
                    conn_str = (
                        f"Driver={driver};"
                        f"Server={host},{port};"
                        f"Database={database};"
                        f"Trusted_Connection=yes;"
                    )

            self.connection = pyodbc.connect(conn_str, timeout=30)
            logger.info(f"Connected to SQL Server: {self.config.get('host', 'custom connection string')}")

        except pyodbc.Error as e:
            raise ConnectionException(f"Failed to connect to SQL Server: {str(e)}")

    def disconnect(self) -> None:
        """Close SQL Server connection."""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Disconnected from SQL Server")
            except Exception as e:
                logger.warning(f"Error during disconnect: {str(e)}")

    def execute_query(self, sql: str) -> Any:
        """
        Execute SQL query and return the result.

        Args:
            sql: SQL query to execute

        Returns:
            Single value result from the query
        """
        if not self.connection:
            raise ConnectionException("Not connected to database")

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            cursor.close()

            # Return the first column value, handling NULL
            return result[0] if result else None

        except pyodbc.Error as e:
            raise QueryExecutionException(f"Query execution failed: {str(e)}\nSQL: {sql}")

    def test_connection(self) -> bool:
        """Test if the connection is valid."""
        try:
            if not self.connection:
                return False
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False
