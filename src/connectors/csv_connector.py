"""
CSV file connector.
"""

import pandas as pd
from typing import Any, Dict, Optional
from .base_connector import BaseConnector
from ..utils.exceptions import ConnectionException, QueryExecutionException
from ..utils.logger import logger


class CSVConnector(BaseConnector):
    """Connector for CSV files using pandas for in-memory operations."""

    def get_dialect(self) -> str:
        """Return CSV dialect name."""
        return "csv"

    def connect(self) -> None:
        """Load CSV file into memory."""
        try:
            file_path = self.config.get('file_path') or self.config.get('path')
            if not file_path:
                raise ConnectionException("CSV file path not provided in configuration")

            # Load CSV with optional parameters
            encoding = self.config.get('encoding', 'utf-8')
            delimiter = self.config.get('delimiter', ',')

            self.connection = pd.read_csv(
                file_path,
                encoding=encoding,
                delimiter=delimiter
            )

            logger.info(f"Loaded CSV file: {file_path} ({len(self.connection)} rows)")

        except FileNotFoundError:
            raise ConnectionException(f"CSV file not found: {file_path}")
        except Exception as e:
            raise ConnectionException(f"Failed to load CSV file: {str(e)}")

    def disconnect(self) -> None:
        """Release the dataframe from memory."""
        if self.connection is not None:
            self.connection = None
            logger.info("Released CSV data from memory")

    def execute_query(self, sql: str) -> Any:
        """
        Execute a pandas operation to simulate SQL aggregation.

        Note: This is a simplified implementation. For CSV, the query_builder
        should generate pandas-compatible operations or use pandasql library.

        Args:
            sql: SQL-like query (or pandas operation description)

        Returns:
            Single value result from the aggregation
        """
        if self.connection is None:
            raise ConnectionException("CSV file not loaded")

        try:
            # For CSV, we expect the query builder to provide special handling
            # This is a placeholder that attempts to use pandasql if available
            try:
                import pandasql as ps
                result_df = ps.sqldf(sql, {"data": self.connection})
                result = result_df.iloc[0, 0] if not result_df.empty else None
                return result
            except ImportError:
                raise QueryExecutionException(
                    "pandasql library required for SQL queries on CSV files. "
                    "Install with: pip install pandasql"
                )

        except Exception as e:
            raise QueryExecutionException(f"Query execution failed on CSV: {str(e)}\nSQL: {sql}")

    def test_connection(self) -> bool:
        """Test if the CSV data is loaded."""
        return self.connection is not None and not self.connection.empty
