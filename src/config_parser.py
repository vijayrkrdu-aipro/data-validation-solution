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
    # Source details
    source_type: str  # Database type (SQLServer, Oracle, Netezza, etc.)
    source_host: str  # Host identifier for .env file lookup
    source_port: Optional[int]  # Optional - loaded from .env file if not provided
    source_database: str
    source_schema: Optional[str]
    source_table: str
    source_column: Optional[str]
    source_column_expression: Optional[str]  # Custom expression for source column
    source_filter: Optional[str]
    # Target details
    target_type: str  # Database type
    target_host: str  # Host identifier for .env file lookup
    target_port: Optional[int]  # Optional - loaded from .env file if not provided
    target_database: str
    target_schema: Optional[str]
    target_table: str
    target_column: Optional[str]
    target_column_expression: Optional[str]  # Custom expression for target column
    target_filter: Optional[str]
    # Validation rules
    rule_type: str
    threshold_type: str = 'EXACT'
    threshold_value: float = 0.0
    enabled: bool = True


class ConfigParser:
    """Parser for Excel validation configuration files with horizontal layout."""

    # Required column names in Excel (case-insensitive)
    REQUIRED_COLUMNS = [
        'Validation Name',
        'Validation_id',
        'Source Type',
        'Source Host Name',
        'Source Database Name',
        'Source Table Name',
        'Target Type',
        'Target Host Name',
        'Target Database Name',
        'Target Table Name',
        'Rule Type',
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
        Parse Excel file with horizontal layout (standard Excel format).

        Expected format:
        Row 1: Column headers (Validation Name, Source Type, etc.)
        Row 2+: Each row is one validation

        Returns:
            List of ValidationConfig objects

        Raises:
            ConfigurationException: If parsing fails or validation errors occur
        """
        try:
            # Read Excel file with first row as headers
            df = pd.read_excel(self.excel_path, sheet_name=self.sheet_name)
            logger.info(f"Loaded Excel file: {self.excel_path} (sheet: {self.sheet_name})")

            if df.empty:
                raise ConfigurationException("Excel file has no data rows")

            # Normalize column names (strip whitespace, but preserve case for lookup)
            df.columns = df.columns.str.strip()

            # Create case-insensitive column mapping
            col_map = {col.lower(): col for col in df.columns}

            # Verify required columns exist
            missing_cols = []
            for req_col in self.REQUIRED_COLUMNS:
                if req_col.lower() not in col_map:
                    missing_cols.append(req_col)

            if missing_cols:
                raise ConfigurationException(
                    f"Missing required columns in Excel: {', '.join(missing_cols)}"
                )

            # Parse each row as a validation
            validations = []
            for idx, row in df.iterrows():
                try:
                    validation = self._parse_row(row, col_map)
                    if validation:
                        validations.append(validation)
                except Exception as e:
                    logger.warning(f"Skipping row {idx + 2}: {str(e)}")  # +2 for header and 0-indexing

            logger.info(f"Parsed {len(validations)} validation configurations")
            return validations

        except FileNotFoundError:
            raise ConfigurationException(f"Excel file not found: {self.excel_path}")
        except Exception as e:
            raise ConfigurationException(f"Failed to parse Excel file: {str(e)}")

    def _parse_row(self, row: pd.Series, col_map: dict) -> Optional[ValidationConfig]:
        """
        Parse a single row into a ValidationConfig object.

        Args:
            row: DataFrame row
            col_map: Mapping of lowercase column names to actual column names

        Returns:
            ValidationConfig object or None if row should be skipped
        """
        def get_value(field_name: str, required: bool = False, default=None):
            """Get value for a field from the current row."""
            field_key = field_name.lower()
            if field_key not in col_map:
                if required:
                    raise ConfigurationException(f"Required column '{field_name}' not found in Excel")
                return default

            actual_col = col_map[field_key]
            value = row[actual_col]

            if pd.isna(value) or (isinstance(value, str) and not value.strip()):
                if required:
                    raise ConfigurationException(f"Required field '{field_name}' is empty")
                return default

            return value

        # Parse required fields
        validation_name = str(get_value('validation name', required=True)).strip()
        validation_id = str(get_value('validation_id', required=True)).strip()

        # Source details
        source_type = str(get_value('source type', required=True)).strip()
        source_host = str(get_value('source host name', required=True)).strip()
        source_database = str(get_value('source database name', required=True)).strip()
        source_schema = str(get_value('source schema name', default='')).strip() or None
        source_table = str(get_value('source table name', required=True)).strip()
        source_column = str(get_value('source column name', default='')).strip() or None
        source_column_expr = str(get_value('source column expression', default='')).strip() or None
        source_filter = str(get_value('source filter', default='')).strip() or None

        # Target details
        target_type = str(get_value('target type', required=True)).strip()
        target_host = str(get_value('target host name', required=True)).strip()
        target_database = str(get_value('target database name', required=True)).strip()
        target_schema = str(get_value('target schema name', default='')).strip() or None
        target_table = str(get_value('target table name', required=True)).strip()
        target_column = str(get_value('target column name', default='')).strip() or None
        target_column_expr = str(get_value('target column expression', default='')).strip() or None
        target_filter = str(get_value('target filter', default='')).strip() or None

        # Validation rules
        rule_type = str(get_value('rule type', required=True)).strip().upper()
        threshold_type = str(get_value('threshold type', default='EXACT')).strip().upper()
        threshold_value = float(get_value('threshold value', default=0.0))

        # Validate threshold type
        if threshold_type not in ['EXACT', 'PERCENTAGE', 'ABSOLUTE']:
            raise ConfigurationException(
                f"Invalid threshold_type '{threshold_type}' for {validation_id}. "
                f"Must be one of: EXACT, PERCENTAGE, ABSOLUTE"
            )

        # Ports are always None - loaded from .env files
        source_port = None
        target_port = None

        # Create and return ValidationConfig
        return ValidationConfig(
            validation_id=validation_id,
            validation_name=validation_name,
            source_type=source_type,
            source_host=source_host,
            source_port=source_port,
            source_database=source_database,
            source_schema=source_schema,
            source_table=source_table,
            source_column=source_column,
            source_column_expression=source_column_expr,
            source_filter=source_filter,
            target_type=target_type,
            target_host=target_host,
            target_port=target_port,
            target_database=target_database,
            target_schema=target_schema,
            target_table=target_table,
            target_column=target_column,
            target_column_expression=target_column_expr,
            target_filter=target_filter,
            rule_type=rule_type,
            threshold_type=threshold_type,
            threshold_value=threshold_value
        )
