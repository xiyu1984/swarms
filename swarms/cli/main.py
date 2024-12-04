import argparse
import os
import subprocess
import time
import webbrowser

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from swarms.agents.auto_generate_swarm_config import (
    generate_swarm_config,
)
from swarms.agents.create_agents_from_yaml import (
    create_agents_from_yaml,
)
from swarms.cli.onboarding_process import OnboardingProcess
from swarms.utils.formatter import formatter

# Initialize console with custom styling
console = Console()


class SwarmCLIError(Exception):
    """Custom exception for Swarm CLI errors"""

    pass


# Color scheme
COLORS = {
    "primary": "red",
    "secondary": "#FF6B6B",
    "accent": "#4A90E2",
    "success": "#2ECC71",
    "warning": "#F1C40F",
    "error": "#E74C3C",
    "text": "#FFFFFF",
}

ASCII_ART = """
   ▄████████  ▄█     █▄     ▄████████    ▄████████   ▄▄▄▄███▄▄▄▄      ▄████████ 
  ███    ███ ███     ███   ███    ███   ███    ███ ▄██▀▀▀███▀▀▀██▄   ███    ███ 
  ███    █▀  ███     ███   ███    ███   ███    ███ ███   ███   ███   ███    █▀  
  ███        ███     ███   ███    ███  ▄███▄▄▄▄██▀ ███   ███   ███   ███        
▀███████████ ███     ███ ▀███████████ ▀▀███▀▀▀▀▀   ███   ███   ███ ▀███████████ 
         ███ ███     ███   ███    ███ ▀███████████ ███   ███   ███          ███ 
   ▄█    ███ ███ ▄█▄ ███   ███    ███   ███    ███ ███   ███   ███    ▄█    ███ 
 ▄████████▀   ▀███▀███▀    ███    █▀    ███    ███  ▀█   ███   █▀   ▄████████▀  
                                        ███    ███                                 
"""


def create_spinner(text: str) -> Progress:
    """Create a custom spinner with the given text."""
    return Progress(
        SpinnerColumn(style=COLORS["primary"]),
        TextColumn("[{task.description}]", style=COLORS["text"]),
        console=console,
    )


def show_ascii_art():
    """Display the ASCII art with a glowing effect."""
    panel = Panel(
        Text(ASCII_ART, style=f"bold {COLORS['primary']}"),
        border_style=COLORS["secondary"],
        title="[bold]Welcome to Swarms[/bold]",
        subtitle="[dim]Power to the Swarms[/dim]",
    )
    console.print(panel)


def create_command_table() -> Table:
    """Create a beautifully formatted table of commands."""
    table = Table(
        show_header=True,
        header_style=f"bold {COLORS['primary']}",
        border_style=COLORS["secondary"],
        title="Available Commands",
        padding=(0, 2),
    )

    table.add_column("Command", style="bold white")
    table.add_column("Description", style="dim white")

    commands = [
        ("onboarding", "Start the interactive onboarding process"),
        ("help", "Display this help message"),
        ("get-api-key", "Retrieve your API key from the platform"),
        ("check-login", "Verify login status and initialize cache"),
        ("run-agents", "Execute agents from your YAML configuration"),
        ("auto-upgrade", "Update Swarms to the latest version"),
        ("book-call", "Schedule a strategy session with our team"),
        ("autoswarm", "Generate and execute an autonomous swarm"),
    ]

    for cmd, desc in commands:
        table.add_row(cmd, desc)

    return table


def show_help():
    """Display a beautifully formatted help message."""
    console.print(
        "\n[bold]Swarms CLI - Command Reference[/bold]\n",
        style=COLORS["primary"],
    )
    console.print(create_command_table())
    console.print(
        "\n[dim]For detailed documentation, visit: https://docs.swarms.world[/dim]"
    )


def show_error(message: str, help_text: str = None):
    """Display error message in a formatted panel"""
    error_panel = Panel(
        f"[bold red]{message}[/bold red]",
        title="Error",
        border_style="red",
    )
    console.print(error_panel)

    if help_text:
        console.print(f"\n[yellow]ℹ️ {help_text}[/yellow]")


def execute_with_spinner(action: callable, text: str) -> None:
    """Execute an action with a spinner animation."""
    with create_spinner(text) as progress:
        task = progress.add_task(text, total=None)
        result = action()
        progress.remove_task(task)
    return result


def get_api_key():
    """Retrieve API key with visual feedback."""
    with create_spinner("Opening API key portal...") as progress:
        task = progress.add_task("Opening browser...")
        webbrowser.open("https://swarms.world/platform/api-keys")
        time.sleep(1)
        progress.remove_task(task)
    console.print(
        f"\n[{COLORS['success']}]✓ API key page opened in your browser[/{COLORS['success']}]"
    )


