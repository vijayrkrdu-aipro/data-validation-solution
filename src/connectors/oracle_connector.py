"""
Oracle database connector.
"""

import cx_Oracle
from typing import Any, Dict, Optional
from .base_connector import BaseConnector
from ..utils.exceptions import ConnectionException, QueryExecutionException
from ..utils.logger import logger


class OracleConnector(BaseConnector):
    """Connector for Oracle databases."""

    def get_dialect(self) -> str:
        """Return Oracle dialect name."""
        return "oracle"

    def connect(self) -> None:
        """Establish connection to Oracle."""
        try:
            if self.config.get('connection_string'):
                conn_str = self.config['connection_string']
                self.connection = cx_Oracle.connect(conn_str)
            else:
                host = self.config['host']
                port = self.config.get('port', 1521)
                username = self.config['username']
                password = self.config['password']

                # Oracle can use either service_name or SID
                service_name = self.config.get('service_name')
                sid = self.config.get('sid')

                if service_name:
                    dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
                elif sid:
                    dsn = cx_Oracle.makedsn(host, port, sid=sid)
                else:
                    raise ConnectionException("Either 'service_name' or 'sid' must be provided for Oracle connection")

                self.connection = cx_Oracle.connect(
                    user=username,
                    password=password,
                    dsn=dsn
                )

            logger.info(f"Connected to Oracle: {self.config.get('host', 'custom connection string')}")

        except cx_Oracle.Error as e:
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

        except cx_Oracle.Error as e:
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
