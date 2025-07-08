import datetime

import psutil
from loguru import logger


def get_system_metrics() -> str:
    """Retrieves current system metrics including CPU usage, memory usage, and disk space.
    Use this tool to check the health and status of the local machine.
    """
    try:
        logger.info("Fetching system metrics.")
        # CPU Usage (with a 1-second interval for a more accurate reading)
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory Usage
        memory = psutil.virtual_memory()
        # memory_percent = memory.percent
        memory_used_gb = f"{memory.used / (1024**3):.2f} GB"
        memory_total_gb = f"{memory.total / (1024**3):.2f} GB"

        # Disk Usage (for the root partition)
        disk = psutil.disk_usage("/")
        # disk_percent = disk.percent
        disk_free_gb = f"{disk.free / (1024**3):.2f} GB"
        disk_total_gb = f"{disk.total / (1024**3):.2f} GB"

        metrics = (
            "System Metrics:\n"
            f"- CPU Usage: {cpu_percent}%\n"
            f"- Memory Usage: {memory_used_gb} / {memory_total_gb}\n"
            f"- Disk Space: {disk_free_gb} free / {disk_total_gb} total"
        )
        logger.success("Successfully fetched system metrics.")
        return metrics
    except Exception as e:
        logger.opt(exception=True).error(
            f"An error occurred while fetching system metrics: {e}"
        )
        return f"An error occurred while fetching system metrics: {e}"


def get_current_time() -> str:
    """Retrieves the current date and time, including the timezone."""
    logger.info("Fetching current time.")
    now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    return f"The current date and time is: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
