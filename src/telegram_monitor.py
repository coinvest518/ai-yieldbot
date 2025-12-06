"""Telegram Group Monitor Subagent for YBot.

This subagent monitors Telegram groups and REPORTS to the main agent.
It does NOT respond directly - it collects messages and lets main agent decide.

Flow:
1. Monitor checks for new messages (TELEGRAM_GET_UPDATES)
2. Collects and summarizes messages
3. Saves to daily report file
4. Main agent reads report and decides responses
"""

import time
import json
import os
from datetime import datetime
from typing import Optional
from src.config import config
from src.tools import get_telegram_tools


def get_updates_simple() -> dict:
    """
    Get Telegram updates using Composio tools directly.
    Returns raw updates for main agent to process.
    """
    tools = get_telegram_tools()
    
    # Find the GET_UPDATES tool
    get_updates_tool = None
    for tool in tools:
        if "GET_UPDATES" in tool.name:
            get_updates_tool = tool
            break
    
    if not get_updates_tool:
        return {"error": "TELEGRAM_GET_UPDATES tool not found"}
    
    try:
        result = get_updates_tool.invoke({})
        return {"status": "success", "updates": result}
    except Exception as e:
        return {"error": str(e)}


def save_daily_report(messages: list, report_type: str = "telegram"):
    """
    Save messages to daily report file for main agent to review.
    
    Args:
        messages: List of messages/updates
        report_type: Type of report (telegram, mentions, commands)
    """
    date_str = datetime.now().strftime('%Y%m%d')
    report_file = f"daily_{report_type}_report_{date_str}.json"
    report_path = os.path.join(os.path.dirname(__file__), "..", report_file)
    
    # Load existing report if exists
    existing = []
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            data = json.load(f)
            existing = data.get("messages", [])
    
    # Append new messages
    existing.extend(messages)
    
    report = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "last_updated": datetime.now().isoformat(),
        "message_count": len(existing),
        "messages": existing
    }
    
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    return report_path


def check_and_report():
    """
    Check for new Telegram messages and save report for main agent.
    Does NOT respond - just collects data.
    """
    print(f"📡 Checking Telegram updates... ({datetime.now().strftime('%H:%M:%S')})")
    
    result = get_updates_simple()
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return None
    
    updates = result.get("updates", [])
    
    if updates:
        report_path = save_daily_report(updates)
        print(f"✅ Saved {len(updates)} updates to report")
        print(f"   Report: {report_path}")
        print(f"   Main agent can now review and respond")
    else:
        print("   No new updates")
    
    return result


def get_todays_report() -> dict:
    """
    Get today's Telegram report for main agent to review.
    """
    date_str = datetime.now().strftime('%Y%m%d')
    report_file = f"daily_telegram_report_{date_str}.json"
    report_path = os.path.join(os.path.dirname(__file__), "..", report_file)
    
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            return json.load(f)
    
    return {"status": "no_report", "date": datetime.now().strftime('%Y-%m-%d')}


def run_monitor_loop(interval_seconds: int = 1800):
    """
    Run the monitoring loop. Checks and saves reports.
    Main agent reviews reports separately.
    
    Args:
        interval_seconds: Time between checks (default 30 mins = 1800 seconds)
    """
    print(f"🤖 Starting Telegram Monitor (every {interval_seconds}s)")
    print(f"   Bot: @ybotai_bot")
    print(f"   Mode: COLLECT ONLY (main agent responds)")
    print(f"   Press Ctrl+C to stop")
    print()
    
    while True:
        try:
            check_and_report()
            print(f"   Next check in {interval_seconds//60} minutes...")
            print()
            time.sleep(interval_seconds)
            
        except KeyboardInterrupt:
            print("\n👋 Monitor stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        check_and_report()
    elif len(sys.argv) > 1 and sys.argv[1] == "--report":
        report = get_todays_report()
        print(json.dumps(report, indent=2))
    else:
        interval = int(sys.argv[1]) if len(sys.argv) > 1 else 1800
        run_monitor_loop(interval)
