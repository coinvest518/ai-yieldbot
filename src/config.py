"""Configuration settings for AI Agent YBot."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SECURITY: prevent accidental Google provider initialization by clearing
# common Google credential env vars if present. This avoids third-party
# libraries probing Google ADC (Application Default Credentials) when
# we explicitly intend to use Mistral.
for _k in ("GOOGLE_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT", "GOOGLE_OAUTH_ACCESS_TOKEN"):
    os.environ.pop(_k, None)


class Config:
    """Application configuration."""
    
    # Mistral AI settings
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
    
    # LangSmith settings (new format)
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "ai-agent-ybot")
    LANGSMITH_ENDPOINT: str = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    
    # Legacy LangChain format (for compatibility)
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "") or os.getenv("LANGSMITH_API_KEY", "")
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true" or LANGSMITH_TRACING
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "") or os.getenv("LANGSMITH_PROJECT", "ai-agent-ybot")
    
    # Composio settings
    COMPOSIO_API_KEY: str = os.getenv("COMPOSIO_API_KEY", "")
    COMPOSIO_PROJECT_ID: str = os.getenv("COMPOSIO_PROJECT_ID", "pr_asakoILZk0P_")
    COMPOSIO_ORG_ID: str = os.getenv("COMPOSIO_ORG_ID", "ok_ciHslaEbAI2t")
    COMPOSIO_USER_ID: str = os.getenv("COMPOSIO_USER_ID", "f7631f58-67ef-454c-bb39-984b3f271f2b")
    
    # Twitter Connected Account (from Composio)
    TWITTER_CONNECTED_ACCOUNT_ID: str = os.getenv("TWITTER_CONNECTED_ACCOUNT_ID", "ca__qCCy0ttpxeh")
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CONNECTED_ACCOUNT_ID: str = os.getenv("TELEGRAM_CONNECTED_ACCOUNT_ID", "ca_ZPVfCDk6sSxt")
    TELEGRAM_AUTH_CONFIG_ID: str = os.getenv("TELEGRAM_AUTH_CONFIG_ID", "")
    
    # Firecrawl settings (for DeFi/crypto research)
    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY", "")
    
    # Memory settings
    MEMORY_BACKEND: str = os.getenv("MEMORY_BACKEND", "memory")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY is required. Please set it in your .env file.")
        if not cls.COMPOSIO_API_KEY:
            raise ValueError("COMPOSIO_API_KEY is required. Please set it in your .env file.")
        return True
    
    @classmethod
    def setup_tracing(cls) -> bool:
        """Set up LangSmith tracing environment variables."""
        if cls.LANGSMITH_TRACING and cls.LANGSMITH_API_KEY:
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGSMITH_API_KEY"] = cls.LANGSMITH_API_KEY
            os.environ["LANGSMITH_PROJECT"] = cls.LANGSMITH_PROJECT
            os.environ["LANGSMITH_ENDPOINT"] = cls.LANGSMITH_ENDPOINT
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = cls.LANGSMITH_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = cls.LANGSMITH_PROJECT
            return True
        return False


config = Config()
