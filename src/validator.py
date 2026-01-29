"""
Core validation engine for data validation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from .config_parser import ValidationConfig
from .query_builder import QueryBuilder
from .connectors.sqlserver_connector import SQLServerConnector
from .connectors.oracle_connector import OracleConnector
from .connectors.netezza_connector import NetezzaConnector
from .connectors.snowflake_connector import SnowflakeConnector
from .connectors.csv_connector import CSVConnector
from .utils.exceptions import ValidationException, ConfigurationException
from .utils.logger import logger


@dataclass
class ValidationResult:
    """Result of a validation execution."""
    validation_id: str
    validation_name: str
    status: str  # PASS, FAIL, ERROR
    source_value: Optional[Any]
    target_value: Optional[Any]
    difference: Optional[float]
    percentage_diff: Optional[float]
    source_details: str
    target_details: str
    rule_type: str
    threshold_type: str
    threshold_value: float
    execution_timestamp: str
    error_message: Optional[str] = None
    source_query: Optional[str] = None
    target_query: Optional[str] = None


class Validator:
    """Core validation engine."""

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

    def __init__(self):
        """Initialize validator."""
        pass

    def _create_connector(self, db_type: str, host: str, port: int, database: str, **kwargs):
        """
        Create a connector instance from connection details.

        Args:
            db_type: Database type (SQLServer, Oracle, etc.)
            host: Host name
            port: Port number
            database: Database name
            **kwargs: Additional connection parameters

        Returns:
            Connector instance
        """
        db_type_lower = db_type.lower().replace(' ', '')

        if db_type_lower not in self.CONNECTOR_MAP:
            raise ConfigurationException(
                f"Unknown database type '{db_type}'. "
                f"Supported types: {list(self.CONNECTOR_MAP.keys())}"
            )

        # Build connection config
        config = {
            'type': db_type_lower,
            'host': host,
            'port': port,
            'database': database,
            **kwargs
        }

        # Get connector class and create instance
        connector_class = self.CONNECTOR_MAP[db_type_lower]
        return connector_class(config)

    def validate(self, config: ValidationConfig) -> ValidationResult:
        """
        Execute a single validation.

        Args:
            config: ValidationConfig object with validation parameters

        Returns:
            ValidationResult with execution results
        """
        logger.info(f"Validating: {config.validation_id} - {config.validation_name}")

        # Initialize result
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            # Create connectors from config details
            source_connector = self._create_connector(
                db_type=config.source_type,
                host=config.source_host,
                port=config.source_port,
                database=config.source_database
            )

            target_connector = self._create_connector(
                db_type=config.target_type,
                host=config.target_host,
                port=config.target_port,
                database=config.target_database
            )

            # Build source details
            source_details = self._build_details(
                f"{config.source_type}@{config.source_host}:{config.source_port}",
                config.source_database,
                config.source_schema,
                config.source_table
            )

            # Build target details
            target_details = self._build_details(
                f"{config.target_type}@{config.target_host}:{config.target_port}",
                config.target_database,
                config.target_schema,
                config.target_table
            )

            # Determine which column/expression to use for source
            source_column_or_expr = config.source_column_expression or config.source_column

            # Determine which column/expression to use for target
            target_column_or_expr = config.target_column_expression or config.target_column

            # Execute source query
            with source_connector as conn:
                source_query = QueryBuilder.build_query(
                    dialect=conn.get_dialect(),
                    database=config.source_database,
                    schema=config.source_schema,
                    table=config.source_table,
                    column=source_column_or_expr,
                    rule_type=config.rule_type,
                    custom_expression=config.source_column_expression,
                    filter_clause=config.source_filter
                )
                logger.debug(f"Source query: {source_query}")
                source_value = conn.execute_query(source_query)

            # Execute target query
            with target_connector as conn:
                target_query = QueryBuilder.build_query(
                    dialect=conn.get_dialect(),
                    database=config.target_database,
                    schema=config.target_schema,
                    table=config.target_table,
                    column=target_column_or_expr,
                    rule_type=config.rule_type,
                    custom_expression=config.target_column_expression,
                    filter_clause=config.target_filter
                )
                logger.debug(f"Target query: {target_query}")
                target_value = conn.execute_query(target_query)

            # Convert to numeric for comparison (handle None)
            source_numeric = self._to_numeric(source_value)
            target_numeric = self._to_numeric(target_value)

            # Calculate difference
            difference = None
            percentage_diff = None
            if source_numeric is not None and target_numeric is not None:
                difference = target_numeric - source_numeric
                if source_numeric != 0:
                    percentage_diff = (difference / source_numeric) * 100

            # Determine pass/fail
            status = self._check_threshold(
                source_numeric,
                target_numeric,
                config.threshold_type,
                config.threshold_value
            )

            logger.info(
                f"Validation {config.validation_id}: {status} "
                f"(Source: {source_value}, Target: {target_value})"
            )

            return ValidationResult(
                validation_id=config.validation_id,
                validation_name=config.validation_name,
                status=status,
                source_value=source_value,
                target_value=target_value,
                difference=difference,
                percentage_diff=percentage_diff,
                source_details=source_details,
                target_details=target_details,
                rule_type=config.rule_type,
                threshold_type=config.threshold_type,
                threshold_value=config.threshold_value,
                execution_timestamp=timestamp,
                source_query=source_query,
                target_query=target_query
            )

        except Exception as e:
            logger.error(f"Validation {config.validation_id} failed with error: {str(e)}")

            return ValidationResult(
                validation_id=config.validation_id,
                validation_name=config.validation_name,
                status='ERROR',
                source_value=None,
                target_value=None,
                difference=None,
                percentage_diff=None,
                source_details=self._build_details(
                    config.source_connection,
                    config.source_database,
                    config.source_schema,
                    config.source_table
                ),
                target_details=self._build_details(
                    config.target_connection,
                    config.target_database,
                    config.target_schema,
                    config.target_table
                ),
                rule_type=config.rule_type,
                threshold_type=config.threshold_type,
                threshold_value=config.threshold_value,
                execution_timestamp=timestamp,
                error_message=str(e)
            )

    @staticmethod
    def _build_details(
        connection: str,
        database: Optional[str],
        schema: Optional[str],
        table: str
    ) -> str:
        """Build details string for source/target."""
        parts = [connection]
        if database:
            parts.append(database)
        if schema:
            parts.append(schema)
        parts.append(table)
        return ':'.join(parts)

    @staticmethod
    def _to_numeric(value: Any) -> Optional[float]:
        """Convert value to numeric, handling None and various types."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _check_threshold(
        source_value: Optional[float],
        target_value: Optional[float],
        threshold_type: str,
        threshold_value: float
    ) -> str:
        """
        Check if values pass the threshold criteria.

        Args:
            source_value: Source value
            target_value: Target value
            threshold_type: Type of threshold (EXACT, PERCENTAGE, ABSOLUTE)
            threshold_value: Threshold value

        Returns:
            'PASS' or 'FAIL'
        """
        # Handle NULL values
        if source_value is None or target_value is None:
            # If both are NULL, consider it a pass
            if source_value is None and target_value is None:
                return 'PASS'
            # If only one is NULL, it's a fail
            return 'FAIL'

        if threshold_type == 'EXACT':
            # Exact match (threshold_value is typically 0)
            return 'PASS' if abs(target_value - source_value) <= threshold_value else 'FAIL'

        elif threshold_type == 'PERCENTAGE':
            # Percentage difference
            if source_value == 0:
                # Can't calculate percentage if source is 0
                return 'PASS' if target_value == 0 else 'FAIL'

            percentage_diff = abs((target_value - source_value) / source_value)
            return 'PASS' if percentage_diff <= threshold_value else 'FAIL'

        elif threshold_type == 'ABSOLUTE':
            # Absolute difference
            difference = abs(target_value - source_value)
            return 'PASS' if difference <= threshold_value else 'FAIL'

        else:
            return 'FAIL'
