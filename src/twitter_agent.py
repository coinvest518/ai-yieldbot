"""Twitter Agent - Handles autonomous Twitter posting with images."""

import sys
from src.config import config
from src.tools import get_all_tools


TWITTER_AGENT_PROMPT = """You are YBot, an AUTONOMOUS Twitter agent for Yieldbot ($YBOT).

## WORKFLOW - 4 STEPS:
1. Generate NFT image: generate_nft_image(topic="DeFi", save_path="nft_image.png")
   - Returns: {"status": "success", "image_url": "https://..."}
   
2. Upload media to Twitter: twitter_upload_media(image_url=image_url_from_step_1)
   - Returns: {"status": "success", "media_id": "1234567890"}
   - WAIT for media_id before proceeding
   
3. Write tweet (280 chars max, include $YBOT, 2-3 hashtags, NO EMOJIS)
   
4. Post to Twitter with media: twitter_create_post(text=tweet_text, media_media_ids=[media_id_from_step_2])
   - Pass media_id in array format

CRITICAL:
- NO EMOJIS in tweet text
- Max 280 characters
- Use $YBOT token symbol
- Include hashtags: #DeFi #AI #Crypto
- ALWAYS upload media first and get media_id
- ALWAYS pass media_id as array: [media_id]

## NEVER:
- Ask for approval
- Use write_todos
- Edit files
- Repeat the same post
- Use emojis
- Skip media upload step

Just execute the 4 steps above.
"""


def create_twitter_agent():
    """Create Twitter agent for autonomous posting."""
    from deepagents import create_deep_agent
    from langchain.chat_models import init_chat_model
    
    model = init_chat_model(
        model=config.MISTRAL_MODEL,
        model_provider="mistralai",
        api_key=config.MISTRAL_API_KEY,
        temperature=0.3,
    )
    
    tools = get_all_tools()
    
    agent = create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=TWITTER_AGENT_PROMPT,
    )
    
    return agent


def run_twitter_post(agent=None, thread_id: str = None) -> str:
    """Run autonomous Twitter post."""
    import uuid
    
    if agent is None:
        agent = create_twitter_agent()
    
    config_dict = {
        "configurable": {
            "thread_id": thread_id or str(uuid.uuid4())
        }
    }
    
    command = "Create and post unique DeFi content NOW. Generate image, upload to Twitter, write tweet, post with media. NO EMOJIS."
    
    result = agent.invoke(
        {"messages": [{"role": "user", "content": command}]},
        config=config_dict
    )
    
    if "messages" in result and result["messages"]:
        return result["messages"][-1].content
    
    return str(result)


def main():
    """Main entry point for Twitter agent."""
    import uuid
    
    print("=" * 65)
    print("Twitter Agent - YBot Autonomous Posting")
    print("=" * 65)
    
    try:
        config.validate()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
    
    if config.setup_tracing():
        print(f"LangSmith tracing enabled -> Project: {config.LANGSMITH_PROJECT}")
    
    print("Initializing Twitter Agent...")
    try:
        agent = create_twitter_agent()
        print("Agent ready!\n")
    except Exception as e:
        print(f"Failed to create agent: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    thread_id = str(uuid.uuid4())
    print(f"Thread ID: {thread_id}\n")
    
    print("Running autonomous Twitter post...\n")
    response = run_twitter_post(agent, thread_id)
    
    print("\nRESULT: Post completed!\n")
    print("Check Twitter for the post.\n")


if __name__ == "__main__":
    main()
