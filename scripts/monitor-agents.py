#!/usr/bin/env python3
"""
Monitor agent coordination via NATS messaging
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.agent_coordinator import monitor_coordination

if __name__ == "__main__":
    try:
        asyncio.run(monitor_coordination())
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
