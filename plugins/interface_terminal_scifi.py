"""
🚀 SOPHIA TUI INTERFACE (UV/DOCKER STYLE)
═══════════════════════════════════════════════════════════════════════════════

A flicker-free, UV/Docker-style terminal interface with:
- Sticky bottom panel for logs
- Scrollable top panel for conversation
- Clean, single-boot startup sequence
- Proper stdout/stderr redirection to the UI
"""

import asyncio
import sys
from collections import deque
from pathlib import Path
from datetime import datetime
from typing import Optional, Deque

# Add project root to path for standalone execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from rich import box
from io import StringIO

from plugins.base_plugin import BasePlugin, PluginType
from core.context import SharedContext
import logging

logger = logging.getLogger(__name__)

SOPHIA_LOGO = """
[bold cyan]╔═══════════════════════════════════════════════╗
║    SOPHIA v2.0 - AI CONSCIOUSNESS ONLINE      ║
╚═══════════════════════════════════════════════╝[/bold cyan]
"""


class OutputCapture:
    """Redirects stdout/stderr to the TUI log panel."""
    def __init__(self, interface_instance):
        self.interface = interface_instance
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def write(self, text: str):
        """Capture text and route it to the log buffer."""
        if text.strip():
            self.interface.log_buffer.append(f"⚙️ {text.strip()}")
            self.interface.update_log_display()

    def flush(self):
        """Flush the stream."""
        pass

    def start(self):
        """Start redirecting stdout and stderr."""
        sys.stdout = self
        sys.stderr = self

    def stop(self):
        """Stop redirecting and restore original streams."""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr


