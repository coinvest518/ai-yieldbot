"""Composio tool integrations for AI Agent YBot - Twitter, Telegram & Image Generation."""

import base64
import requests
import json
import os
import time
from datetime import datetime
from typing import List, Optional
from langchain_core.tools import BaseTool
from src.config import config


def get_twitter_tools(user_id: Optional[str] = None) -> List[BaseTool]:
    """Get Twitter tools using Composio API with connected account."""
    from langchain_core.tools import tool
    
    @tool
    def twitter_upload_media(image_url: str) -> dict:
        """Upload media from URL to Twitter and get media_id."""
        print(f"\n[TWITTER UPLOAD] Uploading media: {image_url[:80]}")
        
        try:
            # Download the image
            print(f"[TWITTER UPLOAD] Downloading image from URL...")
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            
            # Encode as base64
            image_data = base64.b64encode(image_response.content).decode('utf-8')
            print(f"[TWITTER UPLOAD] Encoded image to base64 ({len(image_data)} chars)")
            
            url = "https://backend.composio.dev/api/v3/tools/execute/TWITTER_UPLOAD_MEDIA"
            headers = {
                "x-api-key": config.COMPOSIO_API_KEY,
                "Content-Type": "application/json"
            }
            
            payload = {
                "connected_account_id": config.TWITTER_CONNECTED_ACCOUNT_ID,
                "user_id": config.COMPOSIO_USER_ID,
                "name": "TWITTER_UPLOAD_MEDIA",
                "arguments": {
                    "media_data": image_data,
                    "media_category": "tweet_image"
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()
            print(f"[TWITTER UPLOAD] Response: {result}")
            
            if result.get('successful'):
                media_id = result.get('data', {}).get('media_id_string')
                print(f"[TWITTER UPLOAD] Got media_id: {media_id}")
                return {"status": "success", "media_id": media_id}
            else:
                print(f"[TWITTER UPLOAD] Tool error: {result}")
                return {"status": "error", "error": result.get('error', 'Upload failed')}
        except Exception as e:
            print(f"[TWITTER UPLOAD] Error: {e}")
            return {"status": "error", "error": str(e)}
    
    @tool
    def twitter_create_post(text: str, media_media_ids: Optional[List[str]] = None) -> dict:
        """Create a tweet on Twitter with optional media IDs."""
        print(f"\n[TWITTER] Creating post: {text[:50]}")
        if media_media_ids:
            print(f"[TWITTER] With media IDs: {media_media_ids}")
        
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
                "text": text,
                "for_super_followers_only": False,
                "nullcast": False
            }
        }
        
        if media_media_ids:
            payload["arguments"]["media_media_ids"] = media_media_ids
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()
            print(f"[TWITTER] Response: {result}")
            # On success, save last successful tweet to local cache to avoid duplicate attempts
            try:
                if result.get('successful'):
                    data = result.get('data') or {}
                    # attempt to find tweet id in response
                    tweet_id = None
                    if isinstance(data, dict):
                        tweet_id = data.get('id') or (data.get('data') or {}).get('id')
                    cache_path = os.path.join(os.path.dirname(__file__), '..', 'last_tweet_cache.json')
                    with open(cache_path, 'w', encoding='utf-8') as fh:
                        json.dump({'id': tweet_id, 'text': text, 'timestamp': datetime.utcnow().isoformat()}, fh)
            except Exception as e:
                print(f"[TWITTER] Warning: failed to write last_tweet_cache: {e}")
            return result
        except Exception as e:
            print(f"[TWITTER] Error: {e}")
            return {"error": str(e)}
    
    @tool
    def twitter_reply_to_post(tweet_id: str, reply_text: str) -> dict:
        """Reply to a tweet on Twitter."""
        print(f"\n[TWITTER REPLY] Replying to tweet {tweet_id}: {reply_text[:50]}")

        url = "https://backend.composio.dev/api/v3/tools/execute/TWITTER_CREATION_OF_A_POST"
        headers = {
            "x-api-key": config.COMPOSIO_API_KEY,
            "Content-Type": "application/json"
        }

        # Try to post reply, but handle duplicate-content errors by retrying with a short unique suffix
        attempt = 0
        max_attempts = 2
        last_result = None
        while attempt < max_attempts:
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

            try:
                response = requests.post(url, json=payload, headers=headers)
                result = response.json()
                print(f"[TWITTER REPLY] Response: {result}")
                last_result = result

                # If success, return
                if result.get("successful"):
                    return result

                # If duplicate-content error, modify reply_text slightly and retry once
                resp_text = json.dumps(result) if isinstance(result, dict) else str(result)
                if response.status_code == 403 and ('duplicate' in resp_text.lower() or 'duplicate content' in resp_text.lower()):
                    attempt += 1
                    # Append a short unique suffix (timestamp) to avoid duplicate-content block
                    suffix = f" [{int(time.time())%10000}]"
                    reply_text = (reply_text[:240] + suffix) if len(reply_text) < 270 else reply_text[:270] + suffix
                    print(f"[TWITTER REPLY] Detected duplicate-content; retrying with suffix {suffix}")
                    continue

                # For other 4xx errors, try fallback create and return
                if response.status_code in (400, 403):
                    print("[TWITTER REPLY] Reply failed; attempting fallback create_post for reply_text")
                    fallback = twitter_create_post(reply_text)
                    return {"reply_result": result, "fallback_create": fallback}

                return result

            except Exception as e:
                print(f"[TWITTER REPLY] Error: {e}")
                return {"error": str(e)}

        # If we exhausted retries, return last_result
        return last_result or {"error": "Unknown reply error"}

    @tool
    def twitter_post_and_reply(tweet_text: str, reply_text: str, telegram_chat: str = "@yieldbotai") -> dict:
        """Create a tweet, then reply to it. If tweet creation is forbidden, fallback to Telegram and cache pending tweet locally."""
        print(f"\n[TWITTER COMBINED] Creating tweet and reply (tweet len={len(tweet_text)}, reply len={len(reply_text)})")

        # Duplicate check: if we have a cached last tweet with identical text, reuse it to reply instead of creating duplicate
        cache_path = os.path.join(os.path.dirname(__file__), '..', 'last_tweet_cache.json')
        tweet_id = None
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as fh:
                    last = json.load(fh)
                    if last.get('text') == tweet_text:
                        tweet_id = last.get('id')
                        print(f"[TWITTER COMBINED] Detected duplicate with last_tweet_cache id={tweet_id}; will reply instead of creating new tweet")
        except Exception as e:
            print(f"[TWITTER COMBINED] Failed to read last_tweet_cache: {e}")

        create_res = None
        if not tweet_id:
            create_res = twitter_create_post(tweet_text)
        combined = {"create": create_res}

        # determine if create was successful and extract tweet id
        tweet_id = None
        try:
            if create_res.get("successful"):
                # Composio responses can nest id differently; search common paths
                data = create_res.get("data") or {}
                if isinstance(data, dict):
                    # nested 'data' or direct 'id'
                    tweet_id = data.get("id") or (data.get("data") or {}).get("id")
        except Exception:
            tweet_id = None

        if tweet_id:
            print(f"[TWITTER COMBINED] Tweet created with id: {tweet_id}. Now replying...")
            reply_res = twitter_reply_to_post(tweet_id, reply_text)
            combined["reply"] = reply_res
            return combined

        # If create failed (eg. Forbidden), fallback behavior: save pending tweet and post to Telegram
        print("[TWITTER COMBINED] Tweet creation failed or forbidden. Saving pending tweet and posting to Telegram fallback.")
        # Save pending tweet locally for manual retry
        cache_file = f"pending_tweet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        cache_path = os.path.join(os.path.dirname(__file__), "..", cache_file)
        try:
            with open(cache_path, "w", encoding="utf-8") as fh:
                json.dump({"tweet_text": tweet_text, "reply_text": reply_text, "created_at": datetime.utcnow().isoformat()}, fh, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[TWITTER COMBINED] Failed to write pending tweet cache: {e}")

        # Post fallback to Telegram so message is visible
        bot_token = config.TELEGRAM_BOT_TOKEN
        tg_result = None
        if bot_token:
            tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            tg_payload = {"chat_id": telegram_chat, "text": tweet_text + "\n\n" + reply_text}
            try:
                tg_resp = requests.post(tg_url, json=tg_payload)
                tg_result = tg_resp.json()
            except Exception as e:
                tg_result = {"error": str(e)}

        combined["fallback"] = {"saved_to": cache_path, "telegram_post": tg_result}
        return combined
    
    tools = [twitter_upload_media, twitter_create_post, twitter_reply_to_post]
    print(f"Loaded {len(tools)} Twitter tools (Composio v3 API)")
    print(f"   User ID: {config.COMPOSIO_USER_ID}")
    print(f"   Connected Account: {config.TWITTER_CONNECTED_ACCOUNT_ID}")
    return tools


def get_telegram_tools(user_id: Optional[str] = None) -> List[BaseTool]:
    """Get Telegram bot tools using direct API."""
    from langchain_core.tools import tool
    
    @tool
    def send_telegram_message(chat_id: str, text: str) -> dict:
        """Send a message to Telegram channel or chat."""
        print(f"\n[TELEGRAM] Sending message to {chat_id}: {text[:50]}")
        
        bot_token = config.TELEGRAM_BOT_TOKEN
        if not bot_token:
            return {"error": "TELEGRAM_BOT_TOKEN not set"}
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        
        try:
            response = requests.post(url, json=data)
            result = response.json()
            print(f"[TELEGRAM] Response: {result}")
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message_id": result.get("result", {}).get("message_id"),
                    "chat_id": chat_id,
                    "text": text
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("description", "Unknown error"),
                    "chat_id": chat_id
                }
        except Exception as e:
            print(f"[TELEGRAM] Error: {e}")
            return {"status": "error", "error": str(e)}
    
    @tool
    def send_telegram_photo(chat_id: str, photo_url: str, caption: str = "") -> dict:
        """Send a photo to Telegram channel or chat. photo_url must be a valid HTTP URL."""
        print(f"\n[TELEGRAM PHOTO] Sending photo to {chat_id}: {photo_url}")
        print(f"[TELEGRAM PHOTO] Caption: {caption[:50]}")
        
        bot_token = config.TELEGRAM_BOT_TOKEN
        if not bot_token:
            return {"error": "TELEGRAM_BOT_TOKEN not set"}
        
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        data = {"chat_id": chat_id, "photo": photo_url, "caption": caption, "parse_mode": "HTML"}
        
        try:
            response = requests.post(url, json=data)
            result = response.json()
            print(f"[TELEGRAM PHOTO] Response: {result}")
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message_id": result.get("result", {}).get("message_id"),
                    "chat_id": chat_id
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("description", "Unknown error")
                }
        except Exception as e:
            print(f"[TELEGRAM PHOTO] Error: {e}")
            return {"status": "error", "error": str(e)}
    
    @tool
    def monitor_telegram_group() -> dict:
        """Monitor Telegram group for new messages and return summary."""
        print(f"\n[TELEGRAM MONITOR] Checking for new messages...")
        
        bot_token = config.TELEGRAM_BOT_TOKEN
        if not bot_token:
            return {"error": "TELEGRAM_BOT_TOKEN not set"}
        
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        
        try:
            response = requests.get(url)
            result = response.json()
            print(f"[TELEGRAM MONITOR] Got {len(result.get('result', []))} updates")
            
            if response.status_code == 200 and result.get("ok"):
                updates = result.get("result", [])
                # Simple summary - in real implementation, filter by chat_id and summarize
                summary = f"Found {len(updates)} recent messages in monitored groups"
                return {
                    "status": "success",
                    "summary": summary,
                    "message_count": len(updates)
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("description", "Failed to get updates")
                }
        except Exception as e:
            print(f"[TELEGRAM MONITOR] Error: {e}")
            return {"status": "error", "error": str(e)}
    
    tools = [send_telegram_message, send_telegram_photo, monitor_telegram_group]
    print(f"Loaded {len(tools)} Telegram tools (direct API)")
    return tools


