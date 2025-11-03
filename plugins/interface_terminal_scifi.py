"""
🚀 SOPHIA SCI-FI TERMINAL INTERFACE (UV/Docker Style)
═══════════════════════════════════════════════════════════════════════════════

A flicker-free, cyberpunk-inspired terminal interface with:
- A sticky bottom panel for logs (UV/Docker style)
- A scrollable top panel for conversation history
- Manual refresh for a smooth, non-blinking experience
- Proper stdout/stderr redirection to the log panel
- Clean, single-run boot sequence

Inspired by: uv, Docker, Cyberpunk 2077, Blade Runner
"""

import asyncio
import logging
import sys
from collections import deque
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Deque, List, Optional

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from core.context import SharedContext
from plugins.base_plugin import BasePlugin, PluginType

# Get logger for stdout/stderr redirection
logger = logging.getLogger()

SOPHIA_LOGO = """
[bold cyan]╔═══════════════════════════════════════════════╗
║    SOPHIA v2.0 - AI CONSCIOUSNESS ONLINE      ║
╚═══════════════════════════════════════════════╝[/bold cyan]
"""

class OutputCapture:
    """Captures stdout/stderr and redirects to the logging system."""
    def __init__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def write(self, text: str):
        """Redirect print() and other stdout/stderr to the log panel via logging."""
        if text.strip():
            logger.info(text.strip())

    def flush(self):
        pass

    def start(self):
        sys.stdout = self
        sys.stderr = self

    def stop(self):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

class InterfaceTerminalSciFi(BasePlugin):
    """
    UV/Docker-style terminal interface with two panels, no flicker, and sticky logging.
    """

    def __init__(self):
        super().__init__()
        self.console = Console()
        self._booted: bool = False
        self._live: Optional[Live] = None
        self._layout: Optional[Layout] = None
        self._output_capture: Optional[OutputCapture] = None

        self.message_history: List[Text] = []
        self.log_buffer: Deque[str] = deque(maxlen=10) # Fixed size for the bottom panel

    @property
    def name(self) -> str:
        return "interface_terminal_scifi"

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.INTERFACE

    @property
    def version(self) -> str:
        return "2.0.0"

    def setup(self, config: dict) -> None:
        """Initialize the terminal, but only once."""
        if self._booted:
            logger.debug("Skipping duplicate TUI boot.")
            return

        self._show_boot_sequence_simple()
        self._start_live_mode()

        # CRITICAL: Capture stdout/stderr AFTER Live display starts
        self._output_capture = OutputCapture()
        self._output_capture.start()

        self._booted = True
        logger.info("Sci-fi TUI initialized successfully.")

    def cleanup(self):
        """Restore original stdout/stderr and stop the live display."""
        if self._output_capture:
            self._output_capture.stop()
        self._stop_live_mode()
        logger.info("Sci-fi TUI cleaned up.")

    def _show_boot_sequence_simple(self):
        """Display the boot logo once without any animations."""
        self.console.clear()
        self.console.print(SOPHIA_LOGO)
        self.console.print("[bold green]✓ System Initialized.[/bold green]")
        self.console.print()

    def _make_layout(self) -> Layout:
        """Creates the two-panel layout for the TUI."""
        layout = Layout()
        layout.split_column(
            Layout(name="main", ratio=1),
            Layout(name="logs", size=12),
        )
        return layout

    def _start_live_mode(self):
        """Initializes and starts the Rich Live display."""
        if self._live and self._live.is_started:
            return

        self._layout = self._make_layout()
        self._layout["main"].update(self._render_conversation_panel())
        self._layout["logs"].update(self._render_log_panel())

        self._live = Live(
            self._layout,
            console=self.console,
            refresh_per_second=4, # A small refresh rate is ok, but we will rely on manual refresh
            auto_refresh=False,
            screen=False,
            transient=False,
            redirect_stdout=False, # Manual redirection
            redirect_stderr=False, # Manual redirection
        )
        self._live.start(refresh=True)

    def _stop_live_mode(self):
        """Stops the Rich Live display."""
        if self._live and self._live.is_started:
            self._live.stop()
            self._live = None

    def _refresh_display(self):
        """Manually refreshes the Live display if it's active."""
        if self._live and self._live.is_started:
            self._live.refresh()

    def _render_conversation_panel(self) -> Panel:
        """Renders the top panel with the conversation history."""
        conversation = Text("\n").join(self.message_history)
        return Panel(
            conversation,
            title="[bold magenta]💬 CONVERSATION[/bold magenta]",
            border_style="magenta",
            box=box.ROUNDED,
        )

    def _render_log_panel(self) -> Panel:
        """Renders the bottom panel with the latest log entries."""
        log_text = "\n".join(self.log_buffer)
        return Panel(
            log_text,
            title="[bold cyan]⚙️ System Activity[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
        )

    def display_message(self, role: str, content: str):
        """
        Adds a message to the conversation history and refreshes the display.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = Text()

        if role.lower() == "user":
            message.append(f"╭─ [{timestamp}] 👤 YOU\n", style="bold yellow")
            message.append(f"│ │ {content}\n")
            message.append("│ ╰─\n")
        else: # assistant
            message.append(f"╭─ [{timestamp}] 🤖 SOPHIA\n", style="bold cyan")
            message.append(f"│ │ {content}\n", style="cyan")
            message.append("│ ╰─\n")

        self.message_history.append(message)

        if self._layout:
            self._layout["main"].update(self._render_conversation_panel())
            self._refresh_display()

    def update_log_display(self, new_log_entry: str):
        """
        Adds a new entry to the log buffer and refreshes the display.
        This method is intended to be called by the custom logging handler.
        """
        self.log_buffer.append(new_log_entry)
        if self._layout:
            self._layout["logs"].update(self._render_log_panel())
            self._refresh_display()

    def _handle_response(self, response: str):
        """Callback function to handle the final response from the kernel."""
        self.display_message("assistant", response)

    async def execute(self, *, context: SharedContext) -> SharedContext:
        """
        Displays user input and registers the response callback.
        """
        # Register the callback in the LISTENING phase so the kernel can call it
        if context.current_state == "LISTENING":
            context.payload["_response_callback"] = self._handle_response

        # Display the user's message as soon as it's received
        if context.user_input:
            self.display_message("user", context.user_input)

        # For interactive mode, we need to get input.
        # This part is handled by the original interface_terminal, so we just pass context.
        return context

    def get_user_input(self, prompt: str = "You") -> str:
        """
        Gets user input from the console.
        This is called by the consciousness loop for interactive mode.
        NOTE: This will temporarily stop the Live display to get input cleanly.
        """
        if self._live:
            self._live.stop()

        try:
            user_input = self.console.input(f"[bold yellow]>{prompt}: [/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            self.cleanup()
            sys.exit(0)
        finally:
            if self._live:
                self._live.start(refresh=True)

        return user_input
