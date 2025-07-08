# valai/core/console.py

from rich.console import Console

# This is the single, shared instance of the Console.
# Import this 'console' object into any file where you need rich printing.
console = Console()
