"""
Snowflake database connector.
"""

import snowflake.connector
from typing import Any, Dict, Optional
from .base_connector import BaseConnector
from ..utils.exceptions import ConnectionException, QueryExecutionException
from ..utils.logger import logger


class SnowflakeConnector(BaseConnector):
    """Connector for Snowflake databases."""

    def get_dialect(self) -> str:
        """Return Snowflake dialect name."""
        return "snowflake"

    def connect(self) -> None:
        """Establish connection to Snowflake."""
        try:
            if self.config.get('connection_string'):
                raise NotImplementedError("Connection string parsing not implemented for Snowflake. Use individual parameters.")
            else:
                account = self.config['account']
                username = self.config['username']
                password = self.config['password']
                database = self.config.get('database')
                schema = self.config.get('schema')
                warehouse = self.config.get('warehouse')
                role = self.config.get('role')

                conn_params = {
                    'account': account,
                    'user': username,
                    'password': password,
                }

                # Add optional parameters if provided
                if database:
                    conn_params['database'] = database
                if schema:
                    conn_params['schema'] = schema
                if warehouse:
                    conn_params['warehouse'] = warehouse
                if role:
                    conn_params['role'] = role

                self.connection = snowflake.connector.connect(**conn_params)

            logger.info(f"Connected to Snowflake: {self.config.get('account')}")

        except snowflake.connector.Error as e:
            raise ConnectionException(f"Failed to connect to Snowflake: {str(e)}")

    def disconnect(self) -> None:
        """Close Snowflake connection."""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Disconnected from Snowflake")
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

        except snowflake.connector.Error as e:
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
