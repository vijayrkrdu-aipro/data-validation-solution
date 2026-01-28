"""
Configuration parser for Excel validation files.
"""

import pandas as pd
from dataclasses import dataclass
from typing import List, Optional
from .utils.exceptions import ConfigurationException
from .utils.logger import logger


@dataclass
class ValidationConfig:
    """Configuration for a single validation rule."""
    validation_id: str
    validation_name: str
    source_connection: str
    source_database: Optional[str]
    source_schema: Optional[str]
    source_table: str
    source_column: Optional[str]
    source_filter: Optional[str]
    target_connection: str
    target_database: Optional[str]
    target_schema: Optional[str]
    target_table: str
    target_column: Optional[str]
    target_filter: Optional[str]
    rule_type: str
    custom_expression: Optional[str]
    threshold_type: str
    threshold_value: float
    enabled: bool = True


class ConfigParser:
    """Parser for Excel validation configuration files."""

    REQUIRED_COLUMNS = [
        'validation_id',
        'validation_name',
        'source_connection',
        'source_table',
        'target_connection',
        'target_table',
        'rule_type',
        'threshold_type',
        'threshold_value',
    ]

    OPTIONAL_COLUMNS = [
        'source_database',
        'source_schema',
        'source_column',
        'source_filter',
        'target_database',
        'target_schema',
        'target_column',
        'target_filter',
        'custom_expression',
        'enabled',
    ]

    def __init__(self, excel_path: str, sheet_name: str = 'Validations'):
        """
        Initialize config parser.

        Args:
            excel_path: Path to Excel configuration file
            sheet_name: Name of the sheet containing validations (default: 'Validations')
        """
        self.excel_path = excel_path
        self.sheet_name = sheet_name

    def parse(self) -> List[ValidationConfig]:
        """
        Parse Excel file and return list of validation configurations.

        Returns:
            List of ValidationConfig objects

        Raises:
            ConfigurationException: If parsing fails or validation errors occur
        """
        try:
            # Read Excel file
            df = pd.read_excel(self.excel_path, sheet_name=self.sheet_name)
            logger.info(f"Loaded Excel file: {self.excel_path} (sheet: {self.sheet_name})")

            # Validate required columns
            missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
            if missing_cols:
                raise ConfigurationException(
                    f"Missing required columns in Excel file: {missing_cols}"
                )

            # Parse each row
            validations = []
            for idx, row in df.iterrows():
                try:
                    validation = self._parse_row(row, idx)
                    if validation:
                        validations.append(validation)
                except Exception as e:
                    logger.warning(f"Skipping row {idx + 2}: {str(e)}")

            logger.info(f"Parsed {len(validations)} validation configurations")
            return validations

        except FileNotFoundError:
            raise ConfigurationException(f"Excel file not found: {self.excel_path}")
        except Exception as e:
            raise ConfigurationException(f"Failed to parse Excel file: {str(e)}")

    def _parse_row(self, row: pd.Series, row_idx: int) -> Optional[ValidationConfig]:
        """
        Parse a single row into a ValidationConfig object.

        Args:
            row: Pandas Series representing a row
            row_idx: Row index for error reporting

        Returns:
            ValidationConfig object or None if row should be skipped
        """
        # Check if enabled (default to True if not specified)
        enabled = self._get_bool_value(row, 'enabled', default=True)
        if not enabled:
            logger.info(f"Skipping disabled validation: {row.get('validation_id', f'row {row_idx + 2}')}")
            return None

        # Parse required fields
        validation_id = self._get_string_value(row, 'validation_id', required=True)
        validation_name = self._get_string_value(row, 'validation_name', required=True)
        source_connection = self._get_string_value(row, 'source_connection', required=True)
        source_table = self._get_string_value(row, 'source_table', required=True)
        target_connection = self._get_string_value(row, 'target_connection', required=True)
        target_table = self._get_string_value(row, 'target_table', required=True)
        rule_type = self._get_string_value(row, 'rule_type', required=True).upper()
        threshold_type = self._get_string_value(row, 'threshold_type', required=True).upper()
        threshold_value = self._get_float_value(row, 'threshold_value', required=True)

        # Parse optional fields
        source_database = self._get_string_value(row, 'source_database')
        source_schema = self._get_string_value(row, 'source_schema')
        source_column = self._get_string_value(row, 'source_column')
        source_filter = self._get_string_value(row, 'source_filter')
        target_database = self._get_string_value(row, 'target_database')
        target_schema = self._get_string_value(row, 'target_schema')
        target_column = self._get_string_value(row, 'target_column')
        target_filter = self._get_string_value(row, 'target_filter')
        custom_expression = self._get_string_value(row, 'custom_expression')

        # Validate threshold type
        if threshold_type not in ['EXACT', 'PERCENTAGE', 'ABSOLUTE']:
            raise ConfigurationException(
                f"Invalid threshold_type '{threshold_type}' for {validation_id}. "
                f"Must be one of: EXACT, PERCENTAGE, ABSOLUTE"
            )

        # Create and return ValidationConfig
        return ValidationConfig(
            validation_id=validation_id,
            validation_name=validation_name,
            source_connection=source_connection,
            source_database=source_database,
            source_schema=source_schema,
            source_table=source_table,
            source_column=source_column,
            source_filter=source_filter,
            target_connection=target_connection,
            target_database=target_database,
            target_schema=target_schema,
            target_table=target_table,
            target_column=target_column,
            target_filter=target_filter,
            rule_type=rule_type,
            custom_expression=custom_expression,
            threshold_type=threshold_type,
            threshold_value=threshold_value,
            enabled=enabled
        )

    @staticmethod
    def _get_string_value(row: pd.Series, column: str, required: bool = False) -> Optional[str]:
        """Get string value from row, handling NaN and empty strings."""
        if column not in row or pd.isna(row[column]):
            if required:
                raise ConfigurationException(f"Required column '{column}' is missing or empty")
            return None

        value = str(row[column]).strip()
        if not value and required:
            raise ConfigurationException(f"Required column '{column}' is empty")

        return value if value else None

    @staticmethod
    def _get_float_value(row: pd.Series, column: str, required: bool = False) -> Optional[float]:
        """Get float value from row, handling NaN."""
        if column not in row or pd.isna(row[column]):
            if required:
                raise ConfigurationException(f"Required column '{column}' is missing or empty")
            return None

        try:
            return float(row[column])
        except (ValueError, TypeError):
            if required:
                raise ConfigurationException(f"Column '{column}' must be a number")
            return None

    @staticmethod
    def _get_bool_value(row: pd.Series, column: str, default: bool = False) -> bool:
        """Get boolean value from row, handling various representations."""
        if column not in row or pd.isna(row[column]):
            return default

        value = row[column]

        # Handle boolean type
        if isinstance(value, bool):
            return value

        # Handle string representations
        if isinstance(value, str):
            value_lower = value.strip().lower()
            if value_lower in ['true', 'yes', '1', 't', 'y']:
                return True
            elif value_lower in ['false', 'no', '0', 'f', 'n']:
                return False

        # Handle numeric representations
        try:
            return bool(int(value))
        except (ValueError, TypeError):
            return default
