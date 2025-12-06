# AI Agent YBot - Project Instructions

## Overview
This is a **Deep Agent** project for Twitter content creation with long-term memory, using:
- **Deep Agents 0.2.8** - Planning, file systems, subagents, and memory
- **LangChain 1.1.2** - Framework for building LLM applications
- **LangGraph 1.0.4** - Orchestration framework for multi-agent workflows
- **LangSmith 0.4.53** - Tracing and debugging platform for LLM apps
- **Composio 0.9.4** - Twitter integration (exact slug matching required)
- **Mistral AI 1.1.0** - Large language model provider

## Project Structure
```
AI Agent Ybot/
├── .github/
│   └── copilot-instructions.md
├── src/
│   ├── __init__.py
│   ├── agent.py          # Deep Agent with memory
│   ├── graph.py          # Legacy LangGraph workflow
│   ├── tools.py          # Twitter & Composio tools
│   └── config.py         # Configuration settings
├── .env.example          # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

## Deep Agent Architecture
The agent uses `deepagents` library features:
- **Planning**: `write_todos` tool for task decomposition
- **File System**: `ls`, `read_file`, `write_file`, `edit_file`
- **Subagents**: `task` tool for context isolation
- **Long-term Memory**: CompositeBackend with `/memories/` path routing

## Composio Twitter Integration
Use EXACT slugs as shown in Composio dashboard:
- `TWITTER_CREATION_OF_A_POST` - Create tweets
- `TWITTER_MEDIA_UPLOAD_MEDIA` - Upload media
- `TWITTER_USER_LOOKUP_ME` - Get user info

Connected Account ID: `ca_Ka8OgruDXnxe`

## Development Guidelines
- Use Python 3.11+ (required by deepagents)
- Store API keys in `.env` file (never commit to git)
- Follow PEP 8 coding standards
- Use type hints for function signatures

## Environment Variables Required
- `MISTRAL_API_KEY` - Mistral AI API key
- `COMPOSIO_API_KEY` - Composio API key
- `TWITTER_CONNECTED_ACCOUNT_ID` - From Composio dashboard
- `LANGCHAIN_API_KEY` - LangSmith API key (optional)
- `MEMORY_BACKEND` - 'memory' or 'postgres'

## Running the Agent
1. Activate virtual environment: `.venv\Scripts\activate`
2. Run: `python -m src.agent`
