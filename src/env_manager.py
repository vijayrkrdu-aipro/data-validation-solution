"""
Environment manager for loading host-specific credentials.
"""

import os
from typing import Dict, Optional
from dotenv import dotenv_values
from .utils.exceptions import ConfigurationException
from .utils.logger import logger


class EnvManager:
    """Manages environment-specific credentials from .env files."""

    def __init__(self, env_dir: str = None):
        """
        Initialize environment manager.

        Args:
            env_dir: Directory containing .env files (default: project root)
        """
        self.env_dir = env_dir or os.getcwd()
        self.env_cache = {}

    def get_credentials(self, hostname: str) -> Dict[str, str]:
        """
        Get credentials for a specific hostname from .env file.

        Looks for .env.{hostname} file in the env_dir.

        Args:
            hostname: Hostname identifier (e.g., 'nz-prod-01', 'p8054')

        Returns:
            Dictionary with credentials (HOSTNAME, PORT, USERNAME, PASSWORD, etc.)

        Raises:
            ConfigurationException: If .env file not found or invalid
        """
        # Check cache first
        if hostname in self.env_cache:
            return self.env_cache[hostname]

        # Construct .env filename
        env_filename = f".env.{hostname}"
        env_path = os.path.join(self.env_dir, env_filename)

        # Check if file exists
        if not os.path.exists(env_path):
            raise ConfigurationException(
                f"Credentials file not found: {env_filename}\n"
                f"Expected location: {env_path}\n"
                f"Please create this file with connection credentials."
            )

        try:
            # Load environment variables from file
            env_vars = dotenv_values(env_path)

            if not env_vars:
                raise ConfigurationException(
                    f"Credentials file is empty: {env_filename}"
                )

            # Validate required fields
            required_fields = ['HOSTNAME', 'USERNAME', 'PASSWORD']
            missing_fields = [field for field in required_fields if field not in env_vars or not env_vars[field]]

            if missing_fields:
                raise ConfigurationException(
                    f"Missing required fields in {env_filename}: {', '.join(missing_fields)}\n"
                    f"Required fields: HOSTNAME, USERNAME, PASSWORD\n"
                    f"Optional fields: PORT, DATABASE, SCHEMA, SERVICE_NAME, SID, WAREHOUSE, ROLE, ACCOUNT"
                )

            # Cache the credentials
            self.env_cache[hostname] = env_vars
            logger.info(f"Loaded credentials for hostname: {hostname}")

            return env_vars

        except Exception as e:
            if isinstance(e, ConfigurationException):
                raise
            raise ConfigurationException(
                f"Failed to load credentials from {env_filename}: {str(e)}"
            )

    def clear_cache(self):
        """Clear the credentials cache."""
        self.env_cache = {}