def get_linkedin_tools(user_id: Optional[str] = None) -> List[BaseTool]:
    """Get LinkedIn tools using Composio API with connected account."""
    from langchain_core.tools import tool

    @tool
    def linkedin_get_my_info() -> dict:
        """Get LinkedIn user profile information including author_id for posting."""
        print(f"\n[LINKEDIN] Getting user profile info")

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

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            result = response.json()
            print(f"[LINKEDIN] Profile Response: {result}")
            return result
        except Exception as e:
            print(f"[LINKEDIN] Error getting profile: {e}")
            return {"error": str(e)}

    @tool
    def linkedin_create_post(commentary: str, visibility: str = "PUBLIC") -> dict:
        """Create a professional LinkedIn post."""
        print(f"\n[LINKEDIN] Creating post: {commentary[:100]}...")

        # First get author URN by fetching profile info directly
        profile_url = "https://backend.composio.dev/api/v3/tools/execute/LINKEDIN_GET_MY_INFO"
        headers = {
            "x-api-key": config.COMPOSIO_API_KEY,
            "Content-Type": "application/json"
        }

        profile_payload = {
            "connected_account_id": config.LINKEDIN_CONNECTED_ACCOUNT_ID,
            "user_id": config.COMPOSIO_USER_ID,
            "name": "LINKEDIN_GET_MY_INFO",
            "arguments": {}
        }

        author_urn = None
        try:
            profile_response = requests.post(profile_url, json=profile_payload, headers=headers, timeout=30)
            profile_result = profile_response.json()
            print(f"[LINKEDIN] Profile Response: {profile_result}")
            
            if profile_result.get('successful'):
                data = profile_result.get('data', {})
                if isinstance(data, dict):
                    author_urn = data.get('id') or (data.get('data') or {}).get('id')
        except Exception as e:
            print(f"[LINKEDIN] Failed to get profile for author URN: {e}")

        if not author_urn:
            return {"error": "Could not get LinkedIn author URN from profile"}

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
                "author": author_urn,
                "commentary": commentary,
                "visibility": visibility,
                "lifecycleState": "PUBLISHED",
                "feedDistribution": "MAIN_FEED",
                "isReshareDisabledByAuthor": False
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            result = response.json()
            print(f"[LINKEDIN] Post Response: {result}")
            return result
        except Exception as e:
            print(f"[LINKEDIN] Error creating post: {e}")
            return {"error": str(e)}

    tools = [linkedin_get_my_info, linkedin_create_post]
    print(f"Loaded {len(tools)} LinkedIn tools (Composio v3 API)")
    print(f"   User ID: {config.COMPOSIO_USER_ID}")
    print(f"   Connected Account: {config.LINKEDIN_CONNECTED_ACCOUNT_ID}")
    return tools


