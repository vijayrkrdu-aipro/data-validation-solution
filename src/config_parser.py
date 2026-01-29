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
    source_host: str
    source_port: int
    source_database: str
    source_schema: Optional[str]
    source_table: str
    source_column: Optional[str]
    source_column_expression: Optional[str]  # Custom expression for source column
    source_filter: Optional[str]
    # Target details
    target_type: str  # Database type
    target_host: str
    target_port: int
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
    """Parser for Excel validation configuration files with vertical layout."""

    # Expected row labels in Excel (case-insensitive)
    REQUIRED_ROWS = [
        'Validation Name',
        'Validation_id',
        'Source Type',
        'Source Host Name',
        'Source Port',
        'Source Database Name',
        'Source Schema Name',
        'Source Table Name',
        'Target Type',
        'Target Host Name',
        'Target Port',
        'Target Database Name',
        'Target Schema Name',
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
        Parse Excel file with vertical layout (rows are fields, columns are validations).

        Expected format:
        Column A: Field names (Validation Name, Source Type, etc.)
        Column B+: Validation data (each column is one validation)

        Returns:
            List of ValidationConfig objects

        Raises:
            ConfigurationException: If parsing fails or validation errors occur
        """
        try:
            # Read Excel file without treating first row as header
            df = pd.read_excel(self.excel_path, sheet_name=self.sheet_name, header=None)
            logger.info(f"Loaded Excel file: {self.excel_path} (sheet: {self.sheet_name})")

            if df.empty or df.shape[0] < 2 or df.shape[1] < 2:
                raise ConfigurationException("Excel file must have at least 2 rows and 2 columns")

            # First column contains field names
            field_names = df.iloc[:, 0].tolist()

            # Create a mapping of field names to row indices (case-insensitive)
            field_map = {}
            for idx, field in enumerate(field_names):
                if pd.notna(field):
                    field_map[str(field).strip().lower()] = idx

            # Parse each validation (each column starting from column 1)
            validations = []
            for col_idx in range(1, df.shape[1]):
                try:
                    validation = self._parse_column(df, col_idx, field_map)
                    if validation:
                        validations.append(validation)
                except Exception as e:
                    logger.warning(f"Skipping column {col_idx + 1}: {str(e)}")

            logger.info(f"Parsed {len(validations)} validation configurations")
            return validations

        except FileNotFoundError:
            raise ConfigurationException(f"Excel file not found: {self.excel_path}")
        except Exception as e:
            raise ConfigurationException(f"Failed to parse Excel file: {str(e)}")

    def _parse_column(self, df: pd.DataFrame, col_idx: int, field_map: dict) -> Optional[ValidationConfig]:
        """
        Parse a single column into a ValidationConfig object.

        Args:
            df: DataFrame containing all data
            col_idx: Column index to parse
            field_map: Mapping of field names (lowercase) to row indices

        Returns:
            ValidationConfig object or None if column should be skipped
        """
        def get_value(field_name: str, required: bool = False, default=None):
            """Get value for a field from the current column."""
            field_key = field_name.lower()
            if field_key not in field_map:
                if required:
                    raise ConfigurationException(f"Required field '{field_name}' not found in Excel")
                return default

            row_idx = field_map[field_key]
            value = df.iloc[row_idx, col_idx]

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
        source_port = int(get_value('source port', required=True))
        source_database = str(get_value('source database name', required=True)).strip()
        source_schema = str(get_value('source schema name', default='')).strip() or None
        source_table = str(get_value('source table name', required=True)).strip()
        source_column = str(get_value('source column name', default='')).strip() or None
        source_column_expr = str(get_value('source column expression', default='')).strip() or None
        source_filter = str(get_value('source filter', default='')).strip() or None

        # Target details
        target_type = str(get_value('target type', required=True)).strip()
        target_host = str(get_value('target host name', required=True)).strip()
        target_port = int(get_value('target port', required=True))
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

