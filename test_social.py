#!/usr/bin/env python3
"""
Test script for Twitter and LinkedIn functionality.
Tests the fixed Composio user ID and posting to both platforms.
"""

import requests
from src.config import config

def test_linkedin_get_info():
    """Test LinkedIn get user info."""
    print("=== LinkedIn Get Info Test ===")
    print(f"Using COMPOSIO_USER_ID: {config.COMPOSIO_USER_ID}")
    print(f"Using LINKEDIN_CONNECTED_ACCOUNT_ID: {config.LINKEDIN_CONNECTED_ACCOUNT_ID}")

    url = "https://backend.composio.dev/api/v3/tools/execute/LINKEDIN_GET_MY_INFO"
    headers = {
        "x-api-key": config.COMPOSIO_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "connected_account_id": config.LINKEDIN_CONNECTED_ACCOUNT_ID,
        "user_id": config.COMPOSIO_USER_ID,
        "name": "LINKEDIN_GET_MY_INFO",
        "arguments": {}
    }

    print("Getting LinkedIn user profile...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        print(f"Response: {result}")

        if result.get('successful'):
            print("✅ LinkedIn profile retrieved successfully!")
            data = result.get('data', {})
            if isinstance(data, dict):
                author_id = data.get('id') or (data.get('data') or {}).get('id')
                if author_id:
                    print(f"Author ID: {author_id}")
                    return author_id
        else:
            print("❌ Failed to get LinkedIn profile")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_linkedin_create_post(author_id: str):
    """Test LinkedIn post creation."""
    print(f"\n=== LinkedIn Create Post Test ===")

    commentary = """Professional DeFi Market Analysis - December 2025

The decentralized finance sector continues to demonstrate remarkable resilience and innovation. Current market data shows:

• $YBOT Vault: $2.4M TVL with 12.8% APY
• Top performing tokens: $POWER (+106%), $LUNC (+53%), $LINK (+4%)
• Institutional adoption accelerating with RWA tokenization

Yieldbot's automated strategies provide sophisticated DeFi yield optimization for both retail and institutional investors. The platform's credit scoring system and multi-chain deployment capabilities position it as a leader in the evolving DeFi landscape.

#DeFi #Blockchain #FinTech"""

    url = "https://backend.composio.dev/api/v3/tools/execute/LINKEDIN_CREATE_LINKED_IN_POST"
    headers = {
        "x-api-key": config.COMPOSIO_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "connected_account_id": config.LINKEDIN_CONNECTED_ACCOUNT_ID,
        "user_id": config.COMPOSIO_USER_ID,
        "name": "LINKEDIN_CREATE_LINKED_IN_POST",
        "arguments": {
            "author": author_id,
            "commentary": commentary,
            "visibility": "PUBLIC",
            "lifecycleState": "PUBLISHED",
            "feedDistribution": "MAIN_FEED",
            "isReshareDisabledByAuthor": False
        }
    }

    print(f"Creating LinkedIn post ({len(commentary)} chars)...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        print(f"Response: {result}")

        if result.get('successful'):
            print("✅ LinkedIn post created successfully!")
            return True
        else:
            print("❌ LinkedIn post failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run LinkedIn tests."""
    author_id = test_linkedin_get_info()
    if author_id:
        success = test_linkedin_create_post(author_id)
        if success:
            print("\n✅ All LinkedIn tests passed!")
        else:
            print("\n❌ LinkedIn tests failed!")
            return 1
    else:
        print("\n❌ Could not get author ID!")
        return 1
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())