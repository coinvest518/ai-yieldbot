# AI Agent YBot

A **Deep Agent** for Twitter content creation with long-term memory, built with LangChain, LangGraph, Deep Agents, Composio, and Mistral AI.

## 🚀 Features

- **Deep Agents 0.2.8** - Planning, file systems, and subagent capabilities
- **LangChain 1.1.2** - Framework for building LLM applications
- **LangGraph 1.0.4** - Orchestration framework for multi-agent workflows
- **LangSmith 0.4.53** - Tracing and observability platform
- **Composio 0.9.4** - Twitter integration for posting and media upload
- **Mistral AI 1.1.0** - Large language model provider
- **Long-term Memory** - Persistent memory across conversations

## 🧠 Deep Agent Capabilities

This agent uses the `deepagents` library which provides:

| Feature | Description |
|---------|-------------|
| **Planning** | Built-in `write_todos` tool for task decomposition |
| **File System** | `ls`, `read_file`, `write_file`, `edit_file` for context management |
| **Subagents** | `task` tool to spawn specialized subagents |
| **Long-term Memory** | Persistent `/memories/` path survives across conversations |

## 📋 Prerequisites

- Python 3.11 or higher (required by deepagents)
- Mistral AI API key
- Composio API key with Twitter connected

## 🛠️ Installation

1. **Clone and navigate to the project:**
   ```bash
   cd "AI Agent Ybot"
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your API keys
   ```

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
# Required - Mistral AI
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-large-latest

# Required - Composio (for Twitter)
COMPOSIO_API_KEY=your_composio_api_key_here

# Your Composio Account Info
COMPOSIO_PROJECT_ID
COMPOSIO_ORG_ID=
COMPOSIO_USER_ID

# Twitter Connected Account from Composio Dashboard
TWITTER_CONNECTED_ACCOUNT_ID=ca__qCCy0ttpxeh

# Optional - LangSmith Tracing
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ai-agent-ybot

# Memory Backend ('memory' for dev, 'postgres' for production)
MEMORY_BACKEND=memory
# DATABASE_URL=

## 🧠 Long-term Memory

The agent uses a **CompositeBackend** for hybrid memory storage:

| Path | Storage | Persistence |
|------|---------|-------------|
| `/memories/*` | StoreBackend | ✅ Persists across threads |
| Other paths | StateBackend | ❌ Ephemeral (single thread) |

### Memory Structure

```
/memories/
├── preferences.txt      # User preferences and settings
├── content_history.txt  # Past content and performance notes
├── brand_voice.txt      # Brand voice and style guidelines
└── analytics.txt        # Analytics insights and learnings
```

### Memory Examples

```python
# Save preferences (persists forever)
"Remember that I prefer casual, friendly tone"

# Check memories
"What do you remember about my preferences?"

# The agent automatically saves to /memories/ paths
```

## 🏃 Running the Agent

```bash
python -m src.agent
```

## 📁 Project Structure

```
AI Agent Ybot/
├── .github/
│   └── copilot-instructions.md
├── src/
│   ├── __init__.py          # Package initialization
│   ├── agent.py             # Deep Agent with memory
│   ├── config.py            # Configuration settings
│   ├── graph.py             # LangGraph workflow (legacy)
│   └── tools.py             # Twitter & Composio tools
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## 🐦 Twitter Integration

The agent uses Composio's Twitter tools with **exact slug matching**:

| Action | Slug | Description |
|--------|------|-------------|
| Create Post | `TWITTER_CREATION_OF_A_POST` | Create tweets (max 280 chars) |
| Upload Media | `TWITTER_MEDIA_UPLOAD_MEDIA` | Upload images/videos |
| User Info | `TWITTER_USER_LOOKUP_ME` | Get authenticated user |

### Posting a Tweet with Image

```python
# 1. Upload image first
media_result = TWITTER_MEDIA_UPLOAD_MEDIA(media_url="https://...")

# 2. Create post with media_ids
TWITTER_CREATION_OF_A_POST(
    text="Check out this image! 🚀",
    media_media_ids=["<media_id_from_step_1>"]
)
```

## 🔧 Customization

### Adding Custom Tools

Edit `src/tools.py` to add your own tools:

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(input: str) -> str:
    """Description of what the tool does."""
    return f"Result: {input}"
```

### Adding Image Generation

Replace the placeholder in `src/tools.py` with your preferred API:

```python
# Example with OpenAI DALL-E
from openai import OpenAI

@tool
def generate_image(prompt: str) -> dict:
    """Generate an image using DALL-E."""
    client = OpenAI()
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024"
    )
    return {"image_url": response.data[0].url}
```

### Production Memory (PostgreSQL)

For production, use PostgresStore:

```env
MEMORY_BACKEND=postgres
DATABASE_URL=postgresql://user:password@localhost:5432/ybot_memory
```

Install the postgres dependency:
```bash
pip install psycopg2-binary
```

## 🚀 Deployment

### Railway (Recommended)

1. **Connect Repository:**
   - Create new Railway project
   - Connect to your GitHub repository

2. **Environment Variables:**
   ```env
   MISTRAL_API_KEY=your_mistral_key
   COMPOSIO_API_KEY=your_composio_key
   TWITTER_CONNECTED_ACCOUNT_ID=your_twitter_account_id
   LINKEDIN_CONNECTED_ACCOUNT_ID=your_linkedin_account_id
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   FIRECRAWL_API_KEY=your_firecrawl_key
   MEMORY_BACKEND=memory
   ```

3. **Service Configuration:**
   - Railway will automatically use the `Procfile` to start the continuous scheduler
   - The scheduler runs every 90 minutes internally (respects LinkedIn rate limits)
   - No external cron jobs needed - the app manages its own scheduling

### Local Development

```bash
# Run continuous scheduler (runs every 90 minutes)
python scheduler.py

# Run single test
python -c "from src.agent import create_twitter_agent, run_autonomous_post; agent = create_twitter_agent(); run_autonomous_post(agent)"

# Check status
python -c "from scheduler import get_status; import json; print(json.dumps(get_status(), indent=2))"
```

## 🔧 Rate Limits & Optimization

### LinkedIn API Limits
- **Daily limits** reset at midnight UTC
- **Application + Member limits** apply
- **Profile caching** implemented (24-hour cache)
- **429 errors** when limits exceeded
- **Best practice**: Space requests evenly throughout the day

### Twitter API Limits
- **300 posts per 3 hours** for new accounts
- **Unique content required** (duplicate detection)
- **Media uploads** count toward limits

### Optimization Features
- **Profile caching** avoids unnecessary LinkedIn API calls
- **Content uniqueness** enforced with timestamps
- **Regulated scraping** with daily cache
- **Error handling** with automatic retries

MIT License
