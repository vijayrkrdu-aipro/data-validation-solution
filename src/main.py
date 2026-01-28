"""
Main CLI entry point for data validation solution.
"""

import argparse
import sys
import os
from datetime import datetime
import pandas as pd

from .config_parser import ConfigParser
from .connection_manager import ConnectionManager
from .validator import Validator
from .utils.logger import logger, setup_logger
from .utils.exceptions import ValidationException


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Data Load Validation Solution - Validate data between databases and files'
    )

    parser.add_argument(
        '--config',
        required=True,
        help='Path to Excel validation configuration file'
    )

    parser.add_argument(
        '--connections',
        required=True,
        help='Path to YAML connections configuration file'
    )

    parser.add_argument(
        '--output',
        help='Path to output CSV report (default: output/validation_report_TIMESTAMP.csv)'
    )

    parser.add_argument(
        '--sheet',
        default='Validations',
        help='Excel sheet name containing validations (default: Validations)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--test-connections',
        action='store_true',
        help='Test all connections and exit'
    )

    return parser.parse_args()


def test_connections(connection_manager: ConnectionManager):
    """Test all configured connections."""
    logger.info("Testing all connections...")
    results = connection_manager.test_all_connections()

    print("\n" + "=" * 60)
    print("CONNECTION TEST RESULTS")
    print("=" * 60)

    all_passed = True
    for conn_name, status in results.items():
        status_str = "PASS" if status else "FAIL"
        symbol = "✓" if status else "✗"
        print(f"{symbol} {conn_name:30} {status_str}")
        if not status:
            all_passed = False

    print("=" * 60)
    print(f"\nTotal: {len(results)} | Passed: {sum(results.values())} | Failed: {len(results) - sum(results.values())}")

    return all_passed


def generate_output_path(custom_path: str = None) -> str:
    """Generate output file path with timestamp."""
    if custom_path:
        return custom_path

    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"validation_report_{timestamp}.csv"

    return os.path.join(output_dir, filename)


def save_results_to_csv(results: list, output_path: str):
    """Save validation results to CSV file."""
    # Convert results to dictionary format
    data = []
    for result in results:
        data.append({
            'validation_id': result.validation_id,
            'validation_name': result.validation_name,
            'status': result.status,
            'source_value': result.source_value,
            'target_value': result.target_value,
            'difference': result.difference,
            'percentage_diff': result.percentage_diff,
            'source_details': result.source_details,
            'target_details': result.target_details,
            'rule_type': result.rule_type,
            'threshold_type': result.threshold_type,
            'threshold_value': result.threshold_value,
            'execution_timestamp': result.execution_timestamp,
            'error_message': result.error_message or ''
        })

    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    logger.info(f"Results saved to: {output_path}")


def print_summary(results: list):
    """Print summary of validation results."""
    total = len(results)
    passed = sum(1 for r in results if r.status == 'PASS')
    failed = sum(1 for r in results if r.status == 'FAIL')
    errors = sum(1 for r in results if r.status == 'ERROR')

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Validations: {total}")
    print(f"✓ Passed:          {passed} ({passed/total*100:.1f}%)")
    print(f"✗ Failed:          {failed} ({failed/total*100:.1f}%)")
    print(f"⚠ Errors:          {errors} ({errors/total*100:.1f}%)")
    print("=" * 60)

    # Show failed validations
    if failed > 0:
        print("\nFailed Validations:")
        for result in results:
            if result.status == 'FAIL':
                print(f"  ✗ {result.validation_id}: {result.validation_name}")
                print(f"    Source: {result.source_value} | Target: {result.target_value} | Diff: {result.difference}")

    # Show errors
    if errors > 0:
        print("\nErrors:")
        for result in results:
            if result.status == 'ERROR':
                print(f"  ⚠ {result.validation_id}: {result.validation_name}")
                print(f"    Error: {result.error_message}")

    print()


def main():
    """Main execution function."""
    args = parse_arguments()

    # Setup logging
    if args.verbose:
        import logging
        setup_logger(level=logging.DEBUG)

    try:
        print("\n" + "=" * 60)
        print("DATA VALIDATION SOLUTION")
        print("=" * 60)

        # Initialize connection manager
        logger.info(f"Loading connections from: {args.connections}")
        connection_manager = ConnectionManager(args.connections)

        # Test connections if requested
        if args.test_connections:
            all_passed = test_connections(connection_manager)
            sys.exit(0 if all_passed else 1)

        # Parse validation configurations
        logger.info(f"Loading validation config from: {args.config}")
        config_parser = ConfigParser(args.config, args.sheet)
        validations = config_parser.parse()

        if not validations:
            logger.warning("No validations found in configuration file")
            sys.exit(0)

        print(f"\nFound {len(validations)} validation(s) to execute\n")

        # Initialize validator
        validator = Validator(connection_manager)

        # Execute validations
        results = []
        for idx, validation in enumerate(validations, 1):
            print(f"[{idx}/{len(validations)}] {validation.validation_id}: {validation.validation_name}")
            result = validator.validate(validation)
            results.append(result)

            # Print result
            status_symbol = "✓" if result.status == "PASS" else "✗" if result.status == "FAIL" else "⚠"
            print(f"         {status_symbol} {result.status}")

        # Generate output path
        output_path = generate_output_path(args.output)

        # Save results
        save_results_to_csv(results, output_path)

        # Print summary
        print_summary(results)

        # Exit with appropriate code
        failed_count = sum(1 for r in results if r.status == 'FAIL')
        error_count = sum(1 for r in results if r.status == 'ERROR')
        sys.exit(1 if (failed_count > 0 or error_count > 0) else 0)

    except ValidationException as e:
        logger.error(f"Validation error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