def check_login():
    """Verify login status with enhanced visual feedback."""
    cache_file = "cache.txt"

    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            if f.read() == "logged_in":
                console.print(
                    f"[{COLORS['success']}]✓ Authentication verified[/{COLORS['success']}]"
                )
                return True

    with create_spinner("Authenticating...") as progress:
        task = progress.add_task("Initializing session...")
        time.sleep(1)
        with open(cache_file, "w") as f:
            f.write("logged_in")
        progress.remove_task(task)

    console.print(
        f"[{COLORS['success']}]✓ Login successful![/{COLORS['success']}]"
    )
    return True


def run_autoswarm(task: str, model: str):
    """Run autoswarm with enhanced error handling"""
    try:
        console.print(
            "[yellow]Initializing autoswarm configuration...[/yellow]"
        )

        # Set LiteLLM verbose mode for debugging
        import litellm

        litellm.set_verbose = True

        # Validate inputs
        if not task or task.strip() == "":
            raise SwarmCLIError("Task cannot be empty")

        if not model or model.strip() == "":
            raise SwarmCLIError("Model name cannot be empty")

        # Attempt to generate swarm configuration
        console.print(
            f"[yellow]Generating swarm for task: {task}[/yellow]"
        )
        result = generate_swarm_config(task=task, model=model)

        if result:
            console.print(
                "[green]✓ Swarm configuration generated successfully![/green]"
            )
        else:
            raise SwarmCLIError(
                "Failed to generate swarm configuration"
            )

    except Exception as e:
        if "No YAML content found" in str(e):
            show_error(
                "Failed to generate YAML configuration",
                "This might be due to an API key issue or invalid model configuration.\n"
                + "1. Check if your OpenAI API key is set correctly\n"
                + "2. Verify the model name is valid\n"
                + "3. Try running with --model gpt-4",
            )
        else:
            show_error(
                f"Error during autoswarm execution: {str(e)}",
                "For debugging, try:\n"
                + "1. Check your API keys are set correctly\n"
                + "2. Verify your network connection\n"
                + "3. Try a different model",
            )


def check_and_upgrade_version():
    """Check for updates with visual progress."""

    def check_update():
        result = subprocess.run(
            ["pip", "list", "--outdated", "--format=freeze"],
            capture_output=True,
            text=True,
        )
        return result.stdout.splitlines()

    outdated = execute_with_spinner(
        check_update, "Checking for updates..."
    )

    for package in outdated:
        if package.startswith("swarms=="):
            console.print(
                f"[{COLORS['warning']}]↑ Update available![/{COLORS['warning']}]"
            )
            with create_spinner("Upgrading Swarms...") as progress:
                task = progress.add_task(
                    "Installing latest version..."
                )
                subprocess.run(
                    ["pip", "install", "--upgrade", "swarms"],
                    check=True,
                )
                progress.remove_task(task)
            console.print(
                f"[{COLORS['success']}]✓ Swarms upgraded successfully![/{COLORS['success']}]"
            )
            return

    console.print(
        f"[{COLORS['success']}]✓ Swarms is up to date![/{COLORS['success']}]"
    )


def main():
    try:

        show_ascii_art()

        parser = argparse.ArgumentParser(
            description="Swarms Cloud CLI"
        )
        parser.add_argument(
            "command",
            choices=[
                "onboarding",
                "help",
                "get-api-key",
                "check-login",
                "run-agents",
                "auto-upgrade",
                "book-call",
                "autoswarm",
            ],
            help="Command to execute",
        )
        parser.add_argument(
            "--yaml-file",
            type=str,
            default="agents.yaml",
            help="YAML configuration file path",
        )
        parser.add_argument(
            "--task", type=str, help="Task for autoswarm"
        )
        parser.add_argument(
            "--model",
            type=str,
            default="gpt-4",
            help="Model for autoswarm",
        )

        args = parser.parse_args()

        try:
            if args.command == "onboarding":
                OnboardingProcess().run()
            elif args.command == "help":
                show_help()
            elif args.command == "get-api-key":
                get_api_key()
            elif args.command == "check-login":
                check_login()
            elif args.command == "run-agents":
                create_agents_from_yaml(
                    yaml_file=args.yaml_file, return_type="tasks"
                )
            elif args.command == "auto-upgrade":
                check_and_upgrade_version()
            elif args.command == "book-call":
                webbrowser.open(
                    "https://cal.com/swarms/swarms-strategy-session"
                )
            elif args.command == "autoswarm":
                if not args.task:
                    show_error(
                        "Missing required argument: --task",
                        "Example usage: python cli.py autoswarm --task 'analyze this data' --model gpt-4",
                    )
                    exit(1)
                run_autoswarm(args.task, args.model)
        except Exception as e:
            console.print(
                f"[{COLORS['error']}]Error: {str(e)}[/{COLORS['error']}]"
            )
            return
    except Exception as error:
        formatter.print_panel(
            f"Error detected: {error} check your args"
        )
        raise error


if __name__ == "__main__":
    main()
