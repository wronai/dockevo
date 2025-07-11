#!/usr/bin/env python3
"""
Simple script to run dockevOS in interactive mode.
"""
import asyncio
from dockevos.__main__ import ContainerOSMVP

async def main():
    """Run the application."""
    app = ContainerOSMVP()
    await app.start()

if __name__ == "__main__":
    asyncio.run(main())
