"""
Terminal colors for cross-platform output.
"""

import os
import sys


def supports_color() -> bool:
    """Check if the terminal supports colors."""
    # Check for NO_COLOR environment variable
    if os.environ.get('NO_COLOR'):
        return False

    # Check for FORCE_COLOR
    if os.environ.get('FORCE_COLOR'):
        return True

    # Check if stdout is a TTY
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False

    # Check for Windows
    if sys.platform == 'win32':
        return os.environ.get('TERM') is not None or os.environ.get('ANSICON') is not None

    return True


class Colors:
    """ANSI color codes for terminal output."""

    # Only enable colors if terminal supports it
    _enabled = supports_color()

    # Basic colors
    RED = '\033[0;31m' if _enabled else ''
    GREEN = '\033[0;32m' if _enabled else ''
    YELLOW = '\033[1;33m' if _enabled else ''
    BLUE = '\033[0;34m' if _enabled else ''
    PURPLE = '\033[0;35m' if _enabled else ''
    CYAN = '\033[0;36m' if _enabled else ''
    WHITE = '\033[0;37m' if _enabled else ''

    # Bright colors
    BRIGHT_RED = '\033[1;31m' if _enabled else ''
    BRIGHT_GREEN = '\033[1;32m' if _enabled else ''
    BRIGHT_YELLOW = '\033[1;33m' if _enabled else ''
    BRIGHT_BLUE = '\033[1;34m' if _enabled else ''
    BRIGHT_CYAN = '\033[1;36m' if _enabled else ''

    # Styles
    BOLD = '\033[1m' if _enabled else ''
    DIM = '\033[2m' if _enabled else ''
    UNDERLINE = '\033[4m' if _enabled else ''

    # Reset
    NC = '\033[0m' if _enabled else ''
    RESET = NC

    @classmethod
    def disable(cls) -> None:
        """Disable all colors."""
        cls._enabled = False
        for attr in dir(cls):
            if attr.isupper() and not attr.startswith('_'):
                setattr(cls, attr, '')

    @classmethod
    def enable(cls) -> None:
        """Enable colors (if terminal supports it)."""
        if supports_color():
            cls._enabled = True
            cls.RED = '\033[0;31m'
            cls.GREEN = '\033[0;32m'
            cls.YELLOW = '\033[1;33m'
            cls.BLUE = '\033[0;34m'
            cls.PURPLE = '\033[0;35m'
            cls.CYAN = '\033[0;36m'
            cls.WHITE = '\033[0;37m'
            cls.BRIGHT_RED = '\033[1;31m'
            cls.BRIGHT_GREEN = '\033[1;32m'
            cls.BRIGHT_YELLOW = '\033[1;33m'
            cls.BRIGHT_BLUE = '\033[1;34m'
            cls.BRIGHT_CYAN = '\033[1;36m'
            cls.BOLD = '\033[1m'
            cls.DIM = '\033[2m'
            cls.UNDERLINE = '\033[4m'
            cls.NC = '\033[0m'
            cls.RESET = '\033[0m'


# Convenience print functions
def print_success(msg: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}[+]{Colors.NC} {msg}")


def print_error(msg: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}[-]{Colors.NC} {msg}")


def print_warning(msg: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}[!]{Colors.NC} {msg}")


def print_info(msg: str) -> None:
    """Print an info message."""
    print(f"{Colors.BLUE}[*]{Colors.NC} {msg}")


def print_step(msg: str) -> None:
    """Print a step/progress message."""
    print(f"{Colors.CYAN}[>]{Colors.NC} {msg}")


def print_debug(msg: str) -> None:
    """Print a debug message."""
    print(f"{Colors.DIM}[D]{Colors.NC} {msg}")


def print_header(msg: str) -> None:
    """Print a header/section message."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{msg}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.NC}\n")


def colorize(text: str, color: str) -> str:
    """Wrap text in a color."""
    return f"{color}{text}{Colors.NC}"
