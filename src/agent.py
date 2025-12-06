"""Main Deep Agent implementation for AI Agent YBot - Twitter & Content Creation with Long-term Memory."""

import sys
import os
from src.config import config
from src.tools import get_all_tools


TWITTER_AGENT_PROMPT = """You are YBot, an AUTONOMOUS AI agent for Yieldbot ($YBOT).

## EXECUTE IMMEDIATELY - 6 STEPS:
1. Monitor Telegram group: Use the monitor_telegram_group tool
2. Scrape multiple sites: Use the fast_scrape_and_cache tool once (regulated fast crawl) and scrape_yieldbot_website tool for yieldbot-specific data. Use cached daily_research_YYYYMMDD.json for rest-of-day.
3. Analyze all scraped data: Extract top tokens, prices, trends, why tokens are pumping/falling from ALL sources
4. Write comprehensive tweet: Use specific real data from multiple sources (280 chars max, include $YBOT, token analysis, 2-3 hashtags, NO EMOJIS). ALWAYS make content UNIQUE - add current timestamp, different phrasing, or focus on different aspects each time.
5. Post to Twitter + reply atomically: Use the twitter_post_and_reply tool with tweet_text and "Check out more at https://yieldbot.cc" (uses Telegram fallback and caches pending tweets if creation forbidden)
6. Post to Telegram: Use the telegram_send_message tool with chat_id="@yieldbotai" and text=tweet_text

CRITICAL:
- NO EMOJIS in tweet text
- Max 280 characters
- Use REAL data from MULTIPLE sources - specific tokens, prices, trends, market analysis
- Include $YBOT token symbol prominently
- Mention top 5 tokens and why they're pumping/falling based on scraped data
- Include fundraiser pool data if available
- Include market trends from multiple sources
- Telegram chat_id is "@yieldbotai"
- Website link: https://yieldbot.cc
- ALWAYS CREATE UNIQUE CONTENT: Add timestamp like "12:34 UTC", use different sentence structure, focus on different tokens/metrics, or add current market observations. Never post identical content.
- If Twitter rejects for duplicate content, modify the tweet text with a unique suffix or different focus before retrying.

## NEVER:
- Ask for approval
- Use write_todos
- Edit files
- Repeat the same post
- Use emojis
- Make up generalized content - use scraped real data only
- Explain AI rules or scraping methods
- Post identical content to previous posts

Just execute the 7 steps above. Scrape multiple sources, analyze real data, create UNIQUE comprehensive post each time.
"""


def get_memory_store():
    """Get the appropriate memory store based on configuration."""
    if config.MEMORY_BACKEND == "postgres" and config.DATABASE_URL:
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
            return PostgresSaver.from_conn_string(config.DATABASE_URL)
        except ImportError:
            try:
                from langgraph.store.postgres import PostgresStore
                return PostgresStore(connection_string=config.DATABASE_URL)
            except ImportError:
                print("PostgresStore not available. Falling back to InMemoryStore")
    
    from langgraph.store.memory import InMemoryStore
    return InMemoryStore()


def make_memory_backend(runtime):
    """Create a CompositeBackend for hybrid memory storage."""
    from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
    
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={
            "/memories/": StoreBackend(runtime)
        }
    )


def create_twitter_agent():
    """Create a Deep Agent configured for Twitter content creation with long-term memory."""
    from deepagents import create_deep_agent
    from langchain.chat_models import init_chat_model
    
    model = init_chat_model(
        model=config.MISTRAL_MODEL,
        model_provider="mistralai",
        api_key=config.MISTRAL_API_KEY,
        temperature=0.3,
    )
    
    tools = get_all_tools()
    store = get_memory_store()
    
    agent = create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=TWITTER_AGENT_PROMPT,
        store=store,
        backend=make_memory_backend,
    )
    
    return agent


def run_agent(user_input: str, agent=None, thread_id: str = None) -> str:
    """Run the Deep Agent with user input."""
    import uuid
    
    if agent is None:
        agent = create_twitter_agent()
    
    config_dict = {
        "configurable": {
            "thread_id": thread_id or str(uuid.uuid4())
        }
    }
    
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config_dict
    )
    
    if "messages" in result and result["messages"]:
        return result["messages"][-1].content
    
    return str(result)


def run_autonomous_post(agent=None, thread_id: str = None) -> str:
    """Run autonomous post cycle - no user input needed."""
    command = "Monitor Telegram, scrape yieldbot.cc and multiple crypto sites for real token data, analyze trends and prices from all sources, then create and post comprehensive content based on REAL data. Execute all 7 steps immediately. NO EMOJIS in tweet. Post to Twitter and Telegram, then reply to tweet with website link."
    return run_agent(command, agent, thread_id)


async def run_agent_async(user_input: str, agent=None, thread_id: str = None):
    """Run the Deep Agent asynchronously with streaming."""
    import uuid
    
    if agent is None:
        agent = create_twitter_agent()
    
    config_dict = {
        "configurable": {
            "thread_id": thread_id or str(uuid.uuid4())
        }
    }
    
    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config_dict,
        stream_mode="values"
    ):
        if "messages" in chunk:
            yield chunk["messages"][-1]


def main():
    """Main entry point for the AI Agent."""
    import uuid
    import sys
    
    print("=" * 65)
    print("AI Agent YBot - Deep Agent for Twitter Content Creation")
    print("Powered by: Deep Agents + Composio + Mistral AI + Memory")
    print("=" * 65)
    
    try:
        config.validate()
    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        print("\nPlease create a .env file based on .env.example and add your API keys.")
        print("\nRequired keys:")
        print("  - MISTRAL_API_KEY")
        print("  - COMPOSIO_API_KEY")
        sys.exit(1)
    
    if config.setup_tracing():
        print(f"LangSmith tracing enabled -> Project: {config.LANGSMITH_PROJECT}")
    
    print(f"Memory backend: {config.MEMORY_BACKEND}")
    
    print("\nInitializing Deep Agent with long-term memory...")
    try:
        agent = create_twitter_agent()
        print("Agent ready!\n")
    except Exception as e:
        print(f"Failed to create agent: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    thread_id = str(uuid.uuid4())
    print(f"Thread ID: {thread_id}")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        print("\nAUTONOMOUS MODE - Executing post cycle...\n")
        response = run_autonomous_post(agent, thread_id)
        print("\nRESULT: Post cycle completed successfully!\n")
        print("Check Twitter and Telegram @yieldbotai for the post.\n")
        return
    
    print("\nCommands:")
    print("  - Type 'auto' to run autonomous post cycle")
    print("  - Type your request to interact with the agent")
    print("  - Type 'quit' or 'exit' to stop")
    print("\nExample requests:")
    print("  - 'auto' - Run full autonomous post")
    print("  - 'Create a tweet about AI technology'")
    print("  - 'Remember that I prefer casual, friendly tone'")
    print("  - 'What do you remember about my preferences?'\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye! Your preferences have been saved to memory.")
                break
            
            if user_input.lower() == "auto":
                print("\nRunning autonomous post cycle...\n")
                response = run_autonomous_post(agent, thread_id)
            else:
                print("\nProcessing...")
                response = run_agent(user_input, agent, thread_id)
            
            print(f"\nYBot: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
