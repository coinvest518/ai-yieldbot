#!/usr/bin/env python3
"""
Test script for Twitter functionality only.
Tests the fixed Composio user ID and Twitter posting.
"""

import requests
from src.config import config

def test_twitter_create():
    """Test Twitter create post functionality."""
    print("=== Twitter Create Test ===")
    print(f"Using COMPOSIO_USER_ID: {config.COMPOSIO_USER_ID}")
    print(f"Using TWITTER_CONNECTED_ACCOUNT_ID: {config.TWITTER_CONNECTED_ACCOUNT_ID}")

    # Test tweet content
    test_tweet = "$YBOT Test: This is a test tweet to verify Twitter integration works. #Test"

    url = "https://backend.composio.dev/api/v3/tools/execute/TWITTER_CREATION_OF_A_POST"
    headers = {
        "x-api-key": config.COMPOSIO_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "connected_account_id": config.TWITTER_CONNECTED_ACCOUNT_ID,
        "user_id": config.COMPOSIO_USER_ID,
        "name": "TWITTER_CREATION_OF_A_POST",
        "arguments": {
            "text": test_tweet,
            "for_super_followers_only": False,
            "nullcast": False
        }
    }

    print(f"\nCreating test tweet: {test_tweet}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        print(f"Response: {result}")

        if result.get('successful'):
            print("✅ Create successful!")
            data = result.get('data', {})
            tweet_data = data.get('data', {})
            tweet_id = tweet_data.get('id') or tweet_data.get('rest_id')
            if tweet_id:
                print(f"Tweet ID: {tweet_id}")
                return tweet_id
            else:
                print("❌ No tweet ID found")
                return None
        else:
            print("❌ Create failed")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_twitter_reply(tweet_id: str):
    """Test Twitter reply functionality."""
    print(f"\n=== Twitter Reply Test ===")
    print(f"Replying to tweet ID: {tweet_id}")

    reply_text = "Test reply: Integration successful! Check out https://yieldbot.cc"

    url = "https://backend.composio.dev/api/v3/tools/execute/TWITTER_CREATION_OF_A_POST"
    headers = {
        "x-api-key": config.COMPOSIO_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "connected_account_id": config.TWITTER_CONNECTED_ACCOUNT_ID,
        "user_id": config.COMPOSIO_USER_ID,
        "name": "TWITTER_CREATION_OF_A_POST",
        "arguments": {
            "text": reply_text,
            "reply": {"in_reply_to_tweet_id": tweet_id},
            "for_super_followers_only": False,
            "nullcast": False
        }
    }

    print(f"Replying with: {reply_text}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        print(f"Response: {result}")

        if result.get('successful'):
            print("✅ Reply successful!")
            return True
        else:
            print("❌ Reply failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run the Twitter tests."""
    tweet_id = test_twitter_create()
    if tweet_id:
        test_twitter_reply(tweet_id)
        print("\n✅ All Twitter tests passed!")
    else:
        print("\n❌ Twitter tests failed!")
        return 1
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())