def get_image_generation_tools() -> List[BaseTool]:
    """Get image generation tools using Pollinations AI - NFT/Crypto themed."""
    from langchain_core.tools import tool
    from urllib.parse import quote
    
    @tool
    def generate_nft_image(topic: str = "DeFi", save_path: str = "nft_image.png") -> dict:
        """Generate NFT-style crypto art for tweets. Returns file path and URL."""
        print(f"\n[IMAGE GEN] Generating NFT image for topic: {topic}")
        print(f"[IMAGE GEN] Save path: {save_path}")
        
        try:
            nft_prompts = {
                "DeFi": "Holographic NFT of glowing DeFi dashboard with neon blue and purple lights, blockchain network nodes, animated digital currency symbols, cyberpunk aesthetic, high quality digital art",
                "Bitcoin": "Futuristic holographic Bitcoin coin with neon orange glow, floating in digital space with blockchain particles, cyberpunk style, glowing edges, 3D rendered",
                "Ethereum": "Ethereal holographic Ethereum crystal with purple neon light, surrounded by floating blockchain nodes and digital code, cyberpunk aesthetic, glowing aura",
                "Crypto": "Neon cyberpunk crypto landscape with holographic coins, glowing blockchain network, digital currency symbols, animated particles, futuristic digital art",
                "AI": "AI-powered holographic neural network with glowing nodes, neon blue and purple lights, blockchain integration, cyberpunk digital art, animated feel",
                "Trading": "Holographic trading dashboard with neon charts and graphs, glowing candlesticks, blockchain elements, cyberpunk aesthetic, digital art"
            }
            
            prompt = nft_prompts.get(topic, nft_prompts["Crypto"])
            print(f"[IMAGE GEN] Prompt: {prompt[:80]}")
            
            url = f"https://image.pollinations.ai/prompt/{quote(prompt)}"
            params = {"width": 1024, "height": 1024, "model": "flux"}
            
            print(f"[IMAGE GEN] Requesting from Pollinations API")
            response = requests.get(url, params=params, timeout=60)
            print(f"[IMAGE GEN] Response status: {response.status_code}")
            
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                
                print(f"[IMAGE GEN] SUCCESS - Image saved: {save_path}")
                image_url = f"https://image.pollinations.ai/prompt/{quote(prompt)}"
                return {
                    "status": "success",
                    "file_path": save_path,
                    "image_url": image_url,
                    "topic": topic
                }
            else:
                print(f"[IMAGE GEN] ERROR - Status {response.status_code}: {response.text[:100]}")
                return {
                    "status": "error",
                    "message": response.text,
                    "topic": topic
                }
        except Exception as e:
            print(f"[IMAGE GEN] ERROR: {e}")
            return {
                "status": "error",
                "message": str(e),
                "topic": topic
            }
    
    return [generate_nft_image]