class InterfaceTerminalSciFi(BasePlugin):
    """
    UV/Docker-style terminal interface with two panels:
    - Top: Scrollable conversation history
    - Bottom: Sticky/fixed panel for latest log messages
    """

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.message_history: Deque[str] = deque(maxlen=100)
        self.log_buffer: Deque[str] = deque(maxlen=10)
        self._live: Optional[Live] = None
        self._layout: Optional[Layout] = None
        self._booted = False
        self._output_capture = None

    @property
    def name(self) -> str:
        return "interface_terminal_scifi"

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.INTERFACE

    @property
    def version(self) -> str:
        return "3.0.0"

    def setup(self, config: dict) -> None:
        """Initialize the terminal and start Live display."""
        if self._booted:
            logger.debug("Skipping duplicate TUI boot.")
            return

        self._show_boot_sequence_simple()
        self._create_layout()
        self._start_live_mode()

        # Start capturing stdout/stderr AFTER Live is initialized
        self._output_capture = OutputCapture(self)
        self._output_capture.start()
        
        self._booted = True

    def cleanup(self):
        """Stop Live display and restore terminal state."""
        self._stop_live_mode()
        if hasattr(self, '_output_capture') and self._output_capture:
            self._output_capture.stop()

    def _show_boot_sequence_simple(self):
        """Display a clean, one-time boot logo."""
        self.console.clear()
        self.console.print(Align.center(SOPHIA_LOGO))
        self.console.rule("[bold green]SYSTEM ONLINE[/bold green]")

    def _create_layout(self) -> None:
        """Create the two-panel layout for conversation and logs."""
        self._layout = Layout(name="root")
        self._layout.split(
            Layout(name="main", ratio=1),
            Layout(name="logs", size=12),
        )

        # Initial empty content
        self._layout["main"].update(self._create_conversation_panel())
        self._layout["logs"].update(self._create_log_panel())

    def _start_live_mode(self):
        """Start the Rich Live display with manual refresh."""
        if not self._live and self._layout:
            self._live = Live(
                self._layout,
                console=self.console,
                screen=False,
                auto_refresh=False,
                transient=False,
                redirect_stdout=False,  # Manual redirection
                redirect_stderr=False,
            )
            self._live.start(refresh=True)

    def _stop_live_mode(self):
        """Stop the Rich Live display."""
        if self._live:
            self._live.stop()
            self._live = None

    def _refresh_display(self):
        """Manually refresh the Live display if it's active."""
        if self._live and self._live.is_started:
            self._live.refresh()

    def _create_conversation_panel(self) -> Panel:
        """Create the panel for displaying conversation history."""
        conversation_text = "\n".join(self.message_history)
        return Panel(
            Text(conversation_text, justify="left"),
            title="[bold]💬 CONVERSATION[/bold]",
            border_style="cyan",
            box=box.ROUNDED,
        )

    def _create_log_panel(self) -> Panel:
        """Create the panel for displaying log messages."""
        log_text = "\n".join(self.log_buffer)
        return Panel(
            Text(log_text, justify="left"),
            title="[bold]⚙️ System Activity[/bold]",
            border_style="magenta",
            box=box.ROUNDED,
        )

    def display_message(self, role: str, content: str):
        """
        Add a message to the conversation panel and refresh.
        
        Args:
            role: 'user' or 'assistant'
            content: Message text
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if role.lower() == "user":
            prefix = f"╭─ [dim][{timestamp}][/dim] [bold yellow]👤 YOU[/bold yellow]"
            message = f"│ │ {content}\n│ ╰─"
        else:
            prefix = f"╭─ [dim][{timestamp}][/dim] [bold cyan]🤖 SOPHIA[/bold cyan]"
            message = f"│ │ {content}\n│ ╰─"

        full_message = f"{prefix}\n{message}"
        self.message_history.append(full_message)
        
        if self._layout:
            self._layout["main"].update(self._create_conversation_panel())
            self._refresh_display()

    def update_log_display(self):
        """Update the log panel with the latest messages and refresh."""
        if self._layout:
            self._layout["logs"].update(self._create_log_panel())
            self._refresh_display()

    def get_user_input(self, prompt: str = "You") -> str:
        """
        Temporarily stop Live display to get user input, then restart.
        """
        self._stop_live_mode()
        
        try:
            from rich.prompt import Prompt
            user_input = Prompt.ask(f"[bold yellow]{prompt}[/bold yellow]")
        except:
            # Fallback for terminals not supporting rich.prompt
            self.console.print(f"[bold yellow]{prompt}:[/bold yellow] ", end="")
            user_input = input()
        
        self._start_live_mode()
        return user_input

    async def execute(self, *, context: SharedContext) -> SharedContext:
        """
        Handle non-interactive and interactive execution.
        """
        # Register a callback for the kernel to send the response back
        if context.current_state == "LISTENING":
            context.payload["_response_callback"] = self._handle_response
        
        # Display user's initial message if provided
        if context.user_input:
            self.display_message("user", context.user_input)
        
        return context

    def _handle_response(self, response: str):
        """Callback function to display the assistant's response."""
        self.display_message("assistant", response)

    def display_error(self, error: str):
        """Display an error in the log panel."""
        self.log_buffer.append(f"[red]❌ ERROR: {error}[/red]")
        self.update_log_display()

async def demo():
    """Demonstrate the UV-style TUI."""
    terminal = InterfaceTerminalSciFi()
    terminal.setup({})
    
    terminal.display_message("user", "Hello Sophia!")
    await asyncio.sleep(1)
    
    terminal.log_buffer.append("⚙️ Task classified as 'simple_query'")
    terminal.update_log_display()
    await asyncio.sleep(0.5)
    
    terminal.log_buffer.append("⚙️ Calling LLM 'gemini-2.0-flash-001'")
    terminal.update_log_display()
    await asyncio.sleep(1.5)
    
    terminal.display_message("assistant", "Hello! How can I assist you today?")
    terminal.log_buffer.append("⚙️ Response received successfully")
    terminal.update_log_display()
    
    await asyncio.sleep(1)
    
    # Simulate more conversation to test scrolling
    for i in range(10):
        terminal.display_message("user", f"This is message number {i+2} in a long conversation.")
        await asyncio.sleep(0.3)
        terminal.display_message("assistant", f"I am responding to message {i+2}.")
        terminal.log_buffer.append(f"⚙️ Processed message {i+2}")
        terminal.update_log_display()
        await asyncio.sleep(0.3)

    terminal.display_error("This is a test error message.")
    
    # In a real app, you'd wait for user input here
    # user_input = terminal.get_user_input("Your turn")
    # terminal.display_message("user", user_input)
    
    await asyncio.sleep(5)
    terminal.cleanup()
    print("Demo finished.")

if __name__ == "__main__":
    asyncio.run(demo())
