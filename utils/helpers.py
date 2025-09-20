import sys
import os

def create_progress_bar(percentage: float, width: int = 40) -> str:
    """Creates a text-based progress bar string."""
    filled_width = int(percentage / 100 * width)
    bar = '|' * filled_width + '-' * (width - filled_width)
    return f"|{bar}| {percentage:.2f}%"

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')