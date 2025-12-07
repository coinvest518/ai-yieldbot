#!/usr/bin/env python3
"""Background scheduler for autonomous agent execution."""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import config
from src.agent import create_twitter_agent, run_autonomous_post

logger = logging.getLogger(__name__)

# Status file to track last run
STATUS_FILE = Path("agent_status.json")

# Global status
last_run_status = {
    "last_run": None,
    "status": "Never run",
    "results": {}
}


def save_status(status: dict) -> None:
    """Save agent status to file."""
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump(status, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Failed to save status: {e}")


def load_status() -> dict:
    """Load agent status from file."""
    global last_run_status
    try:
        if STATUS_FILE.exists():
            with open(STATUS_FILE, "r") as f:
                last_run_status = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load status: {e}")
    return last_run_status


async def run_agent_task() -> dict:
    """Run the agent and return results."""
    logger.info("Scheduled agent run starting...")

    try:
        # Validate config
        config.validate()

        # Create agent
        agent = create_twitter_agent()

        # Run agent
        result = run_autonomous_post(agent)

        # Update status
        status = {
            "last_run": datetime.now().isoformat(),
            "status": "Success",
            "results": {
                "tweet": result.get("tweet_text", "N/A") if isinstance(result, dict) else "Posted",
                "linkedin": result.get("linkedin_text", "N/A") if isinstance(result, dict) else "Posted",
                "telegram": "Posted" if result else "Failed",
                "twitter_status": "Posted" if result else "Failed",
                "linkedin_status": "Posted" if result else "Failed"
            }
        }

        logger.info("Agent run completed successfully")

    except Exception as e:
        logger.exception("Agent run failed")
        status = {
            "last_run": datetime.now().isoformat(),
            "status": f"Failed: {str(e)}",
            "results": {}
        }

    # Save and return
    global last_run_status
    last_run_status = status
    save_status(status)
    return status


def start_scheduler() -> AsyncIOScheduler:
    """Start the background scheduler."""
    scheduler = AsyncIOScheduler()

    # Run every 90 minutes (to respect LinkedIn rate limits)
    scheduler.add_job(
        run_agent_task,
        'interval',
        minutes=90,
        id='agent_task',
        name='Run YBot Agent',
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started - agent will run every 90 minutes")

    # Load existing status
    load_status()

    return scheduler


def get_status() -> dict:
    """Get current agent status."""
    return last_run_status


async def main():
    """Main entry point for continuous scheduling."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Ensure Google credential env vars are not present at runtime
    import os
    for _k in ("GOOGLE_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT", "GOOGLE_OAUTH_ACCESS_TOKEN"):
        os.environ.pop(_k, None)

    try:
        # Validate config on startup
        config.validate()
        logger.info("Configuration validated successfully")

        # Start scheduler
        scheduler = start_scheduler()

        # Run initial task immediately
        logger.info("Running initial agent task...")
        await run_agent_task()

        # Keep the event loop running
        logger.info("Scheduler is running. Press Ctrl+C to stop.")

        # Wait indefinitely
        try:
            while True:
                await asyncio.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Shutting down scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler stopped.")

    except Exception as e:
        logger.exception("Failed to start scheduler")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