def get_analytics_tools() -> List[BaseTool]:
    """Get analytics tools for analyzing Twitter data."""
    from langchain_core.tools import tool
    from datetime import datetime
    
    @tool
    def analyze_tweet_performance(tweet_id: str) -> dict:
        """Analyze the performance of a tweet."""
        return {
            "tweet_id": tweet_id,
            "status": "placeholder",
            "message": "Implement with Twitter API v2 to get real metrics",
            "analyzed_at": datetime.now().isoformat()
        }
    
    @tool
    def get_current_time() -> str:
        """Get the current date and time."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return [analyze_tweet_performance, get_current_time]


def get_firecrawl_tools() -> List[BaseTool]:
    """Get Firecrawl tools for searching and scraping DeFi/crypto news."""
    from langchain_core.tools import tool
    from datetime import datetime
    import json
    import os
    
    FIRECRAWL_API_KEY = config.FIRECRAWL_API_KEY
    
    @tool
    def search_defi_news(query: str, limit: int = 5) -> dict:
        """Search for DeFi/crypto news and data. USE SPARINGLY - max 1x per day!"""
        print(f"\n[FIRECRAWL] Searching: {query}")
        
        if not FIRECRAWL_API_KEY:
            return {"error": "FIRECRAWL_API_KEY not set"}
        
        try:
            from firecrawl import Firecrawl
            
            fc = Firecrawl(api_key=FIRECRAWL_API_KEY)
            results = fc.search(query=query, limit=limit)
            
            if hasattr(results, '__dict__'):
                results_dict = results.__dict__
            elif hasattr(results, 'data'):
                results_dict = {"data": results.data}
            else:
                results_dict = {"raw": str(results)}
            
            cache_file = f"daily_research_{datetime.now().strftime('%Y%m%d')}.json"
            cache_path = os.path.join(os.path.dirname(__file__), "..", cache_file)
            
            cache_data = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "results": results_dict
            }
            
            with open(cache_path, "w") as f:
                json.dump(cache_data, f, indent=2, default=str)
            
            result_count = 0
            if hasattr(results, 'data') and results.data:
                result_count = len(results.data) if isinstance(results.data, list) else 1
            
            print(f"[FIRECRAWL] Found {result_count} results")
            return {
                "status": "success",
                "query": query,
                "result_count": result_count,
                "results": results_dict,
                "cached_to": cache_file,
                "note": "Results cached! Use get_cached_research() for rest of day."
            }
            
        except Exception as e:
            print(f"[FIRECRAWL] Error: {e}")
            return {"error": str(e), "query": query}
    
    @tool
    def scrape_page(url: str) -> dict:
        """Scrape a specific page for content. USE SPARINGLY!"""
        print(f"\n[FIRECRAWL] Scraping: {url}")
        
        if not FIRECRAWL_API_KEY:
            return {"error": "FIRECRAWL_API_KEY not set"}
        
        try:
            from firecrawl import Firecrawl
            
            fc = Firecrawl(api_key=FIRECRAWL_API_KEY)
            result = fc.scrape(url, formats=["markdown"])
            
            # Handle Document object from Firecrawl
            if hasattr(result, 'markdown'):
                # Document object has attributes, not dict methods
                content = getattr(result, 'markdown', '')
                # Metadata is also an object with attributes
                metadata = getattr(result, 'metadata', None)
                title = getattr(metadata, 'title', '') if metadata else ''
                markdown = content
            else:
                # Fallback for dict response (older API versions)
                content = result.get("data", {}).get("content", "")
                title = result.get("data", {}).get("metadata", {}).get("title", "")
                markdown = result.get("data", {}).get("markdown", content)
            
            return {
                "status": "success",
                "url": url,
                "title": title,
                "content": markdown[:3000] if markdown else content[:3000],
                "note": "Content truncated to 3000 chars to save tokens"
            }
            
        except Exception as e:
            print(f"[FIRECRAWL] Error: {e}")
            return {"error": str(e), "url": url}
    
    @tool
    def scrape_yieldbot_website() -> dict:
        """Scrape yieldbot.cc website for real token data, trends, and fundraiser info."""
        print(f"\n[YIELDBOT SCRAPE] Scraping yieldbot.cc for real data...")
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get("https://yieldbot.cc", timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text(separator=' ', strip=True)
            
            # Look for specific patterns
            token_info = []
            
            # Find mentions of tokens, prices, etc.
            if '$YBOT' in text_content:
                token_info.append("$YBOT token mentioned")
            
            # Look for price patterns
            import re
            price_patterns = re.findall(r'\$\d+\.?\d*|\d+\.?\d*\s*(?:USD|price)', text_content)
            if price_patterns:
                token_info.append(f"Found price data: {', '.join(price_patterns[:3])}")
            
            # Look for trending/rising patterns
            trend_keywords = ['pump', 'moon', 'bullish', 'rising', 'up', 'growth', 'surge']
            trend_mentions = [word for word in trend_keywords if word in text_content.lower()]
            if trend_mentions:
                token_info.append(f"Trend indicators: {', '.join(trend_mentions)}")
            
            # Extract key sections
            content_summary = text_content[:3000]  # Limit for token usage
            
            token_data = {
                "status": "success",
                "url": "https://yieldbot.ai",
                "content_length": len(text_content),
                "summary": content_summary,
                "extracted_info": token_info,
                "note": "Direct scrape of yieldbot.ai - real token data, trends, fundraiser info"
            }
            
            print(f"[YIELDBOT SCRAPE] Scraped {len(text_content)} chars, found {len(token_info)} data points")
            return token_data
            
        except Exception as e:
            print(f"[YIELDBOT SCRAPE] Error: {e}")
            return {"error": str(e), "url": "https://yieldbot.ai"}

    def _fc_scrape_with_backoff(fc, url, formats=None, maxAge=3600000, max_retries=2):
        """Helper: call Firecrawl.scrape with simple backoff on transient errors and return Document/dict or error."""
        formats = formats or ["markdown"]
        attempt = 0
        while attempt <= max_retries:
            try:
                if maxAge is not None:
                    return fc.scrape(url, formats=formats, max_age=maxAge)
                return fc.scrape(url, formats=formats)
            except Exception as e:
                err = str(e)
                print(f"[FIRECRAWL BACKOFF] Attempt {attempt} error for {url}: {err}")
                # If rate limit, surface it immediately
                if 'Rate Limit' in err or 'rate limit' in err or 'RateLimit' in err:
                    return {"error": err}
                # transient network or engine errors -> backoff and retry
                attempt += 1
                wait = 1 + attempt * 2
                time.sleep(wait)
        return {"error": f"Failed after {max_retries} retries: {url}"}

    @tool
    def fast_scrape_and_cache(force_refresh: bool = False) -> dict:
        """Perform one regulated fast scrape+crawl of selected sources and cache results for the day.

        - Limits the number of target URLs to avoid burning credits
        - Uses Firecrawl `maxAge` caching to reduce fresh scrapes
        - Saves consolidated output to `daily_research_YYYYMMDD.json` for rest-of-day usage
        """
        print("\n[FIRECRAWL FAST] Starting fast regulated scrape and cache")

        if not FIRECRAWL_API_KEY:
            return {"error": "FIRECRAWL_API_KEY not set"}

        # Targets (keep this list small to control credits)
        targets = [
            "https://yieldbot.cc",
            "https://coinmarketcap.com/trending-cryptocurrencies/",
            "https://www.coingecko.com/en/highlights/trending-crypto",
            "https://www.coindesk.com/markets/",
            "https://www.theblock.co/latest",
        ]

        cache_file = f"daily_research_{datetime.now().strftime('%Y%m%d')}.json"
        cache_path = os.path.join(os.path.dirname(__file__), "..", cache_file)

        # If cached and not forcing refresh, return it
        try:
            if os.path.exists(cache_path) and not force_refresh:
                mtime = os.path.getmtime(cache_path)
                age_seconds = time.time() - mtime
                # Use cached file for up to 24 hours
                if age_seconds < 86400:
                    print(f"[FIRECRAWL FAST] Using existing cache ({cache_file}), age {int(age_seconds)}s")
                    with open(cache_path, "r", encoding="utf-8") as fh:
                        return json.load(fh)
        except Exception as e:
            print(f"[FIRECRAWL FAST] Cache check error: {e}")

        from firecrawl import Firecrawl
        fc = Firecrawl(api_key=FIRECRAWL_API_KEY)

        results = {"timestamp": datetime.now().isoformat(), "data": []}

        for url in targets:
            print(f"[FIRECRAWL FAST] Scraping (cached maxAge=1h): {url}")
            res = _fc_scrape_with_backoff(fc, url, formats=["markdown"], maxAge=3600000, max_retries=2)
            # If we get a dict-like error, record and break on rate-limit
            if isinstance(res, dict) and res.get("error"):
                results["data"].append({"url": url, "error": res.get("error")})
                if 'Rate Limit' in res.get("error") or 'rate limit' in res.get("error"):
                    print("[FIRECRAWL FAST] Rate limit encountered; stopping further scrapes")
                    break
                continue

            # Normalize Document or dict response
            try:
                if hasattr(res, 'markdown'):
                    content = getattr(res, 'markdown', '')
                    metadata = getattr(res, 'metadata', None)
                    if metadata and hasattr(metadata, '__dict__'):
                        meta_dict = {k: v for k, v in vars(metadata).items() if not k.startswith('_')}
                    else:
                        meta_dict = metadata if isinstance(metadata, dict) else {}
                    title = meta_dict.get('title', '') if isinstance(meta_dict, dict) else getattr(metadata, 'title', '') if metadata else ''
                else:
                    content = res.get('markdown') or res.get('data', {}).get('markdown') or ''
                    meta_dict = res.get('data', {}).get('metadata', {}) if isinstance(res, dict) else {}
                    title = meta_dict.get('title', '')
            except Exception as e:
                print(f"[FIRECRAWL FAST] Normalization error for {url}: {e}")
                results["data"].append({"url": url, "error": str(e)})
                continue

            snippet = (content or '')[:4000]
            results["data"].append({"url": url, "title": title, "snippet": snippet})
            # small pause to spread requests
            time.sleep(1)

        # Save consolidated cache
        try:
            with open(cache_path, "w", encoding="utf-8") as fh:
                json.dump(results, fh, ensure_ascii=False, indent=2)
            print(f"[FIRECRAWL FAST] Cached results to {cache_file}")
        except Exception as e:
            print(f"[FIRECRAWL FAST] Failed to write cache: {e}")

        return results
    
    @tool
    def get_cached_research() -> dict:
        """Get today's cached research data. Use this instead of new searches!"""
        print(f"\n[RESEARCH] Getting cached research")
        
        import os
        
        cache_file = f"daily_research_{datetime.now().strftime('%Y%m%d')}.json"
        cache_path = os.path.join(os.path.dirname(__file__), "..", cache_file)
        
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                data = json.load(f)
                print(f"[RESEARCH] Found cached data")
                return {
                    "status": "success",
                    "source": cache_file,
                    "data": data
                }
        else:
            print(f"[RESEARCH] No cached data found")
            return {
                "status": "no_cache",
                "message": "No cached research for today. Run search_defi_news() once.",
                "date": datetime.now().strftime('%Y-%m-%d')
            }
    
    return [search_defi_news, fast_scrape_and_cache, scrape_page, scrape_yieldbot_website, get_cached_research]


def get_all_tools(user_id: Optional[str] = None) -> List[BaseTool]:
    """Get all available tools for the agent."""
    all_tools = []
    
    all_tools.extend(get_twitter_tools(user_id))
    all_tools.extend(get_telegram_tools(user_id))
    all_tools.extend(get_linkedin_tools(user_id))
    all_tools.extend(get_image_generation_tools())
    all_tools.extend(get_firecrawl_tools())
    all_tools.extend(get_analytics_tools())
    
    return all_tools
