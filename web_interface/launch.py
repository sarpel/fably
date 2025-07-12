#!/usr/bin/env python3
"""
Fably Web Interface Launcher
Professional story management system entry point.
"""

import sys
from pathlib import Path

# Add parent directory to path for Fably imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and launch the web interface
from web_interface.app import main
from zeroconf import ServiceInfo, Zeroconf
import socket

if __name__ == "__main__":
    # Register mDNS/zeroconf service for masal.local
    zeroconf = Zeroconf()
    ip = socket.gethostbyname(socket.gethostname())
    service_info = ServiceInfo(
        "_http._tcp.local.",
        "masal._http._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=7860,
        properties={},
        server="masal.local."
    )
    zeroconf.register_service(service_info)
    try:
        main()
    finally:
        zeroconf.unregister_service(service_info)
        zeroconf.close()
