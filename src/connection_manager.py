"""
Connection manager for handling database connections from YAML configuration.
"""

import os
import re
import yaml
from typing import Dict, Any
from dotenv import load_dotenv

from .connectors.base_connector import BaseConnector
from .connectors.sqlserver_connector import SQLServerConnector
from .connectors.oracle_connector import OracleConnector
from .connectors.netezza_connector import NetezzaConnector
from .connectors.snowflake_connector import SnowflakeConnector
from .connectors.csv_connector import CSVConnector
from .utils.exceptions import ConfigurationException, ConnectionException
from .utils.logger import logger


class ConnectionManager:
    """Manages database connections from YAML configuration."""

    # Connector type mapping
    CONNECTOR_MAP = {
        'sqlserver': SQLServerConnector,
        'mssql': SQLServerConnector,
        'oracle': OracleConnector,
        'netezza': NetezzaConnector,
        'nz': NetezzaConnector,
        'snowflake': SnowflakeConnector,
        'csv': CSVConnector,
    }

    def __init__(self, config_path: str):
        """
        Initialize connection manager.

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.connections_config = {}
        self.active_connectors = {}

        # Load environment variables
        load_dotenv()

        # Load configuration
        self._load_config()

    def _load_config(self) -> None:
        """Load and parse YAML configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            if not config or 'connections' not in config:
                raise ConfigurationException("Invalid configuration: 'connections' key not found")

            self.connections_config = config['connections']
            logger.info(f"Loaded {len(self.connections_config)} connection configurations")

        except FileNotFoundError:
            raise ConfigurationException(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ConfigurationException(f"Failed to parse YAML configuration: {str(e)}")

    def _resolve_env_vars(self, value: Any) -> Any:
        """
        Resolve environment variable references in configuration values.

        Supports ${VAR_NAME} syntax.

        Args:
            value: Configuration value (string, dict, list, etc.)

        Returns:
            Value with environment variables resolved
        """
        if isinstance(value, str):
            # Pattern to match ${VAR_NAME}
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, value)

            for var_name in matches:
                env_value = os.environ.get(var_name, '')
                if not env_value:
                    logger.warning(f"Environment variable '{var_name}' not set, using empty string")
                value = value.replace(f'${{{var_name}}}', env_value)

            return value

        elif isinstance(value, dict):
            return {k: self._resolve_env_vars(v) for k, v in value.items()}

        elif isinstance(value, list):
            return [self._resolve_env_vars(item) for item in value]

        return value

    def get_connector(self, connection_name: str) -> BaseConnector:
        """
        Get a connector instance for the specified connection name.

        Args:
            connection_name: Name of the connection from YAML config

        Returns:
            Connector instance

        Raises:
            ConfigurationException: If connection name not found or type is invalid
        """
        if connection_name not in self.connections_config:
            raise ConfigurationException(
                f"Connection '{connection_name}' not found in configuration. "
                f"Available connections: {list(self.connections_config.keys())}"
            )

        # Get connection config and resolve environment variables
        conn_config = self._resolve_env_vars(self.connections_config[connection_name].copy())

        # Get connector type
        conn_type = conn_config.get('type', '').lower()
        if not conn_type:
            raise ConfigurationException(f"Connection type not specified for '{connection_name}'")

        # Get connector class
        connector_class = self.CONNECTOR_MAP.get(conn_type)
        if not connector_class:
            raise ConfigurationException(
                f"Unknown connection type '{conn_type}' for '{connection_name}'. "
                f"Supported types: {list(self.CONNECTOR_MAP.keys())}"
            )

        # Create and return connector instance
        try:
            connector = connector_class(conn_config)
            logger.info(f"Created {conn_type} connector for '{connection_name}'")
            return connector

        except Exception as e:
            raise ConnectionException(
                f"Failed to create connector for '{connection_name}': {str(e)}"
            )

    def test_connection(self, connection_name: str) -> bool:
        """
        Test a connection by name.

        Args:
            connection_name: Name of the connection to test

        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_connector(connection_name) as connector:
                return connector.test_connection()
        except Exception as e:
            logger.error(f"Connection test failed for '{connection_name}': {str(e)}")
            return False

    def test_all_connections(self) -> Dict[str, bool]:
        """
        Test all configured connections.

        Returns:
            Dictionary mapping connection names to test results
        """
        results = {}
        for conn_name in self.connections_config.keys():
            results[conn_name] = self.test_connection(conn_name)
        return results
