"""
Oracle database connector using pyodbc.
"""

import pyodbc
from typing import Any, Dict, Optional
from .base_connector import BaseConnector
from ..utils.exceptions import ConnectionException, QueryExecutionException
from ..utils.logger import logger


class OracleConnector(BaseConnector):
    """Connector for Oracle databases using pyodbc."""

    def get_dialect(self) -> str:
        """Return Oracle dialect name."""
        return "oracle"

    def connect(self) -> None:
        """Establish connection to Oracle using pyodbc."""
        try:
            if self.config.get('connection_string'):
                conn_str = self.config['connection_string']
            else:
                host = self.config['host']
                port = self.config.get('port', 1521)
                username = self.config['username']
                password = self.config['password']

                # Oracle ODBC driver name
                driver = self.config.get('driver', '{Oracle in OraClient12Home1}')

                # Oracle can use either service_name or SID
                service_name = self.config.get('service_name')
                sid = self.config.get('sid')

                if service_name:
                    # Use SERVICE_NAME for connection
                    conn_str = (
                        f"Driver={driver};"
                        f"DBQ={host}:{port}/{service_name};"
                        f"UID={username};"
                        f"PWD={password};"
                    )
                elif sid:
                    # Use SID for connection
                    conn_str = (
                        f"Driver={driver};"
                        f"DBQ={host}:{port}/{sid};"
                        f"UID={username};"
                        f"PWD={password};"
                    )
                else:
                    raise ConnectionException("Either 'service_name' or 'sid' must be provided for Oracle connection")

            self.connection = pyodbc.connect(conn_str, timeout=30)
            logger.info(f"Connected to Oracle: {self.config.get('host', 'custom connection string')}")

        except pyodbc.Error as e:
            raise ConnectionException(f"Failed to connect to Oracle: {str(e)}")

    def disconnect(self) -> None:
        """Close Oracle connection."""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Disconnected from Oracle")
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
            cursor.execute("SELECT 1 FROM DUAL")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False
