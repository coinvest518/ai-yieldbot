#!/usr/bin/env python3
"""Check the status of the running agent scheduler."""

import json
import sys
from pathlib import Path

def main():
    status_file = Path("agent_status.json")

    if not status_file.exists():
        print("❌ No status file found. Agent may not have run yet.")
        return

    try:
        with open(status_file, "r") as f:
            status = json.load(f)

        print("🤖 YBot Agent Status")
        print("=" * 30)
        print(f"Last Run: {status.get('last_run', 'Never')}")
        print(f"Status: {status.get('status', 'Unknown')}")

        results = status.get('results', {})
        if results:
            print("\n📊 Last Results:")
            for platform, result in results.items():
                print(f"  {platform.title()}: {result}")
        else:
            print("\n📊 No results recorded yet")

    except Exception as e:
        print(f"❌ Error reading status: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()