"""
Netezza database connector.
"""

import nzpy
from typing import Any, Dict, Optional
from .base_connector import BaseConnector
from ..utils.exceptions import ConnectionException, QueryExecutionException
from ..utils.logger import logger


class NetezzaConnector(BaseConnector):
    """Connector for Netezza databases."""

    def get_dialect(self) -> str:
        """Return Netezza dialect name."""
        return "netezza"

    def connect(self) -> None:
        """Establish connection to Netezza."""
        try:
            if self.config.get('connection_string'):
                # Parse connection string if provided
                raise NotImplementedError("Connection string parsing not implemented for Netezza. Use individual parameters.")
            else:
                host = self.config['host']
                port = self.config.get('port', 5480)
                database = self.config['database']
                username = self.config['username']
                password = self.config['password']

                self.connection = nzpy.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=username,
                    password=password,
                    securityLevel=self.config.get('securityLevel', 0),
                    logLevel=self.config.get('logLevel', 0)
                )

            logger.info(f"Connected to Netezza: {self.config.get('host')}")

        except Exception as e:
            raise ConnectionException(f"Failed to connect to Netezza: {str(e)}")

    def disconnect(self) -> None:
        """Close Netezza connection."""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Disconnected from Netezza")
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

        except Exception as e:
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
