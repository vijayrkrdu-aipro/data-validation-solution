"""
Custom exceptions for the data validation solution.
"""


class ValidationException(Exception):
    """Base exception for validation errors."""
    pass


class ConnectionException(ValidationException):
    """Exception raised for connection errors."""
    pass


class ConfigurationException(ValidationException):
    """Exception raised for configuration errors."""
    pass


class QueryExecutionException(ValidationException):
    """Exception raised for query execution errors."""
    pass


class InvalidRuleTypeException(ValidationException):
    """Exception raised for invalid rule types."""
    pass
