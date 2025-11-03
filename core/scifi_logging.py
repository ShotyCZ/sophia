"""
Logging Handler for Sci-Fi Terminal Interfaces
===============================================

Redirects Python logging to the rich, two-panel sci-fi terminal UI.
"""

import logging
from typing import Optional

class SciFiLoggingHandler(logging.Handler):
    """
    Custom logging handler that redirects logs to the sci-fi terminal interface.
    
    Instead of printing to stdout (which would break the layout), this handler
    calls the `update_log_display` method on the interface plugin, which then
    safely adds the log message to the bottom panel and refreshes the display.
    """

    def __init__(self, interface_plugin, level=logging.INFO):
        super().__init__(level)
        self.interface = interface_plugin
        
        # Color mapping for log levels and corresponding emojis
        self.level_info = {
            'DEBUG': ('[dim]', '🔍'),
            'INFO': ('[cyan]', '⚙️'),
            'WARNING': ('[yellow]', '⚠️'),
            'ERROR': ('[red]', '❌'),
            'CRITICAL': ('[bold red]', '🚨'),
        }

    def emit(self, record: logging.LogRecord):
        """Send the formatted log record to the sci-fi interface's log panel."""
        try:
            msg = self.format(record)
            
            # Skip logs that are too noisy or not useful for the TUI
            if any(skip in msg.lower() for skip in ['plugin_name', 'extra={', 'traceback']):
                return

            # Format the message for the TUI
            level_name = record.levelname
            style, emoji = self.level_info.get(level_name, ('[white]', '•'))
            formatted_msg = f"{style}{emoji} {msg}[/]"

            # Safely update the TUI by calling the interface's dedicated method
            if hasattr(self.interface, 'update_log_display') and callable(self.interface.update_log_display):
                self.interface.update_log_display(formatted_msg)
            else:
                # Fallback if the interface doesn't have the required method (should not happen)
                self.interface.console.print(formatted_msg)
                
        except Exception:
            self.handleError(record)

def install_scifi_logging(interface_plugin, logger_name: Optional[str] = None):
    """
    Installs the sci-fi logging handler to redirect all log output to the TUI.
    
    Args:
        interface_plugin: The sci-fi terminal interface plugin instance.
        logger_name: The name of the logger to hook (default is the root logger).
    """
    target_logger = logging.getLogger(logger_name)
    
    # CRITICAL: Remove any existing StreamHandlers to prevent duplicate output to the raw console.
    for handler in target_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler):
            target_logger.removeHandler(handler)
    
    # Add our custom handler that pipes logs to the TUI panel
    handler = SciFiLoggingHandler(interface_plugin, level=logging.INFO)
    # Use a simple formatter; styling is handled within the handler itself
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    target_logger.addHandler(handler)
    
    return handler
