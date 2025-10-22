"""
Configuration management for the content-tools-server application.
Loads configuration from environment variables and YAML config file.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
import yaml
from pathlib import Path


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    url: str = Field(..., env="DATABASE_URL")
    
    class Config:
        env_prefix = ""


class OpenAIConfig(BaseSettings):
    """OpenAI configuration."""
    api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")
    
    class Config:
        env_prefix = ""


class TelegramConfig(BaseSettings):
    """Telegram configuration."""
    bot_token: Optional[str] = Field(None, env="TELEGRAM_BOT_TOKEN")
    
    class Config:
        env_prefix = ""


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    level: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_prefix = ""


class AppConfig:
    """Main application configuration."""
    
    def __init__(self):
        # Load environment-based configs
        self.database = DatabaseConfig()
        self.openai = OpenAIConfig()
        self.telegram = TelegramConfig()
        self.logging = LoggingConfig()
        
        # Load YAML config
        self._load_yaml_config()
    
    def _load_yaml_config(self):
        """Load configuration from YAML file."""
        config_file = Path("config.yaml")
        if not config_file.exists():
            # Use example config if main config doesn't exist
            config_file = Path("config.yaml.example")
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
                
                # RSSHub configuration
                self.rsshub_base = yaml_config.get('rsshub_base', 'https://rsshub.app')
                
                # Fetch configuration
                fetch_config = yaml_config.get('fetch', {})
                self.fetch_timeout = fetch_config.get('request_timeout_seconds', 12)
                self.user_agent = fetch_config.get('user_agent', 'content-tools-bot/1.0')
                
                # Scheduler configuration
                scheduler_config = yaml_config.get('scheduler', {})
                self.ingest_cron = scheduler_config.get('ingest_cron', '0 * * * *')
                self.transform_cron = scheduler_config.get('transform_cron', '5 * * * *')
                self.publish_cron = scheduler_config.get('publish_cron', '10 * * * *')
                
                # NLP configuration
                nlp_config = yaml_config.get('nlp', {})
                self.nlp_provider = nlp_config.get('provider', 'openai')
                self.summary_prompt_template = nlp_config.get('summary_prompt_template', 
                    'Сожми текст в 2–3 предложения новостного формата на русском, без воды.\n'
                    'Выдели факт/событие и итог для читателя.\n'
                    'Текст:\n{text}')
                
                # Telegram configuration
                telegram_config = yaml_config.get('telegram', {})
                self.telegram_parse_mode = telegram_config.get('parse_mode', 'HTML')
                self.telegram_disable_preview = telegram_config.get('disable_web_page_preview', False)
                
                # Publish configuration
                publish_config = yaml_config.get('publish', {})
                self.publish_default_type = publish_config.get('default_type', 'text')
        else:
            # Default values if no config file exists
            self.rsshub_base = 'https://rsshub.app'
            self.fetch_timeout = 12
            self.user_agent = 'content-tools-bot/1.0'
            self.ingest_cron = '0 * * * *'
            self.transform_cron = '5 * * * *'
            self.publish_cron = '10 * * * *'
            self.nlp_provider = 'openai'
            self.summary_prompt_template = (
                'Сожми текст в 2–3 предложения новостного формата на русском, без воды.\n'
                'Выдели факт/событие и итог для читателя.\n'
                'Текст:\n{text}'
            )
            self.telegram_parse_mode = 'HTML'
            self.telegram_disable_preview = False
            self.publish_default_type = 'text'


# Global config instance
config = AppConfig()
