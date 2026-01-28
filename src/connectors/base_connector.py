"""
Base connector abstract class for database connections.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseConnector(ABC):
    """Abstract base class for all database connectors."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the connector with configuration.

        Args:
            config: Connection configuration dictionary
        """
        self.config = config
        self.connection = None

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the database."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    def execute_query(self, sql: str) -> Any:
        """
        Execute a SQL query and return the result.

        Args:
            sql: SQL query to execute

        Returns:
            Query result (typically a single value for aggregate queries)
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if the connection is valid.

        Returns:
            True if connection is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_dialect(self) -> str:
        """
        Get the SQL dialect name for this connector.

        Returns:
            Dialect name (e.g., 'sqlserver', 'oracle', 'netezza', 'snowflake')
        """
        pass

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
