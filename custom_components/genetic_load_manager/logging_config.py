"""Logging configuration for Genetic Load Manager integration."""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

def setup_comprehensive_logging(domain: str, log_level: str = "DEBUG"):
    """
    Set up comprehensive logging for the Genetic Load Manager integration.
    
    Args:
        domain: The integration domain (e.g., 'genetic_load_manager')
        log_level: The logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    """
    
    # Create logger
    logger = logging.getLogger(domain)
    
    # Set log level
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    logger.setLevel(level_map.get(log_level.upper(), logging.INFO))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler for detailed logging
    try:
        # Create logs directory if it doesn't exist
        log_dir = Path.home() / ".homeassistant" / "logs" / domain
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{domain}_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        # Also create a rotating file handler for ongoing logging
        rotating_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{domain}_current.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        rotating_handler.setLevel(logging.DEBUG)
        rotating_handler.setFormatter(detailed_formatter)
        logger.addHandler(rotating_handler)
        
        logger.info(f"Comprehensive logging enabled. Log files: {log_file} and {log_dir}/{domain}_current.log")
        
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")
        logger.info("Console logging only enabled")
    
    return logger

def log_optimization_summary(logger, data_summary: dict):
    """
    Log a comprehensive summary of optimization data and status.
    
    Args:
        logger: The logger instance
        data_summary: Dictionary containing optimization data summary
    """
    logger.info("=" * 80)
    logger.info("OPTIMIZATION DATA SUMMARY")
    logger.info("=" * 80)
    
    # Log data availability
    logger.info("Data Availability:")
    for key, value in data_summary.get('availability', {}).items():
        status = "✓ AVAILABLE" if value else "✗ MISSING"
        logger.info(f"  {key}: {status}")
    
    # Log data quality
    logger.info("Data Quality:")
    for key, value in data_summary.get('quality', {}).items():
        if isinstance(value, dict):
            logger.info(f"  {key}:")
            for subkey, subvalue in value.items():
                logger.info(f"    {subkey}: {subvalue}")
        else:
            logger.info(f"  {key}: {value}")
    
    # Log optimization status
    logger.info("Optimization Status:")
    for key, value in data_summary.get('status', {}).items():
        logger.info(f"  {key}: {value}")
    
    logger.info("=" * 80)

def log_error_context(logger, error: Exception, context: str = "", **kwargs):
    """
    Log detailed error information with context.
    
    Args:
        logger: The logger instance
        error: The exception that occurred
        context: Context string describing where the error occurred
        **kwargs: Additional context variables to log
    """
    logger.error("=" * 60)
    logger.error(f"ERROR IN {context.upper()}")
    logger.error("=" * 60)
    logger.error(f"Exception type: {type(error).__name__}")
    logger.error(f"Exception message: {str(error)}")
    
    # Log additional context
    if kwargs:
        logger.error("Context variables:")
        for key, value in kwargs.items():
            logger.error(f"  {key}: {value}")
    
    # Log traceback
    import traceback
    logger.error("Full traceback:")
    logger.error(traceback.format_exc())
    logger.error("=" * 60)

def log_entity_status(logger, entity_id: str, state, attributes: dict = None):
    """
    Log detailed entity status information.
    
    Args:
        logger: The logger instance
        entity_id: The entity ID
        state: The entity state
        attributes: The entity attributes
    """
    logger.info(f"Entity Status: {entity_id}")
    logger.info(f"  State: {state}")
    
    if attributes:
        logger.info(f"  Attributes ({len(attributes)}):")
        for key, value in list(attributes.items())[:10]:  # Show first 10 attributes
            if isinstance(value, (list, tuple)) and len(value) > 5:
                logger.info(f"    {key}: {type(value).__name__}[{len(value)}] - Sample: {value[:5]}")
            else:
                logger.info(f"    {key}: {value}")
        
        if len(attributes) > 10:
            logger.info(f"    ... and {len(attributes) - 10} more attributes")
    else:
        logger.info("  Attributes: None")

def log_data_validation(logger, data_name: str, data, expected_type=None, expected_length=None):
    """
    Log data validation results.
    
    Args:
        logger: The logger instance
        data_name: Name of the data being validated
        data: The data to validate
        expected_type: Expected data type
        expected_length: Expected data length
    """
    logger.info(f"Data Validation: {data_name}")
    logger.info(f"  Type: {type(data).__name__}")
    logger.info(f"  Value: {data}")
    
    if data is not None:
        if hasattr(data, '__len__'):
            logger.info(f"  Length: {len(data)}")
        if hasattr(data, 'shape'):
            logger.info(f"  Shape: {data.shape}")
    
    # Validation results
    validation_passed = True
    validation_issues = []
    
    if expected_type and not isinstance(data, expected_type):
        validation_passed = False
        validation_issues.append(f"Type mismatch: expected {expected_type.__name__}, got {type(data).__name__}")
    
    if expected_length and hasattr(data, '__len__') and len(data) != expected_length:
        validation_passed = False
        validation_issues.append(f"Length mismatch: expected {expected_length}, got {len(data)}")
    
    if data is None:
        validation_passed = False
        validation_issues.append("Data is None")
    
    # Check for non-finite values in numeric data
    if isinstance(data, (list, tuple)) and data:
        try:
            numeric_data = [float(x) for x in data if x is not None]
            non_finite_count = sum(1 for x in numeric_data if not (isinstance(x, (int, float)) and (x == x and x != float('inf') and x != float('-inf'))))
            if non_finite_count > 0:
                validation_passed = False
                validation_issues.append(f"Contains {non_finite_count} non-finite values")
        except (ValueError, TypeError):
            pass
    
    if validation_passed:
        logger.info(f"  Validation: ✓ PASSED")
    else:
        logger.error(f"  Validation: ✗ FAILED")
        for issue in validation_issues:
            logger.error(f"    Issue: {issue}")

def create_debug_report(logger, integration_data: dict) -> str:
    """
    Create a comprehensive debug report for troubleshooting.
    
    Args:
        logger: The logger instance
        integration_data: Dictionary containing integration data
        
    Returns:
        String containing the debug report
    """
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("GENETIC LOAD MANAGER DEBUG REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().isoformat()}")
    report_lines.append("")
    
    # System information
    report_lines.append("SYSTEM INFORMATION:")
    report_lines.append(f"  Python version: {os.sys.version}")
    report_lines.append(f"  Platform: {os.sys.platform}")
    report_lines.append("")
    
    # Integration configuration
    report_lines.append("INTEGRATION CONFIGURATION:")
    for key, value in integration_data.get('config', {}).items():
        report_lines.append(f"  {key}: {value}")
    report_lines.append("")
    
    # Entity status
    report_lines.append("ENTITY STATUS:")
    for entity_id, status in integration_data.get('entities', {}).items():
        report_lines.append(f"  {entity_id}: {status}")
    report_lines.append("")
    
    # Data summary
    report_lines.append("DATA SUMMARY:")
    for key, value in integration_data.get('data', {}).items():
        if isinstance(value, (list, tuple)):
            report_lines.append(f"  {key}: {type(value).__name__}[{len(value)}]")
        else:
            report_lines.append(f"  {key}: {value}")
    report_lines.append("")
    
    # Recent errors
    report_lines.append("RECENT ERRORS:")
    errors = integration_data.get('errors', [])
    if errors:
        for error in errors[-5:]:  # Show last 5 errors
            report_lines.append(f"  {error}")
    else:
        report_lines.append("  No recent errors")
    report_lines.append("")
    
    report_lines.append("=" * 80)
    
    report = "\n".join(report_lines)
    logger.info("Debug report generated")
    return report