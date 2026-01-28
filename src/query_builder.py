"""
Query builder for generating SQL aggregate queries.
"""

from typing import Optional
from .utils.exceptions import InvalidRuleTypeException


class QueryBuilder:
    """Builds SQL queries for aggregate validations."""

    # Supported rule types
    RULE_TYPES = {
        'COUNT_STAR': 'COUNT(*)',
        'COUNT_COLUMN': 'COUNT({column})',
        'SUM': 'SUM({column})',
        'AVG': 'AVG({column})',
        'MIN': 'MIN({column})',
        'MAX': 'MAX({column})',
        'COUNT_DISTINCT': 'COUNT(DISTINCT {column})',
        'COUNT_NULL': 'SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END)',
        'COUNT_NOT_NULL': 'SUM(CASE WHEN {column} IS NOT NULL THEN 1 ELSE 0 END)',
    }

    @staticmethod
    def build_query(
        dialect: str,
        database: Optional[str],
        schema: Optional[str],
        table: str,
        column: Optional[str],
        rule_type: str,
        custom_expression: Optional[str],
        filter_clause: Optional[str]
    ) -> str:
        """
        Build a SQL query for aggregate validation.

        Args:
            dialect: SQL dialect (sqlserver, oracle, netezza, snowflake, csv)
            database: Database name (optional, may be in connection)
            schema: Schema name
            table: Table name
            column: Column name (required for most rule types)
            rule_type: Type of aggregate rule
            custom_expression: Custom SQL expression (for CUSTOM rule type)
            filter_clause: WHERE clause filter (without 'WHERE' keyword)

        Returns:
            Complete SQL query string

        Raises:
            InvalidRuleTypeException: If rule type is invalid
        """
        # Handle CUSTOM rule type
        if rule_type == 'CUSTOM':
            if not custom_expression:
                raise InvalidRuleTypeException("Custom expression required for CUSTOM rule type")
            aggregate_expr = custom_expression
        else:
            # Get aggregate expression template
            if rule_type not in QueryBuilder.RULE_TYPES:
                raise InvalidRuleTypeException(
                    f"Invalid rule type: {rule_type}. "
                    f"Supported types: {list(QueryBuilder.RULE_TYPES.keys())}"
                )

            aggregate_template = QueryBuilder.RULE_TYPES[rule_type]

            # Check if column is required
            if '{column}' in aggregate_template:
                if not column:
                    raise InvalidRuleTypeException(
                        f"Column name required for rule type: {rule_type}"
                    )
                aggregate_expr = aggregate_template.format(column=column)
            else:
                aggregate_expr = aggregate_template

        # Build table reference based on dialect
        table_ref = QueryBuilder._build_table_reference(
            dialect, database, schema, table
        )

        # Build complete query
        query = f"SELECT {aggregate_expr} FROM {table_ref}"

        # Add filter clause if provided
        if filter_clause and filter_clause.strip():
            query += f" WHERE {filter_clause}"

        return query

    @staticmethod
    def _build_table_reference(
        dialect: str,
        database: Optional[str],
        schema: Optional[str],
        table: str
    ) -> str:
        """
        Build table reference string based on dialect.

        Args:
            dialect: SQL dialect
            database: Database name
            schema: Schema name
            table: Table name

        Returns:
            Fully qualified table reference
        """
        parts = []

        if dialect == 'sqlserver':
            # SQL Server: [database].[schema].[table]
            if database:
                parts.append(f"[{database}]")
            if schema:
                parts.append(f"[{schema}]")
            parts.append(f"[{table}]")
            return '.'.join(parts)

        elif dialect == 'oracle':
            # Oracle: schema.table (database is typically in connection)
            if schema:
                return f"{schema}.{table}"
            return table

        elif dialect == 'netezza':
            # Netezza: database.schema.table or schema.table
            if database and schema:
                return f"{database}.{schema}.{table}"
            elif schema:
                return f"{schema}.{table}"
            return table

        elif dialect == 'snowflake':
            # Snowflake: database.schema.table
            if database and schema:
                return f"{database}.{schema}.{table}"
            elif schema:
                return f"{schema}.{table}"
            return table

        elif dialect == 'csv':
            # CSV: just use table name (which is actually the dataframe reference)
            # For CSV, the query builder should be handled differently
            # This is a placeholder for CSV handling
            return "data"

        else:
            # Default: schema.table
            if schema:
                return f"{schema}.{table}"
            return table

    @staticmethod
    def validate_rule_type(rule_type: str) -> bool:
        """
        Validate if a rule type is supported.

        Args:
            rule_type: Rule type to validate

        Returns:
            True if valid, False otherwise
        """
        return rule_type in QueryBuilder.RULE_TYPES or rule_type == 'CUSTOM'
