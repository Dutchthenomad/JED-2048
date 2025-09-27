#!/usr/bin/env python3
"""
Production Error Handler for 2048 Bot
Comprehensive error handling, logging, and recovery mechanisms
"""

import logging
import traceback
import time
from typing import Optional, Dict, Any, Callable
from functools import wraps
from pathlib import Path

class ProductionErrorHandler:
    """Comprehensive error handling for production deployment"""

    def __init__(self, log_level: str = "INFO", enable_recovery: bool = True):
        """
        Initialize error handler

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_recovery: Enable automatic error recovery attempts
        """
        self.enable_recovery = enable_recovery
        self.error_count = 0
        self.max_errors = 5
        self.recovery_attempts = {}

        # Setup logging
        self.logger = self._setup_logging(log_level)

    def _setup_logging(self, level: str) -> logging.Logger:
        """Setup comprehensive logging system"""
        logger = logging.getLogger("2048_bot")
        logger.setLevel(getattr(logging, level.upper()))

        # Clear existing handlers
        logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler for errors
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(
            log_dir / f"2048_bot_{int(time.time())}.log"
        )
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        return logger

    def handle_error(self, error: Exception, operation: str,
                    recovery_func: Optional[Callable] = None,
                    max_retries: int = 3) -> Dict[str, Any]:
        """
        Comprehensive error handling with optional recovery

        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
            recovery_func: Optional recovery function to attempt
            max_retries: Maximum number of recovery attempts

        Returns:
            Dict with error info and recovery status
        """
        self.error_count += 1
        error_info = {
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': time.time(),
            'recovery_attempted': False,
            'recovery_successful': False,
            'retry_count': 0
        }

        # Log the error
        self.logger.error(f"❌ {operation} failed: {error_info['error_type']}: {error_info['error_message']}")
        self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")

        # Attempt recovery if enabled and function provided
        if self.enable_recovery and recovery_func and self.error_count < self.max_errors:
            error_info['recovery_attempted'] = True

            # Track recovery attempts for this operation
            if operation not in self.recovery_attempts:
                self.recovery_attempts[operation] = 0

            if self.recovery_attempts[operation] < max_retries:
                self.recovery_attempts[operation] += 1
                error_info['retry_count'] = self.recovery_attempts[operation]

                self.logger.info(f"🔄 Attempting recovery for {operation} (attempt {error_info['retry_count']}/{max_retries})")

                try:
                    recovery_result = recovery_func()
                    if recovery_result:
                        error_info['recovery_successful'] = True
                        self.logger.info(f"✅ Recovery successful for {operation}")
                        # Reset error count on successful recovery
                        self.error_count = max(0, self.error_count - 1)
                    else:
                        self.logger.warning(f"⚠️ Recovery failed for {operation}")
                except Exception as recovery_error:
                    self.logger.error(f"💥 Recovery function failed: {recovery_error}")
                    error_info['recovery_error'] = str(recovery_error)
            else:
                self.logger.error(f"🚫 Maximum recovery attempts ({max_retries}) exceeded for {operation}")

        # Check if we should abort
        if self.error_count >= self.max_errors:
            self.logger.critical(f"🛑 Maximum error count ({self.max_errors}) reached. System may be unstable.")
            error_info['system_abort_recommended'] = True

        return error_info

    def reset_error_count(self):
        """Reset error count (useful after successful operations)"""
        self.error_count = 0
        self.recovery_attempts.clear()
        self.logger.debug("🔄 Error count reset")

def error_handler(operation: str, recovery_func: Optional[Callable] = None,
                 max_retries: int = 3, raise_on_failure: bool = False):
    """
    Decorator for automatic error handling

    Args:
        operation: Description of the operation
        recovery_func: Optional recovery function
        max_retries: Maximum recovery attempts
        raise_on_failure: Whether to re-raise the exception after handling
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get error handler from self if it's a method
            error_handler_instance = None
            if args and hasattr(args[0], 'error_handler'):
                error_handler_instance = args[0].error_handler

            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_handler_instance:
                    error_info = error_handler_instance.handle_error(
                        e, operation, recovery_func, max_retries
                    )

                    # If recovery was successful, try the operation again
                    if error_info.get('recovery_successful'):
                        try:
                            return func(*args, **kwargs)
                        except Exception as retry_error:
                            if raise_on_failure:
                                raise retry_error
                            return None

                    if raise_on_failure or error_info.get('system_abort_recommended'):
                        raise e
                else:
                    # Fallback logging if no error handler available
                    logging.error(f"❌ {operation} failed: {e}")
                    if raise_on_failure:
                        raise e

                return None
        return wrapper
    return decorator

class RobustConnectionManager:
    """Manages robust connections with automatic retry and fallback"""

    def __init__(self, error_handler: ProductionErrorHandler):
        self.error_handler = error_handler
        self.connection_urls = [
            "https://2048game.com/",
            "https://gabrielecirulli.github.io/2048/",
            "https://play2048.co/"
        ]
        self.current_url_index = 0

    def get_next_url(self) -> str:
        """Get next URL for fallback connection"""
        self.current_url_index = (self.current_url_index + 1) % len(self.connection_urls)
        return self.connection_urls[self.current_url_index]

    def attempt_connection(self, controller, max_attempts: int = 3) -> bool:
        """
        Attempt connection with multiple URLs and retries

        Args:
            controller: Browser controller instance
            max_attempts: Maximum connection attempts per URL

        Returns:
            True if connection successful, False otherwise
        """
        for url_attempt in range(len(self.connection_urls)):
            url = self.connection_urls[(self.current_url_index + url_attempt) % len(self.connection_urls)]

            for attempt in range(max_attempts):
                try:
                    self.error_handler.logger.info(f"🌐 Attempting connection to {url} (attempt {attempt + 1}/{max_attempts})")

                    if controller.connect(url):
                        self.error_handler.logger.info(f"✅ Successfully connected to {url}")
                        self.current_url_index = (self.current_url_index + url_attempt) % len(self.connection_urls)
                        return True
                    else:
                        self.error_handler.logger.warning(f"⚠️ Connection attempt failed for {url}")

                except Exception as e:
                    self.error_handler.handle_error(e, f"Connection to {url}", max_retries=1)

                if attempt < max_attempts - 1:
                    time.sleep(2)  # Wait between attempts

        self.error_handler.logger.error("❌ All connection attempts failed")
        return False

# Example usage and integration
if __name__ == "__main__":
    # Demo of error handling capabilities
    error_handler = ProductionErrorHandler(log_level="INFO", enable_recovery=True)

    def example_recovery():
        """Example recovery function"""
        time.sleep(1)
        return True

    # Test error handling
    try:
        raise ValueError("Test error")
    except Exception as e:
        error_info = error_handler.handle_error(e, "Test operation", example_recovery)
        print(f"Error handled: {error_info}")

    print("✅ Error handler demo completed")