#!/usr/bin/env python3
"""One-shot scheduler runner for Railway Scheduled Job.

This script runs a single autonomous post cycle and exits. It's intended
to be used by Railway Scheduled Jobs or any cron-like scheduler that runs
the repository code periodically.
"""
import sys

from src.config import config
from src.agent import create_twitter_agent, run_autonomous_post


def main():
    try:
        config.validate()
    except Exception as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        agent = create_twitter_agent()
    except Exception as e:
        print(f"Failed to create agent: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        print("Running one-shot autonomous post cycle...")
        run_autonomous_post(agent)
        print("One-shot run completed.")
        sys.exit(0)
    except Exception as e:
        import traceback

        print("Error during one-shot run:", file=sys.stderr)
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
