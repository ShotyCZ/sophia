import asyncio
import sys
import os
import argparse
import warnings
import logging
from dotenv import load_dotenv
from core.kernel import Kernel
from plugins.base_plugin import PluginType


async def _load_scifi_interface(kernel, ui_style: str):
    """Load sci-fi terminal interface plugin and REMOVE classic terminal."""
    try:
        if ui_style == "matrix":
            from plugins.interface_terminal_matrix import InterfaceTerminalMatrix
            interface = InterfaceTerminalMatrix()
        elif ui_style == "startrek":
            from plugins.interface_terminal_startrek import InterfaceTerminalStarTrek
            interface = InterfaceTerminalStarTrek()
        elif ui_style == "cyberpunk":
            from plugins.interface_terminal_scifi import InterfaceTerminalSciFi
            interface = InterfaceTerminalSciFi()
        else:
            return None  # Classic mode, use default
        
        # CRITICAL: Remove ALL existing interface plugins first!
        kernel.plugin_manager._plugins[PluginType.INTERFACE] = []
        
        # Setup and register ONLY our sci-fi interface
        interface.setup({})
        kernel.plugin_manager._plugins[PluginType.INTERFACE].append(interface)
        kernel.all_plugins_map[interface.name] = interface
        
        return interface  # Return interface for logging hookup
        
    except Exception as e:
        # Use logging instead of print for errors
        logging.warning(f"Could not load {ui_style} interface: {e}. Falling back to classic terminal.")
        return None


def check_venv():
    """Check if the application is running in a virtual environment."""
    if sys.prefix == sys.base_prefix:
        print("---")
        print(
            "ERROR: It looks like you are not running this application in a virtual environment."
        )
        print("Please activate the virtual environment first.")
        print("Example: source .venv/bin/activate")
        print("---")
        sys.exit(1)


async def main():
    """The main entry point of the application."""
    # Suppress irrelevant warnings before any other output
    warnings.filterwarnings("ignore", message=".*Langfuse.*")
    warnings.filterwarnings("ignore", message=".*Authentication error.*")
    warnings.filterwarnings("ignore", module="chromadb")
    logging.captureWarnings(True)

    check_venv()
    load_dotenv()
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Sophia AI Assistant")
    parser.add_argument(
        "--use-event-driven",
        action="store_true",
        help="Enable event-driven architecture (Phase 1 - EXPERIMENTAL)"
    )
    parser.add_argument(
        "--ui",
        choices=["matrix", "startrek", "cyberpunk", "classic"],
        default=None,
        help="Choose sci-fi terminal UI style (matrix, startrek, cyberpunk, or classic)"
    )
    parser.add_argument(
        "input",
        nargs="*",
        help="Non-interactive input for single-run mode"
    )
    args = parser.parse_args()
    
    # Determine UI style (CLI arg > ENV var > default cyberpunk)
    ui_style = args.ui or os.getenv("SOPHIA_UI_STYLE", "cyberpunk")
    
    kernel = Kernel(use_event_driven=args.use_event_driven)
    
    # IMPORTANT: Initialize kernel FIRST to load all plugins
    await kernel.initialize()
    
    # THEN replace interface plugin if sci-fi mode requested
    scifi_interface = None
    if ui_style != "classic":
        scifi_interface = await _load_scifi_interface(kernel, ui_style)
        
        # Install sci-fi logging handler to redirect logs to colorful UI
        if scifi_interface:
            from core.scifi_logging import install_scifi_logging
            install_scifi_logging(scifi_interface)

    # In non-interactive mode, we don't need the main loop, just a single run
    if args.input:
        user_input = " ".join(args.input)
        await kernel.consciousness_loop(single_run_input=user_input)
    else:
        # In interactive mode, find the right interface to get input
        interface_plugins = kernel.plugin_manager.get_plugins_by_type(PluginType.INTERFACE)
        if not interface_plugins:
            logging.critical("No interface plugin found. Cannot get user input.")
            return

        active_interface = interface_plugins[0]
        if not hasattr(active_interface, 'get_user_input') or not callable(active_interface.get_user_input):
            logging.critical(f"Interface '{active_interface.name}' does not support interactive input.")
            return

        # Custom interactive loop to use the new TUI
        while True:
            try:
                user_input = active_interface.get_user_input()
                if user_input.strip().lower() in ['exit', 'quit']:
                    print("Exiting...")
                    break
                # Manually run a single "turn" of the consciousness loop
                await kernel.consciousness_loop(single_run_input=user_input)
            except (KeyboardInterrupt, EOFError):
                break
            finally:
                if hasattr(active_interface, 'cleanup') and callable(active_interface.cleanup):
                    active_interface.cleanup()

    logging.info("Sophia's kernel has been terminated.")


if __name__ == "__main__":
    asyncio.run(main())
