"""
Tools available to the AI IT Helpdesk Agent.
"""

import platform
import socket
import subprocess
import shutil

import psutil


def get_system_information():
    """Return basic system information."""

    return {
        "operating_system": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": socket.gethostname(),
    }


def check_internet_connection():
    """
    Check internet connectivity.

    Uses Google's public DNS server as the target.
    """

    system = platform.system().lower()

    try:
        if system == "windows":
            command = ["ping", "-n", "1", "8.8.8.8"]
        else:
            command = ["ping", "-c", "1", "8.8.8.8"]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Internet connection appears to be working.",
            }

        return {
            "status": "failed",
            "message": "The internet connectivity test failed.",
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "failed",
            "message": "The internet connectivity test timed out.",
        }

    except Exception as error:
        return {
            "status": "error",
            "message": f"Could not perform the test: {error}",
        }


def get_memory_usage():
    """Return current RAM usage."""

    memory = psutil.virtual_memory()

    return {
        "total_gb": round(memory.total / (1024 ** 3), 2),
        "available_gb": round(memory.available / (1024 ** 3), 2),
        "used_percent": memory.percent,
    }


def get_cpu_usage():
    """Return current CPU usage."""

    usage = psutil.cpu_percent(interval=1)

    return {
        "cpu_usage_percent": usage,
    }


def get_disk_usage():
    """Return disk usage for the main drive."""

    if platform.system().lower() == "windows":
        path = "C:\\"
    else:
        path = "/"

    disk = shutil.disk_usage(path)

    total_gb = disk.total / (1024 ** 3)
    used_gb = disk.used / (1024 ** 3)
    free_gb = disk.free / (1024 ** 3)

    return {
        "path": path,
        "total_gb": round(total_gb, 2),
        "used_gb": round(used_gb, 2),
        "free_gb": round(free_gb, 2),
    }


TOOLS = {
    "system_information": get_system_information,
    "check_internet": check_internet_connection,
    "memory_usage": get_memory_usage,
    "cpu_usage": get_cpu_usage,
    "disk_usage": get_disk_usage,
}


def execute_tool(tool_name: str):
    """Execute a registered tool."""

    if tool_name not in TOOLS:
        return {
            "status": "error",
            "message": f"Unknown tool: {tool_name}",
        }

    try:
        return TOOLS[tool_name]()
    except Exception as error:
        return {
            "status": "error",
            "message": str(error),
        